#!/usr/bin/env python3
"""EgoProactive v2 annotation pipeline (Qwen3-VL-8B via vllm).

Upgrade of annotate.py to the v2 template/schema:
  - prompt assembled from prompt_template_v2.md (granularity block selection,
    EXAMPLE_BLOCK inject/delete, windowed-input note);
  - output schema {"segments":[{summary,end_time,boundary_confidence}],
    "video_assessment":{segmentability,issues,low_confidence_regions}};
  - Stage2 per-boundary refinement returns {end_time,boundary_confidence},
    the refined value overrides Stage1;
  - long videos are split into absolute-time windows (never a lower fps):
    windows fill the frame budget, overlap 8s, merged by absolute time
    (overlap boundaries <2s from two windows averaged; single-window kept);
    video_assessment = lowest-segmentability window, issues/regions unioned.

Reuses annotate.py verbatim for frame extraction, the VLM client, fonts.
"""
from __future__ import annotations
import argparse, glob, json, math, os, re, subprocess, sys, tempfile, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import annotate  # reuse: extract_frames, _b64_image, _find_font_file, client, VLM_MODEL, _probe_duration

VLM_DIR = Path(__file__).parent
TEMPLATE_V2 = VLM_DIR / "prompt_template_v2.md"

# --- config: resolution / frame budget / fps / windowing --------------------
LONG_EDGE      = 448       # frames downscaled to 448 longest-edge (~140 tok/frame @ server max_pixels=150000)
S1_FONTSIZE    = 26        # timestamp font at 448px (verified readable 20/20)
S2_FONTSIZE    = 26
FRAME_BUDGET   = 640       # max frames per Stage1 window (< server --limit-mm-per-prompt image:660)
WINDOW_OVERLAP_S = 8.0
S1_FPS_DEFAULT = {"coarse": 2.0, "fine": 5.0}
S2_WINDOW_RADIUS_S = 3.0
S2_FPS         = 8.0
DEDUPE_S       = 2.0       # overlap boundaries within this (from 2 windows) are the same -> averaged
MAX_TOKENS_S1  = 6144
MAX_TOKENS_S2  = 128


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


# --- v2 template parsing ----------------------------------------------------

def _load_template():
    text = TEMPLATE_V2.read_text()
    def section(hdr, nxt):
        s = text.index("## " + hdr)
        e = text.index("## " + nxt) if nxt else len(text)
        return text[s:e]
    main = section("MAIN PROMPT", "WINDOWED INPUT NOTE")
    windowed = section("WINDOWED INPUT NOTE", "STAGE 2 PROMPT")
    stage2 = section("STAGE 2 PROMPT", "FINE PASS A PROMPT")
    pass_a = section("FINE PASS A PROMPT", "FINE PASS B PROMPT")
    pass_b = section("FINE PASS B PROMPT", None)
    coarse_rule = re.search(r"<!-- coarse 规则块 -->\n(.*?)\n<!-- fine 规则块 -->", main, re.S).group(1).strip()
    fine_rule   = re.search(r"<!-- fine 规则块 -->\n(.*?)\n### Segmentation rules", main, re.S).group(1).strip()
    example_tmpl = re.search(r"<!-- EXAMPLE_BLOCK.*?：\n(.*?)\n-->", main, re.S).group(1).strip()
    # main template: strip the coarse/fine source blocks and the EXAMPLE_BLOCK comment
    main_tmpl = re.sub(r"<!-- coarse 规则块 -->.*?(?=### Segmentation rules)", "", main, flags=re.S)
    main_tmpl = re.sub(r"<!-- EXAMPLE_BLOCK.*?-->\n?", "", main_tmpl, flags=re.S)
    # strip the "## MAIN PROMPT ..." header line and the windowed/stage2 header lines
    main_tmpl = re.sub(r"^## MAIN PROMPT[^\n]*\n", "", main_tmpl)
    windowed = re.sub(r"^## WINDOWED INPUT NOTE[^\n]*\n", "", windowed).strip()
    stage2 = re.sub(r"^## STAGE 2 PROMPT[^\n]*\n", "", stage2).strip()
    pass_a = re.sub(r"^## FINE PASS A PROMPT[^\n]*\n", "", pass_a).strip()
    pass_b = re.sub(r"^## FINE PASS B PROMPT[^\n]*\n", "", pass_b).strip()
    return {"main": main_tmpl, "coarse": coarse_rule, "fine": fine_rule,
            "example": example_tmpl, "windowed": windowed, "stage2": stage2,
            "pass_a": pass_a, "pass_b": pass_b}

_T = _load_template()


def build_stage1_prompt(row, granularity, example_json=None, win_abs=None):
    dur = row["duration_in_sec"]
    rule = _T["coarse"] if granularity == "coarse" else _T["fine"]
    p = _T["main"]
    p = p.replace("{TASK}", str(row.get("task", ""))).replace("{DOMAIN}", str(row.get("domain", "")))
    p = p.replace("{DURATION}", f"{dur:g}").replace("{GRANULARITY_RULE}", rule)
    if example_json:
        p = p.replace("{EXAMPLE_BLOCK}", _T["example"].replace("{EXAMPLE_JSON}", example_json))
    else:
        p = p.replace("{EXAMPLE_BLOCK}", "")
    if win_abs is not None:
        wn = _T["windowed"].replace("{WIN_ABS_START}", f"{win_abs[0]:.1f}") \
                           .replace("{WIN_ABS_END}", f"{win_abs[1]:.1f}").replace("{DURATION}", f"{dur:g}")
        p = p.rstrip() + "\n\n" + wn
    return p


def build_stage2_prompt(coarse_t, prev_summary, next_summary, win_start, win_end, granularity):
    brule = ("the moment the subtask is visibly completed (hands release the object / attention shifts)"
             if granularity == "coarse" else "the exact moment the hand–object configuration changes")
    s = _T["stage2"]
    s = s.replace("{COARSE_T}", f"{coarse_t:.1f}").replace("{PREV_SUMMARY}", prev_summary) \
         .replace("{NEXT_SUMMARY}", next_summary).replace("{WIN_START}", f"{win_start:.1f}") \
         .replace("{WIN_END}", f"{win_end:.1f}").replace("{BOUNDARY_RULE_SHORT}", brule)
    return s


def build_passA_prompt(row, win_abs=None):
    """Fine Pass A: dense per-moment narration (sees frames)."""
    dur = row["duration_in_sec"]
    p = _T["pass_a"].replace("{TASK}", str(row.get("task", ""))) \
                    .replace("{DOMAIN}", str(row.get("domain", ""))).replace("{DURATION}", f"{dur:g}")
    if win_abs is not None:
        wn = _T["windowed"].replace("{WIN_ABS_START}", f"{win_abs[0]:.1f}") \
                           .replace("{WIN_ABS_END}", f"{win_abs[1]:.1f}").replace("{DURATION}", f"{dur:g}")
        p = p.rstrip() + "\n\n" + wn
    return p


def build_passB_prompt(row, narration):
    """Fine Pass B: derive boundaries from the narration (text only, no frames)."""
    dur = row["duration_in_sec"]
    p = _T["pass_b"].replace("{TASK}", str(row.get("task", ""))).replace("{DURATION}", f"{dur:g}")
    p = p.replace("{GRANULARITY_RULE}", _T["fine"])
    p = p.replace("{NARRATION}", json.dumps(narration, ensure_ascii=False))
    return p


# --- VLM call + parsing -----------------------------------------------------

# Sampling for the current attempt. Attempt 1 = temp 0 (deterministic batch default).
# First retry overrides to repetition_penalty 1.1 + temp 0.2 -- the verified fix for
# dense-fine degeneration loops (set per-attempt in main()).
_SAMPLING = {"temperature": 0.0, "repetition_penalty": None}


def _call(prompt, frames, max_tokens):
    content = [{"type": "text", "text": prompt}]
    for _t, path in frames:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{annotate._b64_image(path)}"}})
    kw = dict(model=annotate.VLM_MODEL, messages=[{"role": "user", "content": content}],
              max_tokens=max_tokens, temperature=_SAMPLING["temperature"])
    if _SAMPLING["repetition_penalty"]:
        kw["extra_body"] = {"repetition_penalty": _SAMPLING["repetition_penalty"]}
    r = annotate.client.chat.completions.create(**kw)
    return r.choices[0].message.content


def _call_text(prompt, max_tokens):
    """Text-only call (no images) for Pass B boundary derivation."""
    kw = dict(model=annotate.VLM_MODEL, messages=[{"role": "user", "content": prompt}],
              max_tokens=max_tokens, temperature=_SAMPLING["temperature"])
    if _SAMPLING["repetition_penalty"]:
        kw["extra_body"] = {"repetition_penalty": _SAMPLING["repetition_penalty"]}
    r = annotate.client.chat.completions.create(**kw)
    return r.choices[0].message.content


def _strip_fence(t):
    t = t.strip()
    m = re.match(r"^```(?:json)?\s*\n(.*)\n```\s*$", t, re.S)
    return m.group(1).strip() if m else t


def parse_stage1(raw):
    try:
        data = json.loads(_strip_fence(raw))
    except json.JSONDecodeError as e:
        err = ValueError(f"JSONDecodeError: {e}"); err.raw = raw; raise err
    if not isinstance(data, dict) or "segments" not in data:
        err = ValueError("expected object with 'segments'"); err.raw = raw; raise err
    segs = [{"summary": s["summary"], "end_time": round(float(s["end_time"]), 1),
             "boundary_confidence": float(s.get("boundary_confidence", 0.5))} for s in data["segments"]]
    va = data.get("video_assessment", {}) or {}
    va = {"segmentability": va.get("segmentability"), "issues": va.get("issues", []) or [],
          "low_confidence_regions": va.get("low_confidence_regions", []) or []}
    return segs, va


def parse_stage2(raw):
    d = json.loads(_strip_fence(raw))
    return round(float(d["end_time"]), 1), float(d.get("boundary_confidence", 0.5))


def parse_narration(raw):
    try:
        data = json.loads(_strip_fence(raw))
    except json.JSONDecodeError as e:
        err = ValueError(f"JSONDecodeError(passA): {e}"); err.raw = raw; raise err
    if not isinstance(data, list):
        err = ValueError("passA: expected a JSON array"); err.raw = raw; raise err
    out = []
    for x in data:
        if isinstance(x, dict) and "t" in x and "action" in x:
            out.append({"t": round(float(x["t"]), 1), "action": str(x["action"]).strip()})
    return out


# --- windowing --------------------------------------------------------------

_FONT_CACHE = {}
def _pil_font(size):
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = ImageFont.truetype(annotate.FONT_FILE or annotate._find_font_file(None), size)
    return _FONT_CACHE[size]


def _burn(path, label, fontsize):
    im = Image.open(path).convert("RGB"); d = ImageDraw.Draw(im); f = _pil_font(fontsize)
    x, y = 10, 10
    b = d.textbbox((x, y), label, font=f); pad = max(3, fontsize // 6)
    d.rectangle([b[0]-pad, b[1]-pad, b[2]+pad, b[3]+pad], fill=(0, 0, 0))
    d.text((x, y), label, fill=(255, 255, 0), font=f)
    im.save(path)


def _extract(video, out_dir, fps, t_start, t_end, fontsize):
    """Fast extraction: ONE ffmpeg pass (fps + scale, no drawtext) then PIL-burns
    the Python-computed 't=XX.Xs' per frame. Orders of magnitude faster than one
    ffmpeg-per-frame; same computed-timestamp semantics (fast -ss + fps grid, label
    = requested time). Frames are 448px longest-edge (server also caps at max_pixels)."""
    os.makedirs(out_dir, exist_ok=True)
    dur = t_end - t_start
    if dur <= 0:
        return []
    patt = os.path.join(out_dir, "f_%05d.png")
    vf = f"fps={fps},scale={LONG_EDGE}:{LONG_EDGE}:force_original_aspect_ratio=decrease"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t_start}",
                    "-i", video, "-t", f"{dur}", "-vf", vf, "-start_number", "0", "-y", patt], check=True)
    files = sorted(glob.glob(os.path.join(out_dir, "f_*.png")))
    results = []
    for i, fpath in enumerate(files):
        t = round(t_start + i / fps, 1)
        if t > t_end + 1e-6:
            os.remove(fpath); continue
        _burn(fpath, f"t={t:.1f}s", fontsize)
        results.append((t, fpath))
    return results


def _window_starts(dur, fps):
    span = FRAME_BUDGET / fps
    step = span - WINDOW_OVERLAP_S
    starts, s = [], 0.0
    while True:
        starts.append(s)
        if s + span >= dur:
            break
        s += step
    return starts, span


def merge_windows(windows, dur):
    """windows: list of (ws, we, segments). Merge to one absolute-time segment list."""
    n = len(windows)
    bnds = []  # [end_time, summary, conf, win_idx]
    for wi, (ws, we, segs) in enumerate(windows):
        for si, seg in enumerate(segs):
            et = float(seg["end_time"])
            # drop the artificial cut at a non-final window's end (the action continues into the overlap)
            if wi < n - 1 and si == len(segs) - 1 and abs(et - we) < 1.5:
                continue
            bnds.append([et, seg.get("summary", ""), float(seg.get("boundary_confidence", 0.5)), wi])
    bnds.sort(key=lambda b: b[0])
    merged = []
    for b in bnds:
        if merged and abs(b[0] - merged[-1][0]) < DEDUPE_S and b[3] != merged[-1][3]:
            prev = merged[-1]
            avg_t = (prev[0] + b[0]) / 2
            keep = b if b[2] >= prev[2] else prev            # keep higher-confidence summary
            merged[-1] = [avg_t, keep[1], (prev[2] + b[2]) / 2, keep[3]]
        else:
            merged.append(list(b))
    out, prev_end = [], 0.0
    for et, summ, conf, _ in merged:
        et = round(et, 1)
        if et <= prev_end:
            et = round(prev_end + 0.1, 1)
        out.append({"summary": summ, "end_time": et, "boundary_confidence": round(conf, 3)})
        prev_end = et
    if out and out[-1]["end_time"] < dur - 0.5:   # ensure final segment reaches the video end
        out[-1]["end_time"] = round(dur, 1)
    return out


def merge_assessments(assessments):
    known = [a for a in assessments if a.get("segmentability") is not None]
    lowest = min(known, key=lambda a: a["segmentability"]) if known else (assessments[0] if assessments else {})
    issues, lcr = [], []
    for a in assessments:
        for x in a.get("issues", []):
            if x not in issues:
                issues.append(x)
        for r in a.get("low_confidence_regions", []):
            lcr.append(r)
    return {"segmentability": lowest.get("segmentability"), "issues": issues, "low_confidence_regions": lcr}


def stage1(row, video, granularity, workdir, fps, example_json):
    dur = row["duration_in_sec"]
    need = dur * fps
    if need <= FRAME_BUDGET:
        frames = _extract(video, os.path.join(workdir, "s1"), fps, 0.0, dur, S1_FONTSIZE)
        segs, va = parse_stage1(_call(build_stage1_prompt(row, granularity, example_json), frames, MAX_TOKENS_S1))
        return segs, va, 1
    starts, span = _window_starts(dur, fps)
    windows, assessments = [], []
    for wi, ws in enumerate(starts):
        we = min(dur, ws + span)
        frames = _extract(video, os.path.join(workdir, f"s1_w{wi}"), fps, ws, we, S1_FONTSIZE)
        segs, va = parse_stage1(_call(build_stage1_prompt(row, granularity, example_json, win_abs=(ws, we)), frames, MAX_TOKENS_S1))
        windows.append((ws, we, segs)); assessments.append(va)
        log(f"      window {wi+1}/{len(starts)} [{ws:.0f}-{we:.0f}s]: {len(segs)} segs, {len(frames)} frames")
    return merge_windows(windows, dur), merge_assessments(assessments), len(starts)


def stage2(row, video, granularity, workdir, segments):
    """Refine each INTERNAL boundary (between consecutive segments); the final
    segment's end (= video end) is left as-is. Refined end_time overrides Stage1."""
    dur = row["duration_in_sec"]
    out = [dict(s) for s in segments]
    prev_end = 0.0
    for i in range(len(out) - 1):
        rough = out[i]["end_time"]
        ts, te = max(0.0, rough - S2_WINDOW_RADIUS_S), min(dur, rough + S2_WINDOW_RADIUS_S)
        frames = _extract(video, os.path.join(workdir, f"s2_{i:03d}"), S2_FPS, ts, te, S2_FONTSIZE)
        prev_summary = out[i]["summary"]
        next_summary = out[i + 1]["summary"]
        rend, rconf = parse_stage2(_call(build_stage2_prompt(rough, prev_summary, next_summary, ts, te, granularity), frames, MAX_TOKENS_S2))
        if rend <= prev_end:
            rend = round(prev_end + 0.1, 1)
        if rend >= out[i + 1]["end_time"]:               # keep it below the next boundary
            rend = round(min(rend, out[i + 1]["end_time"] - 0.1), 1)
        out[i]["end_time"] = rend
        out[i]["boundary_confidence"] = round(rconf, 3)
        prev_end = rend
    return out


# --- validation -------------------------------------------------------------

def validate(segments, video_assessment, dur):
    errs, prev = [], 0.0
    for i, s in enumerate(segments):
        if not str(s.get("summary", "")).strip():
            errs.append(f"seg {i}: empty summary")
        et = s.get("end_time")
        if et is None:
            errs.append(f"seg {i}: missing end_time"); continue
        if et <= prev:
            errs.append(f"seg {i}: end_time {et} <= prev {prev}")
        bc = s.get("boundary_confidence")
        if bc is None or not (0.0 <= bc <= 1.0):
            errs.append(f"seg {i}: boundary_confidence {bc} not in [0,1]")
        prev = et
    if not segments:
        errs.append("no segments")
    elif abs(segments[-1]["end_time"] - dur) > 10.0:
        errs.append(f"last end_time {segments[-1]['end_time']} not within 10s of duration {dur}")
    for r in (video_assessment.get("low_confidence_regions") or []):
        if not (isinstance(r, (list, tuple)) and len(r) == 2 and 0 <= r[0] < r[1] <= dur + 1e-6):
            errs.append(f"low_confidence_region {r} invalid for duration {dur}")
    return errs


# --- main -------------------------------------------------------------------

def stage1_fine(row, video, workdir, fps, narr_path=None):
    """Two-pass fine: Pass A dense narration per window (sees frames) -> merge ->
    Pass B text-only boundary derivation into the v2 {segments, video_assessment}."""
    dur = row["duration_in_sec"]
    narration = []
    if dur * fps <= FRAME_BUDGET:
        frames = _extract(video, os.path.join(workdir, "pa"), fps, 0.0, dur, S1_FONTSIZE)
        narration = parse_narration(_call(build_passA_prompt(row), frames, MAX_TOKENS_S1))
        nwin = 1
        log(f"      passA: {len(narration)} narration lines ({len(frames)} frames)")
    else:
        starts, span = _window_starts(dur, fps)
        for wi, ws in enumerate(starts):
            we = min(dur, ws + span)
            frames = _extract(video, os.path.join(workdir, f"pa_w{wi}"), fps, ws, we, S1_FONTSIZE)
            n = parse_narration(_call(build_passA_prompt(row, win_abs=(ws, we)), frames, MAX_TOKENS_S1))
            narration += n
            log(f"      passA window {wi+1}/{len(starts)} [{ws:.0f}-{we:.0f}s]: {len(n)} lines")
        nwin = len(starts)
    # merge narration across windows: sort by t, drop overlap dups (same action within 1s)
    narration.sort(key=lambda e: e["t"])
    merged = []
    for e in narration:
        if merged and abs(e["t"] - merged[-1]["t"]) < 1.0 and e["action"] == merged[-1]["action"]:
            continue
        merged.append(e)
    narration = merged
    if narr_path:
        os.makedirs(os.path.dirname(narr_path), exist_ok=True)
        json.dump(narration, open(narr_path, "w"), ensure_ascii=False, indent=1)
    # Pass B: text-only boundary derivation
    segs, va = parse_stage1(_call_text(build_passB_prompt(row, narration), MAX_TOKENS_S1))
    return segs, va, nwin, narration


def annotate_one(row, video, granularity, workdir, fps, example_json, narr_path=None):
    if granularity == "fine":
        segs, va, nwin, narration = stage1_fine(row, video, workdir, fps, narr_path)
        log(f"    passB: {len(narration)} narration -> {len(segs)} segs ({nwin} window(s)), segmentability={va.get('segmentability')}")
    else:
        segs, va, nwin = stage1(row, video, granularity, workdir, fps, example_json)
        log(f"    stage1: {len(segs)} segs ({nwin} window(s)), segmentability={va.get('segmentability')}")
    segs = stage2(row, video, granularity, workdir, segs)
    log(f"    stage2: refined {max(0, len(segs)-1)} boundaries")
    return segs, va, nwin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default=str(annotate.DEFAULT_JSONL_PATH))
    ap.add_argument("--video_dir", default=str(annotate.DEFAULT_VIDEO_DIR))
    ap.add_argument("--granularity", required=True, choices=["coarse", "fine"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--video_list", default=None, help="optional file of video_path per line to restrict to (e.g. keep list)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--example", default=None, help="JSON file: a segments list [{summary,end_time}] for few-shot")
    ap.add_argument("--s1_fps", type=float, default=None)
    ap.add_argument("--font-file", default=None)
    args = ap.parse_args()

    annotate.FONT_FILE = annotate._find_font_file(args.font_file)
    fps = args.s1_fps if args.s1_fps is not None else S1_FPS_DEFAULT[args.granularity]
    example_json = None
    if args.example:
        example_json = json.dumps(json.loads(Path(args.example).read_text()), indent=2)

    meta = [json.loads(l) for l in open(args.jsonl)]
    if args.video_list:
        want = set(l.strip() for l in open(args.video_list) if l.strip())
        meta = [r for r in meta if r["video_path"] in want]
    if args.limit:
        meta = meta[: args.limit]

    done = set()
    if os.path.exists(args.out):
        for l in open(args.out):
            try:
                done.add(json.loads(l)["video_path"])
            except Exception:
                pass
    if done:
        log(f"resume: {len(done)} already in {args.out}, skipping those")

    out_f = open(args.out, "a")
    n_ok = n_fail = 0
    for k, row in enumerate(meta):
        vp = row["video_path"]
        if vp in done:
            continue
        video = os.path.join(args.video_dir, vp)
        if not os.path.exists(video):
            log(f"SKIP {vp}: not found"); continue
        log(f"[{k+1}/{len(meta)}] {vp} dur={row['duration_in_sec']}s {args.granularity}")
        rec = None
        for attempt in (1, 2):
            # attempt 1: deterministic temp-0. first retry: repetition_penalty 1.1 + temp 0.2
            # together (breaks degeneration loops; verified). Normal batch stays temp-0.
            _SAMPLING["temperature"] = 0.0 if attempt == 1 else 0.2
            _SAMPLING["repetition_penalty"] = None if attempt == 1 else 1.1
            try:
                narr_path = (os.path.join(str(annotate.REPO_ROOT), "vlm", "outputs", "narrations", f"{vp[:-4]}_fine.json")
                             if args.granularity == "fine" else None)
                with tempfile.TemporaryDirectory(dir="/tmp") as wd:
                    segs, va, nwin = annotate_one(row, video, args.granularity, wd, fps, example_json, narr_path)
                errs = validate(segs, va, row["duration_in_sec"])
                rec = {"video_path": vp, "task": row.get("task", ""), "domain": row.get("domain", ""),
                       "query": row.get("query", ""), "granularity": args.granularity,
                       "duration_in_sec": row["duration_in_sec"], "n_windows": nwin,
                       "segments": segs, "video_assessment": va, "validation_errors": errs}
                break
            except Exception as e:
                log(f"    attempt {attempt} failed: {type(e).__name__}: {str(e)[:160]}")
                raw = getattr(e, "raw", None)
                if attempt == 2:
                    rec = {"video_path": vp, "granularity": args.granularity, "status": "failed",
                           "error": f"{type(e).__name__}: {str(e)[:300]}",
                           "raw_output": (raw[:20000] if raw else None)}
        out_f.write(json.dumps(rec, ensure_ascii=False) + "\n"); out_f.flush()
        if rec.get("status") == "failed":
            n_fail += 1; log(f"    -> FAILED")
        else:
            n_ok += 1; log(f"    -> ok: {len(rec['segments'])} segs, errs={len(rec['validation_errors'])}, windows={rec['n_windows']}")
        if (n_ok + n_fail) % 50 == 0:
            log(f"progress: {n_ok} ok / {n_fail} failed / {len(meta)} total")
    out_f.close()
    log(f"DONE {args.granularity}: {n_ok} ok, {n_fail} failed")


if __name__ == "__main__":
    main()
