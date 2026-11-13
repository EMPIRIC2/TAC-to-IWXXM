"""CA_ECCC operational exchange-output contract (EV-071 M2 / #1032 / #1040).

MSC datamart filename pattern, WMO AHL designators, distribution path template,
and profile-gated translation centre defaults. Constants mirror
``config/profiles/catalog.yaml`` ``CA_ECCC.exchange_output``.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC]
"""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.

import os

import re

from datetime import UTC, datetime

from tac2iwxxm.bulletin import bbb_to_report_status, iwxxm_filename

from tac2iwxxm.models import AhlParts, ProfileOutputSpec

CA_ECCC_IWXXM_VERSION = "3.0.0"

CA_MSC_FILENAME_PATTERN = "A_{TTAAiiCCCCYYGGggBBB}_C_{CCC}_{YYYYMMddhhmmss}.xml"

CA_DISTRIBUTION_PATH_TEMPLATE = "https://dd.meteo.gc.ca/today/aviation/iwxxm/{product}/{issuer_code}/{HH}"

_WMO_HEADER_BY_PRODUCT: dict[str, str] = {
    "METAR": "A_LACN",
    "SPECI": "A_LPCN",
    "TAF": "A_LTCN",
    "AIRMET": "A_LWCN",
    "SIGMET": "A_LSCN",
    "VAA": "A_LUCN",
}

_SIGMET_KIND_DESIGNATOR: dict[str, str] = {
    "weather": "A_LSCN",
    "va": "A_LVCN",
    "tc": "A_LYCN",
}

_DATAMART_PRODUCT_SEGMENT: dict[str, str] = {
    "METAR": "metar",
    "SPECI": "speci",
    "TAF": "taf",
    "AIRMET": "airmet",
    "SIGMET": "sigmet",
    "VAA": "vaa",
}

_MSC_FILENAME_PARTS_RE = re.compile(
    r"^A_([A-Z]{2})([A-Z]{2})(\d{2})([A-Z]{4})(\d{6})(?:([A-Z0-9]{3}))?_C_([A-Z]{4})_(\d{14})\.xml$"
)

_MSC_FILENAME_RE = re.compile(r"^A_[A-Z]{2}[A-Z]{2}\d{2}[A-Z]{4}\d{6}(?:[A-Z0-9]{3})?_C_[A-Z]{4}_\d{14}\.xml$")
