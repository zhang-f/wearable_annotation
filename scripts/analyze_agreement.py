#!/usr/bin/env python3
"""Starter inter-annotator agreement analysis for the EgoProactive interrupt-
timing annotations.

NOT a finished statistical framework -- this is a starting point. It
reports the same tolerance-window bidirectional match-rate metric used
earlier in this project's Assembly101 coarse/fine overlap analysis
(Test A): for two annotators' point sets on the same (video, granularity),
"match rate" = fraction of one annotator's points that have some point
from the other annotator within a given time tolerance. This is NOT a
formal kappa -- it doesn't correct for chance agreement -- but it's a
quick, interpretable first read on how much annotators agree, and at
which granularity that agreement is highest/lowest.

Usage:
    python3 analyze_agreement.py [--dir ../annotations] [--tolerances 0.5,1,2.5,5]

Loads every annotations_*.jsonl file in --dir, groups records by
(video_id, granularity), and for every pair of annotators who both
annotated the same (video_id, granularity), computes bidirectional match
rates at each tolerance. Prints a per-granularity summary averaged across
all video/pair combinations, plus the full per-pair table.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from collections import defaultdict
from itertools import combinations


def load_all(directory: str) -> list[dict]:
    records = []
    for path in sorted(glob.glob(os.path.join(directory, "annotations_*.jsonl"))):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def match_rate(points_a: list[float], points_b: list[float], tol: float) -> float:
    """Fraction of points_a that have >=1 point in points_b within tol."""
    if not points_a:
        return float("nan")
    if not points_b:
        return 0.0
    matched = 0
    for pa in points_a:
        if any(abs(pa - pb) <= tol for pb in points_b):
            matched += 1
    return matched / len(points_a)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=os.path.join(os.path.dirname(__file__), "..", "annotations"))
    parser.add_argument("--tolerances", default="0.5,1,2.5,5")
    args = parser.parse_args()
    tolerances = [float(x) for x in args.tolerances.split(",")]

    records = load_all(args.dir)
    if not records:
        print(f"No annotations_*.jsonl files found in {args.dir} -- nothing to analyze yet.")
        return

    # (video_id, granularity) -> annotator_id -> [t, t, ...]
    by_unit: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(dict)
    for r in records:
        key = (r["video_id"], r["granularity"])
        by_unit[key][r["annotator_id"]] = sorted(p["t"] for p in r["points"])

    annotators = sorted({r["annotator_id"] for r in records})
    print(f"Loaded {len(records)} records from {args.dir}")
    print(f"Annotators found: {annotators}")
    print(f"Videos with >=2 annotators on the same granularity: ", end="")
    multi = [k for k, v in by_unit.items() if len(v) >= 2]
    print(len(multi))
    if not multi:
        print("Nothing to compare yet -- need at least 2 annotators on the same video+granularity.")
        return

    # granularity -> tolerance -> list of match rates (both directions, all pairs, all videos)
    by_gran: dict[str, dict[float, list[float]]] = defaultdict(lambda: defaultdict(list))
    pair_rows = []

    for (video_id, gran), ann_points in by_unit.items():
        if len(ann_points) < 2:
            continue
        for a1, a2 in combinations(sorted(ann_points), 2):
            p1, p2 = ann_points[a1], ann_points[a2]
            for tol in tolerances:
                r12 = match_rate(p1, p2, tol)
                r21 = match_rate(p2, p1, tol)
                by_gran[gran][tol].extend([r12, r21])
                pair_rows.append(
                    {
                        "video_id": video_id, "granularity": gran, "tol": tol,
                        "annotator_a": a1, "annotator_b": a2,
                        "n_a": len(p1), "n_b": len(p2),
                        f"{a1}->{a2}": round(r12, 3), f"{a2}->{a1}": round(r21, 3),
                    }
                )

    print("\n=== Summary: mean bidirectional match rate per granularity x tolerance ===")
    print("(NaNs from empty point sets excluded from the mean)")
    for gran in ("free", "coarse", "fine"):
        if gran not in by_gran:
            continue
        print(f"\n{gran}:")
        for tol in tolerances:
            vals = [v for v in by_gran[gran][tol] if v == v]  # drop NaN
            mean = sum(vals) / len(vals) if vals else float("nan")
            print(f"  tolerance={tol}s  mean_match_rate={mean:.3f}  (n={len(vals)} directional comparisons)")

    print("\n=== Full per-pair, per-video table ===")
    for row in pair_rows:
        print(row)


if __name__ == "__main__":
    main()
