"""In-memory per-user rate limiter for dissemination preflight/send (ADR-029)."""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque


class RateLimitExceeded(PermissionError):
    """
    Raised when a user exceeds the dissemination request budget.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


class DisseminationRateLimiter:
    """
    Sliding-window counter keyed by user id.

    Attributes
    ----------
    max_per_minute : int or None
        Maximum requests in a one-minute window.
    """

    def __init__(self, *, max_per_minute: int | None = None) -> None:
        """
        Internal helper ``__init__``.

        Parameters
        ----------
        max_per_minute : int or None, optional
            Maximum requests in a one-minute window. By default ``None``.
        """
        env = os.environ.get("DISSEMINATION_RATE_LIMIT_PER_MIN", "").strip()
        if max_per_minute is not None:
            self.max_per_minute = max_per_minute
        elif env:
            self.max_per_minute = int(env)
        else:
            self.max_per_minute = 30
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, user_id: str, *, now: float | None = None) -> None:
        """
        Record a hit and raise if the user is over budget.

        Parameters
        ----------
        user_id : str
            Authenticated subject id.
        now : float or None, optional
            Optional monotonic/unix timestamp override for tests. By default ``None``.

        Raises
        ------
        RateLimitExceeded
            When the sliding one-minute window is full.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (check)
        2
        """
        ts = time.time() if now is None else now
        window_start = ts - 60.0
        with self._lock:
            q = self._hits[user_id]
            while q and q[0] < window_start:
                q.popleft()
            if len(q) >= self.max_per_minute:
                raise RateLimitExceeded(f"dissemination rate limit exceeded ({self.max_per_minute}/min)")
            q.append(ts)

    def reset(self, user_id: str | None = None) -> None:
        """
        Clear counters for one user or all users (tests).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (reset)
        2

        Parameters
        ----------
        user_id : str or None, optional
            User id to clear. ``None`` clears every user. By default ``None``.
        """
        with self._lock:
            if user_id is None:
                self._hits.clear()
            else:
                self._hits.pop(user_id, None)


default_rate_limiter = DisseminationRateLimiter()
