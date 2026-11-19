# EgoDual v2: 93 video annotations

This directory contains the final agent annotations for 93 `facebook/wearable-ai` EgoProactive validation videos. Each video has a goal, a newly grouped coarse/subtask sequence, and a fine/step sequence. The fine boundaries were made by a human and retained; action descriptions and coarse groups were rewritten after reviewing timestamped video frames. A few inherited fine tracks stop before the video ends or slightly overrun the container duration; the video `notes` and step `boundary_note` fields record those cases. The release does not silently add or retime human steps.

## Files

- `annotations/<video_id>.json`: final per-video record, including all 4,020 fine steps and 506 coarse subtasks across the set.
- `final_annotations.jsonl`: the same 93 records as compact one-record-per-line JSONL, sorted by video ID.
- `manifest.json`: counts and SHA-256 for every per-video JSON.
- `validate_export.py`: standalone structure, checksum, and JSONL consistency check. Run `python egodual_v2/validate_export.py` from the repository root.
- `annotation_code/`: archived Python code used for frame extraction, per-video annotation construction, schema checks, and preparation. Many per-video builders use paths from the original `/home/fan/google` workspace and preserve the annotation process; they are not a one-command pipeline on a new machine. The existing `vlm/annotate.py` and `vlm/annotate_v3.py` in this repository are earlier VLM pipelines and did not directly create this release.
- `editor/`: the local two-timeline editor and live progress page. It expects annotation JSONs in this directory and H.264 video proxies under repository-root `proxies/<video_id>.mp4` (not included). Run `bash egodual_v2/editor/start.sh`, then open `http://127.0.0.1:8766/` or `/progress`.
- `predictability_text/results/<video_id>.json`: one `no`/`weak`/`strong` judgment and reason per coarse subtask. These labels are also merged into each annotation JSON. The [method report](predictability_text/report.md) explains the criteria.

## Method and interpretation

The frame workflow sampled video with original timestamps burned into the image and checked step ends against native frame presentation timestamps. Goal descriptions summarize the observed full task. Coarse segments each cover consecutive fine steps, with boundaries aligned to trusted human step boundaries. Step summaries describe visible hand-object actions; unclear objects or occluded actions are marked with reduced confidence or notes.

Predictability was labeled from the task title and adjacent subtask descriptions at the user's request: `strong` means a natural, nearly necessary next intermediate goal; `weak` means plausible among several next goals; `no` means the prior subtask does not support the next goal or there is no prior subtask. This is a text-based semantic judgment, not an independently measured video-blind prediction rate. Counts: 325 strong, 86 weak, 95 no (including 93 first subtasks).

Validation at packaging: 93 videos, 4,020 fine steps, 506 coarse subtasks, zero structural errors. No video files or extracted frames are included. Nonportable `evidence_manifest` paths to the local frame cache were omitted from the public export; all annotation content and boundaries are otherwise retained.
