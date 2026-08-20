#!/usr/bin/env python3
"""Multi-reviewer human-terminal-review workbench server. Stdlib only
(http.server + fcntl for atomic claim/append), consistent with the rest of
vlm/'s tooling. Never writes to any existing draft/qc jsonl -- routine
per-action writes are review_workbench/assignment.json (claim state) and
corrections/*.jsonl (append-only action logs); the one on-demand exception
is /api/merge_final, which (re)writes outputs/final/annotations_
{coarse,fine}_final.jsonl -- see merge_corrections.py's own docstring.

Run: python3 review_workbench/server.py --port 8910 [--video-dir /path/to/mp4s]
Then open http://<host>:8910/ (reviewers behind the same host/ssh-forward
share one instance and one assignment.json / corrections/ directory).

--video-dir defaults to $EGOPROACTIVE_VIDEO_DIR if set, else ../videos
relative to this file -- pass it explicitly (or set the env var) rather than
editing this file, so the deployment stays portable across machines. See
README.md's Setup section.
"""
import argparse, fcntl, json, mimetypes, os, re, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

WORKBENCH = Path(__file__).parent
VLM = WORKBENCH.parent
sys.path.insert(0, str(VLM))
from review_workbench import merge_corrections, replay, translate  # noqa: E402

ASSIGNMENT = WORKBENCH / "assignment.json"
ASSIGNMENT_LOCK = WORKBENCH / "assignment.json.lock"
CORRECTIONS = VLM / "corrections"
CORRECTIONS.mkdir(exist_ok=True)
STATIC = WORKBENCH / "static"
DEFAULT_VIDEO_DIR = os.environ.get("EGOPROACTIVE_VIDEO_DIR", str(VLM.parent / "videos"))
VIDEO_DIR = Path(DEFAULT_VIDEO_DIR)  # overwritten by --video-dir in __main__

RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


# ---------------------------------------------------------------------------
# assignment.json atomic read/modify/write
# ---------------------------------------------------------------------------

def _with_assignment_lock(fn):
    """Opens assignment.json.lock, takes an exclusive flock, loads
    assignment.json, calls fn(data) -> (data, result), writes data back,
    releases. Guarantees claim/release is a true compare-and-set even under
    concurrent requests (two reviewers hitting claim on the same file_no:
    only one can hold the lock at a time, and each sees the other's write)."""
    with open(ASSIGNMENT_LOCK, "a+") as lockf:
        fcntl.flock(lockf, fcntl.LOCK_EX)
        try:
            data = json.load(open(ASSIGNMENT))
            data, result = fn(data)
            tmp = ASSIGNMENT.with_suffix(".json.tmp")
            json.dump(data, open(tmp, "w"), ensure_ascii=False, indent=1)
            os.replace(tmp, ASSIGNMENT)
            return result
        finally:
            fcntl.flock(lockf, fcntl.LOCK_UN)


def do_claim(file_no, reviewer):
    def fn(data):
        for e in data["entries"]:
            if e["file_no"] == file_no:
                if e["status"] == "no_data":
                    return data, {"ok": False, "error": "no_data (failed_final, nothing to review)"}
                if e["claimed_by"] and e["claimed_by"] != reviewer and e["status"] != "done":
                    return data, {"ok": False, "error": f"already claimed by {e['claimed_by']}"}
                e["claimed_by"] = reviewer
                if e["status"] == "unclaimed":
                    e["status"] = "in_progress"
                e["claimed_at"] = time.time()
                return data, {"ok": True, "entry": e}
        return data, {"ok": False, "error": "file_no not found"}
    return _with_assignment_lock(fn)


def do_release(file_no, reviewer):
    def fn(data):
        for e in data["entries"]:
            if e["file_no"] == file_no:
                if e["claimed_by"] != reviewer:
                    return data, {"ok": False, "error": "not claimed by you"}
                if e["status"] != "done":
                    e["claimed_by"] = None
                    e["status"] = "unclaimed"
                return data, {"ok": True, "entry": e}
        return data, {"ok": False, "error": "file_no not found"}
    return _with_assignment_lock(fn)


def do_claim_range(start_no, end_no, reviewer):
    def fn(data):
        claimed, skipped = [], []
        for e in data["entries"]:
            if start_no <= e["file_no"] <= end_no:
                if e["status"] == "no_data":
                    continue
                if e["claimed_by"] and e["claimed_by"] != reviewer and e["status"] != "done":
                    skipped.append(e["file_no"])
                    continue
                e["claimed_by"] = reviewer
                if e["status"] == "unclaimed":
                    e["status"] = "in_progress"
                e["claimed_at"] = time.time()
                claimed.append(e["file_no"])
        return data, {"ok": True, "claimed": claimed, "skipped": skipped}
    return _with_assignment_lock(fn)


def do_mark_done(file_no, reviewer, done):
    def fn(data):
        for e in data["entries"]:
            if e["file_no"] == file_no:
                if e["claimed_by"] != reviewer:
                    return data, {"ok": False, "error": "not claimed by you"}
                e["status"] = "done" if done else "in_progress"
                return data, {"ok": True, "entry": e}
        return data, {"ok": False, "error": "file_no not found"}
    return _with_assignment_lock(fn)


SEG_FLAG_RE = re.compile(r"^(coarse|fine) seg (\d+):")


def per_segment_flags(qc_flags):
    """Best-effort extraction of per-segment flags from run_qc.py's flag detail
    strings. Only codes whose detail is formatted "<gran> seg <i>: ..." (E1, E2,
    W4, I1, I2) can be attributed to a specific segment this way; bucket-level
    and video-level flags (E3/E4/E5/W1/W2/W3/W5/I3) are not attributable to one
    segment and are surfaced only in the video-level flags banner instead."""
    out = {"coarse": {}, "fine": {}}
    for lvl in ("error", "warn", "info"):
        for fl in qc_flags.get(lvl, []):
            m = SEG_FLAG_RE.match(fl["detail"])
            if not m:
                continue
            gran, idx = m.group(1), int(m.group(2))
            out[gran].setdefault(idx, []).append({"level": lvl, "code": fl["code"], "detail": fl["detail"]})
    return out


def get_entry(file_no):
    data = json.load(open(ASSIGNMENT))
    for e in data["entries"]:
        if e["file_no"] == file_no:
            return e
    return None


def validate_action(current_segs, action, seg_index, payload):
    """Pre-flight check against the CURRENT (pre-action) segment list, so an
    invalid request is rejected with a clear error instead of being logged
    and then silently no-op'd by replay.py (which conservatively skips
    anything out of range -- correct for replay safety, but a bad experience
    if the reviewer gets no feedback that their click had zero effect)."""
    n = len(current_segs)
    if action == "undo":
        return None  # seq existence isn't checked here; a stale undo is harmless (matches nothing)
    if seg_index is None or not (0 <= seg_index < n):
        return f"segment index {seg_index} out of range (0..{n - 1})"
    if action == "merge" and seg_index >= n - 1:
        return "cannot merge the last segment (nothing after it to merge into)"
    if action == "add":
        t = payload.get("t")
        if t is None:
            return "missing playhead time"
        lo = current_segs[seg_index - 1]["end_time"] if seg_index > 0 else 0.0
        hi = current_segs[seg_index]["end_time"]
        if not (lo < t < hi):
            return f"playhead {t:.1f}s is not strictly inside segment {seg_index} ({lo:.1f}s-{hi:.1f}s) -- it's on or outside the boundary, move it and retry"
    return None


# ---------------------------------------------------------------------------
# corrections/*.jsonl atomic append
# ---------------------------------------------------------------------------

def append_action(file_no, video_id, reviewer, granularity, seg_index, action, payload):
    path = CORRECTIONS / f"{file_no}_{video_id}.jsonl"
    lockpath = CORRECTIONS / f".{file_no}_{video_id}.lock"
    with open(lockpath, "a+") as lockf:
        fcntl.flock(lockf, fcntl.LOCK_EX)
        try:
            seq = replay.next_seq(file_no, video_id)
            rec = {"seq": seq, "ts": time.time(), "reviewer": reviewer, "file_no": file_no,
                   "video_id": video_id, "granularity": granularity, "seg_index": seg_index,
                   "action": action, "payload": payload}
            with open(path, "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            return rec
        finally:
            fcntl.flock(lockf, fcntl.LOCK_UN)


def correction_count(file_no, video_id):
    return replay.effective_correction_count(file_no, video_id)


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def _serve_static_file(self, fpath):
        if not fpath.is_file():
            self.send_error(404)
            return
        content_type = mimetypes.guess_type(str(fpath))[0] or "application/octet-stream"
        data = fpath.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_video(self, video_id):
        matches = list(VIDEO_DIR.glob(f"{video_id}.mp4"))
        if not matches:
            self.send_error(404)
            return
        fpath = matches[0]
        file_size = fpath.stat().st_size
        range_header = self.headers.get("Range")
        if range_header:
            m = RANGE_RE.match(range_header)
            start = int(m.group(1)) if m.group(1) else 0
            end = int(m.group(2)) if m.group(2) else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1
            self.send_response(206)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(length))
            self.end_headers()
            with open(fpath, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(file_size))
            self.end_headers()
            with open(fpath, "rb") as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)

    # -- GET --------------------------------------------------------------

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            return self._serve_static_file(STATIC / "index.html")
        if path == "/workbench.html":
            return self._serve_static_file(STATIC / "workbench.html")
        if path.startswith("/static/"):
            return self._serve_static_file(STATIC / path[len("/static/"):])

        if path == "/api/assignment":
            data = json.load(open(ASSIGNMENT))
            return self._json(data)

        if path == "/api/progress":
            return self._json(self._compute_progress())

        if path == "/api/correction_counts":
            data = json.load(open(ASSIGNMENT))
            counts = {}
            for e in data["entries"]:
                fpath = CORRECTIONS / f"{e['file_no']}_{e['video_id']}.jsonl"
                if fpath.exists():
                    counts[e["file_no"]] = correction_count(e["file_no"], e["video_id"])
            return self._json(counts)

        m = re.match(r"^/api/video/(\d{4})$", path)
        if m:
            file_no = m.group(1)
            entry = get_entry(file_no)
            if not entry:
                return self._json({"ok": False, "error": "not found"}, 404)
            if entry["status"] == "no_data":
                return self._json({"ok": False, "error": "no_data"}, 404)
            state = replay.replay_video(entry["video_path"], file_no, entry["video_id"])
            if state is None:
                return self._json({"ok": False, "error": "no QC data"}, 404)
            # Per-segment flags are attributed by ORIGINAL qc-base index (before
            # any corrections). If a segment has never been touched (_origin_seq
            # is None), its position in the current list still equals its
            # original qc index, so this lookup is exact for untouched segments
            # -- the common case -- and simply stops applying once a segment has
            # been merged/split/deleted (that segment's shape already changed,
            # so the original flag no longer cleanly applies to it anyway).
            base_flags = state["base"]["coarse"]["qc"]["flags"]
            seg_flags = per_segment_flags(base_flags)
            for gran in ("coarse", "fine"):
                for i, s in enumerate(state[gran]):
                    if s.get("_origin_seq") is None:
                        s["qc_flag"] = seg_flags[gran].get(i, [])
                    else:
                        s["qc_flag"] = []
            return self._json({
                "ok": True, "entry": entry,
                "coarse": state["coarse"], "fine": state["fine"],
                "task": state["base"]["coarse"].get("task", ""),
                "pass0": state["base"]["coarse"].get("pass0", {}),
                "n_actions": len(state["actions"]),
            })

        m = re.match(r"^/api/video-file/([A-Za-z0-9]+)\.mp4$", path)
        if m:
            return self._serve_video(m.group(1))

        self.send_error(404)

    # -- POST -------------------------------------------------------------

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            body = self._read_json_body()
        except Exception:
            return self._json({"ok": False, "error": "bad json"}, 400)

        if path == "/api/translate":
            text = body.get("text", "")
            summary, translated = translate.translate_and_normalize(text)
            return self._json({"ok": True, "summary": summary, "translated": translated})

        if path == "/api/merge_final":
            # Regenerates outputs/final/annotations_{coarse,fine}_final.jsonl
            # from every video's current replayed state (QC base + that
            # video's corrections/*.jsonl, if any) -- same code path as
            # `python3 review_workbench/merge_corrections.py`. Read-only over
            # assignment.json/corrections/qc jsonl; the two _final.jsonl
            # files are the only thing this ever writes.
            try:
                stats = merge_corrections.run_merge()
            except Exception as exc:  # noqa: BLE001 -- surface any failure to the UI instead of a bare 500
                return self._json({"ok": False, "error": f"merge failed: {exc}"}, 500)
            return self._json({"ok": True, **stats})

        if path == "/api/claim":
            file_no, reviewer = body.get("file_no"), body.get("reviewer")
            if not file_no or not reviewer:
                return self._json({"ok": False, "error": "file_no and reviewer required"}, 400)
            return self._json(do_claim(file_no, reviewer))

        if path == "/api/release":
            file_no, reviewer = body.get("file_no"), body.get("reviewer")
            return self._json(do_release(file_no, reviewer))

        if path == "/api/claim_range":
            reviewer = body.get("reviewer")
            start_no, end_no = body.get("start_no"), body.get("end_no")
            if not (reviewer and start_no and end_no):
                return self._json({"ok": False, "error": "reviewer/start_no/end_no required"}, 400)
            return self._json(do_claim_range(start_no, end_no, reviewer))

        if path == "/api/mark_done":
            file_no, reviewer = body.get("file_no"), body.get("reviewer")
            done = body.get("done", True)
            entry = get_entry(file_no)
            if not entry:
                return self._json({"ok": False, "error": "file_no not found"}, 404)
            result = do_mark_done(file_no, reviewer, done)
            if result.get("ok"):
                append_action(file_no, entry["video_id"], reviewer, "video", None,
                               "mark_done" if done else "undo",
                               {} if done else {"undo_mark_done": True})
            return self._json(result)

        m = re.match(r"^/api/action/(\d{4})$", path)
        if m:
            file_no = m.group(1)
            entry = get_entry(file_no)
            if not entry:
                return self._json({"ok": False, "error": "not found"}, 404)
            reviewer = body.get("reviewer")
            if not reviewer or entry["claimed_by"] != reviewer:
                return self._json({"ok": False, "error": "video not claimed by you"}, 403)
            action = body.get("action")
            if action not in ("retime", "edit", "merge", "delete", "add", "undo", "clear_all"):
                return self._json({"ok": False, "error": f"unknown action {action}"}, 400)
            granularity = body.get("granularity")
            seg_index = body.get("seg_index")
            payload = body.get("payload", {})

            pre_state = replay.replay_video(entry["video_path"], file_no, entry["video_id"])
            if pre_state is None:
                return self._json({"ok": False, "error": "no QC data"}, 404)
            if granularity not in ("coarse", "fine"):
                return self._json({"ok": False, "error": f"invalid granularity {granularity}"}, 400)
            err = validate_action(pre_state[granularity], action, seg_index, payload)
            if err:
                return self._json({"ok": False, "error": err}, 400)

            translated = False
            if action in ("edit", "add") and "summary" in payload:
                raw = payload["summary"]
                final_summary, translated = translate.translate_and_normalize(raw)
                payload = dict(payload, summary=final_summary, summary_raw=raw) if translated else \
                    dict(payload, summary=final_summary)
            rec = append_action(file_no, entry["video_id"], reviewer, granularity, seg_index, action, payload)
            state = replay.replay_video(entry["video_path"], file_no, entry["video_id"])
            return self._json({"ok": True, "seq": rec["seq"], "translated": translated,
                                "coarse": state["coarse"], "fine": state["fine"]})

        self.send_error(404)

    def _compute_progress(self):
        data = json.load(open(ASSIGNMENT))
        entries = [e for e in data["entries"] if e["status"] != "no_data"]
        total = len(entries)
        done = sum(1 for e in entries if e["status"] == "done")
        by_reviewer = {}
        for e in entries:
            r = e.get("claimed_by")
            if not r:
                continue
            by_reviewer.setdefault(r, {"claimed": 0, "done": 0, "corrections": 0})
            by_reviewer[r]["claimed"] += 1
            if e["status"] == "done":
                by_reviewer[r]["done"] += 1
            by_reviewer[r]["corrections"] += correction_count(e["file_no"], e["video_id"])
        return {"total": total, "done": done, "unclaimed": sum(1 for e in entries if e["status"] == "unclaimed"),
                "in_progress": sum(1 for e in entries if e["status"] == "in_progress"),
                "by_reviewer": by_reviewer}


class Server(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    global VIDEO_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8910)
    ap.add_argument("--video-dir", default=DEFAULT_VIDEO_DIR,
                     help="Directory containing the keep-set mp4s (default: $EGOPROACTIVE_VIDEO_DIR or ../../videos)")
    args = ap.parse_args()
    VIDEO_DIR = Path(args.video_dir)
    if not VIDEO_DIR.is_dir():
        print(f"WARNING: --video-dir {VIDEO_DIR} does not exist -- videos will fail to load until this is fixed")
    with Server(("0.0.0.0", args.port), Handler) as httpd:
        print(f"Workbench serving at http://0.0.0.0:{args.port}/  (assignment: {ASSIGNMENT}, videos: {VIDEO_DIR})")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
