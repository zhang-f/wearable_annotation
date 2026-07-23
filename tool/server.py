#!/usr/bin/env python3
"""EgoProactive interrupt-timing annotation tool -- backend. Stdlib only,
no dependencies to install (translation optionally uses transformers/torch,
see translate_backend.py, only imported if you actually click translate).

Serves the single-page annotator UI, streams EgoProactive videos from a
local directory you point it at (with HTTP Range support -- required for
smooth scrubbing/seeking in the browser), and persists every mark/unmark/
complete/translate action immediately to disk, per annotator.

Layout (relative to this file, i.e. <repo>/tool/server.py):
  <repo>/videos/                 default video directory (see README for
                                  how to download EgoProactive videos here;
                                  override with --video-dir)
  <repo>/tool/wearable_ai_2026_egoproactive_val_700.jsonl
                                  bundled metadata (query/task/domain/
                                  duration per video) -- this is text-only,
                                  a few MB, checked into the repo directly
  <repo>/annotations/raw/<annotator_id>__<video_id>__<granularity>.json
                                  source of truth per annotator, one tiny
                                  file per unit, fully rewritten on every
                                  action -- crash-safe.
  <repo>/annotations/annotations_<annotator_id>_<date>.jsonl
                                  consolidated, regenerated in full after
                                  every action for that annotator. THIS is
                                  the file to send back when you're done.
                                  <date> is fixed the first time this file
                                  is created for that annotator_id (found
                                  via glob, not re-picked each run), so a
                                  multi-day annotation session doesn't
                                  fragment across several dated files.

Unit schema:
  {"video_id", "granularity", "annotator_id",
   "points": [{"t": float, "description_en": str}, ...],
   "completed": bool}
  Chinese input is supported in the UI (type a quick note, it's translated
  immediately) but NEVER written to disk -- only description_en persists.

annotator_id comes from the browser (localStorage, prompted on first use)
and is sent with every request; the server does not hardcode it.

Run: python3 server.py [--port 8765] [--video-dir /path/to/videos]
Then open http://localhost:8765/ in a browser.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import http.server
import json
import os
import re
import socketserver
import threading
import urllib.parse

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TOOL_DIR)

JSONL_PATH = os.path.join(TOOL_DIR, "wearable_ai_2026_egoproactive_val_700.jsonl")
DEFAULT_VIDEO_DIR = os.path.join(REPO_DIR, "videos")

ANNOTATIONS_DIR = os.path.join(REPO_DIR, "annotations")
RAW_DIR = os.path.join(ANNOTATIONS_DIR, "raw")

GRANULARITIES = ("free", "coarse", "fine")

VIDEO_DIR = DEFAULT_VIDEO_DIR  # overwritten by --video-dir in main()

os.makedirs(RAW_DIR, exist_ok=True)

_lock = threading.Lock()  # single-writer guard; this is a one-annotator-per-process tool


def _load_meta() -> dict[str, dict]:
    meta = {}
    with open(JSONL_PATH) as f:
        for line in f:
            row = json.loads(line)
            vid = row["video_path"]
            meta[vid] = {
                "video_id": vid,
                "query": row.get("query", ""),
                "task": row.get("task", ""),
                "domain": row.get("domain", ""),
                "duration_in_sec": row.get("duration_in_sec"),
            }
    return meta


_META = _load_meta()


def _safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s)


def _unit_path(annotator_id: str, video_id: str, granularity: str) -> str:
    return f"{RAW_DIR}/{_safe(annotator_id)}__{_safe(video_id)}__{granularity}.json"


def _migrate_unit(unit: dict) -> tuple[dict, bool]:
    """Historical formats this may encounter if you're resuming a raw file
    written by an earlier version of this tool:
      1. oldest: `timestamps: [float, ...]` (no points list at all)
      2. intermediate: `points: [{"t", "raw_zh", "description_en"}, ...]`
    Current format drops raw_zh entirely -- it's never persisted, only
    passed through transiently to /api/translate_point. Returns
    (unit, changed)."""
    changed = False
    if "points" not in unit:
        old_timestamps = unit.pop("timestamps", [])
        unit["points"] = [{"t": t, "description_en": ""} for t in sorted(old_timestamps)]
        changed = True
    for p in unit["points"]:
        if "raw_zh" in p:
            del p["raw_zh"]
            changed = True
    return unit, changed


def _load_unit(annotator_id: str, video_id: str, granularity: str) -> dict:
    path = _unit_path(annotator_id, video_id, granularity)
    if os.path.exists(path):
        with open(path) as f:
            unit = json.load(f)
        unit, changed = _migrate_unit(unit)
        if changed:
            _save_unit(unit)
        return unit
    return {
        "video_id": video_id,
        "granularity": granularity,
        "annotator_id": annotator_id,
        "points": [],
        "completed": False,
    }


def _migrate_all_on_startup() -> None:
    n = 0
    for fname in sorted(os.listdir(RAW_DIR)):
        if not fname.endswith(".json"):
            continue
        fpath = f"{RAW_DIR}/{fname}"
        with open(fpath) as f:
            unit = json.load(f)
        unit, changed = _migrate_unit(unit)
        if changed:
            tmp_path = fpath + ".tmp"
            with open(tmp_path, "w") as f:
                json.dump(unit, f)
            os.replace(tmp_path, fpath)
            n += 1
    if n:
        print(f"Migrated {n} old-format annotation file(s) to the current schema.")
        annotator_ids = {json.load(open(f"{RAW_DIR}/{f}"))["annotator_id"] for f in os.listdir(RAW_DIR) if f.endswith(".json")}
        for aid in annotator_ids:
            _rebuild_consolidated(aid)


def _consolidated_path(annotator_id: str) -> str:
    """Fixed once per annotator: reuse an existing dated file if one
    already exists (found via glob), otherwise mint one with today's date.
    This means a multi-day session keeps appending to the same file rather
    than fragmenting across dates."""
    existing = sorted(glob.glob(f"{ANNOTATIONS_DIR}/annotations_{_safe(annotator_id)}_*.jsonl"))
    if existing:
        return existing[0]
    today = datetime.date.today().isoformat()
    return f"{ANNOTATIONS_DIR}/annotations_{_safe(annotator_id)}_{today}.jsonl"


def _save_unit(unit: dict) -> None:
    path = _unit_path(unit["annotator_id"], unit["video_id"], unit["granularity"])
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(unit, f)
    os.replace(tmp_path, path)  # atomic on same filesystem
    _rebuild_consolidated(unit["annotator_id"])


def _rebuild_consolidated(annotator_id: str) -> None:
    prefix = f"{_safe(annotator_id)}__"
    units = []
    for fname in sorted(os.listdir(RAW_DIR)):
        if fname.startswith(prefix) and fname.endswith(".json"):
            with open(f"{RAW_DIR}/{fname}") as f:
                units.append(json.load(f))
    out_path = _consolidated_path(annotator_id)
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "w") as f:
        for u in units:
            f.write(json.dumps(u, ensure_ascii=False) + "\n")
    os.replace(tmp_path, out_path)


def _all_video_ids() -> list[str]:
    return list(_META.keys())


def _progress_matrix(annotator_id: str) -> dict[str, dict[str, dict]]:
    """video_id -> granularity -> {completed, n_marks}, scoped to one annotator."""
    prefix = f"{_safe(annotator_id)}__"
    matrix = {}
    for fname in sorted(os.listdir(RAW_DIR)):
        if not (fname.startswith(prefix) and fname.endswith(".json")):
            continue
        with open(f"{RAW_DIR}/{fname}") as f:
            u = json.load(f)
        u, _ = _migrate_unit(u)
        matrix.setdefault(u["video_id"], {})[u["granularity"]] = {
            "completed": u["completed"],
            "n_marks": len(u["points"]),
        }
    return matrix


RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep stdout quiet; this is a local pilot tool, not a production server

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw)

    def _require_annotator_id(self, source: dict) -> str | None:
        aid = str(source.get("annotator_id", "")).strip()
        if not aid:
            self._send_json({"error": "annotator_id is required"}, status=400)
            return None
        return aid

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self._serve_file(os.path.join(TOOL_DIR, "index.html"), "text/html; charset=utf-8")
        elif path == "/api/videos":
            self._send_json({"videos": list(_META.values())})
        elif path == "/api/state":
            aid = self._require_annotator_id({"annotator_id": qs.get("annotator_id", [""])[0]})
            if aid is None:
                return
            video_id = qs["video_id"][0]
            state = {g: _load_unit(aid, video_id, g) for g in GRANULARITIES}
            self._send_json({"state": state})
        elif path == "/api/progress":
            aid = self._require_annotator_id({"annotator_id": qs.get("annotator_id", [""])[0]})
            if aid is None:
                return
            self._send_json({"progress": _progress_matrix(aid), "all_video_ids": _all_video_ids()})
        elif path.startswith("/video/"):
            fname = urllib.parse.unquote(path[len("/video/"):])
            fpath = os.path.join(VIDEO_DIR, fname)
            self._serve_video(fpath)
        else:
            self.send_error(404)

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/video/"):
            fname = urllib.parse.unquote(parsed.path[len("/video/"):])
            fpath = os.path.join(VIDEO_DIR, fname)
            if not os.path.exists(fpath):
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(os.path.getsize(fpath)))
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        body = self._read_json_body()
        aid = self._require_annotator_id(body)
        if aid is None:
            return

        if path == "/api/mark":
            with _lock:
                unit = _load_unit(aid, body["video_id"], body["granularity"])
                t = round(float(body["timestamp"]), 1)
                if not any(p["t"] == t for p in unit["points"]):
                    unit["points"].append({"t": t, "description_en": ""})
                    unit["points"].sort(key=lambda p: p["t"])
                _save_unit(unit)
            self._send_json({"unit": unit})

        elif path == "/api/unmark":
            with _lock:
                unit = _load_unit(aid, body["video_id"], body["granularity"])
                t = round(float(body["timestamp"]), 1)
                unit["points"] = [p for p in unit["points"] if p["t"] != t]
                _save_unit(unit)
            self._send_json({"unit": unit})

        elif path == "/api/update_point":
            with _lock:
                unit = _load_unit(aid, body["video_id"], body["granularity"])
                t = round(float(body["t"]), 1)
                for p in unit["points"]:
                    if p["t"] == t:
                        if "description_en" in body:
                            p["description_en"] = body["description_en"]
                        break
                _save_unit(unit)
            self._send_json({"unit": unit})

        elif path == "/api/translate_point":
            with _lock:
                unit = _load_unit(aid, body["video_id"], body["granularity"])
                t = round(float(body["t"]), 1)
                raw_zh = body.get("raw_zh", "")
                try:
                    from translate_backend import translate_batch
                    en = translate_batch([raw_zh])[0] if raw_zh.strip() else ""
                except Exception as e:
                    self._send_json({"error": str(e)}, status=500)
                    return
                for p in unit["points"]:
                    if p["t"] == t:
                        p["description_en"] = en
                        break
                _save_unit(unit)
            self._send_json({"unit": unit, "description_en": en})

        elif path == "/api/complete":
            with _lock:
                unit = _load_unit(aid, body["video_id"], body["granularity"])
                unit["completed"] = bool(body["completed"])
                _save_unit(unit)
            self._send_json({"unit": unit})

        else:
            self.send_error(404)

    def _serve_file(self, path, content_type):
        if not os.path.exists(path):
            self.send_error(404)
            return
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_video(self, fpath):
        if not os.path.exists(fpath):
            self.send_error(404)
            return
        file_size = os.path.getsize(fpath)
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
                chunk = 1024 * 1024
                while remaining > 0:
                    data = f.read(min(chunk, remaining))
                    if not data:
                        break
                    self.wfile.write(data)
                    remaining -= len(data)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(file_size))
            self.end_headers()
            with open(fpath, "rb") as f:
                while True:
                    data = f.read(1024 * 1024)
                    if not data:
                        break
                    self.wfile.write(data)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True  # avoid "Address already in use" on quick restarts


def main():
    global VIDEO_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--video-dir",
        default=DEFAULT_VIDEO_DIR,
        help=f"Directory containing the downloaded egoproactive/val/*.mp4 files (default: {DEFAULT_VIDEO_DIR})",
    )
    args = parser.parse_args()
    VIDEO_DIR = os.path.abspath(args.video_dir)

    if not os.path.isdir(VIDEO_DIR):
        print(f"WARNING: video directory does not exist yet: {VIDEO_DIR}")
        print("The tool will still start, but videos won't play until you download them there.")
        print("See README.md for the download command.")

    _migrate_all_on_startup()

    with Server(("127.0.0.1", args.port), Handler) as httpd:
        print(f"Annotator running at http://localhost:{args.port}/")
        print(f"Videos: {VIDEO_DIR}")
        print(f"Output: {ANNOTATIONS_DIR}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
