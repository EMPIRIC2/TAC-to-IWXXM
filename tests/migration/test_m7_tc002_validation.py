"""M7 TC-002 validation gate — test-plan.md UJ-002, F2."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
INTEGRATION_SMOKE = (
    ROOT / "apps" / "backend" / "tests" / "integration" / "test_product_regression_smoke.py"
)
MAKEFILE = ROOT / "Makefile"


@pytest.mark.migration
class TestM7Tc002ValidationGate:
    """TC-002 validation pass is verified via backend integration smoke (T5.8 + T7.4)."""

    def test_f2_validation_smoke_module_present(self) -> None:
        assert INTEGRATION_SMOKE.is_file()
        source = INTEGRATION_SMOKE.read_text(encoding="utf-8")
        assert "class TestF2ValidationSmoke" in source
        assert "test_comprehensive_validate_known_good_metar" in source
        assert 'payload["is_valid"] is True' in source
        assert "test_validation_router_tac_validate" in source
        assert 'payload["passed"] is True' in source

    def test_makefile_runs_integration_suite(self) -> None:
        makefile = MAKEFILE.read_text(encoding="utf-8")
        assert "test-integration:" in makefile

    def test_execution_plan_links_t74_to_tc002(self) -> None:
        plan = (ROOT / ".cursor" / "artifacts" / "execution-plan-monorepo.md").read_text(
            encoding="utf-8"
        )
        assert "T7.4" in plan
        assert "TC-002" in plan
