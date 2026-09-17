# Granularity-aware when/what-to-speak training pipeline (code only)

This directory holds the **code** for the granularity-aware SFT project
(joint COARSE/FINE decision+content training, `L = Ld + Lc + 0.5*Lg`).
Data manifests, trained checkpoints, evaluation predictions, and a much more
detailed `README.md` covering directory layout, known issues (esp. a Gemma3
LoRA memory bug and its fix), and current results live in the private HF
backup repo instead — GitHub can't hold the checkpoints/data (~40GB+).

Ask whoever gave you access to this code for a link to that HF repo
(`INERTFIN/granularity-aware-final-v1-backup`, private).

## Files

- `final_common.py` — shared model/data loading, prompt construction, the
  PTS-floor frame decoder.
- `scripts/build_dense_manifest.py`, `audit_dense_data.py`,
  `build_train_index.py` — build and validate the training data manifests.
- `scripts/train_granularity_aware.py` — the training loop.
- `scripts/evaluate_egoproactive_new.py`, `score_new_egoproactive.py` — run
  and score trained checkpoints on the official EgoProactive benchmark.
- `scripts/probe_decision_calibration.py` — lighter in-domain decision-
  calibration diagnostic (no full EgoProactive run needed).
- `scripts/diag_gemma_memory.py` — the memory-snapshot diagnostic used to
  root-cause the Gemma LoRA OOM (see the HF repo's README §6 for the story).
- `scripts/sft_supervisor_v2.sh` / `sft_supervisor_v3.sh` — sequential
  multi-job training supervisors (chain smoke-test -> full run across
  backbone/mode/variant combinations without manual intervention).
- `granularity_aware_final_status_2026-09-14.md` — a mid-project status
  snapshot; superseded by the HF repo's README, kept here for history.

```bash
conda activate procedure_vlm
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
torchrun --standalone --nproc_per_node=8 scripts/train_granularity_aware.py \
  --backbone {qwen,gemma} --mode {lora,full} --variant {no_none,weighted_none} \
  --steps 1254 [--smoke-only]
```
