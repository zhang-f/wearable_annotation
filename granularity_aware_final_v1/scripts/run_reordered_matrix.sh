#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1
cd /data/fan/projects/procedure_forecasting
run() {
 local b m v out
 b="$1"; m="$2"; v="$3"; out="$ROOT/${b}_${m}_${v}"
 mkdir -p "$out/logs"
 torchrun --standalone --nproc_per_node=8 "$ROOT/scripts/train_granularity_aware.py" --backbone "$b" --mode "$m" --variant "$v" --smoke-only 2>&1 | tee -a "$out/logs/smoke.log"
 torchrun --standalone --nproc_per_node=8 "$ROOT/scripts/train_granularity_aware.py" --backbone "$b" --mode "$m" --variant "$v" --steps 1254 2>&1 | tee -a "$out/logs/train.log"
}
# Qwen LoRA no-none is complete; the currently running weighted-none is awaited
# by the handoff wrapper. Qwen Full-SFT is deliberately next.
run qwen full no_none
run qwen full weighted_none
run gemma lora no_none
run gemma lora weighted_none
run gemma full no_none
run gemma full weighted_none
