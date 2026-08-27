"""Curated MSC code-ca vocabulary membership registry (EV-069 / #1033).

Offline membership checks for ``xlink:href`` values under the MSC code-ca base URL.
Codes are sourced from CA_ECCC goldens, ``tac2iwxxm`` emit paths, and mining notes -
not fetched from the network at validate time.

[Corpus: product §F2] [Corpus: product §F13] [Corpus: domain-profiles §CA_ECCC]
"""

from __future__ import annotations

CODE_CA_BASE = "https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca"

# Vocabulary directories published by MSC (see docs/domain/mining/eccc-iwxxm-ca-mining-notes.md).
KNOWN_CODE_CA_HREFS: frozenset[str] = frozenset(
    {
        f"{CODE_CA_BASE}/ObservingSystemType/AWOS",
        f"{CODE_CA_BASE}/ObservingSystemType/LWIS",
        f"{CODE_CA_BASE}/ObservingSystemType/SAWR",
        f"{CODE_CA_BASE}/PressureChangingRapidly/FALLING",
        f"{CODE_CA_BASE}/PressureChangingRapidly/RISING",
        f"{CODE_CA_BASE}/AerodromeIcing/LGT",
        f"{CODE_CA_BASE}/AerodromeIcing/MDT",
        f"{CODE_CA_BASE}/AerodromeIcing/SEV",
        f"{CODE_CA_BASE}/airmet_weather_phenomena/FRQ_TCU_ISOL_TS",
        f"{CODE_CA_BASE}/airmet_weather_phenomena/FRQ_TCU_ISOL_TSGR",
        f"{CODE_CA_BASE}/airmet_weather_phenomena/OCNL_TCU_ISOL_TS",
        f"{CODE_CA_BASE}/airmet_weather_phenomena/OCNL_TCU_ISOL_TSGR",
        f"{CODE_CA_BASE}/airmet_weather_phenomena/SFC_VIS_and_BKN_CLD",
        f"{CODE_CA_BASE}/airmet_weather_phenomena/SFC_VIS_and_OVC_CLD",
        f"{CODE_CA_BASE}/present_and_forecast_weather/IC",
    }
)


def normalize_code_ca_href(href: str) -> str:
    """Strip fragment/query and trailing slash for stable membership lookup."""
    value = href.strip()
    if "#" in value:
        value = value.split("#", 1)[0]
    if "?" in value:
        value = value.split("?", 1)[0]
    return value.rstrip("/")


def is_code_ca_href(href: str) -> bool:
    """Return True when ``href`` targets the MSC code-ca vocabulary tree."""
    return normalize_code_ca_href(href).startswith(CODE_CA_BASE)


def code_ca_membership_ok(href: str) -> bool:
    """
    Return True when ``href`` is a known MSC code-ca member URI.

    Parameters
    ----------
    href :
        ``xlink:href`` value from an IWXXM document.
    """
    return normalize_code_ca_href(href) in KNOWN_CODE_CA_HREFS


__all__ = [
    "CODE_CA_BASE",
    "KNOWN_CODE_CA_HREFS",
    "code_ca_membership_ok",
    "is_code_ca_href",
    "normalize_code_ca_href",
]
