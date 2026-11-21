"""WMO-No. 782: option to omit national RMK from IWXXM conversion."""

from __future__ import annotations

from tac2iwxxm import convert


def test_include_national_remarks_false_excludes_rmk_on_iwxxm_us() -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK AO2 WND DATA ESTMD="
    kept = convert(tac, product="METAR", profile="iwxxm_us", include_national_remarks=True)
    omitted = convert(tac, product="METAR", profile="iwxxm_us", include_national_remarks=False)
    assert kept.ok
    assert omitted.ok
    assert "REMARKS_EXCLUDED" not in {i.code for i in kept.issues}
    assert "REMARKS_EXCLUDED" in {i.code for i in omitted.issues}
    assert "WND DATA ESTMD" in (kept.xml or "")
    assert "WND DATA ESTMD" not in (omitted.xml or "")
