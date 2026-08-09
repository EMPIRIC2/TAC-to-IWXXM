"""TC-EV052-001 / T1.1 — coverage surface inventory exists and is complete.

[Corpus: tests] [Corpus: adr/ADR-007] [Corpus: product] EV-052 / #950
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

# Surfaces that must appear in the inventory (CI matrix + scripted runners).
REQUIRED_SURFACE_IDS = frozenset(
    {
        "root-pyproject",
        "backend",
        "worker",
        "auth",
        "shared-py",
        "shared-js",
        "tac2iwxxm",
        "tac-validate",
        "iwxxm-validate",
        "dissemination",
        "frontend",
        "per-file-checker",
    }
)


@pytest.mark.unit
class TestTcEv052CoverageInventory:
    """AC1 / TC-EV052-001 — inventory every coverage surface vs ≥95% target."""

    def test_inventory_file_exists(self) -> None:
        assert INVENTORY.is_file(), f"missing inventory: {INVENTORY}"

    def test_inventory_lists_required_surfaces(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert int(data.get("target_floor", 0)) >= 95
        surfaces = data.get("surfaces")
        assert isinstance(surfaces, list) and surfaces
        ids = {s["id"] for s in surfaces if isinstance(s, dict) and "id" in s}
        missing = REQUIRED_SURFACE_IDS - ids
        assert not missing, f"inventory missing surfaces: {sorted(missing)}"

    def test_inventory_paths_exist_and_target_at_least_floor(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        floor = int(data["target_floor"])
        for surface in data["surfaces"]:
            sid = surface["id"]
            assert int(surface["target_min"]) >= floor, sid
            rel = surface.get("config_path")
            if not rel:
                continue
            path = ROOT / rel
            assert path.is_file(), f"{sid}: missing {rel}"

    def test_inventory_documents_ci_enforcement(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        for surface in data["surfaces"]:
            if surface["id"] == "per-file-checker":
                continue
            assert surface.get("ci_job_or_make"), (
                f"{surface['id']}: need ci_job_or_make for enforcement path"
            )

    def test_frontend_inventory_matches_vitest_config(self) -> None:
        """Inventory current_thresholds must match vitest.config.ts."""
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        fe = next(s for s in data["surfaces"] if s["id"] == "frontend")
        assert fe["target_min"] >= 95
        current = fe.get("current_thresholds") or {}
        vitest = (ROOT / "apps/frontend/vitest.config.ts").read_text(encoding="utf-8")
        for key in ("lines", "statements", "functions", "branches"):
            m = re.search(rf"{key}:\s*(\d+)", vitest)
            assert m, key
            assert int(current[key]) == int(m.group(1)), key
