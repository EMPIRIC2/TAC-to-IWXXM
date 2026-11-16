"""Canonical lint-profile id casing for catalog / sticky / QM consumers.

Catalog keys are lowercase. Quality-matrix YAML historically used UPPERCASE
leaf ids (``CA_MSC_SIGMET``, ``US_NWS_*``). Sticky collectors should casefold
through this helper so Match keys align with ``lint_profiles.yaml``.

[Corpus: product §F15] [Corpus: product §F36]
"""

from __future__ import annotations

from typing import Final

# Legacy spellings that are not a pure casefold of a catalog id.
# Conversion alias ICAO_2025 → annex3 (lint catalog root / defaults).
PROFILE_ID_ALIASES: Final[dict[str, str]] = {
    "icao_2025": "annex3",
}


def canonical_lint_profile_id(raw: str) -> str:
    """
    Return the catalog-facing lint profile id for ``raw``.

    Parameters
    ----------
    raw : str
        Profile token from YAML meta, sticky rows, or API input.

    Returns
    -------
    str
        Lowercased id (hyphens → underscores), after optional alias remap.
        Does not validate catalog membership (callers that need fail-closed
        use ``normalize_profile``).

    Examples
    --------
    >>> canonical_lint_profile_id("CA_MSC_SIGMET")
    'ca_msc_sigmet'
    >>> canonical_lint_profile_id(" iwxxm_us ")
    'iwxxm_us'
    >>> canonical_lint_profile_id("us-nws-vona")
    'us_nws_vona'
    """
    key = (raw or "").strip().lower().replace("-", "_")
    return PROFILE_ID_ALIASES.get(key, key)


__all__ = [
    "PROFILE_ID_ALIASES",
    "canonical_lint_profile_id",
]
