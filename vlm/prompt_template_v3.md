<!-- M-v4.1 patch (2026-08-12): explicit hand-transfer (hand-switch) capture, added to
     FINE PASS A / FINE PASS B V4 / FINE REFINE M below.
     M-v4.2 patch (2026-08-14): no-person/no-hands spans (machine running unattended)
     emit no Pass A entries, added to FINE PASS A below. See METHODS.md §2.11/§2.12
     for verification. Everything else in this file is unchanged M-v4. -->

## PASS 0 PROMPT (coarse — global understanding)

You are watching an egocentric (first-person) video of a person performing a task.

**Overall task:** {TASK}
**Domain:** {DOMAIN}
**Video duration:** {DURATION} seconds

Frames are sampled sparsely across the ENTIRE video; each frame has its timestamp burned into the top-left corner (`t=83.5s`). Read time only from this overlay.

Do NOT segment. Output only a brief global understanding:
- task_understanding: 2–3 sentences — what the person is doing and how the work unfolds.
- phases: the major stages you can distinguish, each with a one-line description and an approximate time range (rough is fine).

Output only:
{"task_understanding": "...", "phases": [{"description": "...", "approx_range": [<start_s>, <end_s>]}, ...]}

## COARSE PASS 1 PROMPT (segmentation guided by the global outline)

You are annotating an egocentric (first-person) video of a person performing a task.

**Overall task:** {TASK}
**Domain:** {DOMAIN}
**Video duration:** {DURATION} seconds

Global outline of this video (from a full watch-through — use it to keep segments complete and consistent):
{PASS0_JSON}

Each frame has its timestamp burned into the top-left corner (`t=83.5s`). **Always read timestamps from this overlay — never estimate time from frame order.**

Segment the video into consecutive subtasks and assess the video.

### Granularity definition

A segment is one **subtask**: a self-contained operation that accomplishes a recognizable intermediate goal of the overall task (e.g. "peels the sticker backing", "spreads glue on the notebook cover", "washes the cutting board").
Decision test: at each moment, ask "has one intermediate goal of the task just been achieved?" If yes, the current segment ends there. Picking up, adjusting, or putting down tools within the same intermediate goal does NOT start a new segment.
Boundary rule: mark the boundary at the moment the subtask is visibly **completed** — the hands release the relevant object, or the person's attention clearly shifts to the next subtask. Do NOT place the boundary at the moment the next subtask starts being prepared.
Your segments should be consistent with the global outline above: do not merge across phase transitions, and do not invent structure the outline contradicts.

### Segmentation rules

1. Segments are consecutive and cover the whole video: first starts at 0.0s; each starts where the previous ends; last ends at approximately {DURATION}s.
2. Each segment: `summary` (one concise English sentence, always naming the objects involved), `end_time` (seconds, one decimal, read from the overlay), `boundary_confidence` (∈[0,1]; ≤0.5 when the boundary falls between frames, is occluded, or the transition is gradual; ≥0.8 only when a specific frame clearly shows it).
3. `end_time` strictly increasing.
4. Idle/transitional stretches longer than a few seconds (walking, searching, waiting) are their own segments.
5. If two adjacent frames skip over an obvious change, place the boundary at the midpoint of the two frame timestamps and set `boundary_confidence` ≤ 0.5.
6. Output only a single JSON object, no code fences, no extra text.

### Video assessment rules

- `segmentability` (1–5): 5 = clear structure, boundaries obvious, hands/objects consistently visible; 4 = mostly clear; 3 = workable with substantial ambiguity; 2 = large portions unreliable; 1 = guesswork.
- `issues`: concrete, checkable problems with time ranges (e.g. "hands out of frame 40–80s", "single continuous action, no sub-structure"). Empty array if none.
- `low_confidence_regions`: [start, end] pairs where boundaries should not be trusted. Empty array if none.
- Base the assessment only on what you observed. An honest 2 is more useful than a polite 4.

{EXAMPLE_BLOCK}

### Output format

{"segments": [{"summary": "...", "end_time": 8.4, "boundary_confidence": 0.9}, ...],
 "video_assessment": {"segmentability": 4, "issues": ["..."], "low_confidence_regions": [[31.0, 36.0]]}}

## WINDOWED INPUT NOTE (appended when a video/segment is processed in windows)

This request covers only {WIN_ABS_START}s–{WIN_ABS_END}s of the full {DURATION}s video. All timestamps must be absolute (as burned into the frames). If an action is already in progress at the window start or still ongoing at the end, annotate the visible portion normally.

## FINE PASS A PROMPT (dense narration within one coarse segment)

You are watching one segment of an egocentric video.

**Overall task:** {TASK}
**This segment (from the coarse annotation):** "{COARSE_SUMMARY}", covering {SEG_START}s–{SEG_END}s.

Frames are sampled densely; timestamps are burned into the top-left corner (`t=83.5s`). Read time only from the overlay.

**Naming hands:** A single visible hand is just "hand" — the same physical hand moves across the frame, so its position does NOT identify it. Only when TWO hands are visible in the same frame, label them by their relative position (image-left = "left hand", image-right = "right hand"). In every other case write "hand".

**Hand-transfer events ARE action changes:** when the object visibly passes from one hand to the other, or the hand performing the action switches — both hands visible during the transition, with clear evidence of the handoff itself (the object crossing from one hand's grip into the other's, or one hand releasing exactly as the other takes over) — output an entry at that moment: {"t": <seconds>, "action": "<verb> <object> (hand switch)"}. Base this ONLY on visible contact evidence at the transition moment, never on positional drift across frames, and never guess a hand switch in a stretch where only one hand is ever visible.

**Timing:** the "t" of each entry is the moment the action BEGINS (the moment of contact/grasp or the moment the verb changes) — not when it ends.

If no person or hands are visible in the frames, output NO entries for that span — machines operating on their own (microwave running, kettle boiling) are not hand actions; such spans are idle.

Do NOT segment. Narrate every action change. Each entry is the moment the verb or the object changes, as {"t": <seconds>, "action": "<hand> <verb> <object>"} — use "hand" for a single visible hand, and "left hand"/"right hand" ONLY when both are visible together (e.g. {"t": 84.2, "action": "hand picks up the screwdriver"}; {"t": 90.0, "action": "left hand holds the box while right hand tightens the screw"}).
Rules:
- Output an entry ONLY when the action changes (different verb or different object) or a hand-transfer event occurs as defined above. A change of which hand is doing it is NOT a change EXCEPT for a genuine hand-transfer event. While the same action continues, output nothing.
- Record every distinct action, including brief ones (reaching, grabbing, setting aside).
- Cover the whole range {SEG_START}s–{SEG_END}s.
Output only a JSON array of entries, no extra text.

## FINE PASS B PROMPT (boundary derivation from narration — text only)

Below is a dense narration of hand actions within one segment of a task video ({SEG_START}s–{SEG_END}s, task: {TASK}, segment: "{COARSE_SUMMARY}"):

{NARRATION_JSON}

Derive a fine-grained segmentation under this definition:

A segment is one **atomic action**. A new segment begins whenever EITHER (a) the object being manipulated changes (picks up, puts down, switches to a different object), OR (b) the manipulation action on the same object changes — the verb changes (e.g. picks up the bulb → unscrews the bulb; holds the board → flips the board). **A change of which hand performs the action is NOT a boundary** — only the verb or the object matters. Sustained repetition of the same verb on the same object is ONE segment regardless of duration.
Auxiliary micro-motions that serve the ongoing action (repositioning the cloth while wiping, shifting grip while unscrewing, moving an item slightly to continue the same activity) are NOT verb changes — they belong to the ongoing action's segment. A new segment requires a change in what the person is substantively doing.
Density reference — replacing a light bulb: "picks up the new bulb" → "unscrews the old bulb from the socket" → "puts the old bulb on the table" → "screws the new bulb into the socket".

Rules:
1. Boundaries lie where the narration's verb or object changes (never where only the hand changes); each segment's `end_time` is the timestamp of the last narration entry belonging to it (or the midpoint to the next entry when the gap is large).
2. `summary`: one sentence rewritten from the corresponding narration entries, naming the verb and object. Do NOT name a side for a single-hand action — write "picks up the spoon", not "right hand picks up the spoon". Name hands (left/right) only when two hands act together in the same moment (e.g. "holds the jar and twists the lid").
3. `boundary_confidence`: a NUMBER in [0,1] (a decimal like 0.9 or 0.4 — never the words "high"/"low"). Use ≥0.8 when consecutive narration entries are close in time around the boundary; use ≤0.5 when the gap between entries exceeds ~2s (the true change moment is uncertain).
4. Segments are consecutive over {SEG_START}s–{SEG_END}s; `end_time` strictly increasing; final `end_time` = {SEG_END}.
5. Also output `video_assessment` for this segment (same fields as usual: segmentability 1–5, issues, low_confidence_regions), judged from the narration density and gaps.
6. Output only a single JSON object: {"segments": [...], "video_assessment": {...}}.

{EXAMPLE_BLOCK}

## FINE PASS B V4 PROMPT (boundary derivation with explicit idle segments; text only)

Below is a dense narration of hand actions within one part of a task video (task: {TASK}; this part: "{COARSE_SUMMARY}", covering {SEG_START}s–{SEG_END}s). Each entry {"t": seconds, "action": "..."} marks the moment an action BEGINS (contact/grasp, or the moment the verb/object changes):

{NARRATION_JSON}

Segment this range into consecutive atomic actions, and make no-activity gaps explicit.

Definition: a new segment begins when the verb or the object changes (NOT when the hand changes on its own) — EXCEPT that a narration entry marked "(hand switch)" always begins a new segment there too, since it records a substantive change of who is performing the action (confirmed handoff evidence), not a mere hand label. Sustained repetition of the same verb on the same object is ONE segment. A single visible hand is "hand"; name left/right only when both hands act together.

Timing: each action begins at its entry's `t` and lasts until the next segment begins (the last segment ends at {SEG_END}). Report each segment's `start_t` = the second at which it begins (copy it from the narration `t`).

Make idle gaps explicit — never stretch an action back over a period when the hands were not engaged:
- If the first action begins more than 1.5s after {SEG_START}, the FIRST segment is idle: {"type":"idle","summary":"no interaction (hands not yet engaged)","start_t":{SEG_START}, ...}; the first action then starts at its own `t`.
- If between two actions there is a gap longer than ~4s during which the hands are clearly NOT engaged (a genuine pause — not a slow continuation of the same action), insert an idle segment {"type":"idle","summary":"no hand activity","start_t":<second the pause begins>}. Do NOT insert idle for a sustained or continuing action.

Each segment:
- "type": "action" or "idle".
- "summary": one sentence (verb + object; no left/right for a single hand). For idle use the phrasings above. If this segment begins at a narration entry marked "(hand switch)", append " (hand switch)" to the summary so downstream steps can identify it.
- "start_t": the second at which this segment begins (a NUMBER — a decimal, never a word).
- "boundary_confidence": a NUMBER in [0,1] — lower when the surrounding narration gap is large.

Rules: segments are consecutive and ordered by `start_t`; the first begins at or after {SEG_START}; they cover through {SEG_END}. Output only {"segments":[...]}, no prose, no code fence.

## FINE REFINE M PROMPT (model-based merge of over-segmented fine segments; text only)

Below is a fine-grained segmentation of one part of an egocentric task video (task: {TASK}; this part: "{COARSE_SUMMARY}", covering {SEG_START}s–{SEG_END}s). Each item is a candidate atomic-action segment with an index:

{SEG_LIST_JSON}

Refine this segmentation by merging over-segmentation noise while preserving genuine action sequences, under this definition:

Auxiliary micro-motions serving the ongoing action (repositioning the cloth while wiping, shifting grip, minor adjustments) are NOT separate actions — merge them into the ongoing action's segment. Genuine alternating action sequences (dip brush → paint → dip → paint) ARE separate segments — keep them. A segment boundary requires a change in what the person is substantively doing.

A segment whose summary is marked "(hand switch)" records a genuine, evidence-confirmed change of which hand is performing the action — this is always a substantive action change, NEVER an auxiliary micro-motion, even if the verb/object otherwise looks continuous with its neighbor.

Produce the merged segmentation. Rules:
1. Output segments are consecutive and cover the whole range; every input index belongs to exactly one output segment; input order is preserved (a segment merges only a contiguous run of input indices). Keep any "no interaction" / "no hand activity" (idle) segment as its own separate segment — never merge it into an action. Likewise, never merge a segment whose summary contains "(hand switch)" into a neighboring segment — keep it standalone.
2. Each output segment:
   - "summary": one sentence naming hand/verb/object (rewrite when merging several); if the merged segment corresponds to a "(hand switch)" input segment, keep the "(hand switch)" marker in the rewritten summary.
   - "end_time": the end timestamp (one decimal) = the end_time of the last input segment it covers; the final output segment's end_time = {SEG_END}.
   - "boundary_confidence": a number in [0,1].
   - "merge_info": {"merged_from": <how many input segments>, "source_indices": [<the input indices merged into this segment>]}.
3. `end_time` values strictly increasing.
4. Output only a single JSON object {"segments": [...]}. No prose, no code fence.

## STAGE 2 PROMPT (per-boundary refinement, both granularities)

You previously annotated a segment boundary at approximately {COARSE_T}s: the transition from "{PREV_SUMMARY}" to "{NEXT_SUMMARY}".
Below are densely sampled frames from {WIN_START}s to {WIN_END}s, timestamps burned into the top-left corner.
Identify the exact moment the first segment ends, per the boundary rule: {BOUNDARY_RULE_SHORT}
(coarse: "the moment the subtask is visibly completed (hands release the object / attention shifts)"; fine: "the exact moment the hand's verb or object changes")
Read the timestamp from the frame overlay. Output only: {"end_time": <float>, "boundary_confidence": <float in [0,1]>}
