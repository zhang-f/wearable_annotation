#!/usr/bin/env python3
"""v5: fix directional-verb errors (insert/remove etc. reversed).

Pipeline (from Pass A; coarse untouched; all prior versions kept):
  Pass A (new directional-rule prompt, sees frames) -> narrations_v5
   -> Pass B v4 (idle-aware) -> raw_v5
     -> Stage 2 direction-check: for each directional segment, feed ±dense 8fps frames and
        ask confirmed/reversed/n-a; auto-flip the verb of "reversed" segments (word-pair map),
        keeping the original in summary_original
       -> refinements R/M/F/FR on the corrected raw
Outputs -> *_v5 dirs; bundle gains raw_v5/R_v5/M_v5/F_v5/FR_v5.
"""
import argparse, json, os, re, tempfile
import annotate_v3 as v3
import refine_fine as rf
import rerun_passB_v4 as v4b

OUT = rf.OUT
VIDDIR = "/ssd/fan/wearable_ai_download/egoproactive/val"

# directional verb pairs (explicit conjugations for correct flipping)
FLIP_RAW = {
    "insert": "remove", "inserts": "removes", "inserting": "removing", "inserted": "removed",
    "remove": "insert", "removes": "inserts", "removing": "inserting", "removed": "inserted",
    "screw": "unscrew", "screws": "unscrews", "screwing": "unscrewing", "screwed": "unscrewed",
    "unscrew": "screw", "unscrews": "screws", "unscrewing": "screwing", "unscrewed": "screwed",
    "open": "close", "opens": "closes", "opening": "closing", "opened": "closed",
    "close": "open", "closes": "opens", "closing": "opening", "closed": "opened",
    "attach": "detach", "attaches": "detaches", "attaching": "detaching", "attached": "detached",
    "detach": "attach", "detaches": "attaches", "detaching": "attaching", "detached": "attached",
    "plug": "unplug", "plugs": "unplugs", "plugging": "unplugging", "plugged": "unplugged",
    "unplug": "plug", "unplugs": "plugs", "unplugging": "plugging", "unplugged": "plugged",
    "put in": "take out", "puts in": "takes out", "putting in": "taking out",
    "take out": "put in", "takes out": "puts in", "taking out": "putting in", "took out": "put in",
    "pick up": "put down", "picks up": "puts down", "picking up": "putting down", "picked up": "put down",
    "put down": "pick up", "puts down": "picks up", "putting down": "picking up",
}
_FLIP_KEYS = sorted(FLIP_RAW, key=len, reverse=True)  # multi-word first

def _is_directional(summary):
    s = (summary or "").lower()
    return any(re.search(r"\b" + re.escape(k) + r"\b", s) for k in _FLIP_KEYS)

def _flip_summary(summary):
    for k in _FLIP_KEYS:
        m = re.search(r"\b" + re.escape(k) + r"\b", summary, re.IGNORECASE)
        if m:
            repl = FLIP_RAW[k]
            if m.group(0)[0].isupper():
                repl = repl[0].upper() + repl[1:]
            return summary[:m.start()] + repl + summary[m.end():]
    return summary


def narrate_only(row, video, wd, coarse_segs):
    """Pass A only (new directional prompt), per coarse segment -> narration archive blocks."""
    full = []; prev = 0.0
    for sidx, cs in enumerate(coarse_segs):
        ss, se = prev, cs["end_time"]; prev = se
        if (se - ss) > v3.BLIND_THRESH_S:
            wins, s = [], ss
            while True:
                we = min(se, s + v3.BLIND_WIN_S); wins.append((s, we))
                if we >= se: break
                s += v3.BLIND_WIN_S - v3.BLIND_OVERLAP_S
        else:
            wins = [(ss, se)]
        narr = []
        for wi, (ws, we) in enumerate(wins):
            frames = v3._ex(video, wd, f"fa_{sidx}_{wi}", v3.FINE_FPS, ws, we)
            n, _ = v3._passA(v3.build_fineA(row, cs["summary"], ws, we, win=((ws, we) if len(wins) > 1 else None)),
                             frames, f"seg{sidx}w{wi}")
            narr += n
        narr.sort(key=lambda e: e["t"])
        merged = []
        for e in narr:
            if merged and abs(e["t"] - merged[-1]["t"]) < 1.0 and e["action"] == merged[-1]["action"]:
                continue
            merged.append(e)
        full.append({"coarse_idx": sidx, "range": [round(ss, 1), round(se, 1)], "coarse_summary": cs["summary"], "narration": merged})
        v3.log(f"      passA seg {sidx+1}/{len(coarse_segs)} [{ss:.0f}-{se:.0f}s]: {len(merged)} narration")
    return full


def build_dir(summary, seg_t, ws, we):
    p = v3._T["stage2_dir"]
    for k, val in {"SUMMARY": summary, "SEG_T": f"{seg_t:.1f}", "WIN_START": f"{ws:.1f}", "WIN_END": f"{we:.1f}"}.items():
        p = p.replace("{" + k + "}", val)
    return p


def stage2_direction(row, video, wd, raw):
    dur = row["duration_in_sec"]
    stats = {"confirmed": 0, "reversed": 0, "n/a": 0}; flips = []; prev = 0.0
    for i, s in enumerate(raw):
        seg_start, seg_end = prev, s["end_time"]; prev = seg_end
        if s.get("type") == "idle" or not _is_directional(s["summary"]):
            s["direction_check"] = "n/a"; stats["n/a"] += 1; continue
        ws = max(0.0, seg_start - 1.0); we = min(dur, seg_start + 2.5)  # frames around the action moment
        frames = v3._ex(video, wd, f"dir_{i:03d}", 8.0, ws, we)
        v3._set(0.0, None)
        dc = "n/a"
        try:
            d = json.loads(v3.v2._strip_fence(v3.v2._call(build_dir(s["summary"], seg_start, ws, we), frames, 128)))
            dc = d.get("direction_check", "n/a")
        except Exception:
            dc = "n/a"
        if dc not in ("confirmed", "reversed", "n/a"):
            dc = "n/a"
        s["direction_check"] = dc; stats[dc] += 1
        if dc == "reversed":
            s["summary_original"] = s["summary"]
            s["summary"] = _flip_summary(s["summary"])
            flips.append({"idx": i, "start": round(seg_start, 1), "end": round(seg_end, 1),
                          "before": s["summary_original"], "after": s["summary"]})
    return raw, stats, flips


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--videos", nargs="+", required=True); args = ap.parse_args()
    coarse = {json.loads(l)["video_path"]: json.loads(l) for l in open(OUT / "phase1v3_coarse.jsonl")}
    for d in ("narrations_v5", "fine_raw_v5", "fine_refined_R_v5", "fine_refined_M_v5",
              "fine_refined_F_v5", "fine_refined_FR_v5"):
        os.makedirs(OUT / d, exist_ok=True)
    report = []
    for vp in args.videos:
        vid = vp[:-4]; c = coarse[vp]; task = c.get("task", "")
        row = {"video_path": vp, "task": task, "domain": c.get("domain", ""), "duration_in_sec": c["duration_in_sec"]}
        video = os.path.join(VIDDIR, vp)
        v3.log(f"[{vid}] Pass A (directional prompt)...")
        with tempfile.TemporaryDirectory(dir="/tmp") as wd:
            narr_arch = narrate_only(row, video, wd, c["segments"])
        json.dump(narr_arch, open(OUT / "narrations_v5" / f"{vid}_fine.json", "w"), ensure_ascii=False, indent=1)
        raw = []
        for blk in narr_arch:
            ss, se = blk["range"]
            for s in v4b.passB_v4({"task": task}, blk["coarse_summary"], ss, se, blk["narration"]):
                s["coarse_idx"] = blk["coarse_idx"]; raw.append(s)
        v3.log(f"[{vid}] raw_v5 {len(raw)} segs -> Stage 2 direction check...")
        with tempfile.TemporaryDirectory(dir="/tmp") as wd:
            raw, stats, flips = stage2_direction(row, video, wd, raw)
        json.dump(raw, open(OUT / "fine_raw_v5" / f"{vid}_fine.json", "w"), ensure_ascii=False, indent=1)
        csums = [x["summary"] for x in c["segments"]]
        R = v4b.refine_preserving_idle(raw, rf.refine_R)
        M = v4b.refine_preserving_idle(raw, lambda run: rf.refine_M(run, task, csums)[0])
        F = v4b.refine_preserving_idle(raw, rf.refine_F)
        FR = v4b.refine_preserving_idle(raw, lambda run: rf.refine_FR(rf.refine_F(run), run))
        for name, data in [("R", R), ("M", M), ("F", F), ("FR", FR)]:
            json.dump(data, open(OUT / f"fine_refined_{name}_v5" / f"{vid}_fine.json", "w"), ensure_ascii=False, indent=1)
        raw_tagged = [{"summary": s["summary"], "end_time": s["end_time"], "boundary_confidence": s["boundary_confidence"],
                       "type": s.get("type", "action"), "direction_check": s.get("direction_check"),
                       "summary_original": s.get("summary_original"),
                       "merge_info": {"merged_from": 1, "rule": ("idle" if v4b._is_idle(s) else None), "source_indices": [i]}}
                      for i, s in enumerate(raw)]
        bpath = OUT / "review_bundle" / f"{vid}.json"; b = json.load(open(bpath))
        b["fine_versions"].update({"raw_v5": raw_tagged, "R_v5": R, "M_v5": M, "F_v5": F, "FR_v5": FR})
        b["direction_v5"] = {"stats": stats, "flips": flips}
        json.dump(b, open(bpath, "w"), ensure_ascii=False)
        report.append((vid, len(raw), stats, flips))
        v3.log(f"[{vid}] v5 done: direction {stats}, {len(flips)} flipped")
    print("\n==== v5 direction check ====")
    for vid, nr, stats, flips in report:
        print(f"\n### {vid}: raw {nr}  |  confirmed {stats['confirmed']} · reversed {stats['reversed']} · n/a {stats['n/a']}")
        for f in flips:
            print(f"   [{f['start']}-{f['end']}s]  {f['before']!r}  ->  {f['after']!r}")


if __name__ == "__main__":
    main()
