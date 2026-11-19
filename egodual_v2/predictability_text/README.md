# Predictability from adjacent subtask descriptions

User correction on 2026-11-11 supersedes the earlier three-predictor blind-test workflow for this annotation pass. Read the task title and subtask descriptions in order. Assess each current subtask against the task title and completed prior subtasks; use the current description only as the target being judged. Do not inspect video or later subtasks. The first subtask has no predecessor and is labeled `no`.

- `strong`: the current intermediate goal is the natural, nearly necessary next stage.
- `weak`: it is plausible from the prior stage, but there are several reasonable next stages.
- `no`: the prior stage does not support predicting this goal, or there is no prior stage.

Each completed video has a sidecar in `results/<video_id>.json` with an index, level, and short reason for every subtask. The previous sealed blind-test bundles and two pilot runs are retained separately under `annotation_v2/predictability/` as historical work; they are not used to assign these labels.
