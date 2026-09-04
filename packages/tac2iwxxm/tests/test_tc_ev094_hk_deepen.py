"""TC-EV094 — HK_HKO deepen (M6 / #1098).

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EV094-002]
"""

from __future__ import annotations

import json
from pathlib import Path

from tac2iwxxm import convert

HK_ROOT = Path(__file__).resolve().parent / "fixtures" / "profiles" / "HK_HKO"
MANIFEST_PATH = HK_ROOT / "manifest.json"


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_ev094_hk_metar_taf_attribution() -> None:
    """METAR/TAF cases carry source_url + observed_at_utc (FR-EV094-03)."""
    data = _manifest()
    assert data.get("profile") == "HK_HKO"
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


def test_tc_ev094_hk_taf_includes_tx_tn() -> None:
    """HKO TAF uses full Annex extremes (TX/TN present — empty overrides)."""
    data = _manifest()
    case = next(c for c in data["cases"] if c["product"] == "TAF")
    tac = (HK_ROOT / case["tac"]).read_text(encoding="utf-8")
    assert "TX" in tac
    assert "TN" in tac


def test_tc_ev094_hk_speci_sigmet_vaa_synthetic_gap() -> None:
    """SPECI/SIGMET/VAA may remain labeled EV-089 synthetic until harvest."""
    data = _manifest()
    for product in ("SPECI", "SIGMET", "VAA"):
        case = next(c for c in data["cases"] if c["product"] == product)
        assert case.get("source_kind") == "synthetic_ev089", product
        assert not case.get("source_url"), product


def test_tc_ev094_hk_sigmet_vaa_still_on_allowlist() -> None:
    """SIGMET and VAA remain convertible under HK_HKO (D-EV094-products)."""
    data = _manifest()
    for product in ("SIGMET", "VAA"):
        case = next(c for c in data["cases"] if c["product"] == product)
        tac = (HK_ROOT / case["tac"]).read_text(encoding="utf-8")
        result = convert(tac, product=product, profile="HK_HKO")
        assert result.ok, (product, result.issues)


def test_tc_ev094_hk_active_cases_convert() -> None:
    """Active HK deepen fixtures convert under HK_HKO."""
    data = _manifest()
    for case in data["cases"]:
        if case.get("status") == "parse_only":
            continue
        tac = (HK_ROOT / case["tac"]).read_text(encoding="utf-8")
        result = convert(tac, product=case["product"], profile="HK_HKO")
        assert result.ok, (case["id"], result.issues)
