#!/usr/bin/env python3
"""Merge granularity_aware_final_v1 EgoProactive finetuned-only shards and score them
with the official starter-kit scorer, without touching runs/egoproactive_eval_v1's
own predictions/reports (the old baseline outputs)."""
import argparse, json, sys
from pathlib import Path

BENCH = Path('/data/fan/projects/procedure_forecasting/runs/egoproactive_eval_v1')
STARTER = BENCH / 'data/wearable-ai/starter_kit'
DATA = BENCH / 'data/wearable-ai/egoproactive/wearable_ai_2026_egoproactive_val_700.jsonl'
ROOT = Path('/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1/egoproactive')
REPORTS = Path('/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1/reports')

sys.path.insert(0, str(STARTER))
from run_evaluation import score_proactive


def read(path):
    with open(path) as f:
        return [json.loads(x) for x in f if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backbone', choices=('qwen', 'gemma'), required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--world-size', type=int, default=8)
    args = ap.parse_args()

    golden = read(DATA)
    merged = {}
    for rank in range(args.world_size):
        p = ROOT / 'predictions' / f'{args.backbone}_finetuned_{args.tag}_rank{rank}.jsonl'
        if not p.exists():
            continue
        for rec in read(p):
            key = rec['video_path']
            if key in merged:
                raise ValueError(f'duplicate {key} in {args.backbone}/{args.tag}')
            merged[key] = rec

    expected = {r['video_path'] for r in golden}
    missing = sorted(expected - set(merged))
    extras = sorted(set(merged) - expected)
    if extras:
        raise ValueError(f'unexpected predictions: {extras[:5]}')

    errors = []
    ordered = []
    for g in golden:
        p = merged.get(g['video_path'])
        if p is None:
            p = {'video_path': g['video_path'], 'answers': []}
        if len(p.get('answers', [])) != len(g['answers']):
            errors.append({
                'video_path': g['video_path'],
                'gold_chunks': len(g['answers']),
                'pred_chunks': len(p.get('answers', [])),
            })
        ordered.append(p)

    REPORTS.mkdir(exist_ok=True)
    out = ROOT / 'predictions' / f'{args.backbone}_finetuned_{args.tag}.jsonl'
    out.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in ordered))

    score = score_proactive(golden, ordered)
    (REPORTS / f'{args.backbone}_finetuned_{args.tag}_metrics.json').write_text(
        json.dumps(score, indent=2) + '\n'
    )

    model_errors = []
    for p in sorted(ROOT.glob(f'logs/{args.backbone}_errors_{args.tag}_rank*.jsonl')):
        for rec in read(p):
            model_errors.append({'log_file': p.name, **rec})
    (REPORTS / f'{args.backbone}_finetuned_{args.tag}_integrity.json').write_text(
        json.dumps({
            'expected_sessions': len(golden),
            'missing_sessions': missing,
            'chunk_length_mismatch': errors,
            'inference_errors': model_errors,
        }, indent=2) + '\n'
    )

    print(args.backbone, args.tag, 'overall', score['overall'],
          'missing_sessions', len(missing), 'chunk_length_mismatch', len(errors),
          'inference_errors', len(model_errors))


if __name__ == '__main__':
    main()
