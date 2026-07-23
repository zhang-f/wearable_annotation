#!/usr/bin/env python3
"""Batch Chinese->English short-phrase translation for annotation
descriptions. Text-only, no vision -- uses Qwen3-8B (a plain text model),
downloaded from Hugging Face on first use if not already cached.

OPTIONAL FEATURE, requires a GPU with ~16GB free VRAM (or a lot of
patience on CPU) and ~16GB disk for the model weights. If you don't have
that, the tool still works fine -- just type your description directly
into the English field in the marks list instead of using the Chinese
popup; server.py already catches any failure here (missing torch/
transformers, no GPU, OOM, etc.) and reports it as a translate error in
the UI rather than crashing.

Lazily loaded on first /api/translate_point call and kept resident for
the life of the server process. Uses whatever GPU device_map="auto" picks
by default -- no hardcoded device index, since that would only be valid
on one specific machine.
"""
from __future__ import annotations

import os
import re

os.environ.setdefault("HF_HUB_OFFLINE", "0")  # allow the first-run download; set to "1" yourself once cached if you want to force offline

MODEL_ID = "Qwen/Qwen3-8B"

_model = None
_tokenizer = None


def _ensure_loaded():
    global _model, _tokenizer
    if _model is not None:
        return
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    _model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.bfloat16, device_map="auto")


PROMPT_TEMPLATE = """You translate short Chinese action-step descriptions into short English phrases for a video annotation tool.

Rules (follow exactly):
- Each output starts with a verb in base form (present tense), e.g. "attach", "pour", "pick up".
- Keep it short: 2-6 words.
- Style examples: "attach the cabin", "pour water into cup", "pick up the peeler".
- Keep the SAME granularity/level of detail as the Chinese input. If the Chinese is coarse/high-level, keep the English coarse. If the Chinese is a fine, specific sub-action, keep the English equally specific. Do NOT summarize, generalize, or add details that are not in the Chinese text.
- Keep wording style consistent across all lines in this batch (they are all steps from the same video).
- Output EXACTLY {n} lines, one per input, in the same order, each formatted as "N. english phrase" where N is the input number.
- Do not add any preamble, explanation, or extra lines.

Input Chinese phrases:
{numbered_input}

Output:"""


def translate_batch(zh_list: list[str]) -> list[str]:
    """zh_list -> list of English phrases, same length/order. Empty strings
    in zh_list pass through as empty strings without calling the model for
    them (but they still occupy a slot so the caller can zip by index)."""
    non_empty_idx = [i for i, z in enumerate(zh_list) if z.strip()]
    if not non_empty_idx:
        return ["" for _ in zh_list]

    _ensure_loaded()
    import torch

    numbered_input = "\n".join(f"{k + 1}. {zh_list[i]}" for k, i in enumerate(non_empty_idx))
    prompt = PROMPT_TEMPLATE.format(n=len(non_empty_idx), numbered_input=numbered_input)

    messages = [{"role": "user", "content": prompt}]
    # Qwen3 defaults to "thinking" mode (long <think> block before the
    # answer) -- disabled explicitly, this is a simple formatting task and
    # thinking mode would blow past max_new_tokens before reaching the
    # actual numbered output.
    text = _tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )
    inputs = _tokenizer([text], return_tensors="pt").to(_model.device)

    with torch.no_grad():
        out_ids = _model.generate(
            **inputs,
            max_new_tokens=64 + 16 * len(non_empty_idx),
            do_sample=False,
        )
    new_tokens = out_ids[0][inputs["input_ids"].shape[1]:]
    decoded = _tokenizer.decode(new_tokens, skip_special_tokens=True)

    parsed: dict[int, str] = {}
    for line in decoded.splitlines():
        m = re.match(r"\s*(\d+)\.\s*(.+?)\s*$", line)
        if m:
            parsed[int(m.group(1))] = m.group(2)

    result = ["" for _ in zh_list]
    for k, i in enumerate(non_empty_idx):
        result[i] = parsed.get(k + 1, "")
    return result
