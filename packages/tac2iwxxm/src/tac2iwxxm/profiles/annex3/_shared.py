"""Annex-3 profile XML writer for METAR/SPECI (F6.a / F20 S3 / F25 W1-W2)."""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.
from typing import Any, cast
from xml.sax.saxutils import escape

NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
    "3.0.0": "http://icao.int/iwxxm/3.0",
}

CLOUD_HREF = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/{amt}"

CLOUD_TYPE_HREF = "http://codes.wmo.int/49-2/SigConvectiveCloudType/{ctype}"

WX_HREF = "http://codes.wmo.int/306/4678/{code}"

NIL_MISSING = "http://codes.wmo.int/common/nil/missing"

NIL_NOSIG = "http://codes.wmo.int/common/nil/noSignificantChange"

NIL_NSC = "http://codes.wmo.int/common/nil/nothingOfOperationalSignificance"

NIL_NCD = "http://codes.wmo.int/common/nil/notDetectedByAutoSystem"

NIL_NOT_OBS = "http://codes.wmo.int/common/nil/notObservable"

NIL_WITHHELD = "http://codes.wmo.int/common/nil/withheld"

_YUDO_NAME = "DONLON/INTERNATIONAL"

_YUDO_POS = "12.34 -12.34"

_YUDO_ELEV_M = "12"
