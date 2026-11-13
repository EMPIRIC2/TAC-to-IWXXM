"""Convert result msgspec models."""

from __future__ import annotations

from typing import Any

import msgspec


class ConvertIssue(msgspec.Struct, frozen=True):
    """
    Structured convert finding (library/CI metrics path).

    Parameters
    ----------
    severity : str
        ``error``, ``warning``, or ``info``.

    code : str
        Machine-readable issue id.

    message : str
        Human-readable description.

    location : str | None
        Optional field / token hint.

    start : int | None
        Optional inclusive character offset into the source TAC.

    end : int | None
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
    ok : bool
        ``True`` when conversion produced IWXXM without fatal parse errors.

    product : str
        Product id (e.g. ``METAR``, ``SPECI``).

    profile : str
        Internal emitter key (``annex3`` or ``iwxxm_us``).

    semantic_profile : str
        Canonical semantic id (``icao_2025`` or ``us_faa_nws``).

    deprecated_alias_used : bool
        ``True`` when a legacy alias id was supplied on input.

    iwxxm_version : str
        Target IWXXM release line.

    xml : str | None
        Serialized IWXXM document, or ``None`` on fatal failure.

    ir : dict[str, Any] | None
        Versioned intermediate representation (dict) for M-field checks.

    issues : list[ConvertIssue]
        Structured findings.

    suggested_filename : str | None
        Guideline ``A_…xml.gz`` name when the input has an abbreviated heading.
        ``None`` when there is no heading, and for the Canada datamart name.

    xml_gzip : bytes | None
        Gzip of ``xml`` when ``suggested_filename`` ends in ``.xml.gz``.
        ``None`` when the name is absent or ends in ``.xml``.
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
    suggested_filename: str | None = None
    xml_gzip: bytes | None = None


__all__ = ["ConvertIssue", "ConvertResult"]
