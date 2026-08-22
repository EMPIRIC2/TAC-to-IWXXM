"""TC-EV064-003 branch coverage for ca_eccc lint overlays."""

from __future__ import annotations

import pytest

from tac_validate import lint


def test_ca_eccc_rejects_unsupported_product() -> None:
    with pytest.raises(ValueError, match="ca_eccc is not applicable"):
        lint("SIGMET TEST", product="SIGMET", profile="ca_eccc")


def test_ca_manobs_p_prefix_visibility_and_remarks() -> None:
    tac = "METAR CYUL 231800Z 24010KT P6SM A3012 RMK SLP123="
    report = lint(tac, product="METAR", profile="ca_eccc")
    codes = {issue.code for issue in report.issues}
    assert "CA_STATUTE_MILE_VIS" in codes
    assert "CA_ALTIMETER_INHG" in codes
    assert "CA_REMARK_MANOBS" in codes


def test_ca_manair_taf_sm_visibility_and_nclws() -> None:
    tac = "TAF CYUL 231800Z 2319/2418 24010KT 3SM WS020/24040KT 9999 FEW240="
    report = lint(tac, product="TAF", profile="ca_eccc")
    codes = {issue.code for issue in report.issues}
    assert "CA_TAF_NCLWS" in codes
    assert "CA_STATUTE_MILE_VIS" in codes


def test_ca_gfa_airmet_chart_remark() -> None:
    tac = (
        "CZUL AIRMET 1 VALID 231200/231800 CZUL-\n"
        "CZUL FIR FRQ TCU ISOL TS OBS N OF N50 TOP FL350 MOV E 20KT WKN=\n"
        "RMK GFACN34\n"
    )
    report = lint(tac, product="AIRMET", profile="ca_eccc")
    codes = {issue.code for issue in report.issues}
    assert "CA_AIRMET_GFA" in codes
