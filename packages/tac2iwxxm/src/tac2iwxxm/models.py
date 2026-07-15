"""msgspec models for bulletin split and convert results (F6 / ADR-016)."""

from __future__ import annotations

from typing import Any

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


class ConvertIssue(msgspec.Struct, frozen=True):
    """
    Structured convert finding (library/CI metrics path).

    Parameters
    ----------
    severity :
        ``error``, ``warning``, or ``info``.
    code :
        Machine-readable issue id.
    message :
        Human-readable description.
    location :
        Optional field / token hint.
    start :
        Optional inclusive character offset into the source TAC.
    end :
        Optional exclusive character offset into the source TAC.
    """

    severity: str
    code: str
    message: str
    location: str | None = None
    start: int | None = None
    end: int | None = None


class ConvertResult(msgspec.Struct, frozen=True):
    """
    Result of :func:`tac2iwxxm.convert`.

    Parameters
    ----------
    ok :
        ``True`` when conversion produced IWXXM without fatal parse errors.
    product :
        Product id (e.g. ``METAR``, ``SPECI``).
    profile :
        ``annex3`` or ``iwxxm_us``.
    iwxxm_version :
        Target IWXXM release line.
    xml :
        Serialized IWXXM document, or ``None`` on fatal failure.
    ir :
        Versioned intermediate representation (dict) for M-field checks.
    issues :
        Structured findings.
    """

    ok: bool
    product: str
    profile: str
    iwxxm_version: str
    xml: str | None = None
    ir: dict[str, Any] | None = None
    issues: list[ConvertIssue] = msgspec.field(default_factory=list)


__all__ = [
    "BulletinMeta",
    "BulletinSplit",
    "ConvertIssue",
    "ConvertResult",
]
