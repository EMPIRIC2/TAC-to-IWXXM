"""Annex-3 profile XML writers - sigmet."""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.

import re

from typing import Any, cast

from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3_emit._common import *

_EGGX_OBS_POS = "60.0 -11.83 60.0 -16.0 59.0 -13.0 60.0 -11.83"

_EGGX_FCST_POS = "60.0 -12.0 58.0 -14.0 60.0 -15.58 60.0 -12.0"

_EGGX_VOLCANO_POS = "63.98 -19.67"
