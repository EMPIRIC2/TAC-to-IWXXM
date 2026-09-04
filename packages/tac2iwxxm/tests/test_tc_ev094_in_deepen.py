"""TC-EV094 — IN_IMD deepen (M5 / #1098).

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EV094-002]
[Corpus: tests §TC-EV094-004]
"""

from __future__ import annotations

import json
from pathlib import Path

from tac_validate import lint

from tac2iwxxm import convert

IN_ROOT = Path(__file__).resolve().parent / "fixtures" / "profiles" / "IN_IMD"
MANIFEST_PATH = IN_ROOT / "manifest.json"


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_ev094_in_metar_taf_attribution() -> None:
    """METAR/TAF cases carry source_url + observed_at_utc (FR-EV094-03)."""
    data = _manifest()
    assert data.get("profile") == "IN_IMD"
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


def test_tc_ev094_in_speci_sigmet_synthetic_gap() -> None:
    """SPECI/SIGMET may remain labeled EV-089 synthetic until harvest."""
    data = _manifest()
    for product in ("SPECI", "SIGMET"):
        case = next(c for c in data["cases"] if c["product"] == product)
        assert case.get("source_kind") == "synthetic_ev089", product
        assert not case.get("source_url"), product


def test_tc_ev094_in_active_cases_convert() -> None:
    """Active IN deepen fixtures convert under IN_IMD."""
    data = _manifest()
    for case in data["cases"]:
        if case.get("status") == "parse_only":
            continue
        tac = (IN_ROOT / case["tac"]).read_text(encoding="utf-8")
        result = convert(tac, product=case["product"], profile="IN_IMD")
        assert result.ok, (case["id"], result.issues)


def test_tc_ev094_in_taf_fixture_lint_overlay() -> None:
    """Attributed TAF without TX/TN emits IN_TAF_TX_TN_OMITTED under in_imd."""
    data = _manifest()
    case = next(c for c in data["cases"] if c["product"] == "TAF")
    tac = (IN_ROOT / case["tac"]).read_text(encoding="utf-8")
    codes = {i.code for i in lint(tac, product="TAF", profile="in_imd").issues}
    assert "IN_TAF_TX_TN_OMITTED" in codes
    annex = {i.code for i in lint(tac, product="TAF", profile="annex3").issues}
    assert "IN_TAF_TX_TN_OMITTED" not in annex
