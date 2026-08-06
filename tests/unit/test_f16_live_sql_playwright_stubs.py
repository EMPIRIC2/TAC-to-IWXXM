"""EV-039 / T2.1 — TC-F16-LIVE Playwright stub markers (contract).

Asserts the live suite file declares LIVE-001..004, is gated by F16_LIVE_SQL,
and does not mock dissemination routes (AC3). Red Playwright bodies land in
``uj027-f16-live-sql.e2e.spec.ts`` until T2.2/T2.3.

[Corpus: product §F16] [Corpus: tests] TC-F16-LIVE [Corpus: tech-spec]
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE_SPEC = ROOT / "apps" / "e2e" / "uj027-f16-live-sql.e2e.spec.ts"

REQUIRED_TC_IDS = (
    "TC-F16-LIVE-001",
    "TC-F16-LIVE-002",
    "TC-F16-LIVE-003",
    "TC-F16-LIVE-004",
)


def test_live_sql_playwright_spec_exists() -> None:
    assert LIVE_SPEC.is_file(), f"missing live Playwright stub: {LIVE_SPEC}"


def test_live_sql_playwright_declares_all_tc_ids() -> None:
    text = LIVE_SPEC.read_text(encoding="utf-8")
    for tc_id in REQUIRED_TC_IDS:
        assert tc_id in text, f"live stub must declare {tc_id}"


def test_live_sql_playwright_gated_by_f16_live_sql_flag() -> None:
    text = LIVE_SPEC.read_text(encoding="utf-8")
    assert "F16_LIVE_SQL" in text
    assert re.search(r"F16_LIVE_SQL\s*===\s*['\"]1['\"]", text), (
        "live suite must skip unless F16_LIVE_SQL===1"
    )


def test_live_sql_playwright_does_not_mock_dissemination_routes() -> None:
    """AC3 — live path must not page.route preflight/send (mocked H6' stays separate)."""
    text = LIVE_SPEC.read_text(encoding="utf-8")
    # Ignore comments/docs that mention page.route; ban actual route() calls.
    code_only = "\n".join(
        line
        for line in text.splitlines()
        if not line.strip().startswith(("*", "//", "/*", "*/"))
        and not line.lstrip().startswith("*")
    )
    assert "page.route" not in code_only, "live suite must not call page.route"
    assert not re.search(
        r"page\.route\s*\(\s*['\"`].*dissemination",
        code_only,
        re.I,
    ), "must not mock /api/v1/dissemination/* in live suite"


def test_live_sql_playwright_red_stub_markers_until_t22() -> None:
    """T2.1 red phase: stubs intentionally fail until T2.2 implements the flow."""
    text = LIVE_SPEC.read_text(encoding="utf-8")
    assert "T2.2" in text or "EV-039 T2.2" in text
    # Four intentional failure markers (expect(false) or throw)
    fail_markers = len(re.findall(r"expect\(\s*false", text)) + len(
        re.findall(r"throw new Error", text)
    )
    assert fail_markers >= 4, "expected ≥4 red stub failure markers for LIVE-001..004"
