"""TC-EV-VPL-004 — R1/R3/R4/R5/R8 theme shadow then flip (#1216 M3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac_validate import lint
from tac_validate.detectors import compare_shadow, load_detector_catalog, run_theme_pack
from tac_validate.product_rules_pkg.metar_speci import _check_metar_speci
from tac_validate.theme_checks import (
    R1_CODES,
    R3_CODES,
    R4_CODES,
    R5_CODES,
    R8_CODES,
    lint_profile,
    r3_weather,
    r4_cloud,
    r8_modifiers,
    r8_nil_gate,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
_MANIFEST = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))

_THEME_PACKS = {
    "R1": ("metar-speci-r1-identity-order", R1_CODES),
    "R3": ("metar-speci-r3-weather", R3_CODES),
    "R4": ("metar-speci-r4-cloud", R4_CODES),
    "R5": ("metar-speci-r5-remarks", R5_CODES),
    "R8": ("metar-speci-r8-modifiers", R8_CODES),
}


def _read(rel: str) -> str:
    return (FIXTURES / rel).read_text(encoding="utf-8")


def _theme_cases(theme: str) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for section in _MANIFEST.values():
        if not isinstance(section, list):
            continue
        cases.extend(case for case in section if isinstance(case, dict) and case.get("theme") == theme)
    return cases


@pytest.mark.parametrize("theme", sorted(_THEME_PACKS))
def test_theme_pack_registered(theme: str) -> None:
    pack_id, _codes = _THEME_PACKS[theme]
    catalog = load_detector_catalog()
    assert pack_id in catalog


@pytest.mark.parametrize("theme", sorted(_THEME_PACKS))
def test_theme_shadow_code_span_parity(theme: str, monkeypatch: pytest.MonkeyPatch) -> None:
    pack_id, codes = _THEME_PACKS[theme]
    cases = _theme_cases(theme)
    assert cases, f"no fixtures for {theme}"
    for case in cases:
        tac = _read(str(case["tac"]))
        product = str(case["product"])
        profile = str(case.get("profile") or "annex3")
        token = lint_profile.set(profile)
        try:
            monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "legacy")
            legacy = [i for i in _check_metar_speci(tac, product, profile=profile) if i.code in codes]
            monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "detector")
            detector = [i for i in run_theme_pack(pack_id, tac, product) if i.code in codes]
            cmp = compare_shadow(legacy, detector, codes=codes)
            assert cmp.matched, (
                f"{theme}/{case['id']}: legacy={sorted(cmp.legacy_keys)} detector={sorted(cmp.detector_keys)}"
            )
        finally:
            lint_profile.reset(token)


@pytest.mark.parametrize("theme", sorted(_THEME_PACKS))
def test_theme_flip_accept_no_error_regressions(theme: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", "detector")
    accept = [c for c in _theme_cases(theme) if c.get("id") and "error" not in str(c.get("id", "")).lower()]
    accept_rows = [c for c in _MANIFEST.get("accept", []) if c.get("theme") == theme]
    rows = accept_rows or accept[:3]
    assert rows
    theme_codes = _THEME_PACKS[theme][1]
    hard = {
        "MISSING_CCCC",
        "MISSING_OBS_TIME",
        "ODD_FIELD_ORDER",
        "INVALID_WEATHER",
        "INVALID_CLOUD_TOKEN",
        "INVALID_REMARK",
        "INVALID_NIL",
        "INVALID_RVR",
        "INVALID_WIND",
    }
    for case in rows:
        report = lint(_read(str(case["tac"])), product=str(case["product"]))
        bad = [i for i in report.issues if i.code in hard & theme_codes and i.severity == "error"]
        assert not bad, f"{case['id']}: {[i.code for i in bad]}"


def test_theme_coverage_edges(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hit membership / recent-wx / NIL branches in theme_checks."""
    monkeypatch.setattr(
        "tac_validate.theme_checks.membership.is_member",
        lambda family, token, sets=None: False,
    )
    recent = r3_weather("METAR KJFK 121255Z 18008KT 10SM RERA SCT040 22/18 A2992=", "METAR")
    assert any(i.code == "UNKNOWN_WMO_MEMBERSHIP" for i in recent)

    clouds = r4_cloud("METAR KJFK 121255Z 18008KT 10SM BKN020CB 22/18 A2992=", "METAR")
    assert any(i.code == "UNKNOWN_WMO_MEMBERSHIP" for i in clouds)

    assert r8_nil_gate("METAR KJFK 121255Z NIL=", "METAR") is not None
    assert r8_nil_gate("METAR KJFK 121255Z 18008KT 10SM SCT040 22/18 A2992=", "METAR") is None
    assert r8_modifiers("METAR KJFK NIL=", "METAR") == []
