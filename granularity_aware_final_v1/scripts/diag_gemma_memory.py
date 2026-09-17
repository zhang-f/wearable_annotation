#!/usr/bin/env python3
"""Single-GPU, no-DDP diagnostic: isolate why Gemma full-SFT OOMs on the very
first forward calls. Checks whether gradient_checkpointing_enable() actually
takes effect for Gemma3ForConditionalGeneration, and reports peak memory after
each forward call within one training microstep (no optimizer, no backward
across multiple branches -- just instrumented single calls)."""
import json, sys, torch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from final_common import configure_trainable, decision_tokens, decode_prefix, device_batch, load_model, load_processor, make_prompt_inputs, append_tokens

DEVICE = 'cuda:0'

def mem():
    return torch.cuda.memory_allocated(DEVICE) / 1e9

def main():
    torch.cuda.init()
    torch.cuda.set_device(DEVICE)
    torch.cuda.reset_peak_memory_stats(DEVICE)
    print(f'[start] allocated={mem():.2f}GB', flush=True)

    processor = load_processor('gemma')
    speak_tokens, silent_tokens = decision_tokens(processor.tokenizer)
    model = load_model('gemma', DEVICE)
    print(f'[after load_model] allocated={mem():.2f}GB', flush=True)

    model, targets, trainable = configure_trainable(model, 'gemma', 'lora')
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f'[after configure_trainable] allocated={mem():.2f}GB trainable_params={n_trainable}', flush=True)

    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    # Report whatever checkpointing flags HF actually set, at every submodule level.
    flags = {}
    for name, mod in model.named_modules():
        if hasattr(mod, 'gradient_checkpointing'):
            flags[name] = mod.gradient_checkpointing
    print('[gradient_checkpointing flags]', json.dumps(flags), flush=True)
    print(f'[after gradient_checkpointing_enable] allocated={mem():.2f}GB', flush=True)

    model.train()

    # Load one real training row to build a realistic prompt+16-frame video input.
    row = json.loads(next(open('/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1/data/dense_train.jsonl')))
    # Find a row with a real coarse_target so content forward is exercised too.
    for line in open('/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1/data/dense_train.jsonl'):
        r = json.loads(line)
        if r.get('coarse_decision') == 'SPEAK' and r.get('coarse_target'):
            row = r
            break
    video, meta, _ = decode_prefix(row)
    print(f'[after decode_prefix] allocated={mem():.2f}GB', flush=True)

    c_in = make_prompt_inputs(row, 'COARSE', processor, video, meta)
    print(f'[after make_prompt_inputs COARSE] allocated={mem():.2f}GB', flush=True)

    def forward_suffix(suffix):
        inputs, original = append_tokens(c_in, suffix)
        out = model(**device_batch(inputs, DEVICE), use_cache=False)
        return out, original

    torch.cuda.reset_peak_memory_stats(DEVICE)
    out1, orig1 = forward_suffix(silent_tokens)
    print(f'[after forward #1 (SILENT probe)] allocated={mem():.2f}GB peak={torch.cuda.max_memory_allocated(DEVICE)/1e9:.2f}GB', flush=True)

    out2, orig2 = forward_suffix(speak_tokens)
    print(f'[after forward #2 (SPEAK probe, graph #1 still retained)] allocated={mem():.2f}GB peak={torch.cuda.max_memory_allocated(DEVICE)/1e9:.2f}GB', flush=True)

    logits1 = out1.logits[:, orig1 - 1: orig1 - 1 + silent_tokens.shape[1], :]
    logits2 = out2.logits[:, orig2 - 1: orig2 - 1 + speak_tokens.shape[1], :]
    loss = -torch.nn.functional.log_softmax(logits1.float(), -1).mean() - torch.nn.functional.log_softmax(logits2.float(), -1).mean()
    loss.backward()
    print(f'[after combined backward] allocated={mem():.2f}GB peak={torch.cuda.max_memory_allocated(DEVICE)/1e9:.2f}GB', flush=True)

    # --- Now replicate the REAL SPEAK+content forward, which the first test skipped. ---
    model.zero_grad(set_to_none=True)
    del out1, out2, logits1, logits2, loss
    torch.cuda.empty_cache()
    print(f'[after cleanup] allocated={mem():.2f}GB', flush=True)

    content = ' ' + row['coarse_target']
    content_ids = processor.tokenizer(content, add_special_tokens=False, return_tensors='pt')['input_ids']
    print(f'[content] n_tokens={content_ids.shape[1]} text={content!r}', flush=True)
    suffix_s = torch.cat([speak_tokens, content_ids], 1)
    torch.cuda.reset_peak_memory_stats(DEVICE)
    out3, orig3 = forward_suffix(suffix_s)
    print(f'[after forward #3 (SPEAK+CONTENT, {suffix_s.shape[1]} suffix tokens)] allocated={mem():.2f}GB peak={torch.cuda.max_memory_allocated(DEVICE)/1e9:.2f}GB', flush=True)
    logits3 = out3.logits[:, orig3 - 1: orig3 - 1 + suffix_s.shape[1], :]
    loss3 = -torch.nn.functional.log_softmax(logits3.float(), -1).mean()
    loss3.backward()
    print(f'[after backward #3] allocated={mem():.2f}GB peak={torch.cuda.max_memory_allocated(DEVICE)/1e9:.2f}GB', flush=True)

    # Now do it again but WITHOUT freeing graph #1/#2 first -- simulate the real
    # training loop's four accumulated forwards (COARSE SILENT, COARSE SPEAK+content,
    # then a second FINE pair) all alive before one shared backward.
    model.zero_grad(set_to_none=True)
    del out3, logits3, loss3
    torch.cuda.empty_cache()
    print(f'[after cleanup 2] allocated={mem():.2f}GB', flush=True)
    torch.cuda.reset_peak_memory_stats(DEVICE)
    outA, origA = forward_suffix(silent_tokens)
    print(f'[4fwd: after #1 SILENT] allocated={mem():.2f}GB peak={torch.cuda.max_memory_allocated(DEVICE)/1e9:.2f}GB', flush=True)
    outB, origB = forward_suffix(suffix_s)
    print(f'[4fwd: after #2 SPEAK+CONTENT] allocated={mem():.2f}GB peak={torch.cuda.max_memory_allocated(DEVICE)/1e9:.2f}GB', flush=True)
    f_in = make_prompt_inputs(row, 'FINE', processor, video, meta)
    def forward_suffix_f(suffix):
        inputs, original = append_tokens(f_in, suffix)
        out = model(**device_batch(inputs, DEVICE), use_cache=False)
        return out, original
    outC, origC = forward_suffix_f(silent_tokens)
    print(f'[4fwd: after #3 FINE-SILENT] allocated={mem():.2f}GB peak={torch.cuda.max_memory_allocated(DEVICE)/1e9:.2f}GB', flush=True)
    outD, origD = forward_suffix_f(silent_tokens)
    print(f'[4fwd: after #4 FINE-SILENT-again] allocated={mem():.2f}GB peak={torch.cuda.max_memory_allocated(DEVICE)/1e9:.2f}GB', flush=True)
    lA = outA.logits[:, origA-1:origA-1+silent_tokens.shape[1], :]
    lB = outB.logits[:, origB-1:origB-1+suffix_s.shape[1], :]
    lC = outC.logits[:, origC-1:origC-1+silent_tokens.shape[1], :]
    lD = outD.logits[:, origD-1:origD-1+silent_tokens.shape[1], :]
    total_loss = sum(-torch.nn.functional.log_softmax(l.float(), -1).mean() for l in (lA,lB,lC,lD))
    total_loss.backward()
    print(f'[4fwd: after combined backward] allocated={mem():.2f}GB peak={torch.cuda.max_memory_allocated(DEVICE)/1e9:.2f}GB', flush=True)


if __name__ == '__main__':
    main()
