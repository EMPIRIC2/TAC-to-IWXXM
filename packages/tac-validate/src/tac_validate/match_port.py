"""Optional decode-match injection for annex3 METAR theme detectors.

Callers pass a :class:`MatchPort` into ``lint``. Omitting it leaves today's TAC
scan in place, including ``/lint-tac``. An empty port is a supplied port: annex3
METAR theme packs then emit ``MISSING_DECODE_MATCH``. ``tac-validate`` does not
import ``tac-decoding``.
"""

from __future__ import annotations

import contextvars
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, cast


@dataclass(frozen=True, slots=True)
class DecodeMatch:
    """One decode span a caller may hand to theme detectors."""

    start: int
    end: int


class MatchPort(Protocol):
    """Source of decode spans. Implemented by apps; not by ``tac-decoding`` here."""

    def matches(self) -> Sequence[DecodeMatch]:
        """Return decode spans for the current report. Empty means none were found."""
        ...


match_port_spans: contextvars.ContextVar[tuple[DecodeMatch, ...] | None] = contextvars.ContextVar(
    "match_port_spans",
    default=None,
)


def spans_from_port(port: MatchPort | Sequence[DecodeMatch] | None) -> tuple[DecodeMatch, ...] | None:
    """Normalize a port, a span sequence, or omission (``None``)."""
    if port is None:
        return None
    if isinstance(port, tuple | list):
        return tuple(port)
    return tuple(cast(MatchPort, port).matches())


__all__ = ["DecodeMatch", "MatchPort", "match_port_spans", "spans_from_port"]
