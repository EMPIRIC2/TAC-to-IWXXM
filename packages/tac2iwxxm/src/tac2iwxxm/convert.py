"""Public ``convert()`` entrypoint (F6 seven products annex3 + iwxxm_us METAR/SPECI)."""

from __future__ import annotations

import re
from typing import Any, Callable, cast

from tac2iwxxm.models import ConvertIssue, ConvertResult
from tac2iwxxm.products.metar_speci import parse_metar_speci
from tac2iwxxm.products.sigmet_airmet import parse_airmet, parse_sigmet
from tac2iwxxm.products.taf import parse_taf
from tac2iwxxm.products.vaa_tca import parse_tca, parse_vaa
from tac2iwxxm.profiles.annex3 import emit_metar_speci_annex3
from tac2iwxxm.profiles.annex3_products import (
    emit_airmet_annex3,
    emit_sigmet_annex3,
    emit_taf_annex3,
    emit_tca_annex3,
    emit_vaa_annex3,
)
from tac2iwxxm.profiles.iwxxm_us import (
    emit_airmet_iwxxm_us,
    emit_metar_speci_iwxxm_us,
    emit_sigmet_iwxxm_us,
    emit_taf_iwxxm_us,
)

_SUPPORTED_PRODUCTS = frozenset({"METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA"})
_SUPPORTED_PROFILES = frozenset({"annex3", "iwxxm_us"})
_US_PRODUCTS = frozenset({"METAR", "SPECI", "TAF", "SIGMET", "AIRMET"})

# Map MALFORMED_REMARKS message needles → token regexes for editor spans (S011 T2.2).
_REMARK_SPAN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("malformed AO", re.compile(r"\bAO(?![12]\b)\w*\b")),
    ("malformed SLP", re.compile(r"\bSLP(?!\d{3}\b)\w*\b")),
    ("malformed PK WND", re.compile(r"\bPK\s+WND\b")),
)


def _content_bounds(tac: str) -> tuple[int, int]:
    """Return inclusive start / exclusive end of stripped TAC content in ``tac``."""
    stripped = tac.strip()
    if not stripped:
        return 0, len(tac)
    leading = len(tac) - len(tac.lstrip())
    return leading, leading + len(stripped)


def _remark_span(tac: str, message: str) -> tuple[int | None, int | None]:
    """Best-effort character span for a US REMARKS diagnostic message."""
    for needle, pattern in _REMARK_SPAN_PATTERNS:
        if needle in message:
            match = pattern.search(tac)
            if match is not None:
                return match.start(), match.end()
    return None, None


class ConvertError(ValueError):
    """
    Fatal conversion failure.

    Parameters
    ----------
    message :
        Human-readable description.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


def _parse(product: str, tac: str) -> dict[str, Any]:
    parsers: dict[str, Callable[..., dict[str, Any]]] = {
        "METAR": parse_metar_speci,
        "SPECI": parse_metar_speci,
        "TAF": parse_taf,
        "SIGMET": parse_sigmet,
        "AIRMET": parse_airmet,
        "VAA": parse_vaa,
        "TCA": parse_tca,
    }
    return parsers[product](tac, product=product)


def _emit(product: str, profile: str, ir: dict[str, Any], iwxxm_version: str) -> str:
    if product in {"METAR", "SPECI"}:
        if profile == "iwxxm_us":
            return emit_metar_speci_iwxxm_us(ir, product=product, iwxxm_version=iwxxm_version)
        return emit_metar_speci_annex3(ir, product=product, iwxxm_version=iwxxm_version)
    if product == "TAF":
        if profile == "iwxxm_us":
            return emit_taf_iwxxm_us(ir, iwxxm_version=iwxxm_version)
        return emit_taf_annex3(ir, iwxxm_version=iwxxm_version)
    if product == "SIGMET":
        if profile == "iwxxm_us":
            return emit_sigmet_iwxxm_us(ir, iwxxm_version=iwxxm_version)
        return emit_sigmet_annex3(ir, iwxxm_version=iwxxm_version)
    if product == "AIRMET":
        if profile == "iwxxm_us":
            return emit_airmet_iwxxm_us(ir, iwxxm_version=iwxxm_version)
        return emit_airmet_annex3(ir, iwxxm_version=iwxxm_version)
    if product == "VAA":
        return emit_vaa_annex3(ir, iwxxm_version=iwxxm_version)
    if product == "TCA":
        return emit_tca_annex3(ir, iwxxm_version=iwxxm_version)
    raise ValueError(f"no emitter for product {product!r}")


def convert(
    tac: str,
    *,
    product: str,
    profile: str = "annex3",
    iwxxm_version: str = "2025-2",
) -> ConvertResult:
    """
    Convert a TAC report to IWXXM XML.

    Parameters
    ----------
    tac :
        TAC text (single report or bulletin containing one report).
    product :
        One of the seven F6 products.
    profile :
        ``annex3`` (default) or ``iwxxm_us`` (METAR/SPECI US extensions; others T5.4–T5.5).
    iwxxm_version :
        Target IWXXM release line.

    Returns
    -------
    ConvertResult
        Structured result with XML, IR, and issues.
    """
    product_u = product.upper()
    profile_l = profile.lower()

    if product_u not in _SUPPORTED_PRODUCTS:
        return ConvertResult(
            ok=False,
            product=product_u,
            profile=profile_l,
            iwxxm_version=iwxxm_version,
            issues=[
                ConvertIssue(
                    severity="error",
                    code="UNSUPPORTED_PRODUCT",
                    message=f"product {product_u!r} not supported yet",
                )
            ],
        )
    if profile_l not in _SUPPORTED_PROFILES:
        return ConvertResult(
            ok=False,
            product=product_u,
            profile=profile_l,
            iwxxm_version=iwxxm_version,
            issues=[
                ConvertIssue(
                    severity="error",
                    code="UNSUPPORTED_PROFILE",
                    message=f"profile {profile_l!r} not supported yet",
                )
            ],
        )
    if profile_l == "iwxxm_us" and product_u not in _US_PRODUCTS:
        return ConvertResult(
            ok=False,
            product=product_u,
            profile=profile_l,
            iwxxm_version=iwxxm_version,
            issues=[
                ConvertIssue(
                    severity="error",
                    code="UNSUPPORTED_PROFILE",
                    message=f"profile iwxxm_us not supported yet for product {product_u!r}",
                )
            ],
        )

    try:
        ir = _parse(product_u, tac)
        xml = _emit(product_u, profile_l, ir, iwxxm_version)
    except ValueError as exc:
        span_start, span_end = _content_bounds(tac)
        return ConvertResult(
            ok=False,
            product=product_u,
            profile=profile_l,
            iwxxm_version=iwxxm_version,
            issues=[
                ConvertIssue(
                    severity="error",
                    code="PARSE_ERROR",
                    message=str(exc),
                    start=span_start,
                    end=span_end,
                )
            ],
        )

    issues: list[ConvertIssue] = []
    if profile_l == "iwxxm_us":
        raw_remarks: object = ir.get("remark_issues")
        if isinstance(raw_remarks, list):
            for item in cast(list[object], raw_remarks):
                message = str(item)
                remark_start, remark_end = _remark_span(tac, message)
                issues.append(
                    ConvertIssue(
                        severity="warning",
                        code="MALFORMED_REMARKS",
                        message=message,
                        location="remarks",
                        start=remark_start,
                        end=remark_end,
                    )
                )

    return ConvertResult(
        ok=True,
        product=product_u,
        profile=profile_l,
        iwxxm_version=iwxxm_version,
        xml=xml,
        ir=ir,
        issues=issues,
    )


__all__ = ["ConvertError", "convert"]
