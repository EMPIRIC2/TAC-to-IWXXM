"""TC-EV094 — JP_JMA deepen (M4 / #1098).

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EV094-003]
"""

from __future__ import annotations

import json
from pathlib import Path

from tac2iwxxm import convert

JP_ROOT = Path(__file__).resolve().parent / "fixtures" / "profiles" / "JP_JMA"
MANIFEST_PATH = JP_ROOT / "manifest.json"
KR_AIRMET = (
    Path(__file__).resolve().parent / "fixtures" / "profiles" / "KR_KMA" / "AIRMET" / "valid" / "airmet_basic.tac"
)


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_ev094_jp_metar_taf_attribution() -> None:
    """METAR/TAF cases carry source_url + observed_at_utc (FR-EV094-03)."""
    data = _manifest()
    assert data.get("profile") == "JP_JMA"
    by_product = {c["product"]: c for c in data["cases"]}
    for product in ("METAR", "TAF"):
        case = by_product[product]
        assert case.get("source_url"), product
        assert case["source_url"].startswith("https://"), product
        observed = case.get("observed_at_utc")
        assert observed, product
        assert "T" in observed, product
        assert observed.endswith("Z"), product
        assert case.get("source_kind") in ("archive", "aggregator", "official")


def test_tc_ev094_jp_speci_allowlist_converts() -> None:
    """SPECI is on JP_JMA convert allowlist and fixture converts (TC-EV094-003)."""
    data = _manifest()
    case = next(c for c in data["cases"] if c["product"] == "SPECI")
    tac = (JP_ROOT / case["tac"]).read_text(encoding="utf-8")
    result = convert(tac, product="SPECI", profile="JP_JMA")
    assert result.ok, result.issues


def test_tc_ev094_jp_airmet_still_excluded() -> None:
    """AIRMET remains unsupported for JP_JMA (D-EV089-jp-va)."""
    tac = KR_AIRMET.read_text(encoding="utf-8")
    bad = convert(tac, product="AIRMET", profile="JP_JMA")
    assert not bad.ok
    assert any(i.code == "UNSUPPORTED_PROFILE" for i in bad.issues)


def test_tc_ev094_jp_sigmet_vaa_synthetic_gap() -> None:
    """SIGMET/VAA may remain labeled EV-089 synthetic until harvest."""
    data = _manifest()
    for product in ("SIGMET", "VAA"):
        case = next(c for c in data["cases"] if c["product"] == product)
        assert case.get("source_kind") == "synthetic_ev089", product
        assert not case.get("source_url"), product


def test_tc_ev094_jp_active_cases_convert() -> None:
    """Active JP deepen fixtures convert under JP_JMA."""
    data = _manifest()
    for case in data["cases"]:
        if case.get("status") == "parse_only":
            continue
        tac = (JP_ROOT / case["tac"]).read_text(encoding="utf-8")
        result = convert(tac, product=case["product"], profile="JP_JMA")
        assert result.ok, (case["id"], result.issues)
