"""TC-EV052-002 / T1.3 — every coverage surface enforces ≥95%; soft gates gone.

[Corpus: tests] [Corpus: adr/ADR-007] EV-052 / #950
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = (
    ROOT
    / "docs"
    / "sessions"
    / "S061-ci-polish-quality-pr-stats"
    / "reports"
    / "coverage-surface-inventory.yaml"
)
CI_YML = ROOT / ".github" / "workflows" / "ci-cd.yml"
FRONTEND_VITEST = ROOT / "apps" / "frontend" / "vitest.config.ts"


def _fail_under_from_toml(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"fail_under\s*=\s*(\d+)", text)
    assert m, f"no fail_under in {path}"
    return int(m.group(1))


def _vitest_thresholds(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    out: dict[str, int] = {}
    for key in ("lines", "functions", "branches", "statements"):
        m = re.search(rf"{key}:\s*(\d+)", text)
        assert m, f"missing {key} threshold in {path}"
        out[key] = int(m.group(1))
    return out


@pytest.mark.unit
class TestTcEv052CoverageGates:
    """AC2 — soft/deferred gates removed; configs enforce ≥95."""

    def test_inventory_soft_gate_flag_cleared_for_frontend(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        fe = next(s for s in data["surfaces"] if s["id"] == "frontend")
        assert fe.get("soft_gate") is not True
        assert int(fe.get("enforced") or 0) >= 95

    def test_all_pytest_surfaces_fail_under_at_least_95(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        for surface in data["surfaces"]:
            if surface["kind"] != "pytest_fail_under":
                continue
            path = ROOT / surface["config_path"]
            assert _fail_under_from_toml(path) >= 95, surface["id"]

    def test_frontend_vitest_lines_stmts_funcs_at_least_95(self) -> None:
        """D-S061-cov-branches=3 — branches waived via child issue; others ≥95."""
        thresholds = _vitest_thresholds(FRONTEND_VITEST)
        for metric in ("lines", "statements", "functions"):
            assert thresholds[metric] >= 95, (
                f"frontend {metric}={thresholds[metric]} < 95"
            )
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        fe = next(s for s in data["surfaces"] if s["id"] == "frontend")
        waiver = fe.get("branch_waiver") or {}
        assert waiver.get("decision") == "D-S061-cov-branches=3"
        assert thresholds["branches"] == int(waiver["threshold"])
        assert int(waiver["threshold"]) < 95

    def test_shared_js_vitest_at_least_95(self) -> None:
        thresholds = _vitest_thresholds(ROOT / "packages/shared/vitest.config.ts")
        for metric, value in thresholds.items():
            assert value >= 95, f"shared-js {metric}={value} < 95"

    def test_ci_python_matrix_uses_cov_fail_under_at_least_95(self) -> None:
        text = CI_YML.read_text(encoding="utf-8")
        # Every --cov-fail-under=N in the unit matrix must be ≥95.
        values = [int(m) for m in re.findall(r"--cov-fail-under=(\d+)", text)]
        assert values, "expected --cov-fail-under in ci-cd.yml"
        below = [v for v in values if v < 95]
        assert not below, f"ci-cd.yml --cov-fail-under below 95: {below}"

    def test_dissemination_script_enforces_95(self) -> None:
        script = (ROOT / "scripts/ci/run_dissemination_coverage.sh").read_text(
            encoding="utf-8"
        )
        assert "--cov-fail-under=95" in script

    def test_no_soften_comments_excusing_sub_95_frontend(self) -> None:
        text = FRONTEND_VITEST.read_text(encoding="utf-8")
        # Soften language that accompanied 94/84 floors must not remain as active policy.
        assert "soften lines" not in text.lower()
        assert "soften functions/branches" not in text.lower()
