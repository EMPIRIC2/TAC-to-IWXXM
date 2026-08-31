"""TC-EV094 — BR_DECEA deepen (M2 / #1098).

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EV094-002]
"""

from __future__ import annotations

import json
from pathlib import Path

from tac2iwxxm import convert

BR_ROOT = Path(__file__).resolve().parent / "fixtures" / "profiles" / "BR_DECEA"
MANIFEST_PATH = BR_ROOT / "manifest.json"


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_ev094_br_metar_taf_attribution() -> None:
    """METAR/TAF cases carry source_url + observed_at_utc (FR-EV094-03)."""
    data = _manifest()
    assert data.get("profile") == "BR_DECEA"
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


def test_tc_ev094_br_speci_sigmet_airmet_synthetic_gap() -> None:
    """SPECI/SIGMET/AIRMET may remain labeled EV-089 synthetic until harvest."""
    data = _manifest()
    for product in ("SPECI", "SIGMET", "AIRMET"):
        case = next(c for c in data["cases"] if c["product"] == product)
        assert case.get("source_kind") == "synthetic_ev089", product
        assert not case.get("source_url"), product


def test_tc_ev094_br_gamet_parse_only_held() -> None:
    """GAMET remains parse_only and is not convertible (D-EV094-gamet)."""
    data = _manifest()
    gamet = next(c for c in data["cases"] if c["product"] == "GAMET")
    assert gamet["status"] == "parse_only"
    assert (BR_ROOT / gamet["tac"]).is_file()
    tac = (BR_ROOT / gamet["tac"]).read_text(encoding="utf-8")
    bad = convert(tac, product="GAMET", profile="BR_DECEA")
    assert not bad.ok
    assert any(i.code == "UNSUPPORTED_PRODUCT" for i in bad.issues)


def test_tc_ev094_br_active_cases_convert() -> None:
    """Active BR deepen fixtures convert under BR_DECEA."""
    data = _manifest()
    for case in data["cases"]:
        if case.get("status") == "parse_only":
            continue
        tac = (BR_ROOT / case["tac"]).read_text(encoding="utf-8")
        result = convert(tac, product=case["product"], profile="BR_DECEA")
        assert result.ok, (case["id"], result.issues)
