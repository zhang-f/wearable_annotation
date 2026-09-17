#!/usr/bin/env bash
set -euo pipefail
cd /data/fan/projects/procedure_forecasting
ROOT=runs/granularity_aware_final_v1
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
run_one() {
  local backbone="$1" mode="$2" variant="$3"
  local out="$ROOT/${backbone}_${mode}_${variant}"
  mkdir -p "$out/logs"
  for phase in smoke main; do
    for attempt in 1 2 3; do
      if [[ "$phase" == smoke ]]; then args=(--smoke-only); log="$out/logs/smoke.log"; else args=(--steps 1254); log="$out/logs/train.log"; fi
      if torchrun --standalone --nproc_per_node=8 "$ROOT/scripts/train_granularity_aware.py" --backbone "$backbone" --mode "$mode" --variant "$variant" "${args[@]}" 2>&1 | tee -a "$log"; then break; fi
      echo "$(date -u +%FT%TZ) retry $attempt failed: $backbone $mode $variant $phase" | tee -a "$out/logs/supervisor.log"
      sleep 15
      [[ "$attempt" == 3 ]] && exit 1
    done
  done
}
for backbone in qwen gemma; do
  for variant in no_none weighted_none; do run_one "$backbone" lora "$variant"; done
done
for backbone in qwen gemma; do
  for variant in no_none weighted_none; do run_one "$backbone" full "$variant"; done
done
