"""TC-EV094 — UK_METOFFICE deepen (M1 / #1098).

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EV094-002]
"""

from __future__ import annotations

import json
from pathlib import Path

from tac2iwxxm import convert

UK_ROOT = Path(__file__).resolve().parent / "fixtures" / "profiles" / "UK_METOFFICE"
MANIFEST_PATH = UK_ROOT / "manifest.json"


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_ev094_uk_metar_taf_attribution() -> None:
    """METAR/TAF cases carry source_url + observed_at_utc (FR-EV094-03)."""
    data = _manifest()
    assert data.get("profile") == "UK_METOFFICE"
    by_product = {c["product"]: c for c in data["cases"]}
    for product in ("METAR", "TAF"):
        case = by_product[product]
        assert case.get("source_url"), product
        assert case["source_url"].startswith("https://"), product
        observed = case.get("observed_at_utc")
        assert observed, product
        assert "T" in observed, product
        assert observed.endswith("Z"), product
        assert case.get("source_kind") in (None, "archive", "aggregator", "official")


def test_tc_ev094_uk_speci_synthetic_gap_labeled() -> None:
    """SPECI may remain labeled EV-089 synthetic until a real corpus is harvested."""
    data = _manifest()
    speci = next(c for c in data["cases"] if c["product"] == "SPECI")
    assert speci.get("source_kind") == "synthetic_ev089"
    assert not speci.get("source_url")


def test_tc_ev094_uk_active_cases_convert() -> None:
    """Active UK deepen fixtures convert under UK_METOFFICE."""
    data = _manifest()
    for case in data["cases"]:
        if case.get("status") == "parse_only":
            continue
        tac = (UK_ROOT / case["tac"]).read_text(encoding="utf-8")
        result = convert(tac, product=case["product"], profile="UK_METOFFICE")
        assert result.ok, (case["id"], result.issues)
