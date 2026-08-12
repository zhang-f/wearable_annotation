#!/usr/bin/env python3
"""v4: re-run ONLY Pass B (boundary derivation) on the existing v3 narrations, fixing the
time-semantics bug (first-segment label stretched over the pre-engagement idle period).

- Pass A narrations are reused unchanged (outputs/narrations_v3/); coarse is untouched.
- Pass B v4 reports each segment's start_t; the segment spans [start_t_k, start_t_{k+1}),
  and explicit idle segments (type:"idle") are emitted for the leading gap (and genuine
  mid pauses). A deterministic leading-idle safety net guarantees the fix even if the model
  forgets. Every segment carries "type": "action" | "idle".
- Refinements R/M/F/FR are re-run on raw_v4 (idle segments preserved as hard anchors).
- Results go to *_v4 dirs; prior versions untouched. Bundle gains raw_v4/R_v4/M_v4/F_v4/FR_v4.
"""
import argparse, json, os
import annotate_v3 as v3
import refine_fine as rf

OUT = rf.OUT
IDLE_LEAD_S = 1.5
_IDLE_LEAD = "no interaction (hands not yet engaged)"
_IDLE_MID = "no hand activity"


def _is_idle(s):
    return s.get("type") == "idle" or str(s.get("summary", "")).lower().startswith("no interaction") \
        or str(s.get("summary", "")).lower().startswith("no hand activity")


def build_passB_v4(row, csum, ss, se, narration):
    p = v3._T["fineB_v4"]
    for k, val in {"TASK": row.get("task", ""), "COARSE_SUMMARY": csum, "SEG_START": f"{ss:.1f}",
                   "SEG_END": f"{se:.1f}", "NARRATION_JSON": json.dumps(narration, ensure_ascii=False)}.items():
        p = p.replace("{" + k + "}", val)
    return p


def _finalize(items, ss, se):
    """items: list of {type, summary, start, bc} -> consecutive segments with end_time."""
    items = [it for it in items if it["start"] is not None]
    items.sort(key=lambda x: x["start"])
    # clamp starts into range
    for it in items:
        it["start"] = max(ss, min(se, it["start"]))
    # leading-idle safety net (deterministic): if the first real segment starts >1.5s in, prepend idle
    if items and items[0]["type"] != "idle" and (items[0]["start"] - ss) > IDLE_LEAD_S:
        items.insert(0, {"type": "idle", "summary": _IDLE_LEAD, "start": round(ss, 1), "bc": 0.5})
    out = []
    for k, it in enumerate(items):
        end = items[k + 1]["start"] if k + 1 < len(items) else se
        if end <= it["start"]:
            end = round(it["start"] + 0.1, 1)
        out.append({"summary": it["summary"], "end_time": round(min(end, se), 1),
                    "boundary_confidence": round(it["bc"], 3), "type": it["type"]})
    if out:
        out[-1]["end_time"] = round(se, 1)
    # enforce idle thresholds: keep a leading idle only if >=1.5s, a mid idle only if >=4s;
    # drop a too-short leading idle (next action starts at seg start), merge a too-short mid
    # idle into the previous action. This removes the model's spurious sub-second "idle"s.
    cleaned = []
    for o in out:
        if o.get("type") == "idle":
            start = cleaned[-1]["end_time"] if cleaned else ss
            dur = o["end_time"] - start
            thresh = 4.0 if cleaned else IDLE_LEAD_S
            if dur < thresh:
                if cleaned:
                    cleaned[-1]["end_time"] = o["end_time"]
                continue
        cleaned.append(o)
    pe = ss
    for o in cleaned:  # strict monotonic
        if o["end_time"] <= pe:
            o["end_time"] = round(pe + 0.1, 1)
        pe = o["end_time"]
    return cleaned


def _deterministic(narration, ss, se):
    if not narration:
        return [{"summary": _IDLE_LEAD, "end_time": round(se, 1), "boundary_confidence": 0.4, "type": "idle"}]
    items = []
    if (narration[0]["t"] - ss) > IDLE_LEAD_S:
        items.append({"type": "idle", "summary": _IDLE_LEAD, "start": round(ss, 1), "bc": 0.5})
    for e in narration:
        items.append({"type": "action", "summary": e["action"], "start": float(e["t"]), "bc": 0.8})
    # confidence from following gap
    for k in range(len(items)):
        nxt = items[k + 1]["start"] if k + 1 < len(items) else se
        gap = nxt - items[k]["start"]
        if items[k]["type"] == "action":
            items[k]["bc"] = 0.9 if gap < 2 else (0.6 if gap < 4 else 0.4)
    return _finalize(items, ss, se)


def passB_v4(row, csum, ss, se, narration):
    prompt = build_passB_v4(row, csum, ss, se, narration)
    for attempt in (1, 2):
        v3.v2._SAMPLING["temperature"] = 0.0 if attempt == 1 else 0.2
        v3.v2._SAMPLING["repetition_penalty"] = 1.1
        try:
            d = json.loads(v3.v2._strip_fence(v3.v2._call_text(prompt, 6144)))
            items = []
            for s in d["segments"]:
                try:
                    start = float(s["start_t"])
                except (KeyError, ValueError, TypeError):
                    continue
                items.append({"type": ("idle" if s.get("type") == "idle" else "action"),
                              "summary": s.get("summary", ""), "start": start,
                              "bc": v3._coerce_conf(s.get("boundary_confidence", 0.5))})
            if items:
                return _finalize(items, ss, se)
        except Exception:
            pass
    v3.log(f"      passB_v4 fell back to deterministic for [{ss:.0f}-{se:.0f}]")
    return _deterministic(narration, ss, se)


def refine_preserving_idle(raw, fn):
    """Apply a refine callable to maximal runs of action segments, keeping idle segments
    as fixed standalone anchors so they are never merged into an action."""
    out = []; run = []
    def flush():
        if run:
            out.extend(fn(run)); run.clear()
    for s in raw:
        if _is_idle(s):
            flush()
            out.append({"summary": s["summary"], "end_time": s["end_time"],
                        "boundary_confidence": s["boundary_confidence"], "type": "idle",
                        "merge_info": {"merged_from": 1, "rule": "idle", "source_indices": s.get("_idx", [])}})
        else:
            run.append(s)
    flush()
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--videos", nargs="+", required=True); args = ap.parse_args()
    coarse = {json.loads(l)["video_path"]: json.loads(l) for l in open(OUT / "phase1v3_coarse.jsonl")}
    for d in ("fine_raw_v4", "fine_refined_R_v4", "fine_refined_M_v4", "fine_refined_F_v4", "fine_refined_FR_v4"):
        os.makedirs(OUT / d, exist_ok=True)
    rep = []
    for vp in args.videos:
        vid = vp[:-4]; c = coarse[vp]; task = c.get("task", "")
        narr_arch = json.load(open(OUT / "narrations_v3" / f"{vid}_fine.json"))
        raw = []
        for blk in narr_arch:
            ss, se = blk["range"]; csum = blk["coarse_summary"]; ci = blk["coarse_idx"]
            segs = passB_v4({"task": task}, csum, ss, se, blk["narration"])
            for s in segs:
                s["coarse_idx"] = ci; raw.append(s)
        for gi, s in enumerate(raw):
            s["_idx"] = [gi]
        json.dump([{k: v for k, v in s.items() if k != "_idx"} for s in raw],
                  open(OUT / "fine_raw_v4" / f"{vid}_fine.json", "w"), ensure_ascii=False, indent=1)
        n_idle = sum(1 for s in raw if _is_idle(s))
        v3.log(f"[{vid}] raw_v4 {len(raw)} segs ({n_idle} idle)")
        csums = [s["summary"] for s in c["segments"]]
        R = refine_preserving_idle(raw, rf.refine_R)
        M = refine_preserving_idle(raw, lambda run: rf.refine_M(run, task, csums)[0])
        F = refine_preserving_idle(raw, rf.refine_F)
        FR = refine_preserving_idle(raw, lambda run: rf.refine_FR(rf.refine_F(run), run))
        for name, data in [("R", R), ("M", M), ("F", F), ("FR", FR)]:
            json.dump(data, open(OUT / f"fine_refined_{name}_v4" / f"{vid}_fine.json", "w"), ensure_ascii=False, indent=1)
        raw_tagged = [{"summary": s["summary"], "end_time": s["end_time"], "boundary_confidence": s["boundary_confidence"],
                       "type": s.get("type", "action"),
                       "merge_info": {"merged_from": 1, "rule": ("idle" if _is_idle(s) else None), "source_indices": [i]}}
                      for i, s in enumerate(raw)]
        bpath = OUT / "review_bundle" / f"{vid}.json"; b = json.load(open(bpath))
        b["fine_versions"].update({"raw_v4": raw_tagged, "R_v4": R, "M_v4": M, "F_v4": F, "FR_v4": FR})
        json.dump(b, open(bpath, "w"), ensure_ascii=False)
        rep.append((vid, len(raw), n_idle, len(R), len(M), len(F), len(FR)))
        v3.log(f"[{vid}] v4 done: raw {len(raw)} ({n_idle} idle) / R {len(R)} / M {len(M)} / F {len(F)} / FR {len(FR)}")
    print("\n==== v4 (idle-explicit) raw(idle) / R / M / F / FR ====")
    for vid, nr, ni, nR, nM, nF, nFR in rep:
        print(f"{vid:18} raw {nr}({ni} idle)  R {nR}  M {nM}  F {nF}  FR {nFR}")


if __name__ == "__main__":
    main()
