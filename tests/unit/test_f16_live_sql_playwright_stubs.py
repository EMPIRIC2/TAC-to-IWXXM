"""EV-039 - TC-F16-LIVE Playwright suite markers (contract).

Asserts the live suite file declares LIVE-001..004, is gated by F16_LIVE_SQL,
and does not mock dissemination routes (AC3).

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
    assert LIVE_SPEC.is_file(), f"missing live Playwright suite: {LIVE_SPEC}"


def test_live_sql_playwright_declares_all_tc_ids() -> None:
    text = LIVE_SPEC.read_text(encoding="utf-8")
    for tc_id in REQUIRED_TC_IDS:
        assert tc_id in text, f"live suite must declare {tc_id}"


def test_live_sql_playwright_gated_by_f16_live_sql_flag() -> None:
    text = LIVE_SPEC.read_text(encoding="utf-8")
    assert "F16_LIVE_SQL" in text
    assert re.search(r"F16_LIVE_SQL\s*===\s*['\"]1['\"]", text), (
        "live suite must skip unless F16_LIVE_SQL===1"
    )


def test_live_sql_playwright_does_not_mock_dissemination_routes() -> None:
    """AC3 - live path must not page.route preflight/send (mocked H6' stays separate)."""
    text = LIVE_SPEC.read_text(encoding="utf-8")
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


def test_live_sql_playwright_invokes_write_assert_helper() -> None:
    """T2.2/T2.3 - suite must call the Python live_write_assert helper."""
    text = LIVE_SPEC.read_text(encoding="utf-8")
    assert "dissemination.live_write_assert" in text
    assert "assertLiveDbWrite" in text or "live_write_assert" in text
