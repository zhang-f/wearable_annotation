# Granularity-Aware Training: Current Status and Audit

Generated: 2026-09-14 UTC

## Scope requested

The requested final experiment matrix is:

1. Qwen3-VL-8B LoRA, no-none
2. Qwen3-VL-8B LoRA, weighted-none
3. Gemma3-12B LoRA, no-none
4. Gemma3-12B LoRA, weighted-none
5. Qwen3-VL-8B Full-SFT, no-none
6. Qwen3-VL-8B Full-SFT, weighted-none
7. Gemma3-12B Full-SFT, no-none
8. Gemma3-12B Full-SFT, weighted-none

Each new final checkpoint is supposed to be evaluated on EgoProactive before the next training job. Existing zero-shot, old LoRA, and old EgoProactive results are preserved and are not being rerun.

## New dense-grid data reconstruction

Created a separate run root:

`runs/granularity_aware_final_v1/`

The new source-of-truth manifests are:

- `data/dense_train.jsonl`
- `data/dense_test.jsonl`
- `data/train_pool_offsets.npz`
- `reports/dense_manifest_audit.json`
- `reports/dense_data_sampler_audit.{json,md}`

### Data semantics implemented

- Queries are constructed on a complete 0.5-second grid.
- Each query carries one canonical 16-frame recent prefix from approximately the preceding 8 seconds.
- Frame timestamps are mapped using decoded PyAV presentation timestamps with a floor rule: each selected frame is at or before the desired timestamp and query time.
- COARSE and FINE use the same `video_id`, query time, frame indices, and frame timestamps.
- COARSE and FINE labels are independently assigned before deriving pair state.
- Coarse `none` is represented as a real positive coarse event (`SPEAK` plus content), never as a negative/SILENT event.
- `none` is masked for no-none, given a separate group weight of 0.25 in weighted-none, and excluded from `L_gran` in both variants.
- The dense construction has no +/-3-second guard band and no 4-second negative deletion rule.

### Manifest size

| Split | Grid queries | Videos |
|---|---:|---:|
| Train | 625,120 | 648 |
| Test | 86,873 | 103 |

### Train raw label counts

| Group | Count |
|---|---:|
| COARSE background | 614,799 |
| COARSE strong | 10,007 |
| COARSE weak | 303 |
| COARSE none | 11 |
| FINE SPEAK | 90,641 |
| FINE SILENT | 534,479 |

### Derived train pair-state counts

| State | Count |
|---|---:|
| BOTH_SILENT | 524,274 |
| FINE_ONLY | 90,525 |
| COARSE_ONLY | 10,194 |
| BOTH_SPEAK | 116 |
| NONE_FINE_SILENT | 11 |

### Sampler audit

The simulated DDP role schedule produces:

- COARSE base decision distribution: 50% SPEAK, 50% SILENT.
- FINE decision distribution: 50% SPEAK, 50% SILENT.
- `L_gran` direction distribution: 50% FINE_ONLY, 50% COARSE_ONLY.
- Weighted-none group formula: `(base + 0.25 * none) / 1.25`; effective group-level none contribution is 20% of the combined coarse group objective.

The new-manifest assertions passed in `reports/dense_data_sampler_audit.md`, including no future manifest frame timestamps, no relabeling of `none` as SILENT, no `none` in the base negative pool, and no `none` in `L_gran`.

## New implementation created

Relevant new files include:

- `runs/granularity_aware_final_v1/scripts/build_dense_manifest.py`
- `runs/granularity_aware_final_v1/scripts/audit_dense_data.py`
- `runs/granularity_aware_final_v1/scripts/build_train_index.py`
- `runs/granularity_aware_final_v1/final_common.py`
- `runs/granularity_aware_final_v1/scripts/train_granularity_aware.py`
- `runs/granularity_aware_final_v1/scripts/launch_matrix.sh`
- `runs/granularity_aware_final_v1/scripts/run_reordered_matrix.sh`
- `runs/granularity_aware_final_v1/scripts/evaluate_egoproactive_new.py`

The training objective computes teacher-forced mean-token log-probability scores for the existing text strings `<SPEAK>` and `<SILENT>`, without adding tokenizer tokens. It uses:

`L = Ld + Lc + 0.5 * Lg`

where `Ld` is decision loss, `Lc` is content loss only on SPEAK targets, and `Lg` is directional ranking loss on valid FINE_ONLY/COARSE_ONLY pairs.

## Training completed

### Qwen3-VL-8B LoRA no-none

- Status: completed.
- Optimizer steps: 1,254.
- Trainable LoRA parameters: 43,646,976.
- Wall time: 4.886 hours.
- Final loss: 2.938.
- Mean final-50 loss: 2.280.
- Final checkpoint: `runs/granularity_aware_final_v1/qwen_lora_no_none/checkpoints/final/`.

### Qwen3-VL-8B LoRA weighted-none

- Status: completed.
- Optimizer steps: 1,254.
- Trainable LoRA parameters: 43,646,976.
- Wall time: 8.636 hours.
- Final loss: 2.590.
- Mean final-50 loss: 2.068.
- Final checkpoint: `runs/granularity_aware_final_v1/qwen_lora_weighted_none/checkpoints/final/`.

The smoke training phase ran 50 optimizer steps for each run. It showed finite losses/gradients and saved a readable adapter checkpoint before continuation.

## Current active work

At the time of this report, Qwen3-VL-8B Full-SFT no-none has been submitted after the requested order change. It starts from the original Qwen base model, not a LoRA adapter. The intended order after the current job is:

1. Qwen Full-SFT weighted-none
2. Gemma LoRA no-none
3. Gemma LoRA weighted-none
4. Gemma Full-SFT no-none
5. Gemma Full-SFT weighted-none

Gemma new training has not started yet.

## EgoProactive status

No EgoProactive result exists yet for either new granularity-aware Qwen LoRA adapter.

This is incomplete work. Existing EgoProactive outputs under `runs/egoproactive_eval_v1/` belong to prior baseline Qwen/Gemma configurations and must not be interpreted as results for the new dense-grid objectives.

A separate evaluator was started at:

`runs/granularity_aware_final_v1/scripts/evaluate_egoproactive_new.py`

However, it requires final cleanup before use as the automatic post-checkpoint evaluator. It must run only the new adapter's finetuned path, reuse the existing official EgoProactive manifest/protocol, write results under the new run root, and then invoke the existing scorer. It must be integrated into the active ordered supervisor so every future final checkpoint is evaluated before the following training job starts.

## Failures and downtime

### 1. Initial Qwen LoRA no-none main-run failure

The first main run hit a 10-minute NCCL watchdog timeout during multi-rank processing. The likely trigger was an exceptionally slow/corrupt video decode preventing one rank from reaching the same collective. A later retry completed.

A bounded decode retry mechanism was added to the training path, with a 120-second per-video decode limit and up to eight replacement candidates. This changed the retry behavior but did not alter manifest labels or raw videos.

### 2. Qwen weighted-none -> Full-SFT handoff failure

Qwen weighted-none completed at:

`2026-09-14 11:44:55 UTC`

The handoff supervisor then failed before submitting Qwen Full-SFT because `run_reordered_matrix.sh` used Bash local variables in a declaration that expanded unset variables under `set -u`:

`local b=$1 m=$2 v=$3 out="$ROOT/${b}_${m}_${v}"`

The corrected script assigns the arguments before constructing `out`.

Qwen Full-SFT was started at approximately:

`2026-09-14 19:58 UTC`

This caused approximately **8 hours 13 minutes** of unintended idle time between weighted-none completion and the Full-SFT restart.

### 3. Health monitoring did not remain effective

A requested 15-minute monitor was attempted, but it did not persist reliably and therefore did not recover the failed handoff. This requirement is currently not satisfied robustly. A future supervisor should use a single durable process with explicit PID/state files, checkpoint-aware resume, periodic progress timestamps, and post-checkpoint evaluation gating.

## Important limitations and unfinished deliverables

The following are not complete:

1. New internal validation metrics for either LoRA adapter.
2. New EgoProactive metrics for either LoRA adapter.
3. Semantic judge outputs for new checkpoints.
4. Gemma LoRA experiments.
5. Any Full-SFT result.
6. Final comparison table and scientific conclusions.
7. A robust, verified 15-minute monitoring and automatic recovery mechanism.
8. Guaranteed post-checkpoint EgoProactive evaluation before each subsequent training run.

No new scientific performance conclusion should be drawn from losses alone.

## Previous baseline results retained

Existing runs remain untouched:

- `runs/mg_sft_v2/` for the prior Qwen baseline.
- `runs/mg_sft_gemma3_12b/` for the prior Gemma baseline.
- `runs/egoproactive_eval_v1/` for prior EgoProactive evaluations.

## Recommended immediate recovery plan

1. Verify and finish a clean finetuned-only EgoProactive evaluation script for `qwen_lora_no_none/checkpoints/final`.
2. Run and score it on all eight GPUs only after the currently active Full-SFT job reaches a safe completion point or is deliberately scheduled between jobs.
3. Build a single checkpoint-aware supervisor that atomically records job state, runs post-checkpoint evaluation, and only then launches the next experiment.
4. Verify the 15-minute monitor by deliberately checking its heartbeat file before relying on it.
5. Continue Qwen Full-SFT, then use the requested Qwen-before-Gemma order.

## Reproducibility: exact paths, environments, and workflow

### Project and environment

| Item | Absolute path / value |
|---|---|
| Project root | `/data/fan/projects/procedure_forecasting` |
| New experiment root | `/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1` |
| Python environment | Conda environment `procedure_vlm` |
| Python executable used by training | `/data/conda_envs/procedure_vlm/bin/python3.11` |
| Distributed launcher | `/data/conda_envs/procedure_vlm/bin/torchrun` |
| Hardware | 8 × NVIDIA H200 GPUs |
| Training precision | BF16 |
| DDP world size | 8 |
| Per-rank pair batch | 1 canonical pair per microstep |
| Gradient accumulation | 2 microsteps per optimizer step |

The active shell should be initialized with the existing `procedure_vlm` Conda environment. No CUDA, driver, dataset, or base-weight files were modified by this work.

### Base-model paths

| Backbone | Base checkpoint |
|---|---|
| Qwen3-VL-8B-Instruct | `/data/fan/models/Qwen3-VL-8B-Instruct` |
| Gemma 3 12B IT | `/data/fan/models/Gemma-3-12B-IT` |
| Qwen235B annotation/judge backend model | Existing local model and vLLM environment configured by `epic_hierarchy_qwen235b_v1`; it is not used in the currently completed new LoRA training steps. |

### Data paths

| Data / annotation source | Absolute path |
|---|---|
| Assembly101 dataset root | `/data/fan/datasets/assembly101` |
| Assembly101 official coarse labels | `/data/fan/datasets/assembly101/annotations/coarse-annotations/coarse_labels/` |
| Assembly101 official fine annotations | `/data/fan/datasets/assembly101/annotations/fine-grained-annotations/` |
| Assembly train recordings split | `/data/fan/projects/procedure_forecasting/runs/mg_sft_v1/data/train_recordings.txt` |
| Assembly test recordings split | `/data/fan/projects/procedure_forecasting/runs/mg_sft_v1/data/test_recordings.txt` |
| Assembly selected-HMC video probe metadata | `/data/fan/projects/procedure_forecasting/runs/mg_sft_v1/data/video_probe.json` |
| EPIC hierarchy V1 per-video annotations | `/data/fan/projects/procedure_forecasting/epic_hierarchy_qwen235b_v1/final_v1/videos/` |
| Existing split/video-path source for EPIC and Assembly | `/data/fan/projects/procedure_forecasting/runs/mg_sft_v2/data/train.jsonl` and `/data/fan/projects/procedure_forecasting/runs/mg_sft_v2/data/val.jsonl` |
| Existing EgoProactive benchmark root | `/data/fan/projects/procedure_forecasting/runs/egoproactive_eval_v1/data/wearable-ai/egoproactive/` |
| EgoProactive validation manifest | `/data/fan/projects/procedure_forecasting/runs/egoproactive_eval_v1/data/wearable-ai/egoproactive/wearable_ai_2026_egoproactive_val_700.jsonl` |
| EgoProactive validation videos | `/data/fan/projects/procedure_forecasting/runs/egoproactive_eval_v1/data/wearable-ai/egoproactive/val/` |

EPIC raw videos are never copied or altered. Their resolved local video paths are stored per query in the dense manifests below.

### Dense-manifest construction workflow

Run from the project root:

```bash
conda activate procedure_vlm
python runs/granularity_aware_final_v1/scripts/build_dense_manifest.py
python runs/granularity_aware_final_v1/scripts/audit_dense_data.py
python runs/granularity_aware_final_v1/scripts/build_train_index.py
```

`build_dense_manifest.py` performs the following deterministic processing:

1. Loads the existing recording/video split definitions before query construction.
2. Loads Assembly101 official coarse and fine temporal annotations and EPIC V1 hierarchy/fine annotations.
3. Constructs 0.5-second query grids over each selected local egocentric video.
4. Caches only decoded video PTS arrays in `data/frame_pts/{dataset}/`; no RGB frames are saved.
5. Produces a 16-frame, 8-second canonical prefix per grid point, using an actual-PTS floor lookup.
6. Independently assigns COARSE and FINE targets, decisions, loss masks, and then derives pair state.
7. Atomically writes `data/dense_train.jsonl` and `data/dense_test.jsonl`.

The complete dense-manifest records contain at least:

```text
pair_id, dataset, video_id, recording_id, split, video_path,
query_time, frame_indices, frame_timestamps, goal, current_subtask,
coarse_predictability, coarse_decision, coarse_target,
fine_decision, fine_target,
use_coarse_decision_loss_base, use_coarse_content_loss_base,
use_coarse_none_loss, use_fine_decision_loss, use_fine_content_loss,
pair_state, pair_valid_for_Lgran, coarse_group, fine_group
```

### Training implementation and commands

| File | Purpose |
|---|---|
| `final_common.py` | model/processor loading, prompt construction, canonical prefix decoding, LoRA/full trainability configuration |
| `scripts/train_granularity_aware.py` | DDP pair-aware loss and training loop |
| `data/train_pool_offsets.npz` | compact dynamic-sampler offsets into the full dense train manifest |
| `qwen_lora_no_none/config.json` | recorded Qwen no-none training configuration |
| `qwen_lora_weighted_none/config.json` | recorded Qwen weighted-none training configuration |

A single smoke run is reproducible with:

```bash
torchrun --standalone --nproc_per_node=8 \
  runs/granularity_aware_final_v1/scripts/train_granularity_aware.py \
  --backbone qwen --mode lora --variant no_none --smoke-only
```

A 1,254-step main run is reproducible with:

```bash
torchrun --standalone --nproc_per_node=8 \
  runs/granularity_aware_final_v1/scripts/train_granularity_aware.py \
  --backbone qwen --mode lora --variant no_none --steps 1254
```

Valid command arguments are:

```text
--backbone {qwen,gemma}
--mode {lora,full}
--variant {no_none,weighted_none}
--steps 1254
--grad-accum 2
```

For LoRA, the implementation targets language-model attention and MLP linear modules whose terminal names are:

```text
q_proj, k_proj, v_proj, o_proj, up_proj, down_proj, gate_proj
```

LoRA configuration is `r=16`, `alpha=32`, `dropout=0.05`, learning rate `5e-5`. Full-SFT starts from the original base checkpoint, freezes visual encoder layers while retaining named merger/projector layers when present, and uses learning rate `1e-5`.

### Prompt and target protocol

COARSE user content:

```text
Goal: {goal}
Granularity: COARSE

Should the assistant predict the next high-level subtask now?
```

FINE user content:

```text
Goal: {goal}
Current subtask: {current_subtask_at_query_time}
Granularity: FINE

Should the assistant predict the next fine-grained action now?
```

Targets are literal existing text strings, without tokenizer additions:

```text
<SPEAK> {target content}
<SILENT>
```

### Loss protocol

The decision score is the teacher-forced mean token log probability difference:

```text
s_g = mean_logP("<SPEAK>" | prefix, g)
    - mean_logP("<SILENT>" | prefix, g)
```

The total objective is:

```text
L = Ld + Lc + 0.5 * Lg
```

where:

- `Ld = 0.5 * (Ld_C + Ld_F)`;
- `Lc = 0.5 * (Lc_C + Lc_F)` and only applies to SPEAK content tokens, excluding the decision marker;
- `Lg` is the symmetric softplus ranking loss on valid FINE_ONLY and COARSE_ONLY pairs;
- coarse `none` is excluded from `L_gran`;
- no-none masks coarse none loss;
- weighted-none combines each coarse base group with its none group as `(base + 0.25 * none) / 1.25`.

### Exact output paths for completed Qwen LoRA adapters

| Variant | Final adapter |
|---|---|
| Qwen LoRA no-none | `/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1/qwen_lora_no_none/checkpoints/final/` |
| Qwen LoRA weighted-none | `/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1/qwen_lora_weighted_none/checkpoints/final/` |

Each adapter directory contains `adapter_model.safetensors`, `adapter_config.json`, tokenizer/processor files, and `checkpoint_meta.json`.

### Logs and state inspection

| Purpose | Path |
|---|---|
| Qwen LoRA no-none loss | `runs/granularity_aware_final_v1/qwen_lora_no_none/logs/loss.csv` |
| Qwen LoRA weighted-none loss | `runs/granularity_aware_final_v1/qwen_lora_weighted_none/logs/loss.csv` |
| Matrix supervisor log | `runs/granularity_aware_final_v1/logs/matrix_supervisor.log` |
| Reordered-supervisor log | `runs/granularity_aware_final_v1/logs/reordered_supervisor.log` |
| Dense data audit | `runs/granularity_aware_final_v1/reports/dense_data_sampler_audit.md` |
| Dense manifest audit | `runs/granularity_aware_final_v1/reports/dense_manifest_audit.json` |

### Reproducing the original old baselines

Old configurations and outputs are intentionally separate:

| Baseline | Root |
|---|---|
| Original Qwen MG-SFT | `/data/fan/projects/procedure_forecasting/runs/mg_sft_v2/` |
| Original Gemma MG-SFT | `/data/fan/projects/procedure_forecasting/runs/mg_sft_gemma3_12b/` |
| Existing EgoProactive baseline evaluation | `/data/fan/projects/procedure_forecasting/runs/egoproactive_eval_v1/` |

Do not overwrite these folders when reproducing the new experiment.

## Historical experiments and artifacts from earlier days

This section records the earlier work that preceded the current corrected dense-grid experiment. These results use earlier task definitions and must not be combined with the current final run without checking the protocol in each linked report.

### Chronology

| Approximate date | Work | Primary root |
|---|---|---|
| 2026-09-10 | Assembly101-only multi-granularity SFT pilot | `/data/fan/projects/procedure_forecasting/runs/mg_sft_v1/` |
| 2026-09-11 | Joint Assembly101 + EPIC initial Qwen MG-SFT | `/data/fan/projects/procedure_forecasting/runs/mg_sft_v2/` |
| 2026-09-11–12 | Gemma 3 12B replication of the initial MG-SFT | `/data/fan/projects/procedure_forecasting/runs/mg_sft_gemma3_12b/` |
| 2026-09-12 | Official EgoProactive evaluation of the old baselines | `/data/fan/projects/procedure_forecasting/runs/egoproactive_eval_v1/` |
| Earlier in project | EPIC V1 hierarchical annotation generation and review | `/data/fan/projects/procedure_forecasting/epic_hierarchy_qwen235b_v1/` |
| 2026-09-13 onward | Corrected dense-grid granularity-aware run | `/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1/` |

### EPIC-KITCHENS hierarchy annotation work

The EPIC hierarchy generation project is rooted at:

`/data/fan/projects/procedure_forecasting/epic_hierarchy_qwen235b_v1/`

It preserves official fine annotations and writes generated hierarchy above them. Important artifacts:

| Artifact | Path |
|---|---|
| Normalized official fine actions | `epic_hierarchy_qwen235b_v1/00_normalized_fine/` |
| Goal annotations | `epic_hierarchy_qwen235b_v1/01_goal_raw/` |
| Coarse boundary/label intermediates | `epic_hierarchy_qwen235b_v1/02_coarse_raw/` |
| Canonicalization intermediates | `epic_hierarchy_qwen235b_v1/03_coarse_canonical/` |
| V0 hierarchy output | `epic_hierarchy_qwen235b_v1/final_v0/` |
| V1 hierarchy per-video output | `epic_hierarchy_qwen235b_v1/final_v1/videos/` |
| V1 global JSONL | `epic_hierarchy_qwen235b_v1/final_v1/epic_hierarchy_v1.jsonl` |
| V1 coarse table | `epic_hierarchy_qwen235b_v1/final_v1/coarse_table_v1.jsonl` |
| Review website | `epic_hierarchy_qwen235b_v1/review_web/` |
| V1 manual review export | `epic_hierarchy_qwen235b_v1/review_v1/random_30.md` |
| Fine annotation audit | `epic_hierarchy_qwen235b_v1/reports/fine_annotation_audit.md` |
| Final annotation report | `epic_hierarchy_qwen235b_v1/reports/final_annotation_report.md` |
| Fast V0 report | `epic_hierarchy_qwen235b_v1/reports/fast_v0_report.md` |
| V1 fast report | `epic_hierarchy_qwen235b_v1/reports/v1_fast_report.md` |
| Backend report | `epic_hierarchy_qwen235b_v1/reports/inference_backend_report.md` |

The annotation backend was the validated local vLLM 0.11.0 deployment in `.venv_vllm11_full`, using the local Qwen 235B-class instruction model with TP=8, BF16, 32k context, eager mode. This is separate from `procedure_vlm` and its PyTorch installation.

### Assembly101-only pilot: `mg_sft_v1`

Root:

`/data/fan/projects/procedure_forecasting/runs/mg_sft_v1/`

- Base model: `/data/fan/models/Qwen3-VL-8B-Instruct`.
- Dataset: Assembly101 HMC egocentric video only.
- Split: 320 recording-level train recordings and 20 held-out recordings.
- Training data: 14,518 samples, balanced 7,259 coarse / 7,259 fine.
- Test data: 952 queries, 476 coarse / 476 fine.
- Training: LoRA, 908 optimizer steps, one epoch, BF16, 8 H200 GPUs, 0.420 hours, final loss 0.906.
- Evaluation used deterministic label normalization/vocabulary membership rather than the later Qwen235B semantic judge.

Recorded pilot metrics:

| Model | Coarse accuracy | Fine accuracy | GCR-Coarse | GCR-Fine |
|---|---:|---:|---:|---:|
| Zero-shot Qwen | 0.000 | 0.000 | 0.000 | 0.002 |
| Assembly-only MG-SFT | 0.107 | 0.069 | 1.000 | 0.998 |

Key reports and configurations:

- `runs/mg_sft_v1/reports/overnight_summary.md`
- `runs/mg_sft_v1/reports/metrics.json`
- `runs/mg_sft_v1/reports/data_audit.md`
- `runs/mg_sft_v1/reports/training_results.json`
- `runs/mg_sft_v1/config/train.yaml`
- `runs/mg_sft_v1/config/eval.yaml`
- `runs/mg_sft_v1/data/train.jsonl`
- `runs/mg_sft_v1/data/val.jsonl`

### Initial joint Qwen MG-SFT: `mg_sft_v2`

Root:

`/data/fan/projects/procedure_forecasting/runs/mg_sft_v2/`

- Base model: `/data/fan/models/Qwen3-VL-8B-Instruct`.
- Training data: Assembly101 plus EPIC V1 hierarchy data.
- Initial task protocol: coarse strong/weak were SPEAK; old treatment and sampling of other states differ from the corrected dense-grid run and should not be treated as equivalent.
- Training: LoRA, 1,254 optimizer steps, 20,055 samples, BF16, 8 H200 GPUs, 1.871 hours, final train loss 0.613.
- Internal test set: 2,272 examples.

Old internal semantic-judge metrics:

| Qwen model | Coarse semantic accuracy | Fine semantic accuracy | Coarse GCR | Fine GCR | Speak coverage |
|---|---:|---:|---:|---:|---:|
| Zero-shot | N/A at SPEAK (coverage 0) | 0.305 | N/A | 0.704 | 0.000 |
| Old MG-SFT | 0.720 | 0.423 | 1.000 | 0.949 | 1.000 |

The old model always emitted SPEAK on this internal protocol, so its apparent timing F1 of 1.0 is not a meaningful abstention result; no `none`/SILENT test examples were available in that protocol. This limitation motivated the corrected dense-grid reconstruction.

Key files:

- `runs/mg_sft_v2/reports/main_results.md`
- `runs/mg_sft_v2/reports/main_results.json`
- `runs/mg_sft_v2/reports/step_0400_eval.md`
- `runs/mg_sft_v2/reports/training_results.json`
- `runs/mg_sft_v2/data/train.jsonl`
- `runs/mg_sft_v2/data/val.jsonl`
- `runs/mg_sft_v2/common.py`
- `runs/mg_sft_v2/train.py`
- `runs/mg_sft_v2/evaluate.py`
- `runs/mg_sft_v2/judge.py`

### Initial Gemma 3 12B MG-SFT: `mg_sft_gemma3_12b`

Root:

`/data/fan/projects/procedure_forecasting/runs/mg_sft_gemma3_12b/`

- Base model: `/data/fan/models/Gemma-3-12B-IT`.
- Training data/protocol: same old initial joint MG-SFT setup as the prior Qwen comparison, not the corrected dense grid.
- Training: LoRA, 1,254 optimizer steps, 20,055 samples, BF16, 8 H200 GPUs, 1.783 hours, final loss 0.763.
- Parameters: total 12,252,795,504; LoRA-trainable 65,470,464.

Old internal semantic-judge metrics:

| Gemma model | Coarse semantic accuracy | Fine semantic accuracy | Coarse GCR | Fine GCR | Speak coverage |
|---|---:|---:|---:|---:|---:|
| Zero-shot | N/A at SPEAK (coverage 0) | 0.470 | N/A | 0.987 | 0.000 |
| Old MG-SFT | 0.696 | 0.338 | 1.000 | 0.945 | 1.000 |

Key files:

- `runs/mg_sft_gemma3_12b/reports/main_results.md`
- `runs/mg_sft_gemma3_12b/reports/main_results.json`
- `runs/mg_sft_gemma3_12b/reports/model_audit.md`
- `runs/mg_sft_gemma3_12b/reports/epoch_adequacy.md`
- `runs/mg_sft_gemma3_12b/reports/training_results.json`
- `runs/mg_sft_gemma3_12b/config/train.yaml`
- `runs/mg_sft_gemma3_12b/common.py`
- `runs/mg_sft_gemma3_12b/train.py`
- `runs/mg_sft_gemma3_12b/evaluate.py`
- `runs/mg_sft_gemma3_12b/judge.py`

### Previous official EgoProactive benchmark evaluation

Root:

`/data/fan/projects/procedure_forecasting/runs/egoproactive_eval_v1/`

- Dataset: `facebook/wearable-ai`, configuration `egoproactive`, validation split.
- Sessions: 700.
- Decision chunks: 9,935.
- Evaluator: `runs/egoproactive_eval_v1/evaluate_models.py`.
- Scorer: `runs/egoproactive_eval_v1/score_results.py`.
- Evaluation report: `runs/egoproactive_eval_v1/reports/main_results.md` and `.json`.

Recorded metrics:

| Model | Macro F1 | Interrupt F1 | Silent F1 | Interrupt coverage |
|---|---:|---:|---:|---:|
| Old Qwen zero-shot | 0.3479 | 0.6944 | 0.0013 | 0.9928 |
| Old Qwen MG-SFT | 0.3896 | 0.5867 | 0.1926 | 0.7841 |
| Old Gemma zero-shot | 0.4047 | 0.1710 | 0.6384 | 0.0687 |
| Old Gemma MG-SFT | 0.4471 | 0.2316 | 0.6627 | 0.0715 |

These are old-model results only. They are not results for `granularity_aware_final_v1` adapters.
