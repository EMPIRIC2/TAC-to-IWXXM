"""Product plugins for tac2iwxxm."""

from __future__ import annotations

from tac2iwxxm.products.metar_speci import parse_metar_speci
from tac2iwxxm.products.sigmet_airmet import parse_airmet, parse_sigmet
from tac2iwxxm.products.swxa import parse_swxa
from tac2iwxxm.products.taf import parse_taf
from tac2iwxxm.products.vaa_tca import parse_tca, parse_vaa

__all__ = [
    "parse_airmet",
    "parse_metar_speci",
    "parse_sigmet",
    "parse_swxa",
    "parse_taf",
    "parse_tca",
    "parse_vaa",
]
