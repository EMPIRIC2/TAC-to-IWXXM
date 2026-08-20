"""IWXXM validation catalog rows for GET /lint-issue-catalog (EV-061 / #1014).

Static operator-facing descriptions of F2 validation layers / common issue codes.
Operator ``source_url`` values are verified landings from
``D-S071-links-resolve`` (2026-08-18 crawl).
"""

from __future__ import annotations

from typing import Any

# Crawl date for verified landings (session catalog-link-crawl-2026-08-18).
_LAST_VERIFIED = "2026-08-18"

_WMO_IM = "https://github.com/wmo-im/iwxxm"
_RELEASE_NOTES = "https://github.com/wmo-im/iwxxm/blob/master/IWXXM/ReleaseNotes-IWXXM.txt"
_CODES_GUIDE = "https://codes.wmo.int/ui/resources/WMO-Codes-Registry_user-guide-v1.0.pdf"
_IWXXM_US = "https://nws.weather.gov/schemas/iwxxm-us/3.0/"


def iwxxm_validation_catalog_rows() -> list[dict[str, Any]]:
    """
    Return IWXXM validation catalog entries (``family=iwxxm``).

    Returns
    -------
    list[dict[str, Any]]
        Rows ready to merge into the lint-issue-catalog response.
    """
    return [
        {
            "code": "XML_WELLFORMED",
            "severity": "error",
            "message_template": "IWXXM document must be well-formed XML",
            "product": None,
            "tags": ["xml", "wellformed", "iwxxm"],
            "family": "iwxxm",
            "source_id": "wmo-im-iwxxm",
            "source_url": _WMO_IM,
            "source_attribution": f"wmo-im-iwxxm — {_WMO_IM}",
            "source_type": "tier1",
            "status": "verified",
            "semantic_identifier": None,
            "last_verified": _LAST_VERIFIED,
            "replacement_url": None,
        },
        {
            "code": "XML_SCHEMA",
            "severity": "error",
            "message_template": ("IWXXM document must validate against the pinned XSD schema"),
            "product": None,
            "tags": ["xsd", "schema", "iwxxm"],
            "family": "iwxxm",
            "source_id": "wmo-im-iwxxm",
            "source_url": _WMO_IM,
            "source_attribution": f"wmo-im-iwxxm — {_WMO_IM}",
            "source_type": "tier1",
            "status": "verified",
            "semantic_identifier": None,
            "last_verified": _LAST_VERIFIED,
            "replacement_url": None,
        },
        {
            "code": "SCHEMATRON",
            "severity": "error",
            "message_template": (
                "IWXXM document must satisfy Schematron business rules for the selected IWXXM version"
            ),
            "product": None,
            "tags": ["schematron", "iwxxm"],
            "family": "iwxxm",
            "source_id": "wmo-im-iwxxm",
            "source_url": _RELEASE_NOTES,
            "source_attribution": f"wmo-im-iwxxm — {_RELEASE_NOTES}",
            "source_type": "tier1",
            "status": "verified",
            "semantic_identifier": None,
            "last_verified": _LAST_VERIFIED,
            "replacement_url": None,
        },
        {
            "code": "GML_REFERENCES",
            "severity": "error",
            "message_template": ("GML identifiers and xlink references in the IWXXM document must resolve"),
            "product": None,
            "tags": ["gml", "iwxxm"],
            "family": "iwxxm",
            "source_id": "wmo-im-iwxxm",
            "source_url": _WMO_IM,
            "source_attribution": f"wmo-im-iwxxm — {_WMO_IM}",
            "source_type": "tier1",
            "status": "verified",
            "semantic_identifier": None,
            "last_verified": _LAST_VERIFIED,
            "replacement_url": None,
        },
        {
            "code": "WMO_CODELISTS",
            "severity": "warning",
            "message_template": ("Coded values should resolve against WMO Codes Registry entries"),
            "product": None,
            "tags": ["codelist", "iwxxm"],
            "family": "iwxxm",
            "source_id": "codes-wmo-int",
            "source_url": _CODES_GUIDE,
            "source_attribution": f"codes-wmo-int — {_CODES_GUIDE}",
            "source_type": "tier3",
            "status": "verified",
            "semantic_identifier": "https://codes.wmo.int/",
            "last_verified": _LAST_VERIFIED,
            "replacement_url": None,
        },
        {
            "code": "IWXXM_US_EXTENSION",
            "severity": "error",
            "message_template": ("United States IWXXM profile validation uses the NWS iwxxm-us schema catalog"),
            "product": None,
            "tags": ["iwxxm_us", "iwxxm"],
            "family": "iwxxm",
            "source_id": "nws-iwxxm-us",
            "source_url": _IWXXM_US,
            "source_attribution": f"nws-iwxxm-us — {_IWXXM_US}",
            "source_type": "tier2",
            "status": "verified",
            "semantic_identifier": None,
            "last_verified": _LAST_VERIFIED,
            "replacement_url": None,
        },
    ]


__all__ = ["iwxxm_validation_catalog_rows"]
