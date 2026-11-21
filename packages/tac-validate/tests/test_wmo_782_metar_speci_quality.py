"""WMO-No. 782 METAR/SPECI quality rules (group order, solidus, CAVOK, VRB)."""

from __future__ import annotations

from tac_validate import lint
from tac_validate.issue_registry import by_code


def _codes(report) -> set[str]:
    return {i.code for i in report.issues}


def test_group_order_error_when_wind_before_station_time() -> None:
    """Wrong identification/wind order is an error under WMO 782."""
    assert by_code("ODD_FIELD_ORDER").severity == "error"
    tac = "METAR 31015KT KJFK 211025Z 10SM FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert report.ok is False
    assert "ODD_FIELD_ORDER" in _codes(report)
    assert any(i.code == "ODD_FIELD_ORDER" and i.severity == "error" for i in report.issues)


def test_solidus_missing_digits_warning_for_non_auto() -> None:
    tac = "METAR KJFK 211025Z ///05KT 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "MISSING_MANDATORY_DIGIT_AS_SOLIDUS" in _codes(report)
    assert by_code("MISSING_MANDATORY_DIGIT_AS_SOLIDUS").severity == "warning"
    assert any(i.code == "MISSING_MANDATORY_DIGIT_AS_SOLIDUS" and i.severity == "warning" for i in report.issues)


def test_solidus_missing_digits_not_required_as_warning_for_auto() -> None:
    tac = "METAR KJFK 211025Z AUTO ///05KT 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "MISSING_MANDATORY_DIGIT_AS_SOLIDUS" not in _codes(report)


def test_cavok_with_significant_weather_warns() -> None:
    tac = "METAR KJFK 211025Z 18005KT CAVOK +RA 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "CAVOK_CONDITIONS_NOT_MET" in _codes(report)
    assert by_code("CAVOK_CONDITIONS_NOT_MET").severity == "warning"


def test_cavok_with_cloud_layer_warns() -> None:
    tac = "METAR KJFK 211025Z 18005KT CAVOK FEW005 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "CAVOK_CONDITIONS_NOT_MET" in _codes(report)


def test_cavok_alone_stays_info_presence() -> None:
    tac = "METAR KJFK 211025Z 18005KT CAVOK 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "CAVOK_CONDITIONS_NOT_MET" not in _codes(report)
    assert "CAVOK_PRESENT" in _codes(report)


def test_vrb_with_direction_variation_group_errors() -> None:
    """VRB and a directed V-group together violate WMO 782 special cases."""
    tac = "METAR KJFK 211025Z VRB15KT 280V350 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert report.ok is False
    assert "WIND_VRB_MISUSE" in _codes(report)
    assert by_code("WIND_VRB_MISUSE").severity == "error"


def test_vrb_light_wind_allowed() -> None:
    tac = "METAR KJFK 211025Z VRB02KT 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "WIND_VRB_MISUSE" not in _codes(report)


def test_hurricane_force_metar_wind_warns() -> None:
    tac = "METAR KJFK 211025Z 24070KT 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "WIND_PHYSICAL_RANGE" in _codes(report)
    assert by_code("WIND_PHYSICAL_RANGE").severity == "warning"


def test_excessive_gust_spread_warns() -> None:
    tac = "METAR KJFK 211025Z 18010G55KT 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "WIND_PHYSICAL_RANGE" in _codes(report)


def test_non_auto_missing_visibility_still_errors() -> None:
    """Non-AUTO without VVVV or CAVOK remains a missing-visibility error."""
    tac = "METAR KJFK 211025Z 18005KT FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert report.ok is False
    assert "MISSING_VISIBILITY" in _codes(report)


def test_auto_visibility_solidus_warns() -> None:
    tac = "METAR KJFK 211025Z AUTO //// FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "AUTO_VISIBILITY_NOT_OBSERVABLE" in _codes(report)
    assert by_code("AUTO_VISIBILITY_NOT_OBSERVABLE").severity == "warning"


def test_visibility_off_reporting_scale_warns() -> None:
    tac = "METAR KJFK 211025Z 18005KT 1234 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "VISIBILITY_SCALE_STEP" in _codes(report)


def test_directional_visibility_bad_shape_warns() -> None:
    tac = "METAR KJFK 211025Z 18005KT 2000 100SW FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "DIRECTIONAL_VISIBILITY_FORMAT" in _codes(report)


def test_auto_before_time_errors() -> None:
    tac = "METAR KJFK AUTO 211025Z 18005KT 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert report.ok is False
    assert "AUTO_MISPLACED" in _codes(report)


def test_cor_after_cccc_errors() -> None:
    tac = "METAR KJFK COR 211025Z 18005KT 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert report.ok is False
    assert "COR_MISPLACED" in _codes(report)


def test_nil_auto_conflict_errors() -> None:
    tac = "METAR KJFK 211025Z NIL AUTO="
    report = lint(tac, product="METAR")
    assert report.ok is False
    assert "NIL_AUTO_CONFLICT" in _codes(report)


def test_valid_first_groups_do_not_emit_format_warning() -> None:
    tac = "METAR KJFK 211025Z 18005KT 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "FIRST_GROUPS_FORMAT" not in _codes(report)
    assert "AUTO_MISPLACED" not in _codes(report)
    assert "COR_MISPLACED" not in _codes(report)
