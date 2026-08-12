#!/usr/bin/env python3
"""Two read-only post-processing refinements of the raw Pass B fine segmentation.

  R = rule-based merge   (string-normalised same verb+object; A-B-A-B oscillation)
  M = model-based merge   (text-only VLM call per coarse segment)

Inputs (never modified): outputs/fine_raw/<vid>_fine.json (raw Pass B segments),
outputs/phase1v3_coarse.jsonl (task + coarse summaries + pass0 + flags).
Outputs: outputs/fine_refined_R/<vid>_fine.json, outputs/fine_refined_M/<vid>_fine.json,
and outputs/review_bundle/<vid>.json (everything the review page needs, all 3 fine versions).
Each refined segment carries merge_info {merged_from, rule, source_indices}.
"""
import argparse, json, os, re
from pathlib import Path
import annotate_v3 as v3

VLM = Path(__file__).parent
OUT = VLM / "outputs"


# ---------- shared stemmed signature ----------
def _stem(v):
    if v.endswith("ing"): v = v[:-3]
    elif v.endswith("ed"): v = v[:-2]
    elif v.endswith("es"): v = v[:-2]
    elif v.endswith("s"): v = v[:-1]
    return v.rstrip("e")

AUX = {_stem(x) for x in v3.AUX_VERBS}

def _sig(summary):
    toks = [t for t in re.sub(r"[^a-z ]", " ", (summary or "").lower()).split() if t]
    toks = [t for t in toks if t not in v3._HANDS]
    verb = _stem(toks[0]) if toks else ""
    objs = [t for t in toks[1:] if t not in v3._FILLER and t not in v3._ADJ]
    return verb, (objs[0] if objs else ""), set(objs)


# ---------- variant R (rule merge) ----------
def _combine(run, rule):
    by = {}
    for it in run:
        k = it["sig"][:2]; by.setdefault(k, {"dur": 0.0, "sum": it["summary"]})
        by[k]["dur"] += it["end"] - it["start"]
    dom = max(by.values(), key=lambda x: x["dur"])["sum"]
    return {"summary": dom, "end": run[-1]["end"], "start": run[0]["start"], "sig": run[0]["sig"],
            "bc": round(min(it["bc"] for it in run), 3), "n": sum(it["n"] for it in run),
            "src": [g for it in run for g in it["src"]], "rule": rule}

def _osc_ok(a, b):
    return bool(a[2] & b[2]) or a[0] in AUX or b[0] in AUX

def _merge_group(items):
    p1 = []; i = 0
    while i < len(items):
        j = i + 1
        while j < len(items) and items[j]["sig"][:2] == items[i]["sig"][:2]: j += 1
        p1.append(_combine(items[i:j], "same") if j - i > 1 else items[i]); i = j
    out = []; i = 0
    while i < len(p1):
        sset = []; j = i
        while j < len(p1):
            s = p1[j]["sig"][:2]
            if s not in sset:
                if len(sset) == 2: break
                sset.append(s)
            j += 1
        if j - i >= 4 and len(sset) == 2 and _osc_ok(p1[i]["sig"], p1[i + 1]["sig"]):
            out.append(_combine(p1[i:j], "osc")); i = j
        else:
            out.append(p1[i]); i += 1
    return out

def refine_R(raw):
    items = []; prev = 0.0
    for g, s in enumerate(raw):
        items.append({"summary": s["summary"], "end": s["end_time"], "start": prev,
                      "bc": float(s["boundary_confidence"]), "sig": _sig(s["summary"]),
                      "n": 1, "src": [g], "rule": None})
        prev = s["end_time"]
    out = []; i = 0
    while i < len(items):
        j = i
        while j < len(items) and raw[j]["coarse_idx"] == raw[i]["coarse_idx"]: j += 1
        out += _merge_group(items[i:j]); i = j
    return [{"summary": o["summary"], "end_time": round(o["end"], 1), "boundary_confidence": o["bc"],
             "merge_info": {"merged_from": o["n"], "rule": o["rule"], "source_indices": o["src"]}} for o in out]


# ---------- variant M (model merge) ----------
def build_M(task, csum, ss, se, group):
    seglist = [{"index": i, "start": round(it["start"], 1), "end": round(it["end_time"], 1), "summary": it["summary"]}
               for i, it in enumerate(group)]
    p = v3._T["refineM"]
    for k, val in {"TASK": task, "COARSE_SUMMARY": csum, "SEG_START": f"{ss:.1f}",
                   "SEG_END": f"{se:.1f}", "SEG_LIST_JSON": json.dumps(seglist, ensure_ascii=False)}.items():
        p = p.replace("{" + k + "}", val)
    return p

def _call_M(task, csum, ss, se, group):
    # The model returns contiguous source_index runs in order; we honour its merge
    # *boundaries* (the max index of each run) and force full contiguous coverage of
    # 0..N-1, so minor index slips don't discard the whole result. Fallback only on
    # a parse failure or empty output.
    n = len(group)
    for attempt in (1, 2):
        v3.v2._SAMPLING["temperature"] = 0.0 if attempt == 1 else 0.2
        v3.v2._SAMPLING["repetition_penalty"] = 1.1
        try:
            d = json.loads(v3.v2._strip_fence(v3.v2._call_text(build_M(task, csum, ss, se, group), 6144)))
            res = []; expected = 0; pe = ss
            for s in d["segments"]:
                si = [x for x in s.get("merge_info", {}).get("source_indices", []) if isinstance(x, int) and 0 <= x < n]
                hi = max(si) if si else expected
                if hi < expected:
                    continue  # this run is already covered (backward/duplicate) -> skip
                idxs = list(range(expected, hi + 1)); expected = hi + 1
                et = round(float(s.get("end_time", group[hi]["end_time"])), 1)
                if et <= pe: et = round(pe + 0.1, 1)
                pe = et
                res.append({"summary": s["summary"], "end_time": et,
                            "boundary_confidence": v3._coerce_conf(s.get("boundary_confidence", 0.5)),
                            "merge_info": {"merged_from": len(idxs), "rule": "model", "source_indices": [group[x]["gidx"] for x in idxs]}})
            if res:
                if expected < n:  # absorb any uncovered tail into the last segment
                    rem = list(range(expected, n))
                    res[-1]["merge_info"]["source_indices"] += [group[x]["gidx"] for x in rem]
                    res[-1]["merge_info"]["merged_from"] += len(rem)
                res[-1]["end_time"] = round(se, 1)
                return res, False
        except Exception:
            pass
    return None, True  # signal fallback

def refine_M(raw, task, coarse_summaries):
    prev = 0.0; segs = []
    for g, s in enumerate(raw):
        segs.append({**s, "start": prev, "gidx": g}); prev = s["end_time"]
    out = []; i = 0; n_fallback = 0
    while i < len(segs):
        j = i
        while j < len(segs) and segs[j]["coarse_idx"] == segs[i]["coarse_idx"]: j += 1
        group = segs[i:j]; ci = segs[i]["coarse_idx"]
        ss = group[0]["start"]; se = group[-1]["end_time"]
        csum = coarse_summaries[ci] if ci < len(coarse_summaries) else ""
        merged, fell = (None, True) if len(group) < 2 else _call_M(task, csum, ss, se, group)
        if merged is None:
            if len(group) >= 2: n_fallback += 1
            for it in group:
                out.append({"summary": it["summary"], "end_time": round(it["end_time"], 1),
                            "boundary_confidence": float(it["boundary_confidence"]),
                            "merge_info": {"merged_from": 1, "rule": None, "source_indices": [it["gidx"]]}})
        else:
            out += merged
        i = j
    return out, n_fallback


# ---------- divergence R vs M ----------
def _merge_map(segs):
    """index -> group-id, for segments that were merged (merged_from>1)."""
    m = {}
    for gid, s in enumerate(segs):
        mi = s.get("merge_info", {})
        if mi.get("merged_from", 1) > 1:
            for idx in mi.get("source_indices", []):
                m[idx] = gid
    return m

def divergence(raw, R, M):
    """Raw indices where R merged but M didn't, or vice versa."""
    rm = _merge_map(R); mm = _merge_map(M)
    rows = []
    for idx in range(len(raw)):
        inR = idx in rm; inM = idx in mm
        if inR != inM:
            rows.append({"raw_idx": idx, "t": raw[idx]["end_time"], "coarse_idx": raw[idx]["coarse_idx"],
                         "summary": raw[idx]["summary"], "R_merged": inR, "M_merged": inM})
    return rows


# ---------- variant F (verb-category rule filter) ----------
# EDITABLE word lists. Each non-action category has a merge DIRECTION; a raw fine
# segment whose primary verb falls in a category is absorbed into a neighbouring
# action segment in that direction. Verbs are stem-normalised before matching.
F_WORDS = {
    "approach": ["reach", "approach", "extend", "move toward", "hover"],       # -> next
    "withdraw": ["withdraw", "retract", "pull back", "move away", "lower"],     # -> prev (empty hand)
    "static":   ["hold", "keep", "stabilize", "support", "steady", "brace", "grip", "cradle"],  # -> same-object adjacent (prev first)
    "adjust":   ["adjust", "reposition", "shift", "regrip", "readjust"],        # -> ongoing action (prev first)
    "continue": ["continue", "keep", "still"],                                  # + same verb+object as prev -> prev
    "hover":    ["hover", "pause over"],                                        # -> next
    "nonhand":  ["look", "glance", "gaze", "camera", "head"],                   # -> adjacent (prev first), desc discarded
    "carry":    ["move", "bring", "carry", "transport"],                        # <object> toward/to -> next
}
F_DIRECTION = {"approach": "next", "hover": "next", "carry": "next",
               "withdraw": "prev", "continue": "prev",
               "static": "prev_same", "adjust": "prev_ongoing", "nonhand": "prev_adj"}

def _sset(*ws): return {_stem(w) for w in ws}
ST_NONHAND = _sset("look", "glance", "gaze")
ST_ADJUST = _sset("adjust", "reposition", "shift", "regrip", "readjust")
ST_APPROACH = _sset("reach", "approach", "extend")
ST_HOVER = _sset("hover")
ST_MOVE = _sset("move", "bring", "carry", "transport") | {"carri"}
ST_WITHDRAW = _sset("withdraw", "retract")
ST_STATIC = _sset("hold", "keep", "stabilize", "support", "steady", "brace", "grip", "cradle")

def classify_F(summary, prev_summary):
    s = " " + re.sub(r"[^a-z ]", " ", (summary or "").lower()) + " "
    verb, obj, _ = _sig(summary)
    pverb, pobj, _ = _sig(prev_summary) if prev_summary else ("", "", set())
    def ph(*p): return any((" " + x + " ") in s for x in p)
    if verb in ST_NONHAND or " camera " in s or (" head " in s and verb in ("turn", "tilt", "mov", "")):
        return "nonhand"
    if verb in ST_ADJUST:
        return "adjust"
    if (verb == "continu" or " still " in s or (verb == "keep" and pobj)) and pobj and obj == pobj:
        return "continue"
    if ph("move away", "moves away", "moving away", "pull back", "pulls back", "pulled back") \
            or verb in ST_WITHDRAW or (verb == "lower" and not obj) or (verb in ST_MOVE and " away " in s):
        return "withdraw"
    if verb in ST_HOVER or ph("pause over", "pauses over"):
        return "hover"
    if verb in ST_APPROACH:
        return "approach"
    if verb in ST_MOVE and (ph("toward", "towards", "over to") or " to " in s):
        return "carry" if obj else "approach"
    if verb in ST_STATIC:
        return "static"
    return None  # real action -> anchor

def _pick_anchor(k, d, anchors, group):
    prevs = [a for a in anchors if a < k]; nexts = [a for a in anchors if a > k]
    np_, nn_ = (max(prevs) if prevs else None), (min(nexts) if nexts else None)
    if d == "next":
        return nn_ if nn_ is not None else np_
    if d == "prev_same":
        _, ko, _ = _sig(group[k]["summary"])
        if np_ is not None and _sig(group[np_]["summary"])[1] == ko: return np_
        if nn_ is not None and _sig(group[nn_]["summary"])[1] == ko: return nn_
        return np_ if np_ is not None else nn_
    # prev / prev_ongoing / prev_adj  -> prev first, else next
    return np_ if np_ is not None else nn_

def _F_seg(members, anchor, cats):
    src = [m["g"] for m in members]
    summ = (anchor if anchor is not None else members[0])["summary"]
    absorbed = sorted({c for c in cats if c})
    rule = "+".join(absorbed) if absorbed else None
    return {"summary": summ, "end_time": round(max(m["end"] for m in members), 1),
            "boundary_confidence": round(min(m["bc"] for m in members), 3),
            "merge_info": {"merged_from": len(members), "rule": rule, "source_indices": src},
            "_start": min(m["start"] for m in members)}

def _F_group(group):
    n = len(group)
    cats = [classify_F(group[k]["summary"], group[k - 1]["summary"] if k > 0 else None) for k in range(n)]
    anchors = [k for k in range(n) if cats[k] is None]
    if not anchors:  # no action anchor in this coarse segment -> keep as-is
        return [_F_seg([group[k]], group[k], []) for k in range(n)]
    assign = {}
    for k in range(n):
        assign[k] = k if cats[k] is None else _pick_anchor(k, F_DIRECTION[cats[k]], anchors, group)
    res = []
    for a in sorted(anchors):
        members = sorted([k for k in range(n) if assign[k] == a])
        res.append(_F_seg([group[k] for k in members], group[a], [cats[k] for k in members if k != a]))
    res.sort(key=lambda x: x["_start"]); pe = 0.0
    for r in res:
        if r["end_time"] <= pe: r["end_time"] = round(pe + 0.1, 1)
        pe = r["end_time"]
    return [{k: v for k, v in r.items() if not k.startswith("_")} for r in res]

def refine_F(raw):
    prev = 0.0; segs = []
    for g, s in enumerate(raw):
        segs.append({"summary": s["summary"], "end": s["end_time"], "start": prev,
                     "bc": float(s["boundary_confidence"]), "ci": s["coarse_idx"], "g": g}); prev = s["end_time"]
    out = []; i = 0
    while i < len(segs):
        j = i
        while j < len(segs) and segs[j]["ci"] == segs[i]["ci"]: j += 1
        out += _F_group(segs[i:j]); i = j
    return out

def _fr_fmt(o):
    rule = o["rule"] if o.get("rule") in ("same", "osc") else o.get("frule")
    return {"summary": o["summary"], "end_time": round(o["end"], 1), "boundary_confidence": o["bc"],
            "merge_info": {"merged_from": o["n"], "rule": rule, "source_indices": o["src"]}}

def refine_FR(F, raw):
    """Chain R's oscillation/same-action merge on top of F (F -> R)."""
    prev = 0.0; items = []
    for s in F:
        ci = raw[s["merge_info"]["source_indices"][0]]["coarse_idx"]
        items.append({"summary": s["summary"], "end": s["end_time"], "start": prev, "bc": s["boundary_confidence"],
                      "sig": _sig(s["summary"]), "n": s["merge_info"]["merged_from"],
                      "src": list(s["merge_info"]["source_indices"]), "ci": ci, "frule": s["merge_info"]["rule"]})
        prev = s["end_time"]
    out = []; i = 0
    while i < len(items):
        j = i
        while j < len(items) and items[j]["ci"] == items[i]["ci"]: j += 1
        out += _merge_group(items[i:j]); i = j
    return [_fr_fmt(o) for o in out]


def _load_or(path, fn):
    return json.load(open(path)) if os.path.exists(path) else fn()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", nargs="+", required=True)
    ap.add_argument("--skip-m", action="store_true", help="only produce R (no model calls)")
    args = ap.parse_args()
    coarse = {json.loads(l)["video_path"]: json.loads(l) for l in open(OUT / "phase1v3_coarse.jsonl")}
    fine = {json.loads(l)["video_path"]: json.loads(l) for l in open(OUT / "phase1v3_fine.jsonl")}
    for d in ("fine_refined_R", "fine_refined_M", "fine_refined_F", "fine_refined_FR", "review_bundle"):
        os.makedirs(OUT / d, exist_ok=True)
    report = []
    for vp in args.videos:
        vid = vp[:-4]
        raw = json.load(open(OUT / "fine_raw" / f"{vid}_fine.json"))
        c = coarse[vp]; f = fine[vp]
        csums = [s["summary"] for s in c["segments"]]
        # R and M already exist from the prior task -> load, do NOT recompute/overwrite
        R = _load_or(OUT / "fine_refined_R" / f"{vid}_fine.json", lambda: refine_R(raw))
        M = _load_or(OUT / "fine_refined_M" / f"{vid}_fine.json",
                     lambda: (refine_M(raw, c.get("task", ""), csums)[0]))
        # NEW: F (verb-category rule filter) and FR (F then R)
        F = refine_F(raw)
        FR = refine_FR(F, raw)
        json.dump(F, open(OUT / "fine_refined_F" / f"{vid}_fine.json", "w"), ensure_ascii=False, indent=1)
        json.dump(FR, open(OUT / "fine_refined_FR" / f"{vid}_fine.json", "w"), ensure_ascii=False, indent=1)
        raw_tagged = [{"summary": s["summary"], "end_time": s["end_time"], "boundary_confidence": s["boundary_confidence"],
                       "merge_info": {"merged_from": 1, "rule": None, "source_indices": [i]}} for i, s in enumerate(raw)]
        bundle = {"video_path": vp, "duration_in_sec": c["duration_in_sec"], "task": c.get("task", ""),
                  "domain": c.get("domain", ""), "pass0": c.get("pass0", {}), "flags": c.get("flags", []),
                  "coarse_segments": c["segments"], "coarse_assessment": c.get("video_assessment", {}),
                  "fine_assessment": f.get("video_assessment", {}),
                  "fine_versions": {"raw": raw_tagged, "R": R, "M": M, "F": F, "FR": FR},
                  "divergence": divergence(raw, R, M)}
        json.dump(bundle, open(OUT / "review_bundle" / f"{vid}.json", "w"), ensure_ascii=False)
        report.append((vid, c["duration_in_sec"], len(raw), len(R), len(M), len(F), len(FR)))
        print(f"[{vid}] raw {len(raw)} -> R {len(R)} / M {len(M)} / F {len(F)} / FR {len(FR)}")
    print("\n==== raw / R / M / F / FR ====")
    print(f"{'video':18} {'dur':>5} {'raw':>4} {'R':>4} {'M':>4} {'F':>4} {'FR':>4}")
    for vid, dur, nr, nR, nM, nF, nFR in report:
        print(f"{vid:18} {dur:5.0f} {nr:4d} {nR:4d} {nM:4d} {nF:4d} {nFR:4d}")


if __name__ == "__main__":
    main()
