"""Product plugins for tac2iwxxm.

Parsers live in ``tac2iwxxm.slot_builders`` after EV-pack-fill-delete-gate.
This package keeps FIR geometry helpers and re-exports parsers for compatibility.
"""

from __future__ import annotations

from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci
from tac2iwxxm.slot_builders.sigmet_airmet import parse_airmet, parse_sigmet
from tac2iwxxm.slot_builders.swxa import parse_swxa
from tac2iwxxm.slot_builders.taf import parse_taf
from tac2iwxxm.slot_builders.vaa_tca import parse_tca, parse_vaa
from tac2iwxxm.slot_builders.vona import parse_vona

__all__ = [
    "parse_airmet",
    "parse_metar_speci",
    "parse_sigmet",
    "parse_swxa",
    "parse_taf",
    "parse_tca",
    "parse_vaa",
    "parse_vona",
]
