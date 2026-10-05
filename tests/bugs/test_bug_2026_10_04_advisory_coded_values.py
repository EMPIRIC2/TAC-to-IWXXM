"""BUG-2026-10-04 - advisory field values stay coded in the decode.

A tropical-cyclone advisory must explain the value after the label, including
wind, movement, cloud extent, pressure, and intensity.
"""

from __future__ import annotations

from pathlib import Path

from tac_decoding.decode import decode_tac

_TCA = (
    Path(__file__).resolve().parents[2]
    / "apps/frontend/src/fixtures/examples/bodies/tca_a2_2.tac"
).read_text(encoding="utf-8")


def test_bug_2026_10_04_gloria_advisory_values_are_plain_language() -> None:
    result = decode_tac(_TCA, product="TCA")
    by_code = {segment.code: segment for segment in result.segments}
    assert _TCA[by_code["MAX WIND"].start : by_code["MAX WIND"].end] == "22MPS"
    assert by_code["MAX WIND"].explanation == "Maximum wind: 22 metres per second"
    assert by_code["MOV"].explanation == "Movement: northwest at 20 kilometres per hour"
    assert by_code["C"].explanation == "Central pressure: 965 hectopascals"
    assert by_code["INTST CHANGE"].explanation == "Intensity change: intensifying"
