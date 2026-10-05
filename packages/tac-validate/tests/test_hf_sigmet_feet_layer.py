"""A feet-to-flight-level SIGMET layer is not a single altitude."""

from __future__ import annotations

from tac_validate.api import lint

_TAC = """WSPSZ1 NZKL 050806
NZZO SIGMET 2 VALID 050811/051211 NZKL-
NZZO AUCKLAND OCEANIC FIR SEV TURB FCST WI S7520
W14200 - S7728 W13100 - S7700 W14410 - S7520 W14200
9000FT/FL290 MOV
S 20KT INTSF="""


def test_feet_flight_level_layer_is_not_a_single_altitude() -> None:
    report = lint(_TAC, product="SIGMET")
    assert "SINGLE_ALTITUDE" not in [issue.code for issue in report.issues]
