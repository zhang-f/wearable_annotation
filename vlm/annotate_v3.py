#!/usr/bin/env python3
"""EgoProactive v3 — four-layer annotation pipeline (Qwen3-VL-8B via vllm).

  Pass 0 (global understanding, low fps, one call)
   -> Coarse Pass 1 (segmentation guided by the outline, 2fps, v2 schema, windowed if over budget)
     -> Fine PER COARSE SEGMENT: Pass A dense narration (5fps) + Pass B text boundary derivation
       -> Stage 2 boundary refinement (both granularities, +/-1.5s, 8fps)

Every single call stays short (top layer feeds the next), which avoids the long-window
degeneration seen in v2. repetition_penalty=1.1 is default-on for the degeneration-prone
Pass A / Pass B; Pass 0 and Coarse Pass 1 add it only on retry. Reuses annotate.py and
annotate_v2.py helpers (frame extraction, VLM calls, parsers, window math).
"""
from __future__ import annotations
import argparse, json, os, re, tempfile, time
from collections import Counter
from pathlib import Path
import annotate
import annotate_v2 as v2

VLM_DIR = Path(__file__).parent
TEMPLATE_V3 = VLM_DIR / "prompt_template_v3.md"

COARSE_FPS = 2.0
FINE_FPS = 5.0
PASS0_LADDER = [2.0, 1.0, 0.5, 0.25]
BLIND_WIN_S = 90.0
BLIND_OVERLAP_S = 4.0
REP_PENALTY = 1.1
UNIQUE_RATIO = 0.5          # Pass A: unique-entry ratio below this => degeneration
PHASE_TOL_S = 15.0
FRAME_BUDGET = v2.FRAME_BUDGET
LONG_EDGE = v2.LONG_EDGE
FONT = v2.S1_FONTSIZE
BLIND_THRESH_S = FRAME_BUDGET / FINE_FPS   # a coarse segment longer than this is blind-cut (fits budget)
MAX_TOK_P0 = 1536
MAX_TOK_COARSE = 6144
MAX_TOK_PASSA = 8192
MAX_TOK_PASSB = 8192
v2.S2_WINDOW_RADIUS_S = 1.5  # v3 Stage-2 window is +/-1.5s (8fps unchanged)
log = v2.log


# --- template ---------------------------------------------------------------

def _load_v3():
    text = TEMPLATE_V3.read_text()
    def section(hdr, nxt):
        s = text.index("## " + hdr); e = text.index("## " + nxt) if nxt else len(text)
        return re.sub(r"^## [^\n]*\n", "", text[s:e]).strip()
    return {"pass0": section("PASS 0 PROMPT", "COARSE PASS 1 PROMPT"),
            "coarse": section("COARSE PASS 1 PROMPT", "WINDOWED INPUT NOTE"),
            "windowed": section("WINDOWED INPUT NOTE", "FINE PASS A PROMPT"),
            "fineA": section("FINE PASS A PROMPT", "FINE PASS B PROMPT"),
            "fineB": section("FINE PASS B PROMPT", "FINE PASS B V4 PROMPT"),
            "fineB_v4": section("FINE PASS B V4 PROMPT", "FINE REFINE M PROMPT"),
            "refineM": section("FINE REFINE M PROMPT", "STAGE 2 PROMPT"),
            "stage2": section("STAGE 2 PROMPT", None)}
_T = _load_v3()


def _fill(t, **kw):
    for k, v in kw.items():
        t = t.replace("{" + k + "}", str(v))
    return t


def _win_note(row, ws, we):
    return _fill(_T["windowed"], WIN_ABS_START=f"{ws:.1f}", WIN_ABS_END=f"{we:.1f}", DURATION=f"{row['duration_in_sec']:g}")


def build_pass0(row):
    return _fill(_T["pass0"], TASK=row.get("task", ""), DOMAIN=row.get("domain", ""), DURATION=f"{row['duration_in_sec']:g}")

def build_coarse(row, p0, win=None):
    p = _fill(_T["coarse"].replace("{EXAMPLE_BLOCK}", ""), TASK=row.get("task", ""), DOMAIN=row.get("domain", ""),
              DURATION=f"{row['duration_in_sec']:g}", PASS0_JSON=json.dumps(p0, ensure_ascii=False))
    return p if win is None else p.rstrip() + "\n\n" + _win_note(row, *win)

def build_fineA(row, csum, ss, se, win=None):
    p = _fill(_T["fineA"], TASK=row.get("task", ""), COARSE_SUMMARY=csum, SEG_START=f"{ss:.1f}", SEG_END=f"{se:.1f}")
    return p if win is None else p.rstrip() + "\n\n" + _win_note(row, *win)

def build_fineB(row, csum, ss, se, narr):
    return _fill(_T["fineB"].replace("{EXAMPLE_BLOCK}", ""), TASK=row.get("task", ""), COARSE_SUMMARY=csum,
                 SEG_START=f"{ss:.1f}", SEG_END=f"{se:.1f}", NARRATION_JSON=json.dumps(narr, ensure_ascii=False))

def build_stage2(ct, prev, nxt, ws, we, gran):
    brule = ("the moment the subtask is visibly completed (hands release the object / attention shifts)"
             if gran == "coarse" else "the exact moment the hand's verb or object changes")
    return _fill(_T["stage2"], COARSE_T=f"{ct:.1f}", PREV_SUMMARY=prev, NEXT_SUMMARY=nxt,
                 WIN_START=f"{ws:.1f}", WIN_END=f"{we:.1f}", BOUNDARY_RULE_SHORT=brule)


_CONF_WORDS = {"high": 0.9, "very high": 0.95, "medium": 0.6, "med": 0.6, "moderate": 0.6,
               "low": 0.4, "very low": 0.2, "certain": 1.0, "uncertain": 0.3, "none": 0.3}
def _coerce_conf(v, default=0.5):
    """Robustly turn a boundary_confidence value into a float — the model sometimes
    emits the word 'high'/'low' instead of a number."""
    if isinstance(v, (int, float)):
        return max(0.0, min(1.0, float(v)))
    if isinstance(v, str):
        s = v.strip().lower()
        try:
            return max(0.0, min(1.0, float(s)))
        except ValueError:
            return _CONF_WORDS.get(s, default)
    return default

def _set(temp, rep): v2._SAMPLING["temperature"] = temp; v2._SAMPLING["repetition_penalty"] = rep
def _ex(video, wd, name, fps, ts, te): return v2._extract(video, os.path.join(wd, name), fps, ts, te, FONT)


# --- layers -----------------------------------------------------------------

def pass0(row, video, wd):
    dur = row["duration_in_sec"]
    fps = next((f for f in PASS0_LADDER if dur * f <= FRAME_BUDGET), PASS0_LADDER[-1])
    frames = _ex(video, wd, "p0", fps, 0.0, dur)
    for attempt in (1, 2):
        _set(0.0 if attempt == 1 else 0.2, None if attempt == 1 else REP_PENALTY)
        try:
            d = json.loads(v2._strip_fence(v2._call(build_pass0(row), frames, MAX_TOK_P0)))
            return {"task_understanding": d.get("task_understanding", ""), "phases": d.get("phases", [])}, fps, len(frames)
        except Exception as e:
            last = e
    raise last


def coarse_pass1(row, video, wd, p0):
    dur = row["duration_in_sec"]
    def call(prompt, frames, tag):
        for attempt in (1, 2):
            _set(0.0 if attempt == 1 else 0.2, None if attempt == 1 else REP_PENALTY)
            try: return v2.parse_stage1(v2._call(prompt, frames, MAX_TOK_COARSE))
            except Exception as e:
                nonlocal_last[0] = e; log(f"      [{tag}] coarse attempt {attempt}: {str(e)[:70]}")
        raise nonlocal_last[0]
    nonlocal_last = [None]
    if dur * COARSE_FPS <= FRAME_BUDGET:
        segs, va = call(build_coarse(row, p0), _ex(video, wd, "c0", COARSE_FPS, 0.0, dur), "coarse")
        return segs, va, 1
    starts, span = v2._window_starts(dur, COARSE_FPS)
    windows, assess = [], []
    for wi, ws in enumerate(starts):
        we = min(dur, ws + span)
        s, va = call(build_coarse(row, p0, win=(ws, we)), _ex(video, wd, f"c{wi}", COARSE_FPS, ws, we), f"coarseW{wi}")
        windows.append((ws, we, s)); assess.append(va)
        log(f"      coarse window {wi+1}/{len(starts)} [{ws:.0f}-{we:.0f}s]: {len(s)} segs")
    return v2.merge_windows(windows, dur), v2.merge_assessments(assess), len(starts)


def _passA(prompt, frames, tag):
    last = None; n = []
    for attempt in (1, 2):
        _set(0.0 if attempt == 1 else 0.2, REP_PENALTY)
        try:
            n = v2.parse_narration(v2._call(prompt, frames, MAX_TOK_PASSA))
            if n and len(set(e["action"] for e in n)) / len(n) < UNIQUE_RATIO and attempt == 1:
                log(f"      [{tag}] passA degeneration (uniq<0.5) -> retry"); continue
            return n, (len(n) > 0 and len(set(e["action"] for e in n)) / len(n) < UNIQUE_RATIO)
        except Exception as e:
            last = e; log(f"      [{tag}] passA attempt {attempt}: {str(e)[:70]}")
    if last:
        raise last
    return n, True


def _passB(row, csum, ss, se, narr):
    last = None
    for attempt in (1, 2):
        _set(0.0 if attempt == 1 else 0.2, REP_PENALTY)
        try:
            segs, va = v2.parse_stage1(v2._call_text(build_fineB(row, csum, ss, se, narr), MAX_TOK_PASSB))
            if len(segs) > max(1, len(narr)) and attempt == 1:
                log(f"      passB abnormal ({len(segs)}>{len(narr)} narr) -> retry"); continue
            return segs, va, (len(segs) > max(1, len(narr)))
        except Exception as e:
            last = e; log(f"      passB attempt {attempt}: {str(e)[:70]}")
    raise last


def _obj(a):
    ws = a.lower().replace(".", "").split()
    return ws[-1] if ws else ""

def reverse_consistency(narr, sidx):
    if len(narr) < 8: return []
    objs = [_obj(e["action"]) for e in narr]; h = len(objs) // 2
    a = Counter(objs[:h]).most_common(1); b = Counter(objs[h:]).most_common(1)
    if a and b and a[0][0] != b[0][0] and a[0][1] >= h * 0.5 and b[0][1] >= (len(objs) - h) * 0.5:
        return [f"suspected coarse-miss: dominant object shifts '{a[0][0]}'->'{b[0][0]}' at ~{narr[h]['t']:.0f}s inside coarse seg {sidx+1}"]
    return []


# --- fine post-merge (programmatic; enforces the "auxiliary micro-motion" rule) ---
# Handling/positioning verbs that typically serve an ongoing action rather than
# constitute a substantive action of their own.
AUX_VERBS = {"move", "moves", "moving", "moved", "reposition", "repositions", "shift", "shifts",
             "adjust", "adjusts", "slide", "slides", "place", "places", "placed", "put", "puts",
             "set", "sets", "pick", "picks", "picked", "grab", "grabs", "grabbed", "reach", "reaches",
             "lift", "lifts", "lifted", "lower", "lowers", "hold", "holds"}
_HANDS = {"left", "right", "both", "hand", "hands"}
_FILLER = {"the", "a", "an", "again", "back", "to", "of", "on", "down", "up", "still", "then", "and",
           "side", "around", "onto", "into", "over", "away", "slightly", "little", "bit", "with", "in",
           "toward", "towards", "another", "other", "new", "first", "second", "it", "its", "her", "his",
           "left", "right", "center", "middle", "top", "bottom", "front", "corner", "edge", "place"}
_ADJ = {"small", "large", "big", "long", "short", "folded", "red", "blue", "green", "black", "white",
        "yellow", "wooden", "plastic", "metal", "clear", "empty", "full", "old", "same", "next"}

def _sig(summary):
    toks = [t for t in re.sub(r"[^a-z ]", " ", (summary or "").lower()).split() if t]
    toks = [t for t in toks if t not in _HANDS]
    verb = toks[0] if toks else ""
    objs = [t for t in toks[1:] if t not in _FILLER and t not in _ADJ]
    # obj = the direct object (first content noun after the verb), so destination/position
    # phrasing ("...to the left", "...back to center") doesn't fragment the signature.
    return verb, (objs[0] if objs else ""), set(objs)

def _osc_mergeable(a, b):
    # a, b are _sig tuples; mergeable oscillation when they share an object token
    # OR at least one side is an auxiliary handling verb serving the other.
    return bool(a[2] & b[2]) or a[0] in AUX_VERBS or b[0] in AUX_VERBS

def _combine(run):
    # dominant action = signature with the highest total duration; conf = min of merged
    by = {}
    for it in run:
        key = it["sig"][:2]; by.setdefault(key, {"dur": 0.0, "sum": it["summary"]})
        by[key]["dur"] += it["end_time"] - it["start"]
    dom = max(by.values(), key=lambda x: x["dur"])["sum"]
    return {"summary": dom, "end_time": run[-1]["end_time"],
            "boundary_confidence": round(min(it["boundary_confidence"] for it in run), 3),
            "start": run[0]["start"], "sig": run[0]["sig"], "_raw": sum(it["_raw"] for it in run)}

def merge_fine(segs, seg_lo):
    """Two passes within one coarse segment: (1) collapse consecutive identical
    verb+object; (2) collapse A-B-A-B oscillation runs on the same/related object.
    Returns segments with a `merged_from` raw count."""
    items = []; prev = seg_lo
    for s in segs:
        items.append({"summary": s["summary"], "end_time": float(s["end_time"]), "start": prev,
                      "boundary_confidence": float(s.get("boundary_confidence", 0.5)),
                      "sig": _sig(s["summary"]), "_raw": 1})
        prev = s["end_time"]
    # pass 1: consecutive identical (verb, object)
    p1 = []; i = 0
    while i < len(items):
        j = i + 1
        while j < len(items) and items[j]["sig"][:2] == items[i]["sig"][:2]:
            j += 1
        p1.append(_combine(items[i:j]) if j - i > 1 else items[i]); i = j
    # pass 2: oscillation (post-pass1 has no consecutive identical, so <=2 distinct over a
    # run of >=4 must alternate A-B-A-B)
    out = []; i = 0
    while i < len(p1):
        sset = []; j = i
        while j < len(p1):
            s = p1[j]["sig"][:2]
            if s not in sset:
                if len(sset) == 2: break
                sset.append(s)
            j += 1
        if j - i >= 4 and len(sset) == 2 and _osc_mergeable(p1[i]["sig"], p1[i + 1]["sig"]):
            out.append(_combine(p1[i:j])); i = j
        else:
            out.append(p1[i]); i += 1
    return [{"summary": o["summary"], "end_time": round(o["end_time"], 1),
             "boundary_confidence": o["boundary_confidence"], "merged_from": o["_raw"]} for o in out]


def fine_from_coarse(row, video, wd, coarse_segs, narr_path, raw_path=None):
    dur = row["duration_in_sec"]; all_fine = []; all_raw = []; assess = []; flags = []; full_narr = []; prev = 0.0
    for sidx, cs in enumerate(coarse_segs):
        ss, se = prev, cs["end_time"]; prev = se
        # blind-cut only when a coarse segment alone exceeds the frame budget
        if (se - ss) > BLIND_THRESH_S:
            wins, s = [], ss
            while True:
                we = min(se, s + BLIND_WIN_S); wins.append((s, we))
                if we >= se: break
                s += BLIND_WIN_S - BLIND_OVERLAP_S
        else:
            wins = [(ss, se)]
        def _fallback(note):
            # keep this coarse segment as a single fine segment instead of aborting the whole video
            pe = all_fine[-1]["end_time"] if all_fine else 0.0
            one = {"summary": cs["summary"], "end_time": round(max(se, pe + 0.1), 1),
                   "boundary_confidence": cs.get("boundary_confidence", 0.5), "merged_from": 1}
            all_fine.append(one); all_raw.append({**one, "coarse_idx": sidx})
            flags.append(f"fine-fallback: coarse seg {sidx+1} kept whole ({note})")
        try:
            narr = []
            for wi, (ws, we) in enumerate(wins):
                frames = _ex(video, wd, f"fa_{sidx}_{wi}", FINE_FPS, ws, we)
                n, _deg = _passA(build_fineA(row, cs["summary"], ws, we, win=((ws, we) if len(wins) > 1 else None)), frames, f"seg{sidx}w{wi}")
                narr += n
            narr.sort(key=lambda e: e["t"])
            merged = []
            for e in narr:
                if merged and abs(e["t"] - merged[-1]["t"]) < 1.0 and e["action"] == merged[-1]["action"]: continue
                merged.append(e)
            narr = merged
            full_narr.append({"coarse_idx": sidx, "range": [round(ss, 1), round(se, 1)], "coarse_summary": cs["summary"], "narration": narr})
            log(f"      coarse seg {sidx+1}/{len(coarse_segs)} [{ss:.0f}-{se:.0f}s] '{cs['summary'][:28]}': {len(narr)} narration")
            flags += reverse_consistency(narr, sidx)
            if not narr:
                _fallback("empty narration"); continue
            segs, va, _abn = _passB(row, cs["summary"], ss, se, narr); assess.append(va)
        except Exception as e:
            log(f"      coarse seg {sidx+1}: fine failed ({type(e).__name__}: {str(e)[:60]}) -> kept whole")
            _fallback(f"{type(e).__name__}"); continue
        pe = all_fine[-1]["end_time"] if all_fine else 0.0
        for s in segs:
            et = round(min(max(float(s["end_time"]), ss + 0.1), se), 1)
            if et <= pe: et = round(pe + 0.1, 1)
            s["end_time"] = et; pe = et
            s["boundary_confidence"] = _coerce_conf(s.get("boundary_confidence", 0.5))
        if segs: segs[-1]["end_time"] = round(max(se, segs[-1]["end_time"]), 1)  # nest: last fine boundary = coarse boundary
        # archive raw Pass B (pre-merge), then programmatic post-merge within this coarse segment
        for s in segs: all_raw.append({"summary": s["summary"], "end_time": s["end_time"], "boundary_confidence": s["boundary_confidence"], "coarse_idx": sidx})
        seg_lo = all_fine[-1]["end_time"] if all_fine else ss
        m = merge_fine(segs, seg_lo)
        nmerged = sum(1 for x in m if x["merged_from"] > 1)
        if nmerged:
            log(f"        post-merge: {len(segs)} -> {len(m)} fine segs ({nmerged} merged group(s))")
        all_fine += m
    if narr_path:
        os.makedirs(os.path.dirname(narr_path), exist_ok=True)
        json.dump(full_narr, open(narr_path, "w"), ensure_ascii=False, indent=1)
    if raw_path:
        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        json.dump(all_raw, open(raw_path, "w"), ensure_ascii=False, indent=1)
    va = v2.merge_assessments(assess) if assess else {"segmentability": None, "issues": [], "low_confidence_regions": []}
    return all_fine, va, flags, len(all_raw)


def phase_flags(coarse_segs, phases):
    ranges = [p["approx_range"] for p in phases if isinstance(p.get("approx_range"), list) and len(p["approx_range"]) == 2]
    if not ranges: return []
    prev = 0.0; miss = 0
    for s in coarse_segs:
        mid = (prev + s["end_time"]) / 2; prev = s["end_time"]
        if not any(r[0] - PHASE_TOL_S <= mid <= r[1] + PHASE_TOL_S for r in ranges): miss += 1
    return [f"outline-mismatch: {miss}/{len(coarse_segs)} coarse midpoints outside all phase ranges (+/-15s)"] if miss > len(coarse_segs) * 0.4 else []


def stage2_v3(row, video, wd, segs, gran):
    dur = row["duration_in_sec"]; out = [dict(s) for s in segs]; prev = 0.0
    for i in range(len(out) - 1):
        rough = out[i]["end_time"]; ts, te = max(0.0, rough - 1.5), min(dur, rough + 1.5)
        frames = _ex(video, wd, f"s2_{gran}_{i:03d}", 8.0, ts, te)
        _set(0.0, None)
        try:
            rend, rconf = v2.parse_stage2(v2._call(build_stage2(rough, out[i]["summary"], out[i+1]["summary"], ts, te, gran), frames, 128))
        except Exception:
            rend, rconf = rough, out[i].get("boundary_confidence", 0.5)
        if rend <= prev: rend = round(prev + 0.1, 1)
        if rend >= out[i+1]["end_time"]: rend = round(min(rend, out[i+1]["end_time"] - 0.1), 1)
        out[i]["end_time"] = rend; out[i]["boundary_confidence"] = round(_coerce_conf(rconf), 3); prev = rend
    return out


def annotate_video(row, video, wd, narr_path, global_path, raw_path=None):
    dur = row["duration_in_sec"]; t = {}
    s = time.time(); p0, p0fps, p0n = pass0(row, video, wd); t["pass0"] = round(time.time() - s, 1)
    log(f"    pass0: {p0fps}fps {p0n} frames, {len(p0['phases'])} phases")
    if global_path:
        os.makedirs(os.path.dirname(global_path), exist_ok=True)
        json.dump({**p0, "pass0_fps": p0fps}, open(global_path, "w"), ensure_ascii=False, indent=1)
    s = time.time(); coarse, cva, cwin = coarse_pass1(row, video, wd, p0); t["coarse_p1"] = round(time.time() - s, 1)
    flags = phase_flags(coarse, p0["phases"])
    log(f"    coarse: {len(coarse)} segs ({cwin} win)")
    s = time.time(); coarse = stage2_v3(row, video, wd, coarse, "coarse"); t["coarse_s2"] = round(time.time() - s, 1)
    s = time.time(); fine, fva, fflags, n_raw = fine_from_coarse(row, video, wd, coarse, narr_path, raw_path); t["fine_AB"] = round(time.time() - s, 1)
    flags += fflags
    log(f"    fine: {n_raw} raw -> {len(fine)} merged segs")
    s = time.time(); fine = stage2_v3(row, video, wd, fine, "fine"); t["fine_s2"] = round(time.time() - s, 1)
    return dict(pass0=p0, pass0_fps=p0fps, coarse=coarse, coarse_va=cva, cwin=cwin, fine=fine, fine_va=fva, n_fine_raw=n_raw, flags=flags, timing=t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default=str(annotate.DEFAULT_JSONL_PATH))
    ap.add_argument("--video_dir", default=str(annotate.DEFAULT_VIDEO_DIR))
    ap.add_argument("--video_list", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out_coarse", required=True)
    ap.add_argument("--out_fine", required=True)
    ap.add_argument("--font-file", default=None)
    args = ap.parse_args()
    annotate.FONT_FILE = annotate._find_font_file(args.font_file)
    meta = [json.loads(l) for l in open(args.jsonl)]
    if args.video_list:
        want = set(l.strip() for l in open(args.video_list) if l.strip())
        meta = [r for r in meta if r["video_path"] in want]
    if args.limit: meta = meta[:args.limit]
    done = set()
    for f in (args.out_coarse,):
        if os.path.exists(f):
            done |= {json.loads(l)["video_path"] for l in open(f)}
    fc = open(args.out_coarse, "a"); ff = open(args.out_fine, "a")
    REPO = str(annotate.REPO_ROOT); nok = nfail = 0
    for k, row in enumerate(meta):
        vp = row["video_path"]
        if vp in done: continue
        video = os.path.join(args.video_dir, vp)
        if not os.path.exists(video): log(f"SKIP {vp}"); continue
        log(f"[{k+1}/{len(meta)}] {vp} dur={row['duration_in_sec']}s")
        narr_path = os.path.join(REPO, "vlm", "outputs", "narrations", f"{vp[:-4]}_fine.json")
        global_path = os.path.join(REPO, "vlm", "outputs", "global", f"{vp[:-4]}.json")
        raw_path = os.path.join(REPO, "vlm", "outputs", "fine_raw", f"{vp[:-4]}_fine.json")
        try:
            with tempfile.TemporaryDirectory(dir="/tmp") as wd:
                r = annotate_video(row, video, wd, narr_path, global_path, raw_path)
            base = dict(video_path=vp, task=row.get("task", ""), domain=row.get("domain", ""), query=row.get("query", ""),
                        duration_in_sec=row["duration_in_sec"], pass0=r["pass0"], pass0_fps=r["pass0_fps"],
                        flags=r["flags"], timing=r["timing"])
            cerr = v2.validate(r["coarse"], r["coarse_va"], row["duration_in_sec"])
            ferr = v2.validate(r["fine"], r["fine_va"], row["duration_in_sec"])
            fc.write(json.dumps({**base, "granularity": "coarse", "n_windows": r["cwin"], "segments": r["coarse"],
                                 "video_assessment": r["coarse_va"], "validation_errors": cerr}, ensure_ascii=False) + "\n"); fc.flush()
            ff.write(json.dumps({**base, "granularity": "fine", "segments": r["fine"], "n_fine_raw": r["n_fine_raw"],
                                 "video_assessment": r["fine_va"], "validation_errors": ferr}, ensure_ascii=False) + "\n"); ff.flush()
            nok += 1
            ratio = len(r["fine"]) / max(1, len(r["coarse"]))
            log(f"    -> ok: coarse {len(r['coarse'])} / fine {r['n_fine_raw']} raw->{len(r['fine'])} merged (x{ratio:.1f}), flags={len(r['flags'])}, cerr={len(cerr)} ferr={len(ferr)}")
        except Exception as e:
            nfail += 1
            rec = {"video_path": vp, "status": "failed", "error": f"{type(e).__name__}: {str(e)[:300]}", "raw_output": getattr(e, "raw", None)}
            fc.write(json.dumps(rec, ensure_ascii=False) + "\n"); fc.flush()
            ff.write(json.dumps(rec, ensure_ascii=False) + "\n"); ff.flush()
            log(f"    -> FAILED: {type(e).__name__}: {str(e)[:120]}")
    log(f"DONE: {nok} ok, {nfail} failed")


if __name__ == "__main__":
    main()
