#!/usr/bin/env python3
"""EgoProactive multi-granularity VLM bootstrap annotation pipeline.

Pipeline per video: extract timestamped frames -> Stage1 whole-video
segmentation (rough end_times, one VLM call over the full span) -> Stage2
boundary refinement (one VLM call per Stage1 boundary, zoomed into a
+/- S2_WINDOW_RADIUS_S window, for a precise end_time) -> validate ->
write one JSONL record per video.

Zero-shot by default. Pass --example <path to a JSON segments list> to add
it to the prompt as a few-shot demonstration (not used in the initial
bootstrap run -- this flag exists for the *next* round, once today's
bootstrap output has been human-corrected).

Frame timestamps are computed in Python (not via ffmpeg's in-filter `t`
expression) and burned in as static text per frame, extracted with one
ffmpeg call per frame using `-ss <t> -i <video> -frames:v 1`. This keeps
the burned-in label and the frame's requested timestamp trivially
consistent by construction; the only open question (verified in the
smoke-test step) is how close ffmpeg's fast (`-ss` before `-i`) seek lands
to the exact requested time.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from openai import OpenAI

# --- config ------------------------------------------------------------

VLM_MODEL = "Qwen3-VL-8B-Instruct"  # must match --served-model-name given to `vllm serve`; edit here if it differs, don't change call sites
VLM_BASE_URL = "http://localhost:8000/v1"
VLM_API_KEY = "EMPTY"  # vLLM doesn't check this; the openai client just requires a non-empty string
VLM_TIMEOUT_S = 300.0

VLM_DIR = Path(__file__).parent
REPO_ROOT = VLM_DIR.parent  # vlm/ is a direct child of the repo root

PROMPT_TEMPLATE_PATH = VLM_DIR / "prompt_template.md"

# Repo conventions (matching tool/server.py): metadata jsonl lives under
# tool/, videos go in videos/ at the repo root. Both overridable via CLI.
DEFAULT_JSONL_PATH = REPO_ROOT / "tool" / "wearable_ai_2026_egoproactive_val_700.jsonl"
DEFAULT_VIDEO_DIR = REPO_ROOT / "videos"

# Candidate fontfile paths for ffmpeg's drawtext (needs libfreetype + an
# actual .ttf on disk -- there's no portable "just use the system default"
# option in ffmpeg's drawtext filter). Checked in order; override with
# --font-file if none of these exist on your machine (e.g. `apt install
# fonts-dejavu-core` provides the first one on Debian/Ubuntu).
FONT_FILE_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
]


def _find_font_file(override: str | None) -> str:
    if override:
        if not os.path.exists(override):
            raise FileNotFoundError(f"--font-file {override!r} does not exist")
        return override
    for candidate in FONT_FILE_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "No usable ffmpeg drawtext font found. Tried: "
        f"{FONT_FILE_CANDIDATES}. Install one (e.g. `apt install "
        "fonts-dejavu-core` on Debian/Ubuntu) or pass --font-file "
        "/path/to/some.ttf."
    )


try:
    FONT_FILE = _find_font_file(os.environ.get("ANNOTATE_FONT_FILE"))
except FileNotFoundError:
    # Deferred: don't hard-fail at import time (e.g. `--help` should still
    # work, and --font-file on the command line hasn't been parsed yet).
    # main() re-resolves this and raises with the same message if it's
    # still unset by the time extract_frames() would actually need it.
    FONT_FILE = None

# Granularity semantics -- aligned in wording with docs/ANNOTATION_SOP.md
# (coarse = major-step/sub-task completion, fine = sub-action via
# hand-object change); meaning unchanged from the original task spec.
GRANULARITY_RULES = {
    "coarse": (
        "One segment = one subtask (a major step / big action toward "
        "completing the overall task, e.g. \"peel the sticker backing "
        "off\"), matching the SOP's coarse definition: mark only when a "
        "major step or big action finishes -- a main step transition, not "
        "every small motion. Place the boundary at the moment the subtask "
        "is VISIBLY COMPLETE -- the hand releases the object and/or "
        "attention shifts to the next step -- NOT at the moment "
        "preparation for the next step begins. This should be sparse."
    ),
    "fine": (
        "One segment = one identifiable sub-action, matching the SOP's "
        "fine definition: mark every sub-action that finishes, even small "
        "ones (e.g. \"picked up the spoon\", \"added the salt\"). The "
        "precise criterion is a HAND-OBJECT CHANGE: cut a new segment the "
        "instant either hand's held/operated object changes -- picked up, "
        "put down, switched hands, or a hand turns to operate a different "
        "object. Record every sub-action, including brief ones (reaching "
        "for something, grabbing a tool, setting something aside). Place "
        "the boundary at the precise moment the hand-object configuration "
        "changes. This should be noticeably denser than coarse."
    ),
}

S1_FPS_DEFAULT = {"coarse": 1.0, "fine": 1.0}
S1_MAX_FRAMES = 128  # safety cap on Stage1 frame count; stride-subsample (lower fps) if exceeded. Must stay <= whatever --limit-mm-per-prompt image= value you passed to `vllm serve`, or requests will fail server-side (see README.md's VLM module section).

S2_WINDOW_RADIUS_S = 3.0  # Stage2 looks at [boundary - radius, boundary + radius]
S2_FPS = 4.0

client = OpenAI(base_url=VLM_BASE_URL, api_key=VLM_API_KEY, timeout=VLM_TIMEOUT_S)


# --- frame extraction ----------------------------------------------------

def _probe_duration(video_path: str) -> float:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path,
        ],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def extract_frames(
    video_path: str,
    out_dir: str,
    fps: float,
    t_start: float = 0.0,
    t_end: float | None = None,
    max_frames: int = 0,
) -> list[tuple[float, str]]:
    """Extract frames from [t_start, t_end] at `fps`, one ffmpeg call per
    frame (precise seek + single-frame extract), burning a static
    `t=XX.Xs` label (computed in Python, matching the requested timestamp
    exactly) into the top-left corner. Returns [(timestamp, frame_path), ...]
    in chronological order. If max_frames > 0 and the naive fps sampling
    would exceed it, the effective fps is reduced to fit."""
    os.makedirs(out_dir, exist_ok=True)

    if t_end is None:
        t_end = _probe_duration(video_path)
    span = t_end - t_start
    if span <= 0:
        return []

    n_frames = max(1, int(round(span * fps)) + 1)
    if max_frames > 0 and n_frames > max_frames:
        fps = (max_frames - 1) / span if span > 0 else fps
        n_frames = max_frames

    timestamps = [round(t_start + i / fps, 1) for i in range(n_frames)]
    timestamps = [t for t in timestamps if t <= t_end + 1e-6]

    results = []
    for idx, t in enumerate(timestamps):
        out_path = os.path.join(out_dir, f"frame_{idx:05d}_t{t:.1f}.png")
        label = f"t={t:.1f}s"
        vf = (
            f"drawtext=fontfile={FONT_FILE}:text='{label}':x=10:y=10:"
            "fontsize=28:fontcolor=yellow:box=1:boxcolor=black@0.5:boxborderw=4"
        )
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", str(t), "-i", video_path,
            "-frames:v", "1", "-vf", vf,
            "-y", out_path,
        ]
        subprocess.run(cmd, check=True)
        results.append((t, out_path))
    return results


def _b64_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# --- prompt construction --------------------------------------------------

def build_prompt(row: dict, granularity: str, stage_instructions: str, example_path: str | None) -> str:
    template = PROMPT_TEMPLATE_PATH.read_text()
    fewshot_block = ""
    if example_path:
        example = json.loads(Path(example_path).read_text())
        fewshot_block = (
            "## Example (for calibration only -- this is a DIFFERENT video)\n\n"
            f"```json\n{json.dumps(example, indent=2)}\n```\n"
        )
    replacements = {
        "{{TASK}}": str(row.get("task", "")),
        "{{QUERY}}": str(row.get("query", "")),
        "{{DOMAIN}}": str(row.get("domain", "")),
        "{{DURATION}}": str(row.get("duration_in_sec", "")),
        "{{GRANULARITY}}": granularity,
        "{{GRANULARITY_RULE}}": GRANULARITY_RULES[granularity],
        "{{STAGE_INSTRUCTIONS}}": stage_instructions,
        "{{FEWSHOT_BLOCK}}": fewshot_block,
    }
    for k, v in replacements.items():
        template = template.replace(k, v)
    return template


def call_vlm(prompt_text: str, frames: list[tuple[float, str]]) -> str:
    content = [{"type": "text", "text": prompt_text}]
    for _t, path in frames:
        content.append(
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{_b64_image(path)}"}}
        )
    resp = client.chat.completions.create(
        model=VLM_MODEL,
        messages=[{"role": "user", "content": content}],
        max_tokens=2048,
        temperature=0.0,
    )
    return resp.choices[0].message.content


# --- JSON parsing ----------------------------------------------------------

def parse_json(raw_text: str) -> list[dict]:
    """Parse the VLM's JSON array output. Only format-level fixes are
    applied (stripping a markdown code fence) -- semantic repair is never
    attempted. Raises ValueError with the raw text attached on failure."""
    text = raw_text.strip()
    fence_match = re.match(r"^```(?:json)?\s*\n(.*)\n```\s*$", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse VLM output as JSON: {e}\n\n--- RAW OUTPUT ---\n{raw_text}\n--- END RAW OUTPUT ---"
        ) from e
    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON array, got {type(data).__name__}.\n\n--- RAW OUTPUT ---\n{raw_text}\n--- END RAW OUTPUT ---"
        )
    return data


# --- stage 1: whole-video segmentation -------------------------------------

def stage1_segment(
    row: dict, video_path: str, granularity: str, workdir: str, s1_fps: float, example_path: str | None
) -> list[dict]:
    frames_dir = os.path.join(workdir, "frames_s1")
    # t_end explicitly pinned to the JSONL's duration_in_sec (the
    # task-relevant span, matching video_intervals' last end time) --
    # NOT left to extract_frames' default of probing the raw mp4's full
    # length, which can be substantially longer than the annotated task
    # (confirmed empirically: this project's videos can have extra footage
    # past the task-relevant span; duration_in_sec is authoritative here).
    frames = extract_frames(video_path, frames_dir, fps=s1_fps, t_end=row["duration_in_sec"], max_frames=S1_MAX_FRAMES)
    stage_instructions = (
        "This is the FULL video from start to end. Segment the entire span "
        "into consecutive segments per the granularity rule above."
    )
    prompt = build_prompt(row, granularity, stage_instructions, example_path)
    raw = call_vlm(prompt, frames)
    return parse_json(raw)


# --- stage 2: boundary refinement ------------------------------------------

def stage2_refine(
    row: dict, video_path: str, granularity: str, workdir: str, rough_segments: list[dict], example_path: str | None
) -> list[dict]:
    duration = row["duration_in_sec"]
    refined = []
    prev_final_end = 0.0
    for i, seg in enumerate(rough_segments):
        rough_end = seg["end_time"]
        t_start = max(0.0, rough_end - S2_WINDOW_RADIUS_S)
        t_end = min(duration, rough_end + S2_WINDOW_RADIUS_S)
        win_dir = os.path.join(workdir, "frames_s2", f"boundary_{i:02d}")
        frames = extract_frames(video_path, win_dir, fps=S2_FPS, t_start=t_start, t_end=t_end)
        stage_instructions = (
            f"This is a SHORT WINDOW (not the full video) around a candidate "
            f"boundary a previous rough pass placed at approximately "
            f"t={rough_end:.1f}s. The window spans t={t_start:.1f}s to "
            f"t={t_end:.1f}s. Output exactly ONE segment covering this whole "
            f"window, with `end_time` corrected to the PRECISE moment "
            f"described by the granularity rule above (it may differ from "
            f"the rough estimate). `summary` should describe what happens "
            f"in this window."
        )
        prompt = build_prompt(row, granularity, stage_instructions, example_path)
        raw = call_vlm(prompt, frames)
        parsed = parse_json(raw)
        if not parsed:
            raise ValueError(f"Stage2 boundary {i} returned no segments.\n\n--- RAW OUTPUT ---\n{raw}")
        refined_end = round(float(parsed[-1]["end_time"]), 1)  # take the last if the model returned >1 despite instructions

        # Each window is refined independently, so nothing stops two
        # adjacent boundaries from crossing (observed in practice: dense
        # fine-grained segments near a stage1 boundary cluster, and
        # multiple boundaries clamped to the same video-end t_end). Enforce
        # monotonicity here rather than let validate() silently fail later
        # -- log every clamp so it's visible how often this fires, since a
        # high rate would mean stage1's rough boundaries are too dense for
        # S2_WINDOW_RADIUS_S to resolve independently.
        if refined_end <= prev_final_end:
            clamped = round(prev_final_end + 0.1, 1)
            print(
                f"[stage2] boundary {i}: refined end_time {refined_end} <= previous final "
                f"end_time {prev_final_end}; clamping to {clamped}",
                file=sys.stderr,
            )
            refined_end = clamped

        refined.append({"summary": seg["summary"], "end_time": refined_end})
        prev_final_end = refined_end
    return refined


# --- validation --------------------------------------------------------

def validate(segments: list[dict], duration_in_sec: float) -> list[str]:
    errors = []
    prev_end = 0.0
    for i, seg in enumerate(segments):
        if not str(seg.get("summary", "")).strip():
            errors.append(f"segment {i}: empty summary")
        end = seg.get("end_time")
        if end is None:
            errors.append(f"segment {i}: missing end_time")
            continue
        if end <= prev_end:
            errors.append(f"segment {i}: end_time {end} not strictly greater than previous end_time {prev_end}")
        prev_end = end
    if segments:
        last_end = segments[-1].get("end_time", 0.0)
        if abs(last_end - duration_in_sec) > 10.0:
            errors.append(f"last segment end_time {last_end} not within 10s of duration {duration_in_sec}")
    else:
        errors.append("no segments produced")
    return errors


# --- main ----------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--jsonl", default=str(DEFAULT_JSONL_PATH),
        help=f"Path to the metadata jsonl (default: repo convention, {DEFAULT_JSONL_PATH})",
    )
    parser.add_argument(
        "--video_dir", default=str(DEFAULT_VIDEO_DIR),
        help=f"Directory containing the downloaded mp4s (default: repo convention, {DEFAULT_VIDEO_DIR})",
    )
    parser.add_argument("--granularity", required=True, choices=["coarse", "fine"])
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--example", default=None,
        help="Path to a JSON few-shot example (a segments list) to include in the prompt. Omit for zero-shot.",
    )
    parser.add_argument(
        "--workdir", default=None,
        help="Fixed working directory for extracted frames (default: a fresh temp dir per video, deleted after).",
    )
    parser.add_argument(
        "--s1_fps", type=float, default=None,
        help=f"Override Stage1 sampling fps (default per-granularity: {S1_FPS_DEFAULT})",
    )
    parser.add_argument(
        "--font-file", default=None,
        help="Override the ffmpeg drawtext font (default: auto-detected, see FONT_FILE_CANDIDATES).",
    )
    args = parser.parse_args()

    global FONT_FILE
    FONT_FILE = _find_font_file(args.font_file)  # re-resolves from candidates if --font-file wasn't given; raises clearly if nothing usable exists

    rows = [json.loads(l) for l in open(args.jsonl)]
    if args.limit:
        rows = rows[: args.limit]

    s1_fps = args.s1_fps if args.s1_fps is not None else S1_FPS_DEFAULT[args.granularity]

    with open(args.out, "w") as out_f:
        for row in rows:
            video_path = os.path.join(args.video_dir, row["video_path"])
            if not os.path.exists(video_path):
                print(f"SKIP {row['video_path']}: not found in {args.video_dir}", file=sys.stderr)
                continue

            def _run(workdir: str):
                print(f"[{row['video_path']}] workdir: {workdir}")
                rough = stage1_segment(row, video_path, args.granularity, workdir, s1_fps, args.example)
                print(f"[{row['video_path']}] stage1: {len(rough)} rough segments")
                refined = stage2_refine(row, video_path, args.granularity, workdir, rough, args.example)
                print(f"[{row['video_path']}] stage2: refined {len(refined)} boundaries")
                return refined

            if args.workdir:
                os.makedirs(args.workdir, exist_ok=True)
                refined = _run(args.workdir)
            else:
                with tempfile.TemporaryDirectory() as tmp:
                    refined = _run(tmp)

            errors = validate(refined, row["duration_in_sec"])
            record = {
                "video_path": row["video_path"],
                "task": row.get("task", ""),
                "domain": row.get("domain", ""),
                "query": row.get("query", ""),
                "granularity": args.granularity,
                "duration_in_sec": row["duration_in_sec"],
                "segments": refined,
                "validation_errors": errors,
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_f.flush()
            print(f"[{row['video_path']}] validation_errors: {errors or 'none'}")


if __name__ == "__main__":
    main()
