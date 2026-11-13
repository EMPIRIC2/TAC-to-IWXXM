"""CA_ECCC profile XML writer - Canadian METAR/SPECI/TAF (IWXXM 3.0.0 + iwxxm-ca).

Encodes MANOBS surface observations and MANAIR TAF extensions on the MSC operational
line: statute-mile visibility, inch-of-mercury altimeter (via QNH), AUTO observing
systems, Canadian REMARKS in ``iwxxm-ca:Addendum``, and non-convective low-level wind
shear (NCLWS) in TAF base forecasts.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: adr/ADR-036]
"""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.

import re

from typing import Any, cast

from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3 import NS, aerodrome_block, build_observation_and_trends, obs_timestamp

from tac2iwxxm.profiles.annex3_emit import (
    emit_airmet_annex3,
    emit_sigmet_annex3,
    emit_taf_annex3,
    emit_vaa_annex3,
)

CA_IWXXM_VERSION = "3.0.0"

CA_NS = "https://dd.meteo.gc.ca/today/aviation/iwxxm/"

_CODE_CA_BASE = "https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca"

CA_OBS_AWOS = f"{_CODE_CA_BASE}/ObservingSystemType/AWOS"

CA_OBS_LWIS = f"{_CODE_CA_BASE}/ObservingSystemType/LWIS"

CA_OBS_SAWR = f"{_CODE_CA_BASE}/ObservingSystemType/SAWR"

CA_PRES_FALLING = f"{_CODE_CA_BASE}/PressureChangingRapidly/FALLING"

CA_PRES_RISING = f"{_CODE_CA_BASE}/PressureChangingRapidly/RISING"

CA_AIRMET_PHENOM_BASE = f"{_CODE_CA_BASE}/airmet_weather_phenomena"

CA_ICING_BASE = f"{_CODE_CA_BASE}/AerodromeIcing"

CA_PRESENT_FORECAST_WEATHER_BASE = f"{_CODE_CA_BASE}/present_and_forecast_weather"

CA_METAR_FAMILY_TAC_LEADS = frozenset({"METAR", "SPECI", "LWIS", "SAWR"})

CA_IWXXM_CA_SUBSTITUTION_ROOTS = frozenset({"LWIS", "SAWR"})
