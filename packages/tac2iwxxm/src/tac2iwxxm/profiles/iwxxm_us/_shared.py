"""IWXXM-US profile XML writer for METAR/SPECI (F6.b).

Emits WMO annex3 body plus ``iwxxm-us`` extension blocks (Addendum, AerodromePeakWind,
AerodromeWindShift, AerodromeVariableRVR) per ADR-013 / docs/context/general-tac-iwxxm-converter.md.
"""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.
from typing import Any, cast
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3 import NS, build_observation_and_trends, obs_timestamp

_US_NS = 'xmlns:iwxxm-us="http://www.weather.gov/iwxxm-us/3.0"'
