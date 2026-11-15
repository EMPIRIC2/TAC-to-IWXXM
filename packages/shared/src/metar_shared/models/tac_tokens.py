"""Typed TAC token fragments shared across packages [Corpus: system-spec]."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StationIcao:
    """
    Letter-first ICAO location indicator (CCCC).

    Digits are allowed in positions 2-4 (US METAR e.g. ``K10U``).

    Parameters
    ----------
    code : str
        Four-character upper-case station id.
    """

    code: str

    def __post_init__(self) -> None:
        """Normalize and validate station code."""
        raw = self.code.strip().upper()
        if len(raw) != 4 or not raw[0].isalpha() or not raw.isalnum():
            msg = f"invalid station ICAO: {self.code!r}"
            raise ValueError(msg)
        object.__setattr__(self, "code", raw)


@dataclass(frozen=True, slots=True)
class AhlHeadingParts:
    """
    WMO abbreviated heading line parts (TTAAii CCCC YYGGgg [BBB]).

    Parameters
    ----------
    ttaaii : str
        Data type designator + geographical designator + number (6 chars).
    cccc : str
        Issuing centre ICAO.
    yygggg : str
        Day-hour-minute group (6 digits).
    bbb : str or None
        Optional BBB correction/delay/amendment group.
    """

    ttaaii: str
    cccc: str
    yygggg: str
    bbb: str | None = None

    def __post_init__(self) -> None:
        """Normalize AHL heading parts."""
        object.__setattr__(self, "ttaaii", self.ttaaii.strip().upper())
        object.__setattr__(self, "cccc", self.cccc.strip().upper())
        object.__setattr__(self, "yygggg", self.yygggg.strip())
        if self.bbb is not None:
            object.__setattr__(self, "bbb", self.bbb.strip().upper() or None)
