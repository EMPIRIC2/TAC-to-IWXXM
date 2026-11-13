"""Bulletin / AHL msgspec models."""

from __future__ import annotations

import msgspec


class AhlParts(msgspec.Struct, frozen=True):
    """
    Parsed WMO abbreviated-header (AHL) fields with derived IWXXM helpers.

    Parameters
    ----------
    ahl : str
        Full AHL line (e.g. ``SAUS31 KZNY 121200``).

    tt : str
        TAC ``T1T2`` designator as parsed (e.g. ``SA``, ``FN``).

    aa : str
        Geographical designator ``A1A2``.

    ii : str
        Bulletin number ``ii`` (2 digits).

    cccc : str
        Originating centre CCCC.

    yygggg : str
        Day-hour-minute group (YYGGgg).

    bbb : str | None
        Optional BBB indicator (``AAx`` / ``CCx`` / ``RRx``, x ∈ A…X).

    iwxxm_tt : str
        Mapped IWXXM ``T1T2`` (L*).

    report_status : str
        ``NORMAL``, ``AMENDMENT``, or ``CORRECTION`` from BBB rules.
    """

    ahl: str
    tt: str
    aa: str
    ii: str
    cccc: str
    yygggg: str
    iwxxm_tt: str
    report_status: str
    bbb: str | None = None


class BulletinMeta(msgspec.Struct, frozen=True):
    """
    Parsed WMO abbreviated-header (AHL) metadata.

    Parameters
    ----------
    ahl : str
        Full AHL line (e.g. ``SAUS31 KZNY 121200``).

    report_count : int
        Number of TAC reports extracted from the bulletin body.

    tt : str
        T1T2 designator (e.g. ``SA``, ``SP``).

    aa : str
        Geographical designator (e.g. ``US``).

    cccc : str
        Originating centre CCCC.

    yygggg : str
        Day-hour-minute group (YYGGgg).

    bbb : str | None
        Optional BBB amendment indicator (e.g. ``CCA``).

    ii : str | None
        Optional bulletin number ``ii`` (additive; EV-029).

    report_status : str
        Derived IWXXM ``reportStatus`` from BBB (``NORMAL`` / ``AMENDMENT`` /
        ``CORRECTION``); additive EV-029 M2.
    """

    ahl: str
    report_count: int
    tt: str
    aa: str
    cccc: str
    yygggg: str
    bbb: str | None = None
    ii: str | None = None
    report_status: str = "NORMAL"


class BulletinSplit(msgspec.Struct, frozen=True):
    """
    Result of :func:`tac2iwxxm.split_bulletin`.

    Parameters
    ----------
    meta : BulletinMeta
        Parsed AHL metadata including ``report_count``.

    reports : list[str]
        Ordered TAC report strings (each typically ending with ``=``).
    """

    meta: BulletinMeta
    reports: list[str]


__all__ = ["AhlParts", "BulletinMeta", "BulletinSplit"]
