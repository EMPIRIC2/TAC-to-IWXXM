"""TC-EV094 — KR_KMA deepen (M3 / #1098).

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EV094-003]
"""

from __future__ import annotations

import json
from pathlib import Path

from tac2iwxxm import convert

KR_ROOT = Path(__file__).resolve().parent / "fixtures" / "profiles" / "KR_KMA"
MANIFEST_PATH = KR_ROOT / "manifest.json"


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_ev094_kr_metar_taf_attribution() -> None:
    """METAR/TAF cases carry source_url + observed_at_utc (FR-EV094-03)."""
    data = _manifest()
    assert data.get("profile") == "KR_KMA"
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


def test_tc_ev094_kr_speci_allowlist_converts() -> None:
    """SPECI is on KR_KMA convert allowlist and fixture converts (TC-EV094-003)."""
    data = _manifest()
    case = next(c for c in data["cases"] if c["product"] == "SPECI")
    tac = (KR_ROOT / case["tac"]).read_text(encoding="utf-8")
    result = convert(tac, product="SPECI", profile="KR_KMA")
    assert result.ok, result.issues


def test_tc_ev094_kr_sigmet_airmet_synthetic_gap() -> None:
    """SIGMET/AIRMET may remain labeled EV-089 synthetic until harvest."""
    data = _manifest()
    for product in ("SIGMET", "AIRMET"):
        case = next(c for c in data["cases"] if c["product"] == product)
        assert case.get("source_kind") == "synthetic_ev089", product
        assert not case.get("source_url"), product


def test_tc_ev094_kr_active_cases_convert() -> None:
    """Active KR deepen fixtures convert under KR_KMA."""
    data = _manifest()
    for case in data["cases"]:
        if case.get("status") == "parse_only":
            continue
        tac = (KR_ROOT / case["tac"]).read_text(encoding="utf-8")
        result = convert(tac, product=case["product"], profile="KR_KMA")
        assert result.ok, (case["id"], result.issues)
