"""msgspec models for WMO AHL bulletin split (F6.bulletin / ADR-016)."""

from __future__ import annotations

import msgspec


class BulletinMeta(msgspec.Struct, frozen=True):
    """
    Parsed WMO abbreviated-header (AHL) metadata.

    Parameters
    ----------
    ahl :
        Full AHL line (e.g. ``SAUS31 KZNY 121200``).
    report_count :
        Number of TAC reports extracted from the bulletin body.
    tt :
        T1T2 designator (e.g. ``SA``, ``SP``).
    aa :
        Geographical designator (e.g. ``US``).
    cccc :
        Originating centre CCCC.
    yygggg :
        Day-hour-minute group (YYGGgg).
    bbb :
        Optional BBB amendment indicator (e.g. ``CCA``).
    """

    ahl: str
    report_count: int
    tt: str
    aa: str
    cccc: str
    yygggg: str
    bbb: str | None = None


class BulletinSplit(msgspec.Struct, frozen=True):
    """
    Result of :func:`tac2iwxxm.split_bulletin`.

    Parameters
    ----------
    meta :
        Parsed AHL metadata including ``report_count``.
    reports :
        Ordered TAC report strings (each typically ending with ``=``).
    """

    meta: BulletinMeta
    reports: list[str]


__all__ = ["BulletinMeta", "BulletinSplit"]
