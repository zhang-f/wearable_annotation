#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1
# Do not touch the active Qwen weighted-none workers. Once they finish, stop
# the obsolete supervisor before it can submit Gemma, then start new order.
while pgrep -f 'train_granularity_aware.py --backbone qwen --mode lora --variant weighted_none --steps 1254' >/dev/null; do sleep 15; done
pkill -TERM -f 'bash runs/granularity_aware_final_v1/scripts/launch_matrix.sh' || true
# If old supervisor raced and began Gemma loading, stop only its just-started job.
pkill -TERM -f 'train_granularity_aware.py --backbone gemma' || true
sleep 20
setsid bash "$ROOT/scripts/run_reordered_matrix.sh" >> "$ROOT/logs/reordered_supervisor.log" 2>&1 < /dev/null &
