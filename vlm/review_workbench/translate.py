#!/usr/bin/env python3
"""Chinese->English translation + format unification for reviewer-typed segment
summaries. Any summary a reviewer submits (via the edit action or the add
action's new-segment text) is routed through here before being stored, so the
corpus stays uniformly English and in the existing corpus's style regardless
of what language/format the reviewer typed in.

Two paths:
- Contains CJK characters -> one text-only call to the already-running vLLM
  instance (reuses the deployed Qwen3-VL-8B-Instruct server, no new
  dependency/service). Falls back to local normalization of the raw text if
  the model call fails or returns something unusable, so a translation outage
  never blocks a reviewer's edit.
- Pure ASCII/English input -> local normalization only (no network round
  trip; keeps ordinary English edits fast).

Format convention matched to the existing corpus (see prompt_template_v3.md /
outputs/final/*_qc.jsonl): lowercase-started, "hand"/"left hand"/"right hand"
+ verb + object phrasing, no trailing punctuation, single spaces.

Requires the frozen chain's vLLM server (see ../RUNBOOK.md) reachable at
$VLM_TRANSLATE_URL (default http://localhost:8000/v1). Optional -- if it's
not running or unreachable, every call transparently falls back to
local_normalize() (see translate_and_normalize below), so the workbench is
still fully usable for English-only editing without it.
"""
import os, re

VLM_BASE_URL = os.environ.get("VLM_TRANSLATE_URL", "http://localhost:8000/v1")
VLM_MODEL = "Qwen3-VL-8B-Instruct"
_client = None
_openai_available = True

CJK_RE = re.compile(r"[一-鿿]")

PROMPT = """Translate the following into English and rewrite it to match this exact style used throughout an egocentric-video hand-action dataset:
- lowercase, starting with "hand", "left hand", or "right hand" (only name a side if the input specifies one) -- unless the action has no hand as its subject (e.g. an idle/no-activity description or a scene note), in which case keep its own natural subject
- concise, one sentence, no trailing period
- do not invent detail the input doesn't contain; do not drop detail the input does contain

Examples of the target style: "hand picks up the jar" / "left hand holds the box while right hand tightens the screw" / "hand unplugs the nightlight from the wall outlet" / "no interaction (hands not yet engaged)"

Input: {text}

Output only the rewritten sentence, nothing else, no quotes."""


def _get_client():
    # Lazy import: the `openai` package is only needed for the Chinese
    # translation path. Importing it at module load time would make the
    # whole server (and every English-only edit) fail to start in an
    # environment that doesn't have it installed -- translation is meant to
    # be optional, so the import failure has to be contained to just this
    # function, not propagate up to breaking server.py's own import of this
    # module.
    global _client, _openai_available
    if not _openai_available:
        return None
    if _client is None:
        try:
            from openai import OpenAI
        except ImportError:
            _openai_available = False
            return None
        _client = OpenAI(base_url=VLM_BASE_URL, api_key="EMPTY", timeout=30.0)
    return _client


def _lower_word(w):
    # Preserve acronyms/brand-ish tokens as-is (LED, M&M's, TV, GPS-2) --
    # anything that's already all-uppercase-alpha or contains a non-letter
    # character (digits, apostrophes, ampersands, hyphens); lowercase
    # everything else (ordinary words, including accidental Title Case).
    core = re.sub(r"[^A-Za-z]", "", w)
    if core.isupper() and len(core) >= 2:
        return w
    if not w.isalpha():
        return w
    return w.lower()


def local_normalize(text):
    t = (text or "").strip()
    t = re.sub(r"\s+", " ", t)
    t = t.rstrip(".!?,;: ")
    if not t:
        return t
    words = t.split(" ")
    words = [_lower_word(w) for w in words]
    return " ".join(words)


def translate_and_normalize(text):
    """Returns (final_text, was_translated). Never raises -- on any failure
    falls back to local_normalize(text) so a reviewer's edit is never lost."""
    text = (text or "").strip()
    if not text:
        return "", False
    if not CJK_RE.search(text):
        return local_normalize(text), False
    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=VLM_MODEL,
            messages=[{"role": "user", "content": PROMPT.format(text=text)}],
            max_tokens=100, temperature=0.0,
        )
        out = resp.choices[0].message.content.strip()
        out = out.strip("\"'“”‘’")
        if not out or CJK_RE.search(out):
            return local_normalize(text), False
        return local_normalize(out), True
    except Exception:
        return local_normalize(text), False
