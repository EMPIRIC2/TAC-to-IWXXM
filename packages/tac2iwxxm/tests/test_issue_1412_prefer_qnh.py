"""#1412: when A and Q are both present, encode the reported QNH."""

from __future__ import annotations

from tac2iwxxm.slot_builders.metar_speci import _inhg_to_hpa, parse_metar_speci

_BOTH = "METAR MZBZ 081200Z 12010KT 9999 FEW020 28/24 A2992 Q1013="
_ALTIMETER_ONLY = "METAR MZBZ 081200Z 12010KT 9999 FEW020 28/24 A2992="
_QNH_ONLY = "METAR MZBZ 081200Z 12010KT 9999 FEW020 28/24 Q1013="


def test_both_altimeter_and_qnh_prefers_reported_hectopascals() -> None:
    both = parse_metar_speci(_BOTH, product="METAR")
    assert both["qnh_hpa"] == 1013.0

    altimeter_only = parse_metar_speci(_ALTIMETER_ONLY, product="METAR")
    converted = _inhg_to_hpa("2992")
    assert altimeter_only["qnh_hpa"] == converted
    assert converted != 1013.0

    qnh_only = parse_metar_speci(_QNH_ONLY, product="METAR")
    assert qnh_only["qnh_hpa"] == 1013.0
