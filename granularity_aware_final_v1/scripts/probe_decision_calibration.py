#!/usr/bin/env python3
"""Forward-only in-domain decision-calibration probe on dense_test.jsonl.

Diagnoses whether the trained decision score s = meanLogP(<SPEAK>) - meanLogP(<SILENT>)
actually SEPARATES gold SPEAK from gold SILENT examples in-domain, versus just
raising the correct target's absolute likelihood (which is all Ld directly
optimizes for). Also compares against the same base model with the LoRA
adapter disabled (zero-shot, in-domain, same frames) for a matched reference.
No training; single forward passes only.
"""
import argparse, json, random, sys
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from final_common import decision_tokens, decode_prefix, device_batch, load_model, load_processor, make_prompt_inputs
from scripts.train_granularity_aware import forward_suffix, content_tokens  # reuse exact scoring math

DATA = Path('/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1/data/dense_test.jsonl')


def load_jsonl(path):
    with open(path) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def build_sample(n_per_bucket, seed):
    rng = random.Random(seed)
    buckets = {'coarse_speak': [], 'coarse_silent': [], 'fine_speak': [], 'fine_silent': []}
    reservoir_i = {k: 0 for k in buckets}
    for row in load_jsonl(DATA):
        keys = []
        if row['coarse_decision'] == 'SPEAK':
            keys.append('coarse_speak')
        else:
            keys.append('coarse_silent')
        if row['fine_decision'] == 'SPEAK':
            keys.append('fine_speak')
        else:
            keys.append('fine_silent')
        for k in keys:
            reservoir_i[k] += 1
            b = buckets[k]
            if len(b) < n_per_bucket:
                b.append(row)
            else:
                j = rng.randint(0, reservoir_i[k] - 1)
                if j < n_per_bucket:
                    b[j] = row
    seen = {}
    for k, rows in buckets.items():
        for row in rows:
            seen[row['pair_id']] = row
    return list(seen.values()), buckets


@torch.inference_mode()
def score_row(model, processor, speak_tokens, silent_tokens, row, device, adapter_ctx):
    video, meta, _ = decode_prefix(row)
    out = {}
    for gran in ('COARSE', 'FINE'):
        prompt_inputs = make_prompt_inputs(row, gran, processor, video, meta)
        with adapter_ctx():
            lp_s = forward_suffix(model, prompt_inputs, speak_tokens, device)
            lp_l = forward_suffix(model, prompt_inputs, silent_tokens, device)
        out[gran] = float(lp_s.mean() - lp_l.mean())
    return out


def summarize(scores, golds, label):
    import statistics as st
    speak_s = [s for s, g in zip(scores, golds) if g == 'SPEAK']
    silent_s = [s for s, g in zip(scores, golds) if g == 'SILENT']
    correct = sum((s > 0) == (g == 'SPEAK') for s, g in zip(scores, golds))
    acc = correct / len(golds) if golds else float('nan')
    m_speak = st.mean(speak_s) if speak_s else float('nan')
    m_silent = st.mean(silent_s) if silent_s else float('nan')
    sd_speak = st.pstdev(speak_s) if len(speak_s) > 1 else float('nan')
    sd_silent = st.pstdev(silent_s) if len(silent_s) > 1 else float('nan')
    print(f'{label:28s} n={len(golds):4d} acc={acc:.3f}  mean_s|SPEAK={m_speak:+.3f}(sd{sd_speak:.2f})  '
          f'mean_s|SILENT={m_silent:+.3f}(sd{sd_silent:.2f})  gap={m_speak - m_silent:+.3f}')
    return {'n': len(golds), 'acc': acc, 'mean_s_speak': m_speak, 'mean_s_silent': m_silent, 'gap': m_speak - m_silent}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backbone', default='qwen')
    ap.add_argument('--adapter', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--n-per-bucket', type=int, default=100)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--device', default='cuda:0')
    args = ap.parse_args()

    from peft import PeftModel
    processor = load_processor(args.backbone)
    speak_tokens, silent_tokens = decision_tokens(processor.tokenizer)
    is_full_checkpoint = not Path(args.adapter, 'adapter_config.json').exists()
    if is_full_checkpoint:
        # Full-SFT checkpoint: complete finetuned weights, load directly (no base+delta).
        import torch as _torch
        from transformers import Qwen3VLForConditionalGeneration, Gemma3ForConditionalGeneration
        cls = Qwen3VLForConditionalGeneration if args.backbone == 'qwen' else Gemma3ForConditionalGeneration
        model = cls.from_pretrained(args.adapter, local_files_only=True, torch_dtype=_torch.bfloat16,
                                     attn_implementation='sdpa', device_map={'': args.device})
    else:
        base = load_model(args.backbone, args.device)
        model = PeftModel.from_pretrained(base, args.adapter, is_trainable=False, local_files_only=True)
    model.eval()

    rows, buckets = build_sample(args.n_per_bucket, args.seed)
    print(f'sampled {len(rows)} unique rows '
          f'(coarse_speak={len(buckets["coarse_speak"])}, coarse_silent={len(buckets["coarse_silent"])}, '
          f'fine_speak={len(buckets["fine_speak"])}, fine_silent={len(buckets["fine_silent"])})', flush=True)

    results = {'finetuned': {'COARSE': [], 'FINE': []}, 'zero_shot': {'COARSE': [], 'FINE': []}}
    golds = {'COARSE': [], 'FINE': []}
    errors = 0
    import contextlib
    for i, row in enumerate(rows):
        try:
            ft = score_row(model, processor, speak_tokens, silent_tokens, row, args.device,
                            lambda: contextlib.nullcontext())
            # Full-SFT checkpoints have no base weights to fall back to (no
            # disable_adapter path); zero-shot numbers for this base model are
            # already recorded from the LoRA probes and are identical here.
            zs = None if is_full_checkpoint else score_row(
                model, processor, speak_tokens, silent_tokens, row, args.device, model.disable_adapter)
        except Exception as e:
            errors += 1
            print(f'  [skip row {i}: {e!r}]', flush=True)
            continue
        for gran in ('COARSE', 'FINE'):
            results['finetuned'][gran].append(ft[gran])
            if zs is not None:
                results['zero_shot'][gran].append(zs[gran])
        golds['COARSE'].append(row['coarse_decision'])
        golds['FINE'].append(row['fine_decision'])
        if (i + 1) % 25 == 0:
            print(f'  ...{i+1}/{len(rows)} scored, {errors} errors', flush=True)

    print(f'\n=== {args.tag} (backbone={args.backbone}, adapter={args.adapter}) ===')
    print(f'errors_skipped={errors}\n')
    summary = {}
    variants = ('finetuned',) if is_full_checkpoint else ('finetuned', 'zero_shot')
    for variant in variants:
        for gran in ('COARSE', 'FINE'):
            summary[f'{variant}_{gran}'] = summarize(results[variant][gran], golds[gran], f'{variant}/{gran}')

    out_path = Path(f'/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1/reports/calibration_probe_{args.tag}.json')
    out_path.write_text(json.dumps({'tag': args.tag, 'adapter': args.adapter, 'n_per_bucket': args.n_per_bucket,
                                     'seed': args.seed, 'errors_skipped': errors, 'summary': summary}, indent=2) + '\n')
    print(f'\nwrote {out_path}')


if __name__ == '__main__':
    main()
