"""TC-F15-006: the MKJP sample keeps nil visibility with reason notObservable."""

from __future__ import annotations

from tac2iwxxm import convert

_MKJP = "METAR MKJP 072300Z 12012KT //// ////// 30/26 Q1013 RMK CLD FROM CEILOMETER RWY 30 NCD="
_NOT_OBSERVABLE = "http://codes.wmo.int/common/nil/notObservable"


def test_mkjp_unobserved_visibility_stays_not_observable() -> None:
    result = convert(_MKJP, product="METAR", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert f'<iwxxm:visibility xsi:nil="true" nilReason="{_NOT_OBSERVABLE}"/>' in result.xml
