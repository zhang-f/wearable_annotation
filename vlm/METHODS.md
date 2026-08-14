# METHODS — M-v4 annotation pipeline: evolution, code map, frozen config

This document records how the coarse/fine annotation pipeline for the EgoProactive
keep-set was developed: what each iteration tested, what broke, how it was fixed, and
**exactly which file/function/prompt-section** each change lives in. Audience: an agent
picking this up on another machine, future-me, and the paper's methods section.

Frozen commit: `f23615f freeze M-v4 annotation pipeline` (on `main`).

> **Naming note (read first).** The suffixes `_v3` / `_v4` / `_v5` on output dirs and
> functions denote *pipeline iterations* (hand-downgrade / idle-fix / direction-check),
> **not** template versions. The prompt file is `prompt_template_v3.md` throughout.
> "**M-v4**" = the model-merge (`M`) refinement applied to the `_v4` (idle-explicit) raw,
> which itself consumes the `_v3` (hand-downgraded) Pass A narration. So the frozen chain
> is: Pass A (hand-downgrade + timing) → Pass B v4 (idle) → M merge → Stage 2.

---

## 1. Architecture overview — M-v4 four-layer chain

```
Pass 0  (global understanding, whole video, low fps)
   │  {task_understanding, phases:[{description, approx_range}]}
   ▼
Pass 1  (COARSE segmentation, guided by the Pass-0 outline, 2 fps, windowed if >budget)
   │  coarse segments = subtasks  {summary, end_time, boundary_confidence}
   ▼
[for each coarse segment independently]
   Pass A  (dense narration, 5 fps, sees frames)   →  [{t, action}]   (per-segment)
   Pass B v4 (text-only, no frames)                →  atomic segments + explicit idle,
   │                                                   timing [t_k, t_{k+1})
   ▼
Pass M  (model semantic merge, text-only)          →  fine segments (idle preserved)
   ▼
Stage 2 (per-boundary refinement, BOTH granularities, ±1.5s @ 8 fps, sees frames)
   │  overwrites end_time; original kept as end_time_stage1
   ▼
outputs: annotations_{coarse,fine}.jsonl
```

Key input/output relations:
- **Pass 0 → Pass 1**: the outline is injected into the coarse prompt (`{PASS0_JSON}`) to
  keep coarse segments complete and consistent; a coarse midpoint outside every phase
  range (±15s) raises an outline-mismatch flag.
- **Pass 1 → Pass A**: each coarse segment's `[start,end]` bounds a Pass A call; a coarse
  segment longer than the frame budget (128s) is blind-cut into 90s windows (overlap 4s).
- **Pass A → Pass B**: Pass B never sees frames; it derives boundaries purely from the
  narration text, so timestamps come from the narration's `t` values.
- **Pass M → Stage 2**: Stage 2 refines each boundary against dense frames; the M-merged
  boundary is preserved as `end_time_stage1`, the refined value becomes `end_time`.

Layer → code:

| Layer | Function | Prompt section (`prompt_template_v3.md`) |
|---|---|---|
| Pass 0 | `annotate_v3.pass0` (L116) | `## PASS 0 PROMPT` |
| Pass 1 (coarse) | `annotate_v3.coarse_pass1` (L130) | `## COARSE PASS 1 PROMPT` |
| Pass A | `annotate_v3._passA` (L153) + `build_fineA` (L80); narration loop in `fine_from_coarse` (L272) | `## FINE PASS A PROMPT` |
| Pass B v4 | `rerun_passB_v4.passB_v4` (L94) + `_finalize` (L36) | `## FINE PASS B V4 PROMPT` |
| Pass M | `refine_fine.refine_M` (L135) + `_call_M` (L100); idle-preserve wrapper `rerun_passB_v4.refine_preserving_idle` (L118) | `## FINE REFINE M PROMPT` |
| Stage 2 | `annotate_v3.stage2_v3` (L348) | `## STAGE 2 PROMPT` |

---

## 2. Version evolution history

Each round: **Trigger → Diagnosis → Fix → Code location → Result.** Numbers verified
against the output archives unless marked `[需查证]`.

### 2.1 v1/v2 baseline + first bootstrap
- **Trigger:** need an initial two-stage annotator. First served Qwen3-VL-8B via vLLM.
- **Approach:** Stage 1 = whole-video segmentation + self-assessment; Stage 2 = per-boundary
  refinement with dense frames. Two granularities (coarse/fine) via a swappable rule block.
- **Fix/build:** fast frame extraction (single `ffmpeg` pass + PIL timestamp burn, ~29s/window
  vs ~190s frame-by-frame) — `annotate_v2._extract`. 448px / 640-frame budget established.
- **Code:** `annotate.py` (v1), `annotate_v2.py` (v2, two-stage), `prompt_template.md`,
  `prompt_template_v2.md`.
- **Result (v2 two-stage, 3 pilot videos, coarse/fine):** 3f83a362 = 16 / 41,
  e15723e5 = 5 / 6, 459e3ad5 = 5 / 8 (from the v2 phase-1 review index).

### 2.2 Degeneration and repetition_penalty
- **Trigger:** on long videos the 8B fine output degenerated into repeated lines — e.g.
  e15723e5 emitted `"picks up flashlight"` ×~50 / `"places flashlight"` ×~49 (≈154 entries,
  ~9 unique) and `3f83a362` Pass A looped `"holds the glass jar steady"` ×~48 `[需查证 exact
  counts]`. The output hit `max_tokens` mid-JSON → `JSONDecodeError`.
- **Diagnosis:** greedy (temp 0) long-output repetition collapse. Raising `max_tokens`
  does **not** help — it just lets the loop finish; the loop itself is the problem.
- **Fix:** `repetition_penalty=1.1` on the retry path breaks the loop. Later made
  **default-on** for the degeneration-prone Pass A / Pass B calls.
- **Code:** retry logic in `annotate_v3._passA` (L153, rep=1.1 both attempts),
  `_passB` (L169), and `coarse_pass1.call` (L132, rep only on attempt 2). Sampling toggled
  via `annotate_v3._set` (L110) → `annotate_v2._SAMPLING`.
- **Result:** loop broken; the failing segment produced a sane handful of segments.

### 2.3 Fine definition extension + two-pass (Pass A / Pass B)
- **Trigger:** fine was severely under-segmented (e.g. e15723e5 coarse 5 vs fine 6);
  single-pass fine merged distinct short actions.
- **Diagnosis:** one dense pass both narrates and segments, and the granularity rule was
  too coarse (only object change triggered a boundary).
- **Fix:** (a) fine definition extended — a boundary fires on **verb OR object change**
  ("picks up the bulb → unscrews the bulb"); (b) split into **Pass A** (dense narration,
  sees frames, no segmentation) → **Pass B** (text-only boundary derivation).
- **Code:** `## FINE PASS A PROMPT` / `## FINE PASS B PROMPT` in `prompt_template_v3.md`;
  original Pass B derivation `annotate_v3._passB` (L169).
- **Result:** fine density up sharply, but the full-window Pass A re-triggered the
  degeneration of 2.2 on long videos → motivated 2.4.

### 2.4 Per-coarse-segment chunking (the four-layer architecture)
- **Trigger:** two-pass fine still degenerated / truncated on long, windowed videos.
- **Diagnosis:** a single Pass A over a whole long video produces a huge output that
  degenerates; the model also lacked global structure to keep coarse consistent.
- **Fix:** top-down four layers — **Pass 0** global outline → **Pass 1** coarse guided by
  it → **Pass A/B run per coarse segment** (each call short → no degeneration) → Stage 2.
  Blind-cut coarse segments longer than the frame budget (128s) into 90s windows.
- **Code:** `annotate_v3.py` (whole module); `pass0` (L116), `coarse_pass1` (L130),
  `fine_from_coarse` (L272, per-segment Pass A + Pass B loop), `stage2_v3` (L348);
  blind-cut constants `BLIND_THRESH_S`/`BLIND_WIN_S`/`BLIND_OVERLAP_S` (L27–35).
  An inline rule-merge `merge_fine` (L236) collapsed same-verb+object and A-B-A-B
  oscillation runs (this is the ancestor of the standalone `R`).
- **Result (base four-layer, coarse / fine-raw):** 3f83a362 = 8 / 133, e15723e5 = 6 / 78,
  459e3ad5 = 3 / 32. Under-segmentation solved; new problem = over-narration noise
  (wipe/move oscillation) → motivated the refinement comparison.

### 2.5 Refinement comparison R / M / F / FR → M wins
- **Trigger:** raw fine over-segments on repetitive micro-motion (a table-wiping stretch
  produced ~40 one-decisecond segments).
- **Diagnosis:** Pass A narrates auxiliary/oscillating micro-motions that are semantically
  one action; a purely mechanical merge can't always tell noise from real alternation
  (dip→paint→dip→paint).
- **Fix:** four post-processors compared on the same raw:
  - **R** — rule merge (stemmed same verb+object; A-B-A-B oscillation) — `refine_fine.refine_R` (L74), `_merge_group` (L53).
  - **M** — model semantic merge, text-only, with contiguous `source_indices` + coverage-repair — `refine_fine.refine_M` (L135), `_call_M` (L100).
  - **F** — verb-category rule filter (approach/withdraw/static/…) absorbing non-action fillers — `refine_fine.refine_F` (L275), `classify_F` (L209), word list `F_WORDS` (L186).
  - **FR** — F then R — `refine_fine.refine_FR` (L292).
- **Result (base raw → M / F / FR):** 3f83a362 133→ M59 / F107 / FR60; e15723e5 78→ M28 / F68 / FR48;
  459e3ad5 32→ M22 / F23 / FR23. M was the most aggressive and cleaned the oscillation
  noise best; chosen as the fine merge. (Confirmed again on `_v4` — see 2.9.)

### 2.6 Hand-downgrade (`_v3` iteration)
- **Trigger:** single-hand videos hallucinated a second hand / mislabeled left vs right,
  and hand identity was driving spurious boundaries.
- **Diagnosis:** the `hand` field forced a per-frame left/right judgment that the model
  can't sustain (a single hand moves across frame; position ≠ identity), and hand-change
  was a boundary trigger.
- **Fix:** a single visible hand is just `"hand"`; left/right only when **both** are in
  frame together; **hand change is not a boundary** (verb/object only).
- **Code:** Pass A prompt `**Naming hands:**` paragraph in `## FINE PASS A PROMPT`; Pass B
  boundary rule ("a change of which hand … is NOT a boundary") in `## FINE PASS B …`.
  Driver `rerun_hand_v3.py` (`rerun_one` L15) re-ran Pass A onward reusing coarse.
- **Result (`_v3` raw / M):** 3f83a362 188 / 49, e15723e5 59 / 43, 459e3ad5 25 / 14. Hand
  hallucination removed; boundaries no longer fragment on hand switches. (During this run a
  Pass B `boundary_confidence:"high"` string crashed e15723e5 → fixed with the number-only
  prompt wording + `annotate_v3._coerce_conf` (L97).)

### 2.7 Time semantics + explicit idle (`_v4` iteration)
- **Trigger:** the first segment's label was stretched over the pre-engagement void — e.g.
  3f83a362 "picks up the white bowl" labeled 0–2.0s when the hand doesn't touch the bowl
  until t=2.0s.
- **Diagnosis:** Pass B's coverage rule made segment-0 start at 0 and absorb the idle gap;
  `t` semantics (start vs end of action) were unstated.
- **Fix:** (a) Pass A `t` = the moment the action **begins**; (b) Pass B v4 spans
  `[t_k, t_{k+1})` via per-segment `start_t`; (c) **explicit idle segments** (`type:"idle"`)
  for a leading gap >1.5s and mid pauses >4s; deterministic threshold enforcement drops the
  model's spurious sub-second idles.
- **Code:** `## FINE PASS B V4 PROMPT`; `rerun_passB_v4.passB_v4` (L94), `_finalize`
  (L36, idle-threshold enforcement), `_deterministic` fallback (L77); `IDLE_LEAD_S=1.5` (L18),
  mid-threshold 4s hardcoded in `_finalize`; idle-preserving refinement wrapper
  `refine_preserving_idle` (L118).
- **Result (`_v4` raw (idle) / M):** 3f83a362 287 (3 idle) / 51, e15723e5 59 (1 idle) / 42,
  459e3ad5 24 (0 idle) / 12. Leading label stretch fixed; idle segments become natural
  silent samples.

### 2.8 (folded into 2.7) — Stage-2 & assessment robustness
- `_coerce_conf` (annotate_v3 L97) maps stray `"high"/"low"` confidences to numbers so one
  bad field can't collapse a whole video; Stage-2 window narrowed to ±1.5s
  (`annotate_v3` L40 overrides `annotate_v2.S2_WINDOW_RADIUS_S`).

### 2.9 M-v4 stability (3× re-run)
- **Trigger:** before freezing, confirm the model merge is reproducible.
- **Method:** ran the M merge on 3f83a362's `_v4` raw three times, same config.
- **Result:** seg counts **[51, 51, 51]**, pairwise boundary Jaccard **1.000**, 100%
  boundaries stable. Deterministic because M runs at temperature 0 (greedy) and the
  coverage-repair in `_call_M` removes the only source of run-to-run drift. Decision:
  **M-v4 is the frozen fine config** (agreement ≫ 95% bar).

### 2.10 v5 directional re-check — attempted and REJECTED
- **Trigger:** directional verbs sometimes reversed (insert↔remove, screw↔unscrew).
- **Attempt:** Pass A directional rule (state-transition decides) + a Stage-2 direction
  check returning `confirmed/reversed/n-a`, auto-flipping reversed verbs via a word-pair map.
  Code quarantined in `experimental/rerun_direction_v5.py` (`stage2_direction` L92,
  `_flip_summary` L44, `FLIP_RAW` L22).
- **Result / why rejected:** on e15723e5, **confirmed 63 / reversed 16 / n-a 13** — but ~10
  of the 16 flips were the *same* repeated `inserts the battery into the flashlight`
  turned into `removes`, i.e. likely **over-flagging**; and the verb-only flip broke grammar
  (`removes … into`). Judged unreliable and **not merged into M-v4**. The template and
  `build_review` were reverted to pure M-v4 before the freeze; v5 kept only for reference.
  Directional correctness is an **open item** (to be re-tried on a larger model — see §5).

### 2.11 M-v4.1 — hand-transfer (hand-switch) capture
- **Trigger:** post-freeze review found a real miss — §2.6's hand-downgrade fix correctly
  suppressed hand-identity as a boundary trigger (killing hallucination), but as a side
  effect it also suppressed **genuine** hand-to-hand object transfers, which were silently
  absorbed into whichever action segment happened to span them.
- **Fix:** Pass A gets a narrow carve-out — a hand-transfer is captured ONLY on visible
  handoff evidence at the transition moment (object crossing from one hand's grip into the
  other's, or one hand releasing exactly as the other takes over), never on positional
  drift, emitting `"<verb> <object> (hand switch)"`. Pass B v4 treats a `(hand switch)`-
  marked narration entry as an always-boundary and carries the marker into the segment
  summary. Pass M (`refine_fine.refine_M`) is told never to merge a `(hand switch)`-marked
  segment as an auxiliary micro-motion.
- **Code:** `## FINE PASS A PROMPT` / `## FINE PASS B V4 PROMPT` / `## FINE REFINE M PROMPT`
  in `prompt_template_v3.md` (patch marker at file top, dated 2026-08-12).
- **Verification (bidirectional regression, 3 videos, before=pure M-v4 vs after=M-v4.1):**
  - `cd72f9f2a62b3317`: real transfer at 6.0–7.4s (`"hand transfers bulb to left hand (hand
    switch)"`) now cut out and Pass-M-protected; before, absorbed into one 6.0–24.0s segment.
  - `459e3ad53e531fca` (the hand-hallucination-sensitive video from §2.6): before/after both
    clean at 0–3.6s — no false hand-switch, no left/right hallucination reappeared.
  - `fced96b0f5b0dbf1`: 0 hand-switch activations either way; before/after fine counts do
    diverge (133 vs 123), but entirely from Pass A/B/M run-to-run variance on an unrelated,
    ambiguous coarse segment (127–158s, "cleaning up") — not caused by this patch (see new
    limitation in §5).
- **Result:** adopted. Real hand-transfers now segmented; no hallucination regression on the
  known-sensitive case.

### 2.12 M-v4.2 — no-person / unattended-machine idle rule
- **Trigger:** `fced96b0f5b0dbf1`'s microwave span (61.5–111.0s) produced ~48 near-identical
  Pass A entries (`"Hand continues pressing microwave buttons"`, one per second) while the
  microwave ran unattended and no hand was in frame — a fake-repetition artifact distinct
  from §2.2's degeneration pattern (phrasing barely varies, so it evades `UNIQUE_RATIO`,
  and timestamps are all genuine so it never triggers the retry path).
- **Fix:** Pass A prompt: *"If no person or hands are visible in the frames, output NO
  entries for that span — machines operating on their own (microwave running, kettle
  boiling) are not hand actions; such spans are idle."*
- **Code:** `## FINE PASS A PROMPT` in `prompt_template_v3.md` (patch marker dated
  2026-08-14).
- **Verification:** microwave span rerun — 48 fake entries → 7 real entries (puts pizza in /
  closes door / presses buttons / steps back / reaches for mitt / puts on mitt / opens
  door); hand-switch regression re-checked on `cd72f9f2a62b3317`, unaffected (identical
  6.0–7.4s hand-switch segment).
- **Result — adopted with a caveat, not iterated further:** the spam is eliminated (the
  actual harm). The ~36s unattended stretch (66.3–102.7s) is **not** typed `idle`, though —
  Pass B v4's mid-narration-gap idle rule (model-judgment only, no deterministic safety net)
  didn't fire; it became a single `"hand steps back from microwave"` action segment spanning
  the whole gap instead. Recorded as a known limitation (§5) rather than re-tuned, per the
  explicit decision not to repeatedly adjust the prompt chasing a second fix in one pass.

---

## 3. Current code map (`vlm/`)

| File | Role | Called by / status |
|---|---|---|
| `annotate.py` | v1 base helpers: paths, font, frame extraction primitives, `_find_font_file` | imported by `annotate_v2`; **historical (v1)**, kept for its shared constants |
| `annotate_v2.py` | v2 two-stage annotator + low-level primitives reused by M-v4: `_extract` (L213, fast frame extraction), `_call`/`_call_text`, `parse_*`, `merge_windows`, `_window_starts`, `validate` (L338), `_SAMPLING`, budget/resolution constants | imported by `annotate_v3` (M-v4 reuses these primitives); the **two-stage flow itself is historical** |
| `annotate_v3.py` | **M-v4 core.** Four-layer orchestration primitives: `pass0`, `coarse_pass1`, `fine_from_coarse`, `stage2_v3`, `_passA`, `build_*`, `merge_fine`, `phase_flags`, `_coerce_conf`, config constants (validation itself is `annotate_v2.validate`, called here) | **M-v4 active** |
| `prompt_template_v3.md` | all M-v4 prompts (Pass 0, Coarse Pass 1, Pass A, Pass B, **Pass B v4**, Refine M, Stage 2) + windowed note; carries the M-v4.1/M-v4.2 patches (§2.11, §2.12) | **M-v4.2 active** |
| `rerun_passB_v4.py` | **M-v4 active.** Pass B v4 (`passB_v4`, idle-explicit, `[t_k,t_{k+1})`), idle-threshold enforcement (`_finalize`), deterministic fallback, and the idle-preserving refinement wrapper (`refine_preserving_idle`) | **M-v4 active**; also the v4 batch driver (`main`) |
| `refine_fine.py` | the four fine post-processors `refine_R/M/F/FR`, `classify_F`+`F_WORDS`, `_call_M` (coverage-repair), `divergence` | **`refine_M` is M-v4 active**; R/F/FR retained for comparison/archive |
| `rerun_hand_v3.py` | driver that re-ran Pass A→onward with the hand-downgrade prompt (`rerun_one`) | historical driver; the prompt change it introduced is **active** |
| `build_review.py` | generates the static review page (video + dual timeline + per-segment conf/type/merge badges + version toggle) from a bundle | tooling (review), active |
| `serve_review.py` | serves the review directory over HTTP | tooling (review), active |
| `requirements.txt` | python deps | active |
| `experimental/rerun_direction_v5.py` | **isolated / rejected** v5 directional re-check + flip | quarantined, not in the chain |
| `prompt_template.md`, `prompt_template_v2.md` | v1/v2 prompts | historical (v2 template still loaded at import by `annotate_v2`) |

Production runner `final_annotate.py` (single entry point emitting
`annotations_{coarse,fine}.jsonl` with `end_time_stage1`) is **specified but not yet
written** as of this freeze.

---

## 4. Frozen configuration (value — source)

| Item | Value | Where set / why |
|---|---|---|
| Pass 0 fps | 2.0, auto-drop 1.0 / 0.5 / 0.25 to fit budget | `PASS0_LADDER` (annotate_v3 L26); Pass 0 only needs gross structure |
| Coarse fps | 2.0 | `COARSE_FPS` (annotate_v3 L24) |
| Pass A fps | 5.0 | `FINE_FPS` (annotate_v3 L25); dense enough for atomic actions |
| Stage 2 fps | 8.0 | hardcoded in `stage2_v3` `_ex(…,8.0,…)` (annotate_v3 L352) |
| Resolution | 448 px longest edge (~140 tok/frame) | `LONG_EDGE` (annotate_v2 L29); chosen to fit VRAM/context |
| Frame budget | 640 frames/window (server `--limit-mm-per-prompt image:660`) | `FRAME_BUDGET` (annotate_v2 L32) |
| temperature | 0.0 (attempt 1); 0.2 on retry | `_set` calls (annotate_v3 L110); greedy for reproducibility |
| repetition_penalty | **Pass A/B: 1.1 default (both attempts)**; Pass 0 / Coarse: only on retry; M merge: 1.1 both | `_passA` L153, `_passB` L169, `coarse_pass1.call` L132, `_call_M` L108 (§2.2) |
| Blind-cut threshold | coarse segment > 128s → 90s windows, overlap 4s | `BLIND_THRESH_S = 640/5` (annotate_v3 L35), `BLIND_WIN_S`/`BLIND_OVERLAP_S` (L27–28) |
| Stage 2 window | ±1.5s | `annotate_v3` L40 overrides `annotate_v2.S2_WINDOW_RADIUS_S` (was 3.0) (§2.7) |
| Stage 2 "acceptance" | refined `end_time` clamped to `(prev_end, next_end)`; on parse-fail keep the rough boundary | `stage2_v3` (annotate_v3 L358–361) — a clamp, **not** a distance threshold |
| Degeneration criterion | Pass A: unique-entry ratio < 0.5 → retry; Pass B: seg count > narration entries → retry | `UNIQUE_RATIO=0.5` (annotate_v3 L30, used L159); `_passB` L175 |
| Idle thresholds | leading ≥ 1.5s, mid ≥ 4.0s (else dropped/merged) | `IDLE_LEAD_S=1.5` (rerun_passB_v4 L18) + 4.0 in `_finalize` (§2.7) |
| Token caps | Pass 0 1536 / Coarse 6144 / Pass A,B 8192 | `MAX_TOK_*` (annotate_v3 L36–39; A/B raised to 8192 in §2.6/2.7) |
| Circuit breaker | pause after 10 consecutive same-type failures | **specified for `final_annotate.py` (not yet in code)** |

Server: Qwen3-VL-8B-Instruct via vLLM on GPU1, `max_pixels=150000`, `image:660`,
`--enforce-eager`, context capped at 98304 (VRAM-limited on a single 48GB card). `[需查证:
exact vLLM launch flags are not stored in this repo]`.

---

## 5. Known limitations & open items

- **Directional verbs still wrong.** insert/remove, screw/unscrew etc. can be reversed by
  Pass A. The v5 Stage-2 re-check (§2.10) over-flagged and produced broken grammar, so it
  was **rejected**. To retry on a larger model (e.g. 235B) and/or with preposition-aware
  flipping. This is the main correctness caveat for the benchmark.
- **Few-shot / example calibration line not completed.** The prompts support an
  `{EXAMPLE_BLOCK}`, but a calibrated human example was never wired in; all results are
  zero-shot.
- **Fine `video_assessment` is inherited, not measured.** Pass B v4 emits no per-segment
  assessment, so the fine record reuses the coarse/video-level `segmentability` `[需查证:
  confirm once final_annotate.py exists]`.
- **8B summary language quality.** Segment summaries are serviceable but occasionally
  awkward/generic; a larger model would improve wording (and possibly directional accuracy).
- **Idle detection is heuristic, and confirmed unreliable for unattended-machine spans.**
  Mid-video idle relies on a >4s narration gap being a true pause vs a sustained action; the
  model's judgment here is not independently validated. Concretely (§2.12): M-v4.2's
  no-person rule stops Pass A from spamming fake hand actions during a >30s unattended
  machine-running stretch, but Pass B v4's mid-gap idle insertion (model-judgment only, no
  deterministic safety net unlike the leading-idle case) did not fire on it — the whole gap
  was absorbed into the end_time of the preceding action segment instead. Downstream
  consumers should not assume every genuinely idle stretch carries `type:"idle"`.
- **Pass A/B/M are not reproducible run-to-run on ambiguous/cluttered footage**, even at
  temperature 0. Two independent full reruns of the same video/prompt (`fced96b0f5b0dbf1`,
  §2.11 verification) produced 45 vs 15 fine segments with largely uncorrelated content —
  including objects named in only one run — on its vaguest coarse segment ("cleaning up and
  finalizing the setup", 127–158s); the rest of the video also shifted by dozens of segments
  in the opposite direction. §2.9's stability result covers only the M-merge step in
  isolation on fixed input, not the full Pass A→B→M chain run fresh. Not caused by the
  M-v4.1/M-v4.2 patches (reproduced with zero hand-switch/idle-rule activation on that
  video) — a pre-existing property of the frozen chain, newly documented here.
- **Archived `*_v4` results are pre-Stage-2.** The stability test and the `fine_refined_M_v4/`
  archives are the M merge *before* Stage 2; the production runner adds Stage 2 and records
  the pre-Stage-2 boundary as `end_time_stage1`.
- **`final_annotate.py` production runner not yet written** (resume, progress, circuit
  breaker, schema assembly are specified but uncommitted).
