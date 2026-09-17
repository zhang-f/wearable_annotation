#!/usr/bin/env bash
set -uo pipefail
ROOT=/data/fan/projects/procedure_forecasting
LOG=$ROOT/runs/granularity_aware_final_v1/logs/sft_supervisor_v2.log
TRAIN=$ROOT/runs/granularity_aware_final_v1/scripts/train_granularity_aware.py
TORCHRUN=/data/conda_envs/procedure_vlm/bin/torchrun

log() { echo "[$(date -u +%FT%TZ)] $*" | tee -a "$LOG"; }

run_combo() {
  backbone="$1"
  mode="$2"
  variant="$3"
  skip_smoke="$4"
  outdir="$ROOT/runs/granularity_aware_final_v1/${backbone}_${mode}_${variant}"

  if [ "$skip_smoke" != "yes" ]; then
    log "SMOKE start ${backbone}/${mode}/${variant}"
    "$TORCHRUN" --standalone --nproc_per_node=8 "$TRAIN" \
      --backbone "$backbone" --mode "$mode" --variant "$variant" --smoke-only \
      >> "$ROOT/runs/granularity_aware_final_v1/${backbone}_${mode}_${variant}/logs/train.log" 2>&1
    rc=$?
    if [ $rc -ne 0 ]; then
      log "SMOKE FAILED ${backbone}/${mode}/${variant} rc=$rc -- skipping main run for this combo"
      return 1
    fi
    log "SMOKE OK ${backbone}/${mode}/${variant}"
  else
    log "SMOKE skipped (already validated) ${backbone}/${mode}/${variant}"
  fi

  log "MAIN start ${backbone}/${mode}/${variant} (1254 steps)"
  "$TORCHRUN" --standalone --nproc_per_node=8 "$TRAIN" \
    --backbone "$backbone" --mode "$mode" --variant "$variant" --steps 1254 \
    >> "$ROOT/runs/granularity_aware_final_v1/${backbone}_${mode}_${variant}/logs/train.log" 2>&1
  rc=$?
  if [ $rc -ne 0 ]; then
    log "MAIN FAILED ${backbone}/${mode}/${variant} rc=$rc"
    return 1
  fi
  if [ -f "$outdir/checkpoints/final/checkpoint_meta.json" ]; then
    log "MAIN OK ${backbone}/${mode}/${variant} -- final checkpoint present"
  else
    log "MAIN exited 0 but no final checkpoint found for ${backbone}/${mode}/${variant} -- treat as incomplete"
    return 1
  fi
  return 0
}

log "=== sft_supervisor_v2 starting ==="

run_combo qwen full no_none yes
log "combo 1 (qwen/full/no_none) exit_status=$?"

run_combo qwen full weighted_none no
log "combo 2 (qwen/full/weighted_none) exit_status=$?"

run_combo gemma full no_none no
log "combo 3 (gemma/full/no_none) exit_status=$?"

run_combo gemma full weighted_none no
log "combo 4 (gemma/full/weighted_none) exit_status=$?"

log "=== sft_supervisor_v2 finished all combos ==="
