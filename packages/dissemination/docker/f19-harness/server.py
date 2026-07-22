"""F19 mock destination harness — accepts AMHS / SWIM / AFS HTTP POSTs (local/CI only).

Not a live protocol gateway. Memory-only receipt log for BYOC mock testing.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

_LOCK = threading.Lock()
_RECEIPTS: list[dict[str, Any]] = []
_SINKS = frozenset({"amhs", "swim", "afs"})


class Handler(BaseHTTPRequestHandler):
    server_version = "F19MockHarness/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[f19-harness] {self.address_string()} - {fmt % args}")

    def _json(self, code: int, body: dict[str, Any]) -> None:
        raw = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            with _LOCK:
                counts = {s: sum(1 for r in _RECEIPTS if r["sink"] == s) for s in sorted(_SINKS)}
            self._json(200, {"status": "ok", "receipts": counts})
            return
        if path == "/receipts":
            with _LOCK:
                items = list(_RECEIPTS)
            self._json(200, {"total": len(items), "items": items[-50:]})
            return
        self._json(404, {"detail": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        parts = [p for p in path.split("/") if p]
        if len(parts) != 1 or parts[0] not in _SINKS:
            self._json(404, {"detail": "use POST /amhs|/swim|/afs"})
            return
        sink = parts[0]
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b""
        key = f"mock:{sink}:{uuid.uuid4().hex}"
        receipt = {
            "sink": sink,
            "kv_upload_key": key,
            "bytes": len(body),
            "content_type": self.headers.get("Content-Type"),
            "ts": time.time(),
        }
        with _LOCK:
            _RECEIPTS.append(receipt)
        self._json(201, {"ok": True, "kv_upload_key": key, "detail": f"mock received ({sink})"})


def main() -> None:
    host = "0.0.0.0"
    port = int(__import__("os").environ.get("F19_HARNESS_PORT", "9099"))
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"[f19-harness] listening on {host}:{port}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
