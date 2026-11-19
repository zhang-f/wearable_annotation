# Predictability labeling result

Completed 93 videos and 506 subtasks by reading the task title and adjacent subtask descriptions. The previous independent video blind-test design was superseded by the user's instruction on 2026-11-11 to decide directly from subtask descriptions. No video was rewatched for this stage.

- strong: 325
- weak: 86
- no: 95 (93 first subtasks have no predecessor)

Rule: strong means the next intermediate goal follows naturally and nearly necessarily from the prior stage; weak means it is plausible but alternatives remain; no means the prior stage does not support the next goal. The current subtask description identifies the target to judge. Each label and reason is in `results/<video_id>.json` and has been merged into `videos/<video_id>.json` as `coarse[].predictability_level` and `coarse[].predictability_reason`.

Validation: 93 videos, 4020 fine segments, 506 coarse segments, zero structural errors in `validation_after_merge.json`. The human fine boundaries were not changed by the merge. Because this is a text-based judgment, these labels describe subtask sequence predictability from descriptions; they are not estimates of a video-blind human or model prediction rate.

## Focused visual corrections found during final review

- `af57359bc6056d66`: overview frame at t=150–159s shows a white wooden chair with backrest and seat. Earlier output called it a table; new action, subtask, goal, inventory, and predictability rationale now use chair. The original task metadata and `old_summary` remain preserved.
- `3a122ee7ff513956`: step #42 frames at t=115–124.333s show the person handling chips with a fork and fingers. The goal final-state text now describes that observed action; the mouth is outside the frame, so eating is not asserted. The fine boundary and strict overrun handling remain unchanged.
