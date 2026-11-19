#!/usr/bin/env bash
set -eu
editor_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
editor_port="${1:-8766}"
if [ -f "$editor_dir/server.pid" ]; then
  editor_old_pid="$(cat "$editor_dir/server.pid")"
  if kill -0 "$editor_old_pid" 2>/dev/null && ps -p "$editor_old_pid" -o args= | grep -Fq "$editor_dir/server.py"; then
    if command -v curl >/dev/null && curl -fsS --max-time 2 "http://127.0.0.1:$editor_port/progress" >/dev/null 2>&1; then
      echo "Server already current: http://127.0.0.1:$editor_port/progress (PID $editor_old_pid)"
      exit 0
    fi
    echo "Restarting older editor server PID $editor_old_pid"
    kill "$editor_old_pid"
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      kill -0 "$editor_old_pid" 2>/dev/null || break
      sleep 0.2
    done
  fi
  rm -f "$editor_dir/server.pid"
fi
nohup python "$editor_dir/server.py" --port "$editor_port" > "$editor_dir/server.log" 2>&1 < /dev/null &
editor_pid=$!
sleep 0.5
if kill -0 "$editor_pid" 2>/dev/null; then
  printf '%s\n' "$editor_pid" > "$editor_dir/server.pid"
  echo "Server PID $editor_pid: http://127.0.0.1:$editor_port/progress"
  head -1 "$editor_dir/server.log"
else
  cat "$editor_dir/server.log"
  exit 1
fi
