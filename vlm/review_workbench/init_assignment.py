#!/usr/bin/env python3
"""One-time (idempotent) generator for review_workbench/assignment.json: assigns a
fixed 0001-0500 file_no to every keep-list video in review_priority order.
The 4 failed_final videos (no QC segments to review) get trailing numbers
with status "no_data" so numbering stays stable and the full 500-video scope
from the task is visible in the UI, rather than silently omitted.

Re-running this script does NOT reset claimed_by/status/corrections_count for
existing entries (idempotent refresh of metadata only) -- it must never be
run casually once reviewers have started claiming videos.
"""
import json
from pathlib import Path

VLM = Path(__file__).parent.parent
FINAL = VLM / "outputs" / "final"
WORKBENCH = Path(__file__).parent
ASSIGNMENT = WORKBENCH / "assignment.json"


def flags_summary(flags):
    return {"error": len(flags.get("error", [])), "warn": len(flags.get("warn", [])), "info": len(flags.get("info", []))}


def main():
    priority = json.load(open(FINAL / "review_priority.json"))
    qc_coarse = {r["video_path"]: r for l in open(FINAL / "annotations_coarse_qc.jsonl") for r in [json.loads(l)]}
    qc_fine = {r["video_path"]: r for l in open(FINAL / "annotations_fine_qc.jsonl") for r in [json.loads(l)]}

    existing = {}
    if ASSIGNMENT.exists():
        existing = {e["file_no"]: e for e in json.load(open(ASSIGNMENT)).get("entries", [])}

    entries = []
    n = 1
    for e in priority["order"]:
        vp = e["video_path"]
        vid = vp[:-4]
        file_no = f"{n:04d}"
        crec = qc_coarse[vp]
        frec = qc_fine[vp]
        prior = existing.get(file_no, {})
        entries.append({
            "file_no": file_no, "video_id": vid, "video_path": vp,
            "domain": crec.get("domain", ""), "duration_in_sec": crec["duration_in_sec"],
            "n_coarse": len(crec["segments"]), "n_fine": len(frec["segments"]),
            "tier": e["tier"], "flags": flags_summary(crec["qc"]["flags"]),
            "o2": vp in set(priority.get("o2_spotcheck", [])),
            "claimed_by": prior.get("claimed_by"), "status": prior.get("status", "unclaimed"),
            "claimed_at": prior.get("claimed_at"),
        })
        n += 1

    for vp in priority.get("failed_final", []):
        vid = vp[:-4]
        file_no = f"{n:04d}"
        prior = existing.get(file_no, {})
        entries.append({
            "file_no": file_no, "video_id": vid, "video_path": vp,
            "domain": "", "duration_in_sec": None, "n_coarse": 0, "n_fine": 0,
            "tier": "failed_final", "flags": {"error": 0, "warn": 0, "info": 0}, "o2": False,
            "claimed_by": None, "status": "no_data", "claimed_at": None,
        })
        n += 1

    json.dump({"entries": entries}, open(ASSIGNMENT, "w"), ensure_ascii=False, indent=1)
    print(f"wrote {ASSIGNMENT}: {len(entries)} entries ({n-1} total, "
          f"{sum(1 for e in entries if e['status']!='no_data')} reviewable)")


if __name__ == "__main__":
    main()
