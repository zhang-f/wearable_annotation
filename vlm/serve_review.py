#!/usr/bin/env python3
"""Minimal static file server with HTTP Range support, for serving
review.html + the co-located mp4 over HTTP (needed for proper video
seeking -- plain `python -m http.server` ignores Range requests and
would force a full-file download before any seek works).

Run: python3 serve_review.py [--port 8768]
Then open http://localhost:<port>/review.html
"""
import argparse
import http.server
import mimetypes
import os
import re
import socketserver

VLM_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SERVE_DIR = os.path.join(VLM_DIR, "examples")  # matches build_review.py's default --out-dir
RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")
DIR = DEFAULT_SERVE_DIR  # overwritten by --dir in __main__


class RangeHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            path = "/review.html"
        fpath = os.path.join(DIR, path.lstrip("/"))
        if not os.path.isfile(fpath):
            self.send_error(404)
            return

        content_type = mimetypes.guess_type(fpath)[0] or "application/octet-stream"
        file_size = os.path.getsize(fpath)
        range_header = self.headers.get("Range")

        if range_header:
            m = RANGE_RE.match(range_header)
            start = int(m.group(1)) if m.group(1) else 0
            end = int(m.group(2)) if m.group(2) else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1

            self.send_response(206)
            self.send_header("Content-Type", content_type)
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
            self.send_header("Content-Type", content_type)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(file_size))
            self.end_headers()
            with open(fpath, "rb") as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8768)
    parser.add_argument("--dir", default=DEFAULT_SERVE_DIR, help=f"Directory to serve (default: {DEFAULT_SERVE_DIR})")
    args = parser.parse_args()
    DIR = os.path.abspath(args.dir)
    with Server(("127.0.0.1", args.port), RangeHandler) as httpd:
        print(f"Serving {DIR} at http://localhost:{args.port}/review.html")
        httpd.serve_forever()
