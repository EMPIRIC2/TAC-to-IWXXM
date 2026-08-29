"""Semantic profile id registry (F35 / ADR-036).

Canonical semantic ids map to internal emitter keys (`annex3` / `iwxxm_us`).
Legacy aliases remain accepted during the deprecation window ([#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025)).
"""

from __future__ import annotations

from dataclasses import dataclass

CANONICAL_ICAO_2025 = "icao_2025"
CANONICAL_US_FAA_NWS = "us_faa_nws"
CANONICAL_CA_ECCC = "ca_eccc"
CANONICAL_AU_BOM = "au_bom"
CANONICAL_NZ_CAA_MET = "nz_caa_met"
CANONICAL_UK_METOFFICE = "uk_metoffice"
CANONICAL_BR_DECEA = "br_decea"
CANONICAL_KR_KMA = "kr_kma"
CANONICAL_JP_JMA = "jp_jma"
CANONICAL_IN_IMD = "in_imd"
CANONICAL_HK_HKO = "hk_hko"

EMIT_ANNEX3 = "annex3"
EMIT_IWXXM_US = "iwxxm_us"
EMIT_CA_ECCC = "ca_eccc"
EMIT_AU_BOM = "au_bom"
EMIT_NZ_CAA_MET = "nz_caa_met"
EMIT_UK_METOFFICE = "uk_metoffice"
EMIT_BR_DECEA = "br_decea"
EMIT_KR_KMA = "kr_kma"
EMIT_JP_JMA = "jp_jma"
EMIT_IN_IMD = "in_imd"
EMIT_HK_HKO = "hk_hko"

_ALIAS_TO_CANONICAL: dict[str, str] = {
    EMIT_ANNEX3: CANONICAL_ICAO_2025,
    EMIT_IWXXM_US: CANONICAL_US_FAA_NWS,
}

_CANONICAL_TO_EMIT: dict[str, str] = {
    CANONICAL_ICAO_2025: EMIT_ANNEX3,
    CANONICAL_US_FAA_NWS: EMIT_IWXXM_US,
    CANONICAL_CA_ECCC: EMIT_CA_ECCC,
    CANONICAL_AU_BOM: EMIT_AU_BOM,
    CANONICAL_NZ_CAA_MET: EMIT_NZ_CAA_MET,
    CANONICAL_UK_METOFFICE: EMIT_UK_METOFFICE,
    CANONICAL_BR_DECEA: EMIT_BR_DECEA,
    CANONICAL_KR_KMA: EMIT_KR_KMA,
    CANONICAL_JP_JMA: EMIT_JP_JMA,
    CANONICAL_IN_IMD: EMIT_IN_IMD,
    CANONICAL_HK_HKO: EMIT_HK_HKO,
}

_KNOWN_WIRE_IDS: frozenset[str] = frozenset(_ALIAS_TO_CANONICAL) | frozenset(_CANONICAL_TO_EMIT)


@dataclass(frozen=True, slots=True)
class ResolvedSemanticProfile:
    """Resolved semantic profile with canonical id and internal emit key."""

    canonical: str
    emit_key: str
    alias_used: bool


def normalize_profile_id(profile: str) -> str:
    """
    Normalize a wire or library profile id for lookup.

    Parameters
    ----------
    profile :
        Profile id (e.g. ``ICAO_2025``, ``annex3``).

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
    profile :
        Canonical id or legacy alias.

    Returns
    -------
    ResolvedSemanticProfile | None
        ``None`` when the id is unknown.
    """
    norm = normalize_profile_id(profile)
    if norm in _ALIAS_TO_CANONICAL:
        canonical = _ALIAS_TO_CANONICAL[norm]
        return ResolvedSemanticProfile(
            canonical=canonical,
            emit_key=_CANONICAL_TO_EMIT[canonical],
            alias_used=True,
        )
    if norm in _CANONICAL_TO_EMIT:
        return ResolvedSemanticProfile(
            canonical=norm,
            emit_key=_CANONICAL_TO_EMIT[norm],
            alias_used=False,
        )
    return None


def known_semantic_profile_ids() -> frozenset[str]:
    """Return all accepted semantic profile wire ids (canonical + aliases)."""
    return _KNOWN_WIRE_IDS


__all__ = [
    "CANONICAL_AU_BOM",
    "CANONICAL_BR_DECEA",
    "CANONICAL_CA_ECCC",
    "CANONICAL_HK_HKO",
    "CANONICAL_ICAO_2025",
    "CANONICAL_IN_IMD",
    "CANONICAL_JP_JMA",
    "CANONICAL_KR_KMA",
    "CANONICAL_NZ_CAA_MET",
    "CANONICAL_UK_METOFFICE",
    "CANONICAL_US_FAA_NWS",
    "EMIT_ANNEX3",
    "EMIT_AU_BOM",
    "EMIT_BR_DECEA",
    "EMIT_CA_ECCC",
    "EMIT_HK_HKO",
    "EMIT_IN_IMD",
    "EMIT_IWXXM_US",
    "EMIT_JP_JMA",
    "EMIT_KR_KMA",
    "EMIT_NZ_CAA_MET",
    "EMIT_UK_METOFFICE",
    "ResolvedSemanticProfile",
    "known_semantic_profile_ids",
    "normalize_profile_id",
    "resolve_semantic_profile",
]
