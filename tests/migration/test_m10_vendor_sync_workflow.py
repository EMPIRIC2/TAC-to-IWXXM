"""M10 vendor sync workflow — T10.3, M6, ADR-001."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VENDOR_SYNC_WORKFLOW = ROOT / ".github" / "workflows" / "vendor-sync.yml"


@pytest.mark.migration
class TestM10VendorSyncWorkflow:
    """Weekly Action syncs wmo-im iwxxm-* only; GIFTs stays manual."""

    @pytest.fixture
    def workflow_text(self) -> str:
        return VENDOR_SYNC_WORKFLOW.read_text(encoding="utf-8")

    def test_vendor_sync_workflow_exists(self) -> None:
        assert VENDOR_SYNC_WORKFLOW.is_file()

    def test_vendor_sync_runs_on_weekly_schedule(self, workflow_text: str) -> None:
        assert "schedule:" in workflow_text
        assert "cron:" in workflow_text

    def test_vendor_sync_supports_manual_dispatch(self, workflow_text: str) -> None:
        assert "workflow_dispatch:" in workflow_text

    def test_vendor_sync_uses_vendor_scripts(self, workflow_text: str) -> None:
        assert "scripts/vendor/check_upstream.py" in workflow_text
        assert "scripts/vendor/sync_iwxxm.py" in workflow_text
        assert "--no-verify" in workflow_text
        assert "--refresh-tree-hashes" in workflow_text
        assert workflow_text.index("sync_iwxxm.py") < workflow_text.index(
            "--refresh-tree-hashes"
        )

    def test_vendor_sync_runs_tc_m002(self, workflow_text: str) -> None:
        assert "tests/vendor" in workflow_text

    def test_vendor_sync_excludes_gifts(self, workflow_text: str) -> None:
        lowered = workflow_text.lower()
        assert "mgoberfield" not in lowered
        assert "packages/gifts" not in lowered
        assert "gifts/" not in lowered
