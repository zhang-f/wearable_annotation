#!/usr/bin/env python3
"""Final gold generator: QC base (read-only) + every corrections/*.jsonl action
log (read-only) -> annotations_{coarse,fine}_final.jsonl (the only file this
script writes). A video's segments are replayed via review_workbench/replay.py;
a segment untouched by any correction is emitted byte-for-byte as it was in
the QC jsonl (the "default pass" contract) with human_reviewed set according
to whether that video has been marked done by a reviewer. Videos never marked
done are still included (using their current, possibly-mid-review, replayed
state) but with human_reviewed=false, so partially-reviewed batches remain
usable/inspectable without blocking on 100% completion.

Never writes to draft/qc jsonl. Never writes to corrections/ or
assignment.json. The only output is annotations_{coarse,fine}_final.jsonl in
--out-dir (default vlm/outputs/final/).

Run from anywhere: `python3 review_workbench/merge_corrections.py` (paths are
resolved relative to this file's location, not the current working directory).
"""
import argparse, json, sys
from pathlib import Path

WORKBENCH = Path(__file__).parent
VLM = WORKBENCH.parent
sys.path.insert(0, str(VLM))
from review_workbench import replay  # noqa: E402

FINAL = VLM / "outputs" / "final"


def strip_internal(seg):
    return {k: v for k, v in seg.items() if not k.startswith("_")}


def build_output_record(base_rec, segments, human_reviewed):
    return {
        "video_path": base_rec["video_path"], "task": base_rec.get("task", ""),
        "domain": base_rec.get("domain", ""), "query": base_rec.get("query", ""),
        "duration_in_sec": base_rec["duration_in_sec"], "pass0": base_rec.get("pass0", {}),
        "granularity": base_rec["granularity"],
        **({"n_windows": base_rec["n_windows"]} if "n_windows" in base_rec else {}),
        "segments": [strip_internal(s) for s in segments],
        "video_assessment": base_rec.get("video_assessment", {}),
        "validation_flags": base_rec.get("validation_flags", []),
        "human_reviewed": human_reviewed,
    }


def run_merge(out_dir=FINAL):
    """Core merge logic, importable by both the CLI below and the review
    server (so the workbench's "merge all" button runs the exact same code
    path, not a reimplementation). Returns a stats dict; writes the same two
    files as always."""
    out_dir = Path(out_dir)
    assignment = json.load(open(WORKBENCH / "assignment.json"))
    coarse_out, fine_out = [], []
    n_done = n_touched = n_untouched_default_pass = 0

    for e in assignment["entries"]:
        if e["status"] == "no_data":
            continue
        vp, file_no, vid = e["video_path"], e["file_no"], e["video_id"]
        state = replay.replay_video(vp, file_no, vid)
        if state is None:
            continue
        done = replay.is_marked_done(file_no, vid)
        touched = len(state["actions"]) > 0 and any(
            a["action"] not in ("mark_done", "undo") for a in state["actions"])
        if done:
            n_done += 1
        if touched:
            n_touched += 1
        else:
            n_untouched_default_pass += 1

        coarse_out.append(build_output_record(state["base"]["coarse"], state["coarse"], done))
        fine_out.append(build_output_record(state["base"]["fine"], state["fine"], done))

    with open(out_dir / "annotations_coarse_final.jsonl", "w") as f:
        for r in coarse_out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out_dir / "annotations_fine_final.jsonl", "w") as f:
        for r in fine_out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return {
        "n_coarse": len(coarse_out), "n_fine": len(fine_out),
        "n_done": n_done, "n_touched": n_touched,
        "n_untouched_default_pass": n_untouched_default_pass,
        "out_dir": str(out_dir),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(FINAL))
    args = ap.parse_args()
    stats = run_merge(args.out_dir)
    print(f"wrote {stats['n_coarse']} coarse / {stats['n_fine']} fine records to {stats['out_dir']}")
    print(f"  human_reviewed=true (marked done): {stats['n_done']}")
    print(f"  touched by >=1 correction: {stats['n_touched']}")
    print(f"  untouched (default pass, emitted as-is from qc): {stats['n_untouched_default_pass']}")


if __name__ == "__main__":
    main()
