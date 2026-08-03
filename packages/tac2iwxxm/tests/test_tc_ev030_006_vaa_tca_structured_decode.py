"""TC-EV030-006 / T3.2 — structured VAA/TCA field + forecast-hour decode (#820).

Major labeled fields and ``+N HR`` forecasts become segments; residual count
must drop below the T3.1 baseline.
"""

from __future__ import annotations

from pathlib import Path

from tac2iwxxm.decode import decode_tac

ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"

# T3.1 baseline residual counts — T3.2 must shrink strictly below these.
_BASELINE_VAA = 13
_BASELINE_TCA = 14


def _residual_count(product: str, stem: str) -> int:
    tac = (ANNEX3 / f"{stem}.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product=product)
    return len([r for r in result.residuals if r.text.strip()])


def test_tc_ev030_006_vaa_major_field_labels_are_segments() -> None:
    tac = (ANNEX3 / "vaa_a7_2.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product="VAA")
    blob = " | ".join(f"{s.code}::{s.explanation}" for s in result.segments).lower()
    for needle in (
        "dtg",
        "vaac",
        "volcano",
        "advisory nr",
        "obs va cld",
        "fcst va cld +6 hr",
        "fcst va cld +12 hr",
        "fcst va cld +18 hr",
        "nxt advisory",
    ):
        assert needle in blob, f"missing structured field {needle!r} in segments"


def test_tc_ev030_006_tca_major_field_labels_are_segments() -> None:
    tac = (ANNEX3 / "tca_a2_2.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product="TCA")
    blob = " | ".join(f"{s.code}::{s.explanation}" for s in result.segments).lower()
    for needle in (
        "dtg",
        "tcac",
        "advisory nr",
        "obs psn",
        "max wind",
        "fcst psn +6 hr",
        "fcst max wind +6 hr",
        "fcst psn +24 hr",
        "nxt msg",
    ):
        assert needle in blob, f"missing structured field {needle!r} in segments"


def test_tc_ev030_006_vaa_residual_count_shrinks_below_baseline() -> None:
    count = _residual_count("VAA", "vaa_a7_2")
    assert count < _BASELINE_VAA, f"VAA residuals {count} not below baseline {_BASELINE_VAA}"


def test_tc_ev030_006_tca_residual_count_shrinks_below_baseline() -> None:
    count = _residual_count("TCA", "tca_a2_2")
    assert count < _BASELINE_TCA, f"TCA residuals {count} not below baseline {_BASELINE_TCA}"


def test_tc_ev030_006_forecast_hour_explanations_name_horizon() -> None:
    tac = (ANNEX3 / "tca_a2_2.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product="TCA")
    fcst = [s for s in result.segments if "+6 hr" in s.code.lower() or "+6 hr" in s.explanation.lower()]
    assert fcst, "expected +6 HR forecast segments"
    assert any("6" in s.explanation and "hour" in s.explanation.lower() for s in fcst)
