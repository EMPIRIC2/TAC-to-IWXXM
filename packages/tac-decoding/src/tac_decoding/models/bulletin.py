"""Bulletin splitter protocols (injected port).

[Corpus: product §F9]
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class _BulletinMeta(Protocol):
    """Internal bulletin metadata."""

    ahl: str
    report_count: int


class _BulletinSplit(Protocol):
    """Internal bulletin split result."""

    reports: Sequence[str]
    meta: _BulletinMeta


__all__ = ["_BulletinMeta", "_BulletinSplit"]
