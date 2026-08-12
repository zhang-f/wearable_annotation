#!/usr/bin/env python3
"""Re-run ONLY the fine layer (Pass A -> Pass B -> Stage 2) with the hand-downgraded
prompts, reusing the existing coarse segmentation. All prior outputs are preserved;
new results are written to *_v3 directories and merged into the review bundle as the
raw_v3 / R_v3 / M_v3 / F_v3 / FR_v3 versions.
"""
import argparse, json, os, tempfile
import annotate_v3 as v3
import refine_fine as rf

OUT = rf.OUT
VIDDIR = "/ssd/fan/wearable_ai_download/egoproactive/val"


def rerun_one(vp, c):
    vid = vp[:-4]
    row = {"video_path": vp, "task": c.get("task", ""), "domain": c.get("domain", ""),
           "duration_in_sec": c["duration_in_sec"]}
    video = os.path.join(VIDDIR, vp)
    narr = OUT / "narrations_v3" / f"{vid}_fine.json"
    raw = OUT / "fine_raw_v3" / f"{vid}_fine.json"
    os.makedirs(narr.parent, exist_ok=True); os.makedirs(raw.parent, exist_ok=True)
    with tempfile.TemporaryDirectory(dir="/tmp") as wd:
        fine, fva, fflags, n_raw = v3.fine_from_coarse(row, video, wd, c["segments"], str(narr), str(raw))
        fine = v3.stage2_v3(row, video, wd, fine, "fine")
    return fine, fva, n_raw


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--videos", nargs="+", required=True); args = ap.parse_args()
    coarse = {json.loads(l)["video_path"]: json.loads(l) for l in open(OUT / "phase1v3_coarse.jsonl")}
    fine_rec = {json.loads(l)["video_path"]: json.loads(l) for l in open(OUT / "phase1v3_fine.jsonl")}
    for d in ("fine_raw_v3", "fine_refined_R_v3", "fine_refined_M_v3", "fine_refined_F_v3", "fine_refined_FR_v3"):
        os.makedirs(OUT / d, exist_ok=True)
    fc = open(OUT / "phase1v3_fine_v3.jsonl", "a")
    rep = []
    for vp in args.videos:
        vid = vp[:-4]; c = coarse[vp]; csums = [s["summary"] for s in c["segments"]]
        v3.log(f"[{vid}] re-running fine (hand-downgraded)...")
        fine, fva, n_raw = rerun_one(vp, c)
        raw = json.load(open(OUT / "fine_raw_v3" / f"{vid}_fine.json"))
        R = rf.refine_R(raw); M, _ = rf.refine_M(raw, c.get("task", ""), csums); F = rf.refine_F(raw); FR = rf.refine_FR(F, raw)
        for name, data in [("R", R), ("M", M), ("F", F), ("FR", FR)]:
            json.dump(data, open(OUT / f"fine_refined_{name}_v3" / f"{vid}_fine.json", "w"), ensure_ascii=False, indent=1)
        raw_tagged = [{"summary": s["summary"], "end_time": s["end_time"], "boundary_confidence": s["boundary_confidence"],
                       "merge_info": {"merged_from": 1, "rule": None, "source_indices": [i]}} for i, s in enumerate(raw)]
        fc.write(json.dumps({"video_path": vp, "granularity": "fine_v3", "segments": fine,
                             "n_fine_raw": n_raw, "video_assessment": fva}, ensure_ascii=False) + "\n"); fc.flush()
        bpath = OUT / "review_bundle" / f"{vid}.json"; b = json.load(open(bpath))
        b["fine_versions"].update({"raw_v3": raw_tagged, "R_v3": R, "M_v3": M, "F_v3": F, "FR_v3": FR})
        json.dump(b, open(bpath, "w"), ensure_ascii=False)
        rep.append((vid, len(raw), len(R), len(M), len(F), len(FR)))
        v3.log(f"[{vid}] v3 done: raw {len(raw)} / R {len(R)} / M {len(M)} / F {len(F)} / FR {len(FR)}")
    print("\n==== v3 (hand-downgraded) raw / R / M / F / FR ====")
    for vid, nr, nR, nM, nF, nFR in rep:
        print(f"{vid:18} {nr:4d} {nR:4d} {nM:4d} {nF:4d} {nFR:4d}")


if __name__ == "__main__":
    main()
