"""Package-owned Dissemination rule-catalog rows.

Operator trust metadata for ``GET /rule-catalogs?family=dissemination``.
Wire ids carry the readable summary. Lowercase registry ids are aliases.
"""

from __future__ import annotations

from typing import Any

from dissemination.exchange_registry import known_exchange_profile_ids, normalize_exchange_id_key

_OPMET_URL = (
    "https://www.icao.int/sites/default/files/METP/Documents/"
    "Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf"
)
_OPMET_LABEL = "OPMET IWXXM Exchange Guidelines (5th Ed.)"

# Canonical key → public source and operator copy. No planning ids.
_META: dict[str, dict[str, str]] = {
    "global_afs": {
        "wire_id": "GLOBAL_AFS",
        "summary": (
            "Global AFS exchange profile for COLLECT bulletins and FTBP filenames "
            "under the ICAO OPMET IWXXM exchange guidelines. Regional exchange "
            "profiles share this baseline."
        ),
        "source_url": _OPMET_URL,
        "source_attribution": _OPMET_LABEL,
        "conform_note": "Baseline COLLECT and AFS exchange used by the regional profiles.",
    },
    "apac_robex": {
        "wire_id": "APAC_ROBEX",
        "summary": (
            "Asia and Pacific ROBEX exchange profile for regional OPMET bulletin "
            "exchange. It uses the global AFS COLLECT baseline together with the "
            "APAC ROBEX handbook."
        ),
        "source_url": (
            "https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2026-02-APAC-ROBEX-HB-19TH-ED.pdf"
        ),
        "source_attribution": "APAC ROBEX Handbook (19th Ed.)",
        "conform_note": "Regional ROBEX conventions on top of the global AFS COLLECT baseline.",
    },
    "eur_rodex": {
        "wire_id": "EUR_RODEX",
        "summary": (
            "European RODEX exchange profile for regional OPMET data management. "
            "It uses the global AFS COLLECT baseline together with the EUR OPMET handbook."
        ),
        "source_url": (
            "https://www.icao.int/sites/default/files/EURNAT/Documents/EUR%20and%20Nat%20Docs/"
            "EUR%20Documents/EUR%20Documents/018%20-%20OPMET%20Handbook/"
            "EUR-Doc-18-EN-Edition-15-Amd-0.pdf"
        ),
        "source_attribution": "EUR OPMET Data Management Handbook (EUR Doc 018)",
        "conform_note": "Regional RODEX guidance on top of the global AFS COLLECT baseline.",
    },
    "afi": {
        "wire_id": "AFI",
        "summary": (
            "Africa-Indian Ocean exchange profile for regional IWXXM exchange. "
            "It uses the global AFS COLLECT baseline together with the AFI IWXXM "
            "implementation guideline."
        ),
        "source_url": (
            "https://www.icao.int/sites/default/files/sp-files/ESAF/Documents/"
            "AFI%20IWXXM%20Guideline%20Documents/"
            "AFI%20IWXXM%20Implementation%20Guideline%20Doc%20Ed.1_2020.pdf"
        ),
        "source_attribution": "AFI IWXXM Implementation Guideline (Ed. 1)",
        "conform_note": "Regional AFI guidance on top of the global AFS COLLECT baseline.",
    },
    "car_sam": {
        "wire_id": "CAR_SAM",
        "summary": (
            "Caribbean and South American exchange profile for regional OPMET exchange. "
            "It uses the global AFS COLLECT baseline. A region-specific handbook is not applied."
        ),
        "source_url": _OPMET_URL,
        "source_attribution": _OPMET_LABEL,
        "conform_note": "Uses the global AFS COLLECT baseline until a regional handbook is applied.",
    },
}


def catalog_entries() -> list[dict[str, Any]]:
    """
    Export exchange profiles as Dissemination catalog rows.

    Returns
    -------
    list[dict[str, Any]]
        Items with ``id``, ``title``, ``summary``, ``tags``, ``issue_type=profile``,
        and public source metadata.

    Raises
    ------
    KeyError
        When a registered exchange id has no catalog metadata.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (catalog_entries)
    2
    """
    items: list[dict[str, Any]] = []
    for pid in sorted(known_exchange_profile_ids()):
        key = normalize_exchange_id_key(pid)
        meta = _META.get(key)
        if meta is None:
            raise KeyError(pid)
        wire_id = meta["wire_id"]
        alias = pid != wire_id
        tags = ["dissemination", "exchange"]
        if alias:
            tags.append("alias")
            summary = f"Lowercase registry id for the {wire_id} exchange profile. Prefer {wire_id} for new work."
            conform = f"Alias of {wire_id}."
        else:
            summary = meta["summary"]
            conform = meta["conform_note"]
        items.append(
            {
                "id": pid,
                "title": pid,
                "summary": summary,
                "tags": tags,
                "issue_type": "profile",
                "severity": None,
                "source_url": meta["source_url"],
                "source_attribution": meta["source_attribution"],
                "source_access": "public",
                "source_locator": None,
                "conform_note": conform,
            }
        )
    return items
