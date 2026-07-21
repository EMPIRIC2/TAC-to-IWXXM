#!/usr/bin/env python3
"""Minimal HTTP dataset store for the F17 Compose wis2box harness (T3.3).

Supports GET/HEAD/PUT under ``/datasets/*`` plus ``GET /health``. Not a full
wis2box stack — MQTT + HTTP surfaces only (E14-04 / Q17 test harness).
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


class DatasetHandler(BaseHTTPRequestHandler):
    """Serve PUT/GET dataset objects from an on-disk directory."""

    storage_root: Path

    def log_message(self, fmt: str, *args: object) -> None:
        """Quiet default access logs (compose healthchecks are noisy)."""
        if self.path.startswith("/health"):
            return
        super().log_message(fmt, *args)

    def _dataset_path(self) -> Path | None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if not path.startswith("/datasets/"):
            return None
        rel = path[len("/datasets/") :]
        if not rel or ".." in Path(rel).parts:
            return None
        return self.storage_root / rel

    def do_GET(self) -> None:  # noqa: N802 — BaseHTTPRequestHandler API
        if urlparse(self.path).path == "/health":
            body = b'{"ok":true,"service":"wis2box-harness"}\n'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        target = self._dataset_path()
        if target is None:
            self.send_error(404, "not found")
            return
        if not target.is_file():
            self.send_error(404, "dataset missing")
            return
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_HEAD(self) -> None:  # noqa: N802
        if urlparse(self.path).path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            return
        target = self._dataset_path()
        if target is None or not target.is_file():
            self.send_error(404, "not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(target.stat().st_size))
        self.end_headers()

    def do_PUT(self) -> None:  # noqa: N802
        target = self._dataset_path()
        if target is None:
            self.send_error(404, "not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b""
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        self.send_response(201)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", "0")
        self.end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(
        "--storage",
        default="/var/lib/wis2box-harness/datasets",
        help="Directory for PUT/GET dataset objects",
    )
    args = parser.parse_args()
    root = Path(args.storage)
    root.mkdir(parents=True, exist_ok=True)
    DatasetHandler.storage_root = root
    server = ThreadingHTTPServer((args.host, args.port), DatasetHandler)
    print(f"[wis2box-harness] HTTP dataset store on {args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
