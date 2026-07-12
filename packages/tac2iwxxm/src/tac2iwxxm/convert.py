"""Public ``convert()`` entrypoint (F6.a METAR/SPECI annex3)."""

from __future__ import annotations

from tac2iwxxm.models import ConvertIssue, ConvertResult
from tac2iwxxm.products.metar_speci import parse_metar_speci
from tac2iwxxm.profiles.annex3 import emit_metar_speci_annex3

_SUPPORTED_PRODUCTS = frozenset({"METAR", "SPECI"})
_SUPPORTED_PROFILES = frozenset({"annex3"})


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
        Product id (``METAR`` or ``SPECI`` in this milestone).
    profile :
        ``annex3`` (default) or ``iwxxm_us`` (US path lands in T4.10+).
    iwxxm_version :
        Target IWXXM release line.

    Returns
    -------
    ConvertResult
        Structured result with XML, IR, and issues.

    Raises
    ------
    ConvertError
        Not raised for decode failures — those return ``ok=False``. Raised only for
        programmer misuse that cannot be represented as a result (reserved).
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

    try:
        ir = parse_metar_speci(tac, product=product_u)
        xml = emit_metar_speci_annex3(ir, product=product_u, iwxxm_version=iwxxm_version)
    except ValueError as exc:
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
                )
            ],
        )

    return ConvertResult(
        ok=True,
        product=product_u,
        profile=profile_l,
        iwxxm_version=iwxxm_version,
        xml=xml,
        ir=ir,
        issues=[],
    )


__all__ = ["ConvertError", "convert"]
