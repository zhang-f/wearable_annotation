## MAIN PROMPT (Stage 1 — full-video segmentation + self-assessment)

You are annotating an egocentric (first-person) video of a person performing a task.

**Overall task:** {TASK}
**Domain:** {DOMAIN}
**Video duration:** {DURATION} seconds

The video is provided as a sequence of frames. Each frame has its timestamp burned into the top-left corner in the format `t=83.5s`. **Always read timestamps from this overlay — never estimate time from frame order or frame count.**

You have two jobs: (1) segment the entire video into consecutive segments and describe each one; (2) honestly assess how well this video supports segmentation at the required granularity.

### Granularity definition

{GRANULARITY_RULE}

<!-- coarse 规则块 -->
A segment is one **subtask**: a self-contained operation that accomplishes a recognizable intermediate goal of the overall task (e.g. "peels the sticker backing", "spreads glue on the notebook cover", "washes the cutting board").
Decision test: at each moment, ask "has one intermediate goal of the task just been achieved?" If yes, the current segment ends there. Picking up, adjusting, or putting down tools within the same intermediate goal does NOT start a new segment.
Boundary rule: mark the boundary at the moment the subtask is visibly **completed** — the hands release the relevant object, or the person's attention clearly shifts to the next subtask. Do NOT place the boundary at the moment the next subtask starts being prepared.
Density reference — wrapping a gift, coarse segmentation:
"measures and cuts the wrapping paper" → "folds the paper around the box and tapes it" → "ties the ribbon into a bow".

<!-- fine 规则块 -->
A segment is one **atomic action**. A new segment begins whenever EITHER:
(a) the object held or manipulated by either hand changes (picks up, puts
down, swaps hands, switches to a different object), OR
(b) the manipulation action on the same object changes — the verb changes
(e.g. picks up the bulb → unscrews the bulb; holds the board → flips the
board; grabs the cloth → wipes the table).
Decision test: describe each moment as "hand + verb + object". If the verb
or the object differs from the previous moment, a boundary lies between them.
Sustained repetition of the same verb on the same object (continuous
unscrewing, continuous cutting) is ONE segment regardless of duration.
Every distinct action must be recorded, including brief ones.
Density reference — replacing a light bulb, fine segmentation:
"picks up the new bulb" → "unscrews the old bulb from the socket" →
"puts the old bulb on the table" → "screws the new bulb into the socket".

### Segmentation rules

1. Segments are consecutive and cover the whole video: the first segment starts at 0.0s; each segment starts where the previous one ends; the last segment ends at approximately {DURATION}s.
2. For each segment output:
   - `summary`: one concise English sentence describing what the person is doing. Always name the objects involved (e.g. "picks up the scissors and cuts the ribbon" — never "does something with an item").
   - `end_time`: the timestamp in seconds (one decimal) at which this segment ends, read from the frame overlay.
   - `boundary_confidence`: a number in [0,1] for how certain you are about the *location* of this segment's end boundary. Use low values (≤0.5) when: the change happens between two frames and you had to interpolate; hands or the manipulated object are occluded or out of frame near the boundary; the transition is gradual with no clear completion moment. Use high values (≥0.8) only when a specific frame clearly shows the boundary event.
3. `end_time` values must be strictly increasing.
4. If a stretch is idle or transitional (walking, searching for an item, waiting) and lasts more than a few seconds, annotate it as its own segment (e.g. "walks to the shelf looking for the tape").
5. Match the granularity defined above exactly: do not merge distinct units into one segment, and do not split one unit into several.
6. If two adjacent frames skip over an obvious change (the hand-held object differs between them with no intermediate frame), place the boundary at the midpoint of the two frame timestamps and set `boundary_confidence` ≤ 0.5.
7. Output **only** a single JSON object in the format below. No preamble, no markdown code fences, no trailing text.

### Video assessment rules

After segmenting, fill in `video_assessment`:

- `segmentability` (integer 1–5): how well this video supports segmentation **at the required granularity**.
  5 = clear task structure, boundaries obvious, hands and objects consistently visible;
  4 = mostly clear, a few ambiguous transitions;
  3 = workable but with substantial ambiguous stretches or partial visibility;
  2 = large portions cannot be segmented reliably (hands out of frame, chaotic camera, unclear activity);
  1 = segmentation at this granularity is essentially guesswork for most of the video.
- `issues` (array of short strings): concrete, checkable problems you observed, with time ranges where applicable. Examples: "hands out of frame 40–80s", "single continuous action, no sub-structure", "camera motion blurs most object interactions", "long idle stretch 100–160s". Empty array if none.
- `low_confidence_regions` (array of [start, end] second pairs): time ranges where your boundaries should not be trusted. Empty array if none.

Base the assessment only on what you actually observed in the frames. Do not inflate `segmentability` to appear helpful: an honest 2 is more useful than a polite 4, and reporting many issues on a genuinely problematic video is correct behavior, not a failure.

{EXAMPLE_BLOCK}
<!-- EXAMPLE_BLOCK（有手标 example 时注入）：
### Granularity reference (calibration example)
The following is a human annotation of a different video at exactly the granularity we want. Match this density — neither coarser nor finer. (The example shows only summary/end_time; you must additionally output the confidence and assessment fields defined above.)
{EXAMPLE_JSON}
-->

### Output format

{
  "segments": [
    {"summary": "picks up the sticker sheet from the desk", "end_time": 8.4, "boundary_confidence": 0.9},
    {"summary": "peels the backing off the first sticker", "end_time": 15.1, "boundary_confidence": 0.6}
  ],
  "video_assessment": {
    "segmentability": 4,
    "issues": ["hands briefly out of frame 31–35s"],
    "low_confidence_regions": [[31.0, 36.0]]
  }
}

## WINDOWED INPUT NOTE (only included when the video is processed in windows)

This request covers only the time window {WIN_ABS_START}s–{WIN_ABS_END}s of the full {DURATION}s video. All timestamps you output must be absolute (as burned into the frames). Segment this window under the same rules; if an action is already in progress at the window start or still ongoing at the window end, annotate the visible portion and describe it normally.

## STAGE 2 PROMPT (per-boundary refinement)

You previously annotated a segment boundary at approximately {COARSE_T}s: the transition from "{PREV_SUMMARY}" to "{NEXT_SUMMARY}".
Below are densely sampled frames from {WIN_START}s to {WIN_END}s, with timestamps burned into the top-left corner of each frame.
Identify the exact moment the first segment ends, according to the boundary rule: {BOUNDARY_RULE_SHORT}
(coarse: "the moment the subtask is visibly completed (hands release the object / attention shifts)"; fine: "the exact moment the hand–object configuration changes")
Read the timestamp from the frame overlay. Output only: {"end_time": <float>, "boundary_confidence": <float in [0,1]>}

## FINE PASS A PROMPT (dense narration; sees frames)

You are watching an egocentric (first-person) video of a person performing a task.

**Overall task:** {TASK}
**Domain:** {DOMAIN}
**Video duration:** {DURATION} seconds

The video is a sequence of frames, each with its timestamp burned into the top-left corner in the format `t=83.5s`. **Always read timestamps from this overlay — never estimate time from frame order.**

Do NOT segment and do NOT decide boundaries. Your only job is to narrate, moment by moment, what the hands are doing, as densely as the action actually changes.

Rules:
- Describe each moment as "<hand> <verb> <object>" — name the specific hand (left/right/both), the specific verb, and the specific object (e.g. "right hand unscrews the old bulb", "left hand holds the socket"). Never vague ("does something with an item").
- Emit a new entry every time the action changes — whenever the verb changes, the object changes, or a hand picks up / puts down / swaps an object. Include brief actions (reaching, grabbing, setting aside).
- If the same action continues across several frames (still unscrewing), do NOT repeat it — emit it ONCE, at the timestamp where it first becomes visible.
- Read `t` from the burned-in timestamp of that frame. Cover the whole span shown, in chronological order.
- Output ONLY a JSON array, no prose, no markdown fence. Each element is {"t": <seconds, one decimal>, "action": "<hand> <verb> <object>"}.

Example:
[
  {"t": 4.0, "action": "right hand picks up the new bulb from the table"},
  {"t": 7.5, "action": "right hand unscrews the old bulb from the socket"},
  {"t": 12.0, "action": "left hand puts the old bulb on the table"}
]

## FINE PASS B PROMPT (boundary derivation; text only, no frames)

Below is a time-ordered narration of an egocentric video of a person performing the task "{TASK}", produced by reading the video frames. Each entry is {"t": seconds, "action": "<hand> <verb> <object>"}. Video duration: {DURATION} seconds.

Narration:
{NARRATION}

Your job: segment the video into fine-grained atomic-action segments using ONLY this narration, following the definition below.

### Granularity definition (fine)

{GRANULARITY_RULE}

Rules:
1. A boundary lies wherever the verb OR the object changes from the previous narration entry (per the definition above). Sustained repetition of the same verb on the same object is ONE segment.
2. For each segment output:
   - `summary`: one concise sentence rewritten from the narration entries the segment covers, naming the objects (summarise, do not copy an entry verbatim if several belong to one segment).
   - `end_time`: the timestamp (seconds, one decimal) at which the segment ends = the `t` at which the next action starts (for the last segment, ≈ {DURATION}s).
   - `boundary_confidence`: a number in [0,1]. Set it LOW (≤0.5) when the time gap between the two narration entries around this boundary is large (the exact boundary moment is uncertain); HIGH (≥0.8) when the surrounding entries are close together in time.
3. `end_time` values must be strictly increasing; the last ends at approximately {DURATION}s; `summary` never empty.
4. Fill in `video_assessment`: `segmentability` (integer 1–5) for how clearly the narration supports fine segmentation; `issues` (short strings for narration gaps/ambiguities, with time ranges); `low_confidence_regions` ([start, end] second pairs where the narration is sparse or uncertain). Empty arrays if none.
5. Output ONLY a single JSON object {"segments": [...], "video_assessment": {...}}, no prose, no markdown fence.
