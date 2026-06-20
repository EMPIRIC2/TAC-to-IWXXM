"""TC-M003: GIFTs Conversion Regression — test-plan.md §TC-M003, UJ-DEV-003.

Compares live GIFTs conversion output against checked-in golden baselines using
normalized canonical XML (REQ-018).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.migration.gifts_baseline import convert_tac_bulletin_to_observation_xml

from metar_shared.xml_canonical import canonicalize_xml, compare_canonical_xml

ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = ROOT / "test-data" / "golden"
MANIFEST_PATH = GOLDEN_DIR / "manifest.json"

# Static ids — must match scripts/test-data/export_tc_m003_golden.py FIXTURE_CASES.
GOLDEN_CASE_IDS = [
    "kjfk_basic",
    "klax_basic",
    "kord_basic",
    "speci_sn",
    "metar_nil",
]


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(
            "test-data/golden/manifest.json missing — run "
            "scripts/test-data/export_tc_m003_golden.py"
        )
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def golden_manifest() -> dict:
    return _load_manifest()


@pytest.mark.migration
class TestTcM003GoldenConversionRegression:
    """Representative METAR set converts identically pre/post migration."""

    @pytest.fixture(autouse=True)
    def _require_gifts_tree(self) -> None:
        from tests.migration.gifts_baseline import resolve_gifts_root

        try:
            resolve_gifts_root()
        except FileNotFoundError:
            pytest.skip("GIFTs source not present under packages/gifts or GIFTs/")

    def test_golden_manifest_present(self, golden_manifest: dict) -> None:
        """Precondition: golden fixtures exported under test-data/golden/."""
        assert golden_manifest.get("schema_version") == 1
        cases = golden_manifest.get("cases", [])
        assert cases, "golden manifest must list at least one case"
        for case in cases:
            tac_path = GOLDEN_DIR / case["tac"]
            golden_path = GOLDEN_DIR / case["golden"]
            assert tac_path.is_file(), f"missing TAC fixture: {tac_path}"
            assert golden_path.is_file(), f"missing golden XML: {golden_path}"

    @pytest.mark.parametrize("case_id", GOLDEN_CASE_IDS)
    def test_conversion_matches_golden_baseline(
        self, case_id: str, golden_manifest: dict
    ) -> None:
        """Steps 1-2: convert fixture set; zero unexpected diffs after normalization."""
        case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
        tac = (GOLDEN_DIR / case["tac"]).read_text(encoding="utf-8").strip()
        expected_canonical = (GOLDEN_DIR / case["golden"]).read_text(
            encoding="utf-8"
        ).strip()

        actual_xml = convert_tac_bulletin_to_observation_xml(tac)
        actual_canonical = canonicalize_xml(actual_xml)

        assert actual_canonical == expected_canonical, (
            f"TC-M003 mismatch for {case_id}:\n"
            f"expected: {expected_canonical[:200]}...\n"
            f"actual:   {actual_canonical[:200]}..."
        )

    def test_canonical_comparison_is_order_insensitive(self) -> None:
        """Normalized comparison ignores element order (REQ-018)."""
        xml_a = "<root><b>2</b><a>1</a></root>"
        xml_b = "<root><a>1</a><b>2</b></root>"
        assert compare_canonical_xml(xml_a, xml_b)
