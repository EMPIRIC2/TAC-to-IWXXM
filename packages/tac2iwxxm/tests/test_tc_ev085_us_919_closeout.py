"""TC-EV085 - US_FAA_NWS #919 closeout (EV-085 M20-M22).

[Corpus: product §F36] [Corpus: tests] [Corpus: domain-profiles §US_FAA_NWS]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from tac2iwxxm.geometry.reference_point import UnknownVOR
from tac2iwxxm.products.sigmet_airmet import parse_sigmet
from tac_validate import lint
from tac_validate.profiles import PROFILE_ANNEX3, PROFILE_IWXXM_US

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "US_FAA_NWS"
MANIFEST_PATH = FIXTURES / "manifest.json"
CATALOG_PATH = Path(__file__).resolve().parents[3] / "docs" / "domain" / "profiles" / "catalog.yaml"
PROFILE = "US_FAA_NWS"


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(f"missing US_FAA_NWS manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def us_manifest() -> dict:
    return _load_manifest()


def test_tc_ev085_001_manifest_valid_cases_complete(us_manifest: dict) -> None:
    """M20 - every valid manifest row has tac, golden, and rule_id on disk."""
    cases = us_manifest.get("cases", [])
    assert len(cases) >= 28
    for case in cases:
        assert case.get("rule_id"), f"missing rule_id on {case.get('id')}"
        tac = FIXTURES / case["tac"]
        golden = FIXTURES / case["golden"]
        assert tac.is_file(), f"missing tac for {case['id']}: {tac}"
        assert golden.is_file(), f"missing golden for {case['id']}: {golden}"


def test_tc_ev085_002_manifest_negative_cases(us_manifest: dict) -> None:
    """M20 - negative_cases registered with lint or parse expectations."""
    negatives = us_manifest.get("negative_cases", [])
    assert len(negatives) >= 5
    ids = {c["id"] for c in negatives}
    assert {
        "sigmet_vor_unknown",
        "taf_becmg",
        "taf_tempo_over_4h",
        "swxa_satcom",
        "tca_observed_cb",
    }.issubset(ids)
    for case in negatives:
        assert (FIXTURES / case["tac"]).is_file()
        assert case.get("rule_id")


@pytest.mark.parametrize(
    ("case_id", "expected_codes"),
    [
        ("taf_becmg", {"US_TAF_BECMG_FORBIDDEN"}),
        ("taf_tempo_over_4h", {"US_TAF_TEMPO_MAX_4H"}),
        ("swxa_satcom", {"US_SWXA_SATCOM_NOT_ISSUED"}),
        ("tca_observed_cb", {"US_TCA_OBSERVED_CB_NOT_PROVIDED"}),
    ],
)
def test_tc_ev085_003_us_lint_negative_cases(
    us_manifest: dict,
    case_id: str,
    expected_codes: set[str],
) -> None:
    """M20/M22 - US profile lint negatives fire only under iwxxm_us."""
    case = next(c for c in us_manifest["negative_cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    product = case["product"]
    us_codes = {i.code for i in lint(tac, product=product, profile=PROFILE_IWXXM_US).issues}
    annex_codes = {i.code for i in lint(tac, product=product, profile=PROFILE_ANNEX3).issues}
    assert expected_codes <= us_codes
    assert expected_codes.isdisjoint(annex_codes)


def test_tc_ev085_004_sigmet_vor_unknown_parse_error(us_manifest: dict) -> None:
    """M20 - unknown VOR invalid fixture fails closed at parse."""
    case = next(c for c in us_manifest["negative_cases"] if c["id"] == "sigmet_vor_unknown")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    with pytest.raises(UnknownVOR):
        parse_sigmet(tac)


def test_tc_ev085_005_catalog_us_faa_nws_row() -> None:
    """M20 - catalog.yaml lists US_FAA_NWS #919 acceptance closed."""
    data = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    row = next(p for p in data["profiles"] if p["id"] == "US_FAA_NWS")
    assert row["implementation"]["deepen_issue"] == "#919"
    assert row["legacy_alias"] == "iwxxm_us"
    assert row.get("acceptance", {}).get("status") == "closed"
    assert row.get("acceptance", {}).get("cycle") == "EV-085"


def test_tc_ev085_006_tca_cb_nil_allowed_under_us() -> None:
    """M22 - CB NIL remains valid under iwxxm_us (info, not US error)."""
    tac = (Path(__file__).resolve().parents[2] / "tac-validate/tests/fixtures/accept/tca_t1_cb_nil.tac").read_text(
        encoding="utf-8"
    )
    codes = {i.code for i in lint(tac, product="TCA", profile=PROFILE_IWXXM_US).issues}
    assert "US_TCA_OBSERVED_CB_NOT_PROVIDED" not in codes
    assert "TCA_CB_NIL" in codes
