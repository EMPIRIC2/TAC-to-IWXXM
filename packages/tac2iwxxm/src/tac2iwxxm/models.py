"""msgspec models for bulletin split and convert results (F6 / ADR-016)."""

from __future__ import annotations

from typing import Any

import msgspec


class AhlParts(msgspec.Struct, frozen=True):
    """
    Parsed WMO abbreviated-header (AHL) fields with derived IWXXM helpers.

    Parameters
    ----------
    ahl :
        Full AHL line (e.g. ``SAUS31 KZNY 121200``).
    tt :
        TAC ``T1T2`` designator as parsed (e.g. ``SA``, ``FN``).
    aa :
        Geographical designator ``A1A2``.
    ii :
        Bulletin number ``ii`` (2 digits).
    cccc :
        Originating centre CCCC.
    yygggg :
        Day-hour-minute group (YYGGgg).
    bbb :
        Optional BBB indicator (``AAx`` / ``CCx`` / ``RRx``, x ∈ A…X).
    iwxxm_tt :
        Mapped IWXXM ``T1T2`` (L*).
    report_status :
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
    ii :
        Optional bulletin number ``ii`` (additive; EV-029).
    report_status :
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
        Internal emitter key (``annex3`` or ``iwxxm_us``).
    semantic_profile :
        Canonical semantic id (``icao_2025`` or ``us_faa_nws``).
    deprecated_alias_used :
        ``True`` when a legacy alias id was supplied on input.
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
    semantic_profile: str = ""
    deprecated_alias_used: bool = False
    xml: str | None = None
    ir: dict[str, Any] | None = None
    issues: list[ConvertIssue] = msgspec.field(default_factory=list)


__all__ = [
    "AhlParts",
    "BulletinMeta",
    "BulletinSplit",
    "ConvertIssue",
    "ConvertResult",
]
