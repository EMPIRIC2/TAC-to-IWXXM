"""Semantic profile id registry (F35).

Canonical semantic ids map to internal emitter keys (`annex3` / `iwxxm_us`).
Wire aliases `annex3` / `iwxxm_us` were removed after 2026-10-31
([#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025)); callers use
`ICAO_2025` / `US_FAA_NWS` (and other canonical ids).
"""

from __future__ import annotations

from dataclasses import dataclass

CANONICAL_ICAO_2025 = "icao_2025"
CANONICAL_US_FAA_NWS = "us_faa_nws"
CANONICAL_US_MILITARY = "us_military"
CANONICAL_LATAM_TAF = "latam_taf"
CANONICAL_CA_ECCC = "ca_eccc"
CANONICAL_AU_BOM = "au_bom"
CANONICAL_NZ_CAA_MET = "nz_caa_met"
CANONICAL_UK_METOFFICE = "uk_metoffice"
CANONICAL_BR_DECEA = "br_decea"
CANONICAL_KR_KMA = "kr_kma"
CANONICAL_JP_JMA = "jp_jma"
CANONICAL_IN_IMD = "in_imd"
CANONICAL_HK_HKO = "hk_hko"
CANONICAL_US_NWS_CONVECTIVE_SIGMET = "us_nws_convective_sigmet"
CANONICAL_US_NWS_G_AIRMET = "us_nws_g_airmet"
CANONICAL_US_NWS_VONA = "us_nws_vona"
CANONICAL_CA_MSC_SIGMET = "ca_msc_sigmet"

EMIT_ANNEX3 = "annex3"
EMIT_IWXXM_US = "iwxxm_us"
EMIT_US_MILITARY = "us_military"
EMIT_LATAM_TAF = "latam_taf"
EMIT_CA_ECCC = "ca_eccc"
EMIT_AU_BOM = "au_bom"
EMIT_NZ_CAA_MET = "nz_caa_met"
EMIT_UK_METOFFICE = "uk_metoffice"
EMIT_BR_DECEA = "br_decea"
EMIT_KR_KMA = "kr_kma"
EMIT_JP_JMA = "jp_jma"
EMIT_IN_IMD = "in_imd"
EMIT_HK_HKO = "hk_hko"
EMIT_US_NWS_CONVECTIVE_SIGMET = "us_nws_convective_sigmet"
EMIT_US_NWS_G_AIRMET = "us_nws_g_airmet"
EMIT_US_NWS_VONA = "us_nws_vona"
EMIT_CA_MSC_SIGMET = "ca_msc_sigmet"

# Wire aliases annex3 / iwxxm_us removed after 2026-10-31 (#1025).
# Internal emit keys remain for plugin dispatch via _CANONICAL_TO_EMIT values.
_REMOVED_WIRE_ALIASES: frozenset[str] = frozenset({EMIT_ANNEX3, EMIT_IWXXM_US})

_CANONICAL_TO_EMIT: dict[str, str] = {
    CANONICAL_ICAO_2025: EMIT_ANNEX3,
    CANONICAL_US_FAA_NWS: EMIT_IWXXM_US,
    CANONICAL_US_MILITARY: EMIT_US_MILITARY,
    CANONICAL_LATAM_TAF: EMIT_LATAM_TAF,
    CANONICAL_CA_ECCC: EMIT_CA_ECCC,
    CANONICAL_AU_BOM: EMIT_AU_BOM,
    CANONICAL_NZ_CAA_MET: EMIT_NZ_CAA_MET,
    CANONICAL_UK_METOFFICE: EMIT_UK_METOFFICE,
    CANONICAL_BR_DECEA: EMIT_BR_DECEA,
    CANONICAL_KR_KMA: EMIT_KR_KMA,
    CANONICAL_JP_JMA: EMIT_JP_JMA,
    CANONICAL_IN_IMD: EMIT_IN_IMD,
    CANONICAL_HK_HKO: EMIT_HK_HKO,
    CANONICAL_US_NWS_CONVECTIVE_SIGMET: EMIT_US_NWS_CONVECTIVE_SIGMET,
    CANONICAL_US_NWS_G_AIRMET: EMIT_US_NWS_G_AIRMET,
    CANONICAL_US_NWS_VONA: EMIT_US_NWS_VONA,
    CANONICAL_CA_MSC_SIGMET: EMIT_CA_MSC_SIGMET,
}

_KNOWN_WIRE_IDS: frozenset[str] = frozenset(_CANONICAL_TO_EMIT)
_GENERAL_IWXXM_VERSIONS = frozenset({"2025-2", "2023-1"})
_PROFILE_SCOPED_IWXXM_VERSIONS: dict[str, frozenset[str]] = {
    EMIT_CA_ECCC: frozenset({"3.0.0"}),
    EMIT_CA_MSC_SIGMET: frozenset({"3.0.0"}),
}
_PROFILE_REPORT_VARIANTS: dict[str, dict[str, frozenset[str]]] = {
    EMIT_CA_ECCC: {
        "METAR": frozenset({"METAR", "LWIS", "SAWR"}),
        "SPECI": frozenset({"SPECI"}),
    }
}

# FR-019..022 / M1: product HTTP / first-party library / inspector ship ICAO only.
# Full registry above remains for emit-package unit suites until a later delete.
_SHIPPED_PRODUCT_CANONICAL: frozenset[str] = frozenset({CANONICAL_ICAO_2025})


@dataclass(frozen=True, slots=True)
class ResolvedSemanticProfile:
    """
    Resolved semantic profile with canonical id and internal emit key.

    Attributes
    ----------
    canonical : str
        Canonical.
    emit_key : str
        Emit key.
    alias_used : bool
        Alias used.
    """

    canonical: str
    emit_key: str
    alias_used: bool


def normalize_profile_id(profile: str) -> str:
    """
    Normalize a wire or library profile id for lookup.

    Parameters
    ----------
    profile : str
        Profile id (e.g. ``ICAO_2025``).

    Returns
    -------
    str
        Lowercase id with hyphens as underscores.
    """
    return profile.strip().lower().replace("-", "_")


def resolve_semantic_profile(profile: str) -> ResolvedSemanticProfile | None:
    """
    Resolve a semantic profile id to canonical + emitter key.

    Parameters
    ----------
    profile : str
        Canonical semantic id (for example ``ICAO_2025``). Former wire
        aliases ``annex3`` / ``iwxxm_us`` are rejected (#1025).

    Returns
    -------
    ResolvedSemanticProfile | None
        ``None`` when the id is unknown or a removed wire alias.
    """
    norm = normalize_profile_id(profile)
    if norm in _REMOVED_WIRE_ALIASES:
        return None
    if norm in _CANONICAL_TO_EMIT:
        return ResolvedSemanticProfile(
            canonical=norm,
            emit_key=_CANONICAL_TO_EMIT[norm],
            alias_used=False,
        )
    return None


def known_semantic_profile_ids() -> frozenset[str]:
    """
    Return all accepted semantic profile wire ids (canonical only).

    Returns
    -------
    frozenset[str]
        All accepted semantic profile wire ids (canonical only; no aliases).
    """
    return _KNOWN_WIRE_IDS


def is_shipped_product_semantic_profile(profile: str) -> bool:
    """
    Return whether a profile is on the product convert/UI ship list (M1).

    Emit-package unit suites may still resolve other registry ids via
    ``resolve_semantic_profile``; product HTTP and first-party library seeds
    use this gate.

    Parameters
    ----------
    profile : str
        Semantic profile id (for example ``ICAO_2025``).

    Returns
    -------
    bool
        ``True`` when the resolved canonical id is on the product ship list.
    """
    resolved = resolve_semantic_profile(profile)
    if resolved is None:
        return False
    return resolved.canonical in _SHIPPED_PRODUCT_CANONICAL


def shipped_product_semantic_wire_ids() -> tuple[str, ...]:
    """
    Return uppercase OpenAPI ids shipped on the product surface (ICAO only).

    Returns
    -------
    tuple[str, ...]
        Sorted OpenAPI-style wire ids such as ``ICAO_2025``.
    """
    return tuple(sorted(key.upper() for key in _SHIPPED_PRODUCT_CANONICAL))


def canonical_semantic_profile_wire_ids() -> tuple[str, ...]:
    """
    Return sorted uppercase OpenAPI-style canonical semantic profile ids.

    Returns
    -------
    tuple[str, ...]
        Ids such as ``ICAO_2025`` (no legacy aliases).
    """
    return tuple(sorted(key.upper() for key in _CANONICAL_TO_EMIT))


def supported_iwxxm_versions_for_profile(profile: str) -> frozenset[str]:
    """
    Return the supported IWXXM lines for a semantic profile id or emit key.

    Parameters
    ----------
    profile : str
        Semantic profile id.

    Returns
    -------
    frozenset[str]
        The supported IWXXM lines for a semantic profile id or emit key.
    """
    resolved = resolve_semantic_profile(profile)
    emit_key = resolved.emit_key if resolved is not None else normalize_profile_id(profile)
    return _PROFILE_SCOPED_IWXXM_VERSIONS.get(emit_key, _GENERAL_IWXXM_VERSIONS)


def supported_report_variants_for_profile(profile: str, product: str) -> frozenset[str]:
    """
    Return allowed report-variant ids for a semantic profile + API product.

    Parameters
    ----------
    profile : str
        Semantic profile id.

    product : str
        Product name.

    Returns
    -------
    frozenset[str]
        Allowed report-variant ids for a semantic profile + API product.
    """
    resolved = resolve_semantic_profile(profile)
    emit_key = resolved.emit_key if resolved is not None else normalize_profile_id(profile)
    product_u = product.strip().upper()
    by_product = _PROFILE_REPORT_VARIANTS.get(emit_key, {})
    return by_product.get(product_u, frozenset())


__all__ = [
    "CANONICAL_AU_BOM",
    "CANONICAL_BR_DECEA",
    "CANONICAL_CA_ECCC",
    "CANONICAL_CA_MSC_SIGMET",
    "CANONICAL_HK_HKO",
    "CANONICAL_ICAO_2025",
    "CANONICAL_IN_IMD",
    "CANONICAL_JP_JMA",
    "CANONICAL_KR_KMA",
    "CANONICAL_LATAM_TAF",
    "CANONICAL_NZ_CAA_MET",
    "CANONICAL_UK_METOFFICE",
    "CANONICAL_US_FAA_NWS",
    "CANONICAL_US_MILITARY",
    "CANONICAL_US_NWS_CONVECTIVE_SIGMET",
    "CANONICAL_US_NWS_G_AIRMET",
    "CANONICAL_US_NWS_VONA",
    "EMIT_ANNEX3",
    "EMIT_AU_BOM",
    "EMIT_BR_DECEA",
    "EMIT_CA_ECCC",
    "EMIT_CA_MSC_SIGMET",
    "EMIT_HK_HKO",
    "EMIT_IN_IMD",
    "EMIT_IWXXM_US",
    "EMIT_JP_JMA",
    "EMIT_KR_KMA",
    "EMIT_LATAM_TAF",
    "EMIT_NZ_CAA_MET",
    "EMIT_UK_METOFFICE",
    "EMIT_US_MILITARY",
    "EMIT_US_NWS_CONVECTIVE_SIGMET",
    "EMIT_US_NWS_G_AIRMET",
    "EMIT_US_NWS_VONA",
    "ResolvedSemanticProfile",
    "canonical_semantic_profile_wire_ids",
    "is_shipped_product_semantic_profile",
    "known_semantic_profile_ids",
    "normalize_profile_id",
    "resolve_semantic_profile",
    "shipped_product_semantic_wire_ids",
    "supported_iwxxm_versions_for_profile",
    "supported_report_variants_for_profile",
]
