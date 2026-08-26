"""Lint profile constants for annex3 vs iwxxm_us (S059 / EV-050 / AC7).

``iwxxm_us`` applicability mirrors ``tac2iwxxm.convert`` ``_US_PRODUCTS`` —
VAA/TCA/SWXA/VONA are **N/A** (not fail) for dual-profile compare.
"""

from __future__ import annotations

from typing import Final

PROFILE_ANNEX3: Final[str] = "annex3"
PROFILE_IWXXM_US: Final[str] = "iwxxm_us"
PROFILE_CA_ECCC: Final[str] = "ca_eccc"

SUPPORTED_PROFILES: Final[frozenset[str]] = frozenset({PROFILE_ANNEX3, PROFILE_IWXXM_US, PROFILE_CA_ECCC})

# Products with a defined US profile overlay (L5 REMARKS / FMH-1 / iwxxm-us encode).
IWXXM_US_PRODUCTS: Final[frozenset[str]] = frozenset({"METAR", "SPECI", "TAF", "SIGMET", "AIRMET"})

# Thin US national validation policy only (#919 M22) — no convert/dual-profile parity.
IWXXM_US_THIN_LINT_PRODUCTS: Final[frozenset[str]] = frozenset({"SWXA", "TCA"})

IWXXM_US_LINT_PRODUCTS: Final[frozenset[str]] = IWXXM_US_PRODUCTS | IWXXM_US_THIN_LINT_PRODUCTS

# Products with CA_ECCC MANOBS/MANAIR overlay (EV-064 M3/M4).
CA_ECCC_PRODUCTS: Final[frozenset[str]] = frozenset({"METAR", "SPECI", "TAF", "AIRMET"})

# Full F6 + deepen products covered by the dual-profile matrix (AC7).
F6_DUAL_PROFILE_PRODUCTS: Final[tuple[str, ...]] = (
    "METAR",
    "SPECI",
    "TAF",
    "SIGMET",
    "AIRMET",
    "VAA",
    "TCA",
    "SWXA",
    "VONA",
)


def normalize_profile(profile: str) -> str:
    """
    Return lowercased profile id.

    Raises
    ------
    ValueError
        When ``profile`` is not ``annex3`` or ``iwxxm_us``.
    """
    key = profile.strip().lower()
    if key not in SUPPORTED_PROFILES:
        raise ValueError(f"unsupported lint profile {profile!r}; expected one of {sorted(SUPPORTED_PROFILES)}")
    return key


def ca_eccc_applicable(product: str) -> bool:
    """Return True when ``profile=ca_eccc`` is defined for ``product``."""
    return product.upper() in CA_ECCC_PRODUCTS


def iwxxm_us_applicable(product: str) -> bool:
    """Return True when ``profile=iwxxm_us`` is defined for ``product``."""
    return product.upper() in IWXXM_US_PRODUCTS


def iwxxm_us_lint_applicable(product: str) -> bool:
    """Return True when ``lint(..., profile=iwxxm_us)`` is allowed for ``product``."""
    return product.upper() in IWXXM_US_LINT_PRODUCTS


__all__ = [
    "CA_ECCC_PRODUCTS",
    "F6_DUAL_PROFILE_PRODUCTS",
    "IWXXM_US_LINT_PRODUCTS",
    "IWXXM_US_PRODUCTS",
    "IWXXM_US_THIN_LINT_PRODUCTS",
    "PROFILE_ANNEX3",
    "PROFILE_CA_ECCC",
    "PROFILE_IWXXM_US",
    "SUPPORTED_PROFILES",
    "ca_eccc_applicable",
    "iwxxm_us_applicable",
    "iwxxm_us_lint_applicable",
    "normalize_profile",
]
