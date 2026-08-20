#!/usr/bin/env python3
"""Shared segment-state reconstruction: QC base segments + an append-only
corrections/{file_no}_{video_id}.jsonl action log -> current segment list.
Used by BOTH server.py (to render the live editing state) and
merge_corrections.py (to produce the final gold). Single source of truth for
replay semantics so the two never drift.

Action log line: {"seq", "ts", "reviewer", "file_no", "video_id",
"granularity", "seg_index", "action", "payload"}. `seq` is assigned by the
server at write time (monotonic per video-file, across both granularities)
and is what "undo" targets (payload {"undo_seq": N} means: when replaying,
skip the line whose seq == N, as if it never happened -- this also correctly
"undoes" a merge/delete/add, since skipping that line restores the pre-action
segment layout it would otherwise have produced).

Documented decisions (ambiguous in the task spec, recorded here as the single
source of truth -- see README.md's "Correction semantics" section for the
same list restated for a non-code audience):
- "merge m: 当前段并入下一段" -- the CURRENT segment (seg_index) is absorbed
  INTO the next one (seg_index+1), which survives: result end_time = the
  next segment's end_time (unchanged), summary = the NEXT segment's summary
  (it is the "host"), boundary_confidence = min of the two, merge_info
  merged_from summed and source_indices concatenated. If a review wants the
  *current* segment's summary to survive, that's an `edit` after the merge.
- "delete x: 删除当前段（其时间并入前段；首段则并入后段）" -- for
  seg_index>0: the previous segment's end_time is extended to the deleted
  segment's end_time (absorbing its span), then the deleted segment is
  removed. For seg_index==0 (no previous): the segment is simply removed;
  because every segment's start is *derived* (previous segment's end_time,
  or 0 for the first), the new first segment's start becomes 0 automatically
  -- no explicit "merge into next" arithmetic is needed for this case.
- "add n: 新增边界，原段一分为二，新段 summary 即时输入" -- the FIRST half
  ([old_start, t)) keeps the original segment's summary/confidence/type
  (it's a continuation of what was already there); the SECOND half
  ([t, old_end)) is the genuinely new segment and takes the reviewer's typed
  summary, default boundary_confidence 0.5, type "action" unless payload
  overrides it, and merge_info {merged_from:1, rule:"manual_add",
  source_indices:[]}.
- retime clamps to keep segments strictly ordered (end_time must stay in
  (prev_segment_end, next_segment_end) at replay time) -- the UI is expected
  to prevent an invalid retime interactively, but replay clamps defensively
  so a corrections log can never produce an inverted/zero-length segment
  even if the UI's own guard had a bug.
- "clear_all: 整条轨清空重标" -- collapses every current segment in the
  granularity down to a single blank segment spanning the whole track
  (summary=""), for a reviewer who wants to re-cut a track from scratch
  instead of living with the auto-generated boundaries. One correction
  record regardless of how many segments existed (unlike doing it via
  repeated merges, which would log one record per segment removed) --
  merge_info.merged_from/source_indices are summed/concatenated across all
  the absorbed segments so the provenance isn't lost. seg_index is always 0
  (the action targets the whole track, not a specific segment).
"""
import json
from pathlib import Path

VLM = Path(__file__).parent.parent
FINAL = VLM / "outputs" / "final"
CORRECTIONS = VLM / "corrections"


def load_qc_base(video_path):
    """Returns {"coarse": [...], "fine": [...]} from the read-only QC jsonl,
    or None if the video isn't in the QC set (e.g. failed_final)."""
    out = {}
    for gran in ("coarse", "fine"):
        path = FINAL / f"annotations_{gran}_qc.jsonl"
        found = None
        for line in open(path):
            r = json.loads(line)
            if r["video_path"] == video_path:
                found = r
                break
        if found is None:
            return None
        out[gran] = found
    return out


def load_actions(file_no, video_id):
    """All action log lines for this video, in file order (= chronological)."""
    path = CORRECTIONS / f"{file_no}_{video_id}.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in open(path) if l.strip()]


def _effective_actions(all_actions, granularity):
    """Filters to one granularity, drops mark_done/undo bookkeeping lines,
    and removes any action whose seq is targeted by a later undo."""
    undone_seqs = {a["payload"]["undo_seq"] for a in all_actions
                   if a["action"] == "undo" and "undo_seq" in a.get("payload", {})}
    out = []
    for a in all_actions:
        if a["action"] in ("mark_done", "undo"):
            continue
        if a.get("granularity") != granularity:
            continue
        if a.get("seq") in undone_seqs:
            continue
        out.append(a)
    return out


def replay_granularity(base_segments, all_actions, granularity):
    """Returns the current segment list for one granularity, each segment
    annotated with a non-persisted `_origin_seq` (seq of the action that most
    recently created/touched it; absent for untouched default-pass segments)
    and `_corrections` (list of {action, before} for UI highlighting)."""
    segs = [dict(s, _origin_seq=None, _corrections=[]) for s in base_segments]
    actions = _effective_actions(all_actions, granularity)

    for a in actions:
        act = a["action"]
        idx = a.get("seg_index")
        seq = a.get("seq")
        payload = a.get("payload", {})

        if act == "retime":
            if idx is None or not (0 <= idx < len(segs)):
                continue
            before = segs[idx]["end_time"]
            new_et = float(payload["end_time"])
            lo = segs[idx - 1]["end_time"] if idx > 0 else 0.0
            hi = segs[idx + 1]["end_time"] if idx + 1 < len(segs) else new_et + 1e9
            new_et = max(lo + 0.01, min(new_et, hi - 0.01)) if hi > lo else new_et
            segs[idx]["end_time"] = round(new_et, 2)
            segs[idx]["_origin_seq"] = seq
            segs[idx]["_corrections"].append({"action": "retime", "before": before})

        elif act == "edit":
            if idx is None or not (0 <= idx < len(segs)):
                continue
            before = {"summary": segs[idx]["summary"], "type": segs[idx].get("type")}
            if "summary" in payload:
                segs[idx]["summary"] = payload["summary"]
            if "type" in payload:
                segs[idx]["type"] = payload["type"]
            segs[idx]["_origin_seq"] = seq
            segs[idx]["_corrections"].append({"action": "edit", "before": before})

        elif act == "merge":
            if idx is None or not (0 <= idx < len(segs) - 1):
                continue
            cur, nxt = segs[idx], segs[idx + 1]
            merged = dict(nxt)
            merged["boundary_confidence"] = min(cur.get("boundary_confidence", 0.5),
                                                  nxt.get("boundary_confidence", 0.5))
            cmi = cur.get("merge_info", {"merged_from": 1, "rule": None, "source_indices": []})
            nmi = nxt.get("merge_info", {"merged_from": 1, "rule": None, "source_indices": []})
            merged["merge_info"] = {"merged_from": cmi.get("merged_from", 1) + nmi.get("merged_from", 1),
                                      "rule": "manual_merge",
                                      "source_indices": (cmi.get("source_indices", []) + nmi.get("source_indices", []))}
            merged["_origin_seq"] = seq
            merged["_corrections"] = cur.get("_corrections", []) + nxt.get("_corrections", []) + \
                [{"action": "merge", "before": {"kept": nxt["summary"], "absorbed": cur["summary"]}}]
            segs = segs[:idx] + [merged] + segs[idx + 2:]

        elif act == "delete":
            if idx is None or not (0 <= idx < len(segs)):
                continue
            removed = segs[idx]
            if idx > 0:
                segs[idx - 1]["end_time"] = removed["end_time"]
                segs[idx - 1]["_origin_seq"] = seq
                segs[idx - 1]["_corrections"].append({"action": "delete_absorbed_next", "before": removed["summary"]})
                segs = segs[:idx] + segs[idx + 1:]
            else:
                segs = segs[1:]
                if segs:
                    segs[0]["_corrections"].append({"action": "delete_absorbed_by_next", "before": removed["summary"]})

        elif act == "clear_all":
            if not segs:
                continue
            merged_from = sum(s.get("merge_info", {}).get("merged_from", 1) for s in segs)
            source_indices = []
            corrections = []
            for s in segs:
                source_indices.extend(s.get("merge_info", {}).get("source_indices", []))
                corrections.extend(s.get("_corrections", []))
            combined = dict(segs[-1])  # carries over any extra fields (e.g. end_time_stage1), like merge does
            combined["summary"] = ""
            combined["boundary_confidence"] = 0.5
            combined["type"] = "action"
            combined["merge_info"] = {"merged_from": merged_from, "rule": "manual_clear_all", "source_indices": source_indices}
            combined["_origin_seq"] = seq
            combined["_corrections"] = corrections + [{"action": "clear_all", "before": f"{len(segs)} segments cleared"}]
            segs = [combined]

        elif act == "add":
            if idx is None or not (0 <= idx < len(segs)):
                continue
            t = float(payload["t"])
            orig = segs[idx]
            lo = segs[idx - 1]["end_time"] if idx > 0 else 0.0
            if not (lo < t < orig["end_time"]):
                continue
            first = dict(orig); first["end_time"] = round(t, 2)
            first["_origin_seq"] = seq
            first["_corrections"] = orig.get("_corrections", []) + [{"action": "add_split_left", "before": None}]
            second = {"summary": payload.get("summary", ""), "end_time": orig["end_time"],
                      "boundary_confidence": 0.5, "type": payload.get("type", "action"),
                      "merge_info": {"merged_from": 1, "rule": "manual_add", "source_indices": []},
                      "_origin_seq": seq, "_corrections": [{"action": "add_new", "before": None}]}
            if "end_time_stage1" in orig:
                first["end_time_stage1"] = first["end_time"]
                second["end_time_stage1"] = second["end_time"]
            segs = segs[:idx] + [first, second] + segs[idx + 1:]

    return segs


def replay_video(video_path, file_no, video_id):
    """Full replay for both granularities. Returns None if video not in QC set."""
    base = load_qc_base(video_path)
    if base is None:
        return None
    actions = load_actions(file_no, video_id)
    return {
        "coarse": replay_granularity(base["coarse"]["segments"], actions, "coarse"),
        "fine": replay_granularity(base["fine"]["segments"], actions, "fine"),
        "base": base,
        "actions": actions,
    }


def is_marked_done(file_no, video_id):
    actions = load_actions(file_no, video_id)
    done = False
    for a in actions:
        if a["action"] == "mark_done":
            done = True
        elif a["action"] == "undo" and a.get("payload", {}).get("undo_mark_done"):
            done = False
    return done


def next_seq(file_no, video_id):
    actions = load_actions(file_no, video_id)
    return (max((a.get("seq", 0) for a in actions), default=0)) + 1


def effective_correction_count(file_no, video_id):
    """Count of still-in-force corrective actions (retime/edit/merge/delete/
    add/clear_all) across both granularities -- excludes mark_done/undo
    bookkeeping lines and anything a later undo cancelled."""
    actions = load_actions(file_no, video_id)
    n = 0
    for gran in ("coarse", "fine"):
        n += len(_effective_actions(actions, gran))
    return n
