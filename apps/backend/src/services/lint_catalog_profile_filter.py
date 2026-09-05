"""Lint-issue-catalog profile applicability helpers (EV-1120 / #1121)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

# Tag tokens on IssueSpec / IWXXM catalog rows → canonical semantic profile ids.
_TAG_TO_SEMANTIC: dict[str, str] = {
    "us_faa_nws": "us_faa_nws",
    "iwxxm_us": "us_faa_nws",
    "ca_eccc": "ca_eccc",
    "manobs": "ca_eccc",
    "manair": "ca_eccc",
}

_TAG_TO_EXCHANGE: dict[str, str] = {
    "global_afs": "GLOBAL_AFS",
    "apac_robex": "APAC_ROBEX",
    "eur_rodex": "EUR_RODEX",
    "afi": "AFI",
    "car_sam": "CAR_SAM",
}


def semantic_profiles_from_tags(tags: Sequence[str] | Iterable[str]) -> list[str]:
    """
    Derive semantic profile applicability from catalog tags.

    Empty list means shared/global (visible under every semantic filter).

    Parameters
    ----------
    tags :
        Issue or IWXXM catalog tags.

    Returns
    -------
    list[str]
        Sorted unique canonical semantic profile ids.
    """
    found: set[str] = set()
    for raw in tags:
        key = str(raw).strip().lower()
        mapped = _TAG_TO_SEMANTIC.get(key)
        if mapped:
            found.add(mapped)
    return sorted(found)


def exchange_profiles_from_tags(tags: Sequence[str] | Iterable[str]) -> list[str]:
    """
    Derive exchange profile applicability from catalog tags.

    Empty list means shared (not packaging-specific).

    Parameters
    ----------
    tags :
        Issue or IWXXM catalog tags.

    Returns
    -------
    list[str]
        Sorted unique canonical exchange profile ids.
    """
    found: set[str] = set()
    for raw in tags:
        key = str(raw).strip().lower()
        mapped = _TAG_TO_EXCHANGE.get(key)
        if mapped:
            found.add(mapped)
        # Explicit prefix form: exchange:GLOBAL_AFS
        if key.startswith("exchange:"):
            found.add(str(raw).split(":", 1)[1].strip().upper())
    return sorted(found)


def row_matches_profile(
    applicable: Sequence[str],
    *,
    selected: str,
) -> bool:
    """
    Return True when a catalog row applies to ``selected`` profile.

    Shared rows (empty applicable) always match.
    """
    if not applicable:
        return True
    return selected in applicable
