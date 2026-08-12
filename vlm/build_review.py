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
    parser.add_argument(
        "--out-name", default="review.html",
        help="Filename for the generated page inside --out-dir (default: review.html).",
    )
    parser.add_argument("--bundle", default=None,
        help="v3 review bundle JSON (coarse + pass0 + flags + 3 fine versions raw/R/M). "
             "When given, --coarse/--fine are ignored.")
    args = parser.parse_args()

    if args.bundle:
        b = json.load(open(args.bundle))
        video_path = b["video_path"]; duration = b["duration_in_sec"]
        coarse = {"video_path": video_path, "duration_in_sec": duration, "task": b.get("task", ""),
                  "segments": b["coarse_segments"], "video_assessment": b.get("coarse_assessment", {}),
                  "pass0": b.get("pass0", {}), "flags": b.get("flags", [])}
        fine = {"video_path": video_path, "segments": b["fine_versions"]["R"], "video_assessment": b.get("fine_assessment", {})}
        fine_versions = b["fine_versions"]
    else:
        coarse = load_segments(args.coarse)
        fine = load_segments(args.fine)
        fine_versions = {"raw": fine["segments"], "R": fine["segments"], "M": fine["segments"]}
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
    CANON = ["raw", "R", "M", "F", "FR", "raw_v3", "R_v3", "M_v3", "F_v3", "FR_v3",
             "raw_v4", "R_v4", "M_v4", "F_v4", "FR_v4"]
    order = [v for v in CANON if isinstance(fine_versions.get(v), list) and fine_versions.get(v)]
    for v in fine_versions:  # append any non-canonical versions
        if v not in order and isinstance(fine_versions[v], list) and fine_versions[v]:
            order.append(v)
    html = html.replace("__FINE_VERSIONS__", json.dumps(fine_versions, ensure_ascii=False))
    html = html.replace("__FINE_ORDER__", json.dumps(order))
    html = html.replace("__TASK__", json.dumps(coarse.get("task", "")))
    # v2: per-granularity self-assessment shown at the top (empty dict if a v1 file lacks it)
    html = html.replace("__COARSE_ASSESSMENT__", json.dumps(coarse.get("video_assessment", {}), ensure_ascii=False))
    html = html.replace("__FINE_ASSESSMENT__", json.dumps(fine.get("video_assessment", {}), ensure_ascii=False))
    # v3: Pass 0 global understanding + pipeline flags shown at the top
    html = html.replace("__PASS0__", json.dumps(coarse.get("pass0", {}), ensure_ascii=False))
    html = html.replace("__FLAGS__", json.dumps(coarse.get("flags", []), ensure_ascii=False))

    out_path = os.path.join(args.out_dir, args.out_name)
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
  /* v2 additions (display only; interactions unchanged) */
  .assess { display: flex; gap: 16px; margin: 12px 0 4px; font-size: 12px; }
  .assess .box { flex: 1; border: 1px solid #333; border-radius: 4px; padding: 8px 10px; background: #232323; }
  .assess .box h3 { margin: 0 0 4px; font-size: 12px; color: #7fc7ff; }
  .assess .score { font-weight: bold; color: #fff; }
  .assess ul { margin: 2px 0 4px 16px; padding: 0; }
  .assess .none { color: #7fdc7f; }
  .row .conf { font-family: monospace; font-size: 11px; color: #999; margin-left: 6px; }
  .row .merged { font-size: 10px; color: #d9b06a; background: #2a2618; border: 1px solid #5a4a28; border-radius: 3px; padding: 0 4px; margin-left: 6px; }
  .row .idle-badge { font-size: 10px; color: #9aa7c7; background: #23283a; border: 1px solid #3a4a6a; border-radius: 3px; padding: 0 4px; margin-left: 6px; }
  /* v3 refine: fine version toggle (raw / R / M) */
  .fine-toggle { margin-left: 8px; display: inline-flex; vertical-align: middle; }
  .fine-toggle button { font-size: 12px; padding: 2px 10px; border: 1px solid #444; background: #2a2a2a; color: #bbb; cursor: pointer; }
  .fine-toggle button:first-child { border-radius: 4px 0 0 4px; }
  .fine-toggle button:last-child { border-radius: 0 4px 4px 0; border-left: none; }
  .fine-toggle button:not(:first-child):not(:last-child) { border-left: none; }
  .fine-toggle button.active { background: #2e6da4; color: #fff; border-color: #2e6da4; }
  .fine-count { font-size: 12px; color: #999; font-weight: normal; margin-left: 4px; }
  /* v3: Pass 0 global understanding + flags */
  .pass0 { margin: 12px 0 4px; font-size: 12px; border: 1px solid #333; border-radius: 4px; padding: 8px 10px; background: #202a20; }
  .pass0 h3 { margin: 0 0 4px; font-size: 12px; color: #9fdc9f; }
  .pass0 .phases { margin: 4px 0 0 16px; padding: 0; color: #ccc; }
  .pass0 .phases li { margin: 1px 0; }
  .pass0 .phases .rng { color: #7fc7ff; font-family: monospace; }
  .flags { margin: 8px 0; }
  .flags .flag { border-left: 3px solid #c99a3c; background: #2a2618; padding: 4px 8px; margin: 3px 0; border-radius: 2px; color: #e8d9b0; font-size: 12px; }
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

<div id="pass0"></div>
<div id="flags"></div>

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
    <h2>Fine segments <span id="fine-count" class="fine-count"></span>
      <span class="fine-toggle" id="fine-toggle"></span>
    </h2>
    <div class="seg-list" id="list-fine"></div>
  </div>
</div>

<div class="status" id="status"></div>

<script>
const VIDEO_PATH = __VIDEO_PATH_JSON__;
const DURATION = __DURATION__;
const FINE = __FINE_VERSIONS__;
const FINE_ORDER = __FINE_ORDER__;
let fineVersion = "R";  // default shown version
const DATA = {
  coarse: __COARSE_SEGMENTS__,
  fine: FINE[fineVersion],
};
const ASSESSMENT = { coarse: __COARSE_ASSESSMENT__, fine: __FINE_ASSESSMENT__ };
const PASS0 = __PASS0__;
const FLAGS = __FLAGS__;

// Derive start_time for each segment (previous segment's end_time; 0 for the first).
function deriveStarts(segs) {
  let prevEnd = 0;
  for (const seg of segs) { seg.start_time = prevEnd; prevEnd = seg.end_time; }
}
deriveStarts(DATA.coarse);
for (const v of ["raw", "R", "M"]) deriveStarts(FINE[v]);

// Correction state. coarse -> idx; fine is kept PER VERSION so switching raw/R/M
// preserves each version's ticks/notes independently (export tags the shown version).
const corrections = { coarse: {}, fine: {} };
for (const v of FINE_ORDER) corrections.fine[v] = {};
function corrMap(gran) { return gran === "fine" ? corrections.fine[fineVersion] : corrections.coarse; }
function ensureCorr(gran, i) { const m = corrMap(gran); if (!m[i]) m[i] = { status: null, note: "" }; return m[i]; }
DATA.coarse.forEach((_, i) => { corrections.coarse[i] = { status: null, note: "" }; });

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
    if (seg.boundary_confidence != null) {
      const conf = document.createElement("span");
      conf.className = "conf";
      conf.textContent = `conf ${seg.boundary_confidence.toFixed(2)}`;
      times.appendChild(conf);
    }
    if (seg.type === "idle") {
      const idle = document.createElement("span");
      idle.className = "idle-badge";
      idle.textContent = "idle";
      idle.title = "no-activity segment (natural silent sample, not garbage)";
      times.appendChild(idle);
    }
    const mi = seg.merge_info;
    if (mi && mi.merged_from > 1) {
      const mg = document.createElement("span");
      mg.className = "merged";
      const rule = mi.rule ? ` (${mi.rule})` : "";
      mg.textContent = `merged ${mi.merged_from}${rule}`;
      mg.title = "merged from " + mi.merged_from + " raw Pass-B segments" + (mi.rule ? " via " + mi.rule + " rule" : "")
                 + (mi.source_indices ? "; raw idx " + mi.source_indices.join(",") : "");
      times.appendChild(mg);
    }
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
      const c = ensureCorr(gran, i);
      c.status = c.status === "correct" ? null : "correct";
      renderList(gran); // cheap full re-render; lists are short (<100 rows)
    });
    ctrls.appendChild(btnOk);

    const btnBad = document.createElement("button");
    btnBad.textContent = "✗";
    btnBad.title = "incorrect";
    btnBad.addEventListener("click", (e) => {
      e.stopPropagation();
      const c = ensureCorr(gran, i);
      c.status = c.status === "incorrect" ? null : "incorrect";
      renderList(gran);
    });
    ctrls.appendChild(btnBad);

    const cur = ensureCorr(gran, i);
    if (cur.status === "correct") btnOk.classList.add("on-correct");
    if (cur.status === "incorrect") btnBad.classList.add("on-incorrect");

    const note = document.createElement("input");
    note.type = "text";
    note.placeholder = "note (optional)";
    note.value = cur.note;
    note.addEventListener("click", (e) => e.stopPropagation());
    note.addEventListener("input", () => { ensureCorr(gran, i).note = note.value; });
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
  const out = { video_path: VIDEO_PATH, duration_in_sec: DURATION, fine_version_shown: fineVersion, granularities: {} };
  const emit = (gran, segs, cmap) => segs.map((seg, i) => ({
    index: i, summary: seg.summary, start_time: seg.start_time, end_time: seg.end_time,
    merge_info: seg.merge_info || null,
    status: (cmap[i] || {}).status || null, note: (cmap[i] || {}).note || "",
  }));
  out.granularities.coarse = emit("coarse", DATA.coarse, corrections.coarse);
  // the shown fine version under "fine", plus each version's ticks/notes so nothing is lost
  out.granularities.fine = emit("fine", FINE[fineVersion], corrections.fine[fineVersion]);
  out.fine_all_versions = {};
  for (const v of FINE_ORDER) out.fine_all_versions[v] = emit("fine", FINE[v], corrections.fine[v]);
  const blob = new Blob([JSON.stringify(out, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "corrections.json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  statusEl.textContent = `corrections.json downloaded (fine version shown: ${fineVersion}).`;
});

// --- video assessment (top, display only) --------------------------------

function escapeHtml(s) { const d = document.createElement("div"); d.textContent = String(s); return d.innerHTML; }
function renderAssessment() {
  const el = document.getElementById("assess");
  el.innerHTML = ["coarse", "fine"].map((g) => {
    const a = ASSESSMENT[g] || {};
    const issues = (a.issues && a.issues.length)
      ? "<ul>" + a.issues.map((x) => "<li>" + escapeHtml(x) + "</li>").join("") + "</ul>"
      : "<span class='none'>none</span>";
    const lcr = (a.low_confidence_regions && a.low_confidence_regions.length)
      ? a.low_confidence_regions.map((r) => "[" + r[0] + "–" + r[1] + "s]").join(" ")
      : "<span class='none'>none</span>";
    const sc = (a.segmentability != null) ? a.segmentability : "–";
    return `<div class="box"><h3>${g} &middot; segmentability <span class="score">${sc}/5</span></h3>`
      + `<div>issues: ${issues}</div><div>low-confidence regions: ${lcr}</div></div>`;
  }).join("");
}

// --- Pass 0 global understanding + flags (top, display only) -------------

function renderPass0() {
  const el = document.getElementById("pass0");
  if (!PASS0 || !PASS0.task_understanding) { el.className = ""; el.innerHTML = ""; return; }
  const phases = (PASS0.phases || []).map((p) => {
    const r = (p.approx_range && p.approx_range.length === 2)
      ? `<span class="rng">[${p.approx_range[0]}–${p.approx_range[1]}s]</span> ` : "";
    return "<li>" + r + escapeHtml(p.description || "") + "</li>";
  }).join("");
  el.className = "pass0";
  el.innerHTML = `<h3>Global understanding (Pass 0)</h3><div>${escapeHtml(PASS0.task_understanding)}</div>`
    + (phases ? `<ul class="phases">${phases}</ul>` : "");
}

function renderFlags() {
  const el = document.getElementById("flags");
  if (!FLAGS || !FLAGS.length) { el.className = ""; el.innerHTML = ""; return; }
  el.className = "flags";
  el.innerHTML = FLAGS.map((f) => `<div class="flag">⚑ ${escapeHtml(f)}</div>`).join("");
}

// --- fine version toggle (raw / R / M) -----------------------------------

function switchFine(v) {
  fineVersion = v;
  DATA.fine = FINE[v];
  deriveStarts(DATA.fine);
  document.querySelectorAll("#fine-toggle button").forEach((b) => b.classList.toggle("active", b.dataset.v === v));
  document.getElementById("fine-count").textContent = `${DATA.fine.length} segs · showing ${v}`;
  renderList("fine");
  renderTimeline("fine");
  updateHighlight();
}
// build the toggle buttons from whichever versions are present
document.getElementById("fine-toggle").innerHTML =
  FINE_ORDER.map((v) => `<button data-v="${v}">${v}</button>`).join("");
document.querySelectorAll("#fine-toggle button").forEach((b) => {
  b.addEventListener("click", () => switchFine(b.dataset.v));
});
if (!FINE_ORDER.includes(fineVersion)) fineVersion = FINE_ORDER[0] || "R";

// --- init ------------------------------------------------------------

renderPass0();
renderFlags();
renderList("coarse");
renderTimeline("coarse");
switchFine(fineVersion);  // renders fine list + timeline + count + active toggle
updateHighlight();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
