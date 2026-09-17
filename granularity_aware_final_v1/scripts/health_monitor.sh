#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1
LOG="$ROOT/logs/health_monitor.log"
while true; do
 now=$(date -u +%FT%TZ); active=$(pgrep -fc 'train_granularity_aware|evaluate_egoproactive_new' || true); done_count=$(find "$ROOT" -path '*/checkpoints/final/checkpoint_meta.json' | wc -l); util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | tr '\n' ','); echo "$now active=$active completed_final=$done_count gpu_util=$util" >> "$LOG"
 if [[ "$done_count" -lt 8 && "$active" -eq 0 ]]; then echo "$now recovery restart" >> "$LOG"; setsid bash "$ROOT/scripts/run_reordered_matrix.sh" >> "$ROOT/logs/matrix_supervisor.log" 2>&1 < /dev/null &; fi
 sleep 900
done
