"""Annex-3 profile XML writers for TAF / SIGMET / AIRMET (F6.c–d)."""

from __future__ import annotations

from tac2iwxxm.profiles.annex3_emit.airmet import emit_airmet_annex3
from tac2iwxxm.profiles.annex3_emit.sigmet import emit_convective_sigmet_annex3, emit_sigmet_annex3
from tac2iwxxm.profiles.annex3_emit.swxa import emit_swxa_annex3
from tac2iwxxm.profiles.annex3_emit.taf import emit_taf_annex3
from tac2iwxxm.profiles.annex3_emit.tca import emit_tca_annex3
from tac2iwxxm.profiles.annex3_emit.vaa import emit_vaa_annex3
from tac2iwxxm.profiles.annex3_emit.vona import emit_vona_annex3

__all__ = [
    "emit_airmet_annex3",
    "emit_convective_sigmet_annex3",
    "emit_sigmet_annex3",
    "emit_swxa_annex3",
    "emit_taf_annex3",
    "emit_tca_annex3",
    "emit_vaa_annex3",
    "emit_vona_annex3",
]
