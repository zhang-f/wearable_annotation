"""Shared multimodal preparation for corrected granularity-aware SFT.

The one manifest row is the canonical visual prefix. `prepare_pair` decodes it
once and reuses the same in-memory RGB array for COARSE and FINE prompts.
"""
import json, os, random, re
from pathlib import Path
import av
import numpy as np
import torch

PROJECT = Path('/data/fan/projects/procedure_forecasting')
ROOT = PROJECT / 'runs/granularity_aware_final_v1'
MODELS = {'qwen': '/data/fan/models/Qwen3-VL-8B-Instruct', 'gemma': '/data/fan/models/Gemma-3-12B-IT'}


def seed_all(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)


def atomic_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp'); tmp.write_text(json.dumps(value, indent=2) + '\n'); tmp.replace(path)


def prompt(row, granularity):
    if granularity == 'COARSE':
        return f"Goal: {row['goal']}\nGranularity: COARSE\n\nShould the assistant predict the next high-level subtask now?"
    current = row['current_subtask'] or 'No active subtask is available.'
    return f"Goal: {row['goal']}\nCurrent subtask: {current}\nGranularity: FINE\n\nShould the assistant predict the next fine-grained action now?"


def decode_prefix(row):
    """Decode exactly the saved canonical prefix requests, never a future PTS."""
    wanted = list(map(float, row['frame_timestamps']))
    frames, actual = [], []
    # Repeated timestamps are intentional early-prefix padding; decode once.
    cache = {}
    with av.open(row['video_path']) as container:
        stream = container.streams.video[0]
        stream.thread_type = 'SLICE'; stream.codec_context.thread_count = 1
        tb = float(stream.time_base)
        for timestamp in wanted:
            key = round(timestamp, 8)
            if key not in cache:
                container.seek(max(0, int((timestamp + 1e-8) / tb)), stream=stream, backward=True, any_frame=False)
                best = None
                for frame in container.decode(stream):
                    ft = float(frame.pts * stream.time_base)
                    if ft > timestamp + 1e-7:
                        break
                    best = frame
                if best is None:
                    raise RuntimeError(f'No frame at/before saved PTS {timestamp}: {row["video_id"]}')
                ft = float(best.pts * stream.time_base)
                if ft > timestamp + 1e-7 or ft > float(row['query_time']) + 1e-7:
                    raise RuntimeError(f'Future frame selected {ft}>{timestamp}/{row["query_time"]}')
                cache[key] = (best.to_ndarray(format='rgb24'), ft)
            image, ft = cache[key]; frames.append(image); actual.append(ft)
        meta = {'total_num_frames': int(stream.frames or 0), 'fps': float(stream.average_rate),
                'duration': float(stream.duration * stream.time_base) if stream.duration else float(row['query_time']),
                'frames_indices': list(row['frame_indices']), 'video_backend': 'pyav'}
    if len(frames) != 16 or max(actual) > float(row['query_time']) + 1e-7:
        raise RuntimeError('Canonical visual-prefix assertion failed')
    return np.stack(frames), meta, actual


def load_processor(backbone):
    from transformers import AutoProcessor
    return AutoProcessor.from_pretrained(MODELS[backbone], local_files_only=True)


def make_prompt_inputs(row, granularity, processor, video, metadata):
    text_prompt = prompt(row, granularity)
    if granularity == 'COARSE':
        assert 'Current subtask:' not in text_prompt
    if 'qwen' in str(processor.__class__).lower() or 'Qwen' in getattr(processor, 'name_or_path', ''):
        messages = [{'role': 'user', 'content': [{'type': 'video'}, {'type': 'text', 'text': text_prompt}]}]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        out = processor(text=[text], videos=[video], video_metadata=[metadata], do_sample_frames=False,
                        size={'shortest_edge': 4096, 'longest_edge': 384 * 384 * 16}, return_tensors='pt')
    else:
        # Gemma3's fixed 896x896-per-image SigLIP tower (no size override
        # available) plus fp32 q_norm/k_norm upcasting makes the full 16-frame
        # canonical prefix OOM at 8-way DDP even for LoRA (~136GB/rank
        # observed). Emergency mitigation: halve to every-other-frame (8
        # images) for Gemma only, to roughly halve sequence length/attention
        # memory. This is an asymmetric protocol vs Qwen's 16 frames --
        # documented, not silently identical.
        gemma_frames = list(video)[::2]
        messages = [{'role': 'user', 'content': [{'type': 'image'} for _ in range(len(gemma_frames))] + [{'type': 'text', 'text': text_prompt}]}]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        out = processor(text=[text], images=[gemma_frames], return_tensors='pt')
    return dict(out)


def append_tokens(inputs, tokens):
    """Append assistant-only suffix while retaining visual processor fields."""
    result = dict(inputs)
    original = inputs['input_ids'].shape[1]
    result['input_ids'] = torch.cat([inputs['input_ids'], tokens], dim=1)
    result['attention_mask'] = torch.ones_like(result['input_ids'])
    if 'token_type_ids' in inputs:
        # Gemma's video/image prompt tokens use their original type; assistant
        # continuation uses text token type zero, matching the old stable code.
        result['token_type_ids'] = torch.cat([inputs['token_type_ids'], torch.zeros_like(tokens)], dim=1)
    return result, original


def device_batch(inputs, device):
    return {k: v.to(device=device, dtype=torch.bfloat16 if v.is_floating_point() else v.dtype) if torch.is_tensor(v) else v for k,v in inputs.items()}


def load_model(backbone, device):
    if backbone == 'qwen':
        from transformers import Qwen3VLForConditionalGeneration
        cls = Qwen3VLForConditionalGeneration
    else:
        from transformers import Gemma3ForConditionalGeneration
        cls = Gemma3ForConditionalGeneration
    # device_map is Accelerate's dispatch mechanism for spreading one model
    # across devices/offload targets; combining it with DDP (which expects a
    # plain single-device nn.Module) is a known anti-pattern that leaves extra
    # dispatch bookkeeping/copies resident. Load on CPU, then move explicitly.
    model = cls.from_pretrained(MODELS[backbone], local_files_only=True, torch_dtype=torch.bfloat16,
                                attn_implementation='sdpa')
    return model.to(device)


def configure_trainable(model, backbone, mode):
    """Freeze vision encoder; full mode trains language + projector/merger."""
    from peft import LoraConfig, get_peft_model
    suffix = {'q_proj','k_proj','v_proj','o_proj','up_proj','down_proj','gate_proj'}
    language_targets = [n for n,m in model.named_modules() if n.startswith('model.language_model.') and n.rsplit('.',1)[-1] in suffix and isinstance(m, torch.nn.Linear)]
    if not language_targets:
        raise RuntimeError(f'No language projection modules found for {backbone}')
    if mode == 'lora':
        model.requires_grad_(False)
        # LoRA dropout (0.05, matches Qwen) inserts nn.Dropout before lora_A;
        # a memory snapshot showed native_dropout_cuda's saved masks as the
        # actual site of Gemma3's ~85GB/step blowup (its wider MLP intermediate
        # dim across 48 layers makes each mask far larger than Qwen's) -- not
        # DDP, device_map, frame count, or gradient checkpointing, all of
        # which were ruled out first. Disabling dropout only for Gemma (PEFT
        # substitutes nn.Identity when lora_dropout=0) keeps Qwen's already-
        # completed runs' protocol unchanged.
        lora_dropout = 0.0 if backbone == 'gemma' else .05
        model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=lora_dropout, target_modules=language_targets, bias='none', task_type='CAUSAL_LM'))
        # PEFT creates new LoRA A/B weights in fp32 by default regardless of
        # the base model's dtype. Every LoRA-adapted forward then casts its
        # full-width input activation fp32 up, and the full-width result back
        # down (peft/tuners/lora/layer.py: _cast_input_dtype + the trailing
        # `result.to(torch_result_dtype)`) -- a memory snapshot showed this as
        # the dominant cost (tens of GB across 336 targets x 48 layers on
        # Gemma3's wide MLP), well beyond the smaller dropout-mask cost fixed
        # above. Casting LoRA weights to match the frozen base's bf16 makes
        # both casts no-ops.
        for n, p in model.named_parameters():
            if 'lora_' in n:
                p.data = p.data.to(torch.bfloat16)
        trainable = [n for n,p in model.named_parameters() if p.requires_grad]
    else:
        for name, param in model.named_parameters():
            # All visual encoder layers stay frozen. A named merger/projector
            # is intentionally trainable when exposed by the architecture.
            is_visual_encoder = ('visual' in name or 'vision' in name) and not any(x in name for x in ('merger', 'projector', 'multi_modal_projector'))
            param.requires_grad_(not is_visual_encoder)
        trainable = [n for n,p in model.named_parameters() if p.requires_grad]
    if not trainable:
        raise RuntimeError('No trainable parameters')
    return model, language_targets, trainable


def decision_tokens(tokenizer):
    speak = tokenizer('<SPEAK>', add_special_tokens=False, return_tensors='pt')['input_ids']
    silent = tokenizer('<SILENT>', add_special_tokens=False, return_tensors='pt')['input_ids']
    if speak.numel() == 0 or silent.numel() == 0:
        raise RuntimeError('Decision strings tokenized to an empty sequence')
    return speak, silent

