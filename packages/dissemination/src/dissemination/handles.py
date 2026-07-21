"""Memory-only opaque handles for green preflight results (ADR-029 / ADR-030)."""

from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class HandleRecord:
    user_id: str
    sink_type: str
    uri: str | None
    params: dict[str, Any]
    expires_at: float


class HandleStore:
    """Process-local handle map — never persisted."""

    def __init__(self, *, ttl_seconds: float = 300.0) -> None:
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, HandleRecord] = {}
        self._lock = threading.Lock()

    def create(
        self,
        *,
        user_id: str,
        sink_type: str,
        uri: str | None,
        params: dict[str, Any] | None = None,
        now: float | None = None,
    ) -> str:
        token = secrets.token_urlsafe(24)
        ts = time.time() if now is None else now
        rec = HandleRecord(
            user_id=user_id,
            sink_type=sink_type,
            uri=uri,
            params=dict(params or {}),
            expires_at=ts + self.ttl_seconds,
        )
        with self._lock:
            self._purge(ts)
            self._items[token] = rec
        return token

    def get(
        self,
        handle: str,
        *,
        user_id: str,
        now: float | None = None,
    ) -> HandleRecord | None:
        ts = time.time() if now is None else now
        with self._lock:
            self._purge(ts)
            rec = self._items.get(handle)
            if rec is None:
                return None
            if rec.user_id != user_id:
                return None
            if rec.expires_at < ts:
                self._items.pop(handle, None)
                return None
            return rec

    def pop(self, handle: str, *, user_id: str) -> HandleRecord | None:
        with self._lock:
            rec = self._items.get(handle)
            if rec is None or rec.user_id != user_id:
                return None
            return self._items.pop(handle)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def _purge(self, now: float) -> None:
        expired = [k for k, v in self._items.items() if v.expires_at < now]
        for k in expired:
            del self._items[k]


default_handle_store = HandleStore()
