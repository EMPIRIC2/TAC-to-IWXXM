"""TC-F6-001 / TC-F6-002: annex3 product-matrix fixtures (F6.c–f / T5.1–T5.3).

Spec: docs/test-plan.md TC-F6-001, TC-F6-002; docs/feature-list.md F6 (7 products);
docs/user-journeys.md UJ-005 / UJ-006.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac_validate.products import PRODUCTS

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "product_matrix"
MANIFEST_PATH = FIXTURES / "manifest.json"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"
# F6 convert matrix stays at 7; SWXA encode is TC-F28; VONA encode is TC-F32 (M2 T2.5+ soft path).
EXPECTED_PRODUCTS = frozenset(PRODUCTS) - {"SWXA", "VONA"}

_CASE_IDS = (
    "airmet_basic",
    "metar_basic",
    "sigmet_basic",
    "speci_basic",
    "taf_basic",
    "tca_basic",
    "vaa_basic",
)


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(f"missing product-matrix manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def matrix_manifest() -> dict:
    return _load_manifest()


def test_product_matrix_manifest_covers_seven_products(matrix_manifest: dict) -> None:
    assert matrix_manifest.get("schema_version") == 1
    assert matrix_manifest.get("profile") == PROFILE
    cases = matrix_manifest.get("cases", [])
    products = {c["product"] for c in cases}
    assert products == EXPECTED_PRODUCTS, f"missing products: {EXPECTED_PRODUCTS - products}"
    assert len(cases) == 7
    for case in cases:
        tac_path = FIXTURES / case["tac"]
        assert tac_path.is_file(), f"missing TAC fixture for {case['id']}: {tac_path}"
        text = tac_path.read_text(encoding="utf-8").strip()
        assert text, f"empty TAC fixture for {case['id']}"


@pytest.mark.parametrize("case_id", list(_CASE_IDS))
def test_tc_f6_002_convert_product_matrix_annex3(case_id: str, matrix_manifest: dict) -> None:
    """All seven annex3 product-matrix cases convert (TC-F6-002)."""
    from tac2iwxxm import convert

    case = next(c for c in matrix_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    product = case["product"]

    result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )

    assert result.ok is True, f"convert failed for {case_id}/{product}: {result.issues!r}"
    assert result.xml, f"empty XML for {case_id}"
    assert result.product == product
    assert result.profile == PROFILE
    assert result.iwxxm_version == IWXXM_VERSION
    assert "UNSUPPORTED_PRODUCT" not in {i.code for i in result.issues}
