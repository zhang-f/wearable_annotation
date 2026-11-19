# EgoDual review editor

Run from an ordinary terminal on the video host:

```bash
bash /home/fan/google/review_run/annotation_v2/editor/start.sh
```

The server binds to `127.0.0.1:8766`; if occupied it tries subsequent ports. The log prints the actual port. The startup script writes `server.pid` only after the process survives its initial startup.

From your workstation, replacing `YOUR_HOST` with the SSH hostname you normally use:

```bash
ssh -N -L 8766:127.0.0.1:8766 fan@YOUR_HOST
```

Open `http://localhost:8766`. If the server uses another port, replace the final remote port in the forwarding command. No CDN or Python dependencies are needed for serving.

Editing: choose a video and step, edit fields, save. Saving any editing panel also saves outstanding changes in the other panels as one journal transaction. Navigation, mode/queue switching and undo first save outstanding edits; failed saves prevent navigation. Step timestamps and transition labels are read-only. Object renaming updates structured references and matching text, preserving `old_summary`. Alt-click a step to toggle its preceding subtask boundary; B selects the boundary nearest the playback position. To establish the pilot gold, click “设为金标准” and confirm. The agent source JSON remains unchanged.

Queue mode: T/S are available immediately; D/P show “暂无数据” until independent verification/prediction inputs exist. R is a deterministic 10% sample of eligible steps; steps occurring in T/D are excluded. P is a deterministic 20% sample. Queue decisions and all field edits are journaled; R decisions also go to `human/random_audit.jsonl`, including error fields even if corrected. For custom corrections, enter edit mode, save, return to the queue and confirm. S offers adjacent-boundary movement and merge; text from the moved subtask is preserved. P match checkboxes record per-forecaster human corrections in journal events. P results with missing or mismatched source version, boundaries, or instructions are marked for rerun. Gold creation is a separate explicit action.

The append-only journal uses one JSON line per transaction with the specified audit keys and a `changes` object. Rename/partition transactions can span fields; `before`/`after` contain the complete changed top-level values. Replay applies `changes`, then recomputes all transitions. Undo appends a reverse transaction. JSON snapshots are atomically replaced under a server lock; original `videos/` files are never written. Use a single server instance for a given annotation root.

Tests:

```bash
python /home/fan/google/review_run/annotation_v2/editor/selftest.py
node /home/fan/google/review_run/annotation_v2/editor/selftest_ui.js
```

The Python test copies the real pilot `e531cded0108b6c3.json` into a temporary directory below `editor/`; all test journals are deleted when it exits. No production human records are touched.

## Current execution limitations

The agent's sandbox denies socket creation (`PermissionError: [Errno 1] Operation not permitted`). The requested nohup launch was attempted and failed; **there is no running server PID**. See `server.log`. Playwright and Chromium are installed, but headless launch fails with `TargetClosedError` in this environment. Therefore HTTP networking, video playback, browser rendering, screenshots and browser console checks have not been verified. The HTTP handler tests run against in-memory streams and do not establish browser behavior. Run the startup command above in a normal host terminal to use the editor.

## Two aligned timelines

The coarse and fine tracks share a time ruler, zoom, horizontal scroll and red video playhead. Segment widths reflect durations; Fit and 2×–16× zoom allow inspection of short steps. Click either track to seek to that point and open its fields. Coarse selection loops the whole subtask. Hatched uncovered areas have no segment. Fine boundaries remain the human-defined input; descriptions are editable drafts and must be checked against video. Alt-click a fine segment changes only its preceding coarse boundary.

### 实时运行进度

在正常主机终端运行 `bash /home/fan/google/review_run/annotation_v2/editor/start.sh`，然后打开 `http://127.0.0.1:8766/progress`。页面每 5 秒重新读取 `annotation_v2/videos/`、校验报告、盲测输入包和正式结果，展示阶段进度、逐视频任务与 subtask、最近运行记录及方法说明。编辑器页顶部也有“运行进度”入口。

这个页面只读。独立预测者的试跑文件会单独计数，不算入正式 predictable 完成数。若通过 SSH 访问远程主机，先做本地端口转发：`ssh -N -L 8766:127.0.0.1:8766 fan@YOUR_HOST`。
