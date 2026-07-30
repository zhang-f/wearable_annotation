#!/usr/bin/env python3
"""Generates review.html: a static, no-backend visualization page for
human review of the coarse/fine bootstrap annotations. Data is embedded
directly as JS literals (not fetched at runtime) because file:// pages
can't fetch() local JSON in most browsers -- this keeps "double-click to
open" working with zero setup.
"""
import argparse
import json
import os
import shutil

VLM_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(VLM_DIR)
DEFAULT_EXAMPLES_DIR = os.path.join(VLM_DIR, "examples")
DEFAULT_VIDEO_DIR = os.path.join(REPO_ROOT, "videos")  # repo convention, matching annotate.py/tool/server.py


def load_segments(path: str) -> dict:
    with open(path) as f:
        rec = json.loads(f.readline())
    return rec


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--coarse", default=os.path.join(DEFAULT_EXAMPLES_DIR, "bootstrap_coarse.jsonl"))
    parser.add_argument("--fine", default=os.path.join(DEFAULT_EXAMPLES_DIR, "bootstrap_fine.jsonl"))
    parser.add_argument(
        "--video-dir", default=DEFAULT_VIDEO_DIR,
        help=f"Directory containing the source mp4 (default: repo convention, {DEFAULT_VIDEO_DIR})",
    )
    parser.add_argument(
        "--out-dir", default=DEFAULT_EXAMPLES_DIR,
        help="Where to write review.html and the co-located video copy (default: vlm/examples/)",
    )
    args = parser.parse_args()

    coarse = load_segments(args.coarse)
    fine = load_segments(args.fine)

    assert coarse["video_path"] == fine["video_path"], "coarse/fine video_path mismatch"
    video_path = coarse["video_path"]
    duration = coarse["duration_in_sec"]

    os.makedirs(args.out_dir, exist_ok=True)

    # Copy (not symlink -- symlinks to paths outside the review dir can
    # fail to resolve depending on how the file is opened/shared) the mp4
    # next to review.html so the <video> tag can use a same-directory
    # relative src, which is the most reliable way to load local video
    # from a double-clicked file:// HTML page.
    src_video = os.path.join(args.video_dir, video_path)
    dst_video = os.path.join(args.out_dir, video_path)
    if not os.path.exists(dst_video):
        if os.path.exists(src_video):
            print(f"Copying {src_video} -> {dst_video}")
            shutil.copy2(src_video, dst_video)
        else:
            print(f"WARNING: source video not found at {src_video} -- review.html will be written "
                  f"but its video won't play until you place {video_path} in {args.out_dir}.")
    else:
        print(f"Video already present at {dst_video}, not re-copying")

    html = TEMPLATE.replace("__VIDEO_PATH_RAW__", video_path)  # for the HTML src= attribute and plain-text display
    html = html.replace("__VIDEO_PATH_JSON__", json.dumps(video_path))  # for the JS string literal
    html = html.replace("__DURATION__", json.dumps(duration))
    html = html.replace("__COARSE_SEGMENTS__", json.dumps(coarse["segments"], ensure_ascii=False))
    html = html.replace("__FINE_SEGMENTS__", json.dumps(fine["segments"], ensure_ascii=False))
    html = html.replace("__TASK__", json.dumps(coarse.get("task", "")))

    out_path = os.path.join(args.out_dir, "review.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"Wrote {out_path}")
    print(f"Video co-located: {os.path.exists(dst_video)}")


TEMPLATE = r"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Bootstrap annotation review</title>
<style>
  body { font-family: -apple-system, sans-serif; margin: 0; padding: 16px; background: #1e1e1e; color: #ddd; }
  h1 { font-size: 16px; margin: 0 0 4px; color: #fff; }
  .sub { font-size: 13px; color: #999; margin-bottom: 12px; }
  video { width: 100%; max-height: 50vh; background: #000; border-radius: 4px; display: block; }
  .top-row { display: flex; justify-content: space-between; align-items: center; }
  #export-btn { padding: 8px 16px; background: #2e6da4; border: none; border-radius: 4px; color: #fff; cursor: pointer; font-size: 13px; }
  #export-btn:hover { background: #3a7fc0; }

  .tl-wrap { margin: 14px 0; }
  .tl-label { font-size: 12px; color: #999; margin-bottom: 3px; }
  .timeline { position: relative; height: 30px; border-radius: 3px; overflow: hidden; cursor: pointer; margin-bottom: 8px; }
  .timeline .seg { position: absolute; top: 0; bottom: 0; box-sizing: border-box; border-right: 1px solid #000; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #111; overflow: hidden; white-space: nowrap; }
  .timeline .seg.c0 { background: #7fb2e5; }
  .timeline .seg.c1 { background: #5f92c5; }
  .timeline .seg.current { outline: 2px solid #fff; outline-offset: -2px; }
  .timeline .playhead { position: absolute; top: -2px; bottom: -2px; width: 2px; background: #fff; box-shadow: 0 0 4px #fff; pointer-events: none; z-index: 5; }

  .cols { display: flex; gap: 16px; margin-top: 10px; }
  .col { flex: 1; min-width: 0; }
  .col h2 { font-size: 14px; color: #7fc7ff; margin: 0 0 6px; }
  .seg-list { max-height: 60vh; overflow-y: auto; border: 1px solid #333; border-radius: 4px; }
  .row { display: flex; gap: 8px; align-items: flex-start; padding: 8px; border-bottom: 1px solid #2a2a2a; cursor: pointer; }
  .row:hover { background: #262626; }
  .row.current { background: #24344a; }
  .row.selected { outline: 2px solid #2e6da4; outline-offset: -2px; }
  .row .idx { color: #666; font-family: monospace; width: 22px; flex-shrink: 0; }
  .row .body { flex: 1; min-width: 0; }
  .row .times { font-family: monospace; font-size: 11px; color: #7fc7ff; }
  .row .summary { font-size: 13px; margin: 2px 0 4px; }
  .row .ctrls { display: flex; gap: 6px; align-items: center; }
  .row .ctrls button { width: 26px; height: 24px; border-radius: 3px; border: 1px solid #444; background: #333; color: #ddd; cursor: pointer; font-size: 13px; }
  .row .ctrls button.on-correct { background: #2e7d32; border-color: #2e7d32; color: #fff; }
  .row .ctrls button.on-incorrect { background: #a33; border-color: #a33; color: #fff; }
  .row .ctrls input { flex: 1; background: #1e1e1e; color: #ddd; border: 1px solid #444; border-radius: 3px; padding: 4px 6px; font-size: 12px; }
  .status { font-size: 12px; color: #7fdc7f; min-height: 16px; margin-top: 8px; }
</style>
</head>
<body>

<div class="top-row">
  <div>
    <h1>Bootstrap annotation review</h1>
    <div class="sub">video: __VIDEO_PATH_RAW__ &nbsp;|&nbsp; task: __TASK__ &nbsp;|&nbsp; duration: __DURATION__s</div>
  </div>
  <button id="export-btn">Export corrections.json</button>
</div>

<video id="player" src="__VIDEO_PATH_RAW__" controls></video>

<div class="tl-wrap">
  <div class="tl-label">coarse timeline (click a block to jump to its boundary)</div>
  <div class="timeline" id="tl-coarse"></div>
  <div class="tl-label">fine timeline</div>
  <div class="timeline" id="tl-fine"></div>
</div>

<div class="cols">
  <div class="col">
    <h2>Coarse segments</h2>
    <div class="seg-list" id="list-coarse"></div>
  </div>
  <div class="col">
    <h2>Fine segments</h2>
    <div class="seg-list" id="list-fine"></div>
  </div>
</div>

<div class="status" id="status"></div>

<script>
const VIDEO_PATH = __VIDEO_PATH_JSON__;
const DURATION = __DURATION__;
const DATA = {
  coarse: __COARSE_SEGMENTS__,
  fine: __FINE_SEGMENTS__,
};

// Derive start_time for each segment: previous segment's end_time, 0 for the first.
for (const gran of ["coarse", "fine"]) {
  let prevEnd = 0;
  for (const seg of DATA[gran]) {
    seg.start_time = prevEnd;
    prevEnd = seg.end_time;
  }
}

// Correction state, keyed by granularity -> index -> {status, note}
const corrections = { coarse: {}, fine: {} };
for (const gran of ["coarse", "fine"]) {
  DATA[gran].forEach((_, i) => { corrections[gran][i] = { status: null, note: "" }; });
}

const player = document.getElementById("player");
const statusEl = document.getElementById("status");

function seekTo(endTime) {
  player.currentTime = Math.max(0, endTime - 1.5);
  player.play();
}

function fmt(t) { return t.toFixed(1); }

// --- segment lists -------------------------------------------------------

function renderList(gran) {
  const container = document.getElementById(`list-${gran}`);
  container.innerHTML = "";
  DATA[gran].forEach((seg, i) => {
    const row = document.createElement("div");
    row.className = "row";
    row.dataset.gran = gran;
    row.dataset.idx = i;

    const idx = document.createElement("div");
    idx.className = "idx";
    idx.textContent = i + 1;
    row.appendChild(idx);

    const body = document.createElement("div");
    body.className = "body";

    const times = document.createElement("div");
    times.className = "times";
    times.textContent = `${fmt(seg.start_time)}s – ${fmt(seg.end_time)}s`;
    body.appendChild(times);

    const summary = document.createElement("div");
    summary.className = "summary";
    summary.textContent = seg.summary;
    body.appendChild(summary);

    const ctrls = document.createElement("div");
    ctrls.className = "ctrls";

    const btnOk = document.createElement("button");
    btnOk.textContent = "✓";
    btnOk.title = "correct";
    btnOk.addEventListener("click", (e) => {
      e.stopPropagation();
      const c = corrections[gran][i];
      c.status = c.status === "correct" ? null : "correct";
      renderList(gran); // cheap full re-render; lists are short (<100 rows)
    });
    ctrls.appendChild(btnOk);

    const btnBad = document.createElement("button");
    btnBad.textContent = "✗";
    btnBad.title = "incorrect";
    btnBad.addEventListener("click", (e) => {
      e.stopPropagation();
      const c = corrections[gran][i];
      c.status = c.status === "incorrect" ? null : "incorrect";
      renderList(gran);
    });
    ctrls.appendChild(btnBad);

    if (corrections[gran][i].status === "correct") btnOk.classList.add("on-correct");
    if (corrections[gran][i].status === "incorrect") btnBad.classList.add("on-incorrect");

    const note = document.createElement("input");
    note.type = "text";
    note.placeholder = "note (optional)";
    note.value = corrections[gran][i].note;
    note.addEventListener("click", (e) => e.stopPropagation());
    note.addEventListener("input", () => { corrections[gran][i].note = note.value; });
    ctrls.appendChild(note);

    body.appendChild(ctrls);
    row.appendChild(body);

    row.addEventListener("click", () => {
      seekTo(seg.end_time);
      selectRow(gran, i);
    });

    container.appendChild(row);
  });
}

function selectRow(gran, i) {
  for (const g of ["coarse", "fine"]) {
    document.querySelectorAll(`#list-${g} .row`).forEach((el) => el.classList.remove("selected"));
  }
  const row = document.querySelector(`#list-${gran} .row[data-idx="${i}"]`);
  if (row) row.classList.add("selected");
}

// --- timelines -------------------------------------------------------------

function renderTimeline(gran) {
  const el = document.getElementById(`tl-${gran}`);
  el.innerHTML = "";
  DATA[gran].forEach((seg, i) => {
    const startPct = (seg.start_time / DURATION) * 100;
    const widthPct = ((seg.end_time - seg.start_time) / DURATION) * 100;
    const block = document.createElement("div");
    block.className = `seg ${i % 2 === 0 ? "c0" : "c1"}`;
    block.style.left = startPct + "%";
    block.style.width = widthPct + "%";
    block.title = `[${fmt(seg.start_time)}-${fmt(seg.end_time)}s] ${seg.summary}`;
    block.dataset.gran = gran;
    block.dataset.idx = i;
    block.addEventListener("click", () => { seekTo(seg.end_time); selectRow(gran, i); });
    el.appendChild(block);
  });
  const playhead = document.createElement("div");
  playhead.className = "playhead";
  playhead.id = `playhead-${gran}`;
  el.appendChild(playhead);
}

// --- playback-driven highlighting ------------------------------------------

function segIndexAt(gran, t) {
  const segs = DATA[gran];
  for (let i = 0; i < segs.length; i++) {
    if (t < segs[i].end_time || i === segs.length - 1) return i;
  }
  return segs.length - 1;
}

function updateHighlight() {
  const t = player.currentTime;
  for (const gran of ["coarse", "fine"]) {
    const idx = segIndexAt(gran, t);

    document.querySelectorAll(`#list-${gran} .row`).forEach((el) => {
      el.classList.toggle("current", parseInt(el.dataset.idx) === idx);
    });
    document.querySelectorAll(`#tl-${gran} .seg`).forEach((el) => {
      el.classList.toggle("current", parseInt(el.dataset.idx) === idx);
    });

    const pct = DURATION > 0 ? (t / DURATION) * 100 : 0;
    const ph = document.getElementById(`playhead-${gran}`);
    if (ph) ph.style.left = pct + "%";
  }
}

player.addEventListener("timeupdate", updateHighlight);
player.addEventListener("seeking", updateHighlight);

// --- export ------------------------------------------------------------

document.getElementById("export-btn").addEventListener("click", () => {
  const out = { video_path: VIDEO_PATH, duration_in_sec: DURATION, granularities: {} };
  for (const gran of ["coarse", "fine"]) {
    out.granularities[gran] = DATA[gran].map((seg, i) => ({
      index: i,
      summary: seg.summary,
      start_time: seg.start_time,
      end_time: seg.end_time,
      status: corrections[gran][i].status,
      note: corrections[gran][i].note,
    }));
  }
  const blob = new Blob([JSON.stringify(out, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "corrections.json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  statusEl.textContent = "corrections.json downloaded.";
});

// --- init ------------------------------------------------------------

renderList("coarse");
renderList("fine");
renderTimeline("coarse");
renderTimeline("fine");
updateHighlight();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
