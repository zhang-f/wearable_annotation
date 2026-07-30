# EgoProactive segment-boundary annotation prompt

You are annotating a first-person (egocentric) video of someone performing
a procedural task, for a dataset about when a proactive AI assistant
should speak up. Your job is **not** to write what the assistant should
say -- only to segment the video into consecutive, non-overlapping
segments and give each one a one-sentence summary.

## Task context

- Task: {{TASK}}
- User's query: "{{QUERY}}"
- Domain: {{DOMAIN}}
- Video duration: {{DURATION}} seconds

## Granularity for this pass: {{GRANULARITY}}

{{GRANULARITY_RULE}}

## How to read the frames

You are shown a sequence of frames sampled from the video. **Each frame
has its timestamp burned into the top-left corner**, formatted exactly as
`t=XX.Xs` (seconds, one decimal place). Use these burned-in timestamps as
your source of truth for boundary times -- do not estimate time from frame
position/order alone, read the number on the frame.

{{STAGE_INSTRUCTIONS}}

{{FEWSHOT_BLOCK}}

## Output format

Respond with **only** a JSON array, no markdown code fence, no prose
before or after. Each element is one segment, in chronological order,
covering the entire span shown to you with no gaps and no overlaps:

```
[
  {"summary": "one sentence describing what happens in this segment", "end_time": 12.3},
  {"summary": "...", "end_time": 26.0}
]
```

Rules:
- `end_time` is in seconds, one decimal place, and must exactly match a
  moment you can justify from the burned-in timestamps you were shown.
- `end_time` values must be strictly increasing.
- The last segment's `end_time` should land at (or very close to) the end
  of the span you were shown.
- `summary` must never be empty, and must describe what happens *in that
  segment* (not the boundary event alone).
- Do not include any field other than `summary` and `end_time`.
- Do not wrap the array in a markdown code fence or add any commentary --
  the response must be valid JSON and nothing else.
