"""TC-EV080-001 / TC-EV080-010 — coverage inventory @ 100 floor + approved omits.

[Corpus: tests] [Corpus: adr/ADR-007] [Corpus: product] EV-080 / #1077
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs" / "testing" / "coverage-surface-inventory.yaml"

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
        "scripts-python",
        "scripts-shell-bats",
    }
)

REQUIRED_APPROVED_OMITS = frozenset(
    {
        "vendor",
        "iwxxm_xsd_generated",
        "bugs",
        "e2e-playwright",
    }
)

# Executable FE modules that must be listed for removal (not approved excludes).
FE_EXECUTABLE_EXCLUDES = frozenset(
    {
        "src/utils/tacEditorSpans.ts",
        "src/app/components/TacEditor.tsx",
        "src/utils/liveAssist.ts",
        "src/hooks/useLiveWorkbenchAssist.ts",
        "src/utils/gunzip.ts",
        "src/app/App.tsx",
    }
)


@pytest.mark.unit
class TestTcEv080CoverageInventory:
    """AC1 / TC-EV080-001 — inventory every coverage surface vs 100% target."""

    def test_inventory_file_exists(self) -> None:
        assert INVENTORY.is_file(), f"missing inventory: {INVENTORY}"

    def test_target_floor_is_100(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        assert int(data.get("target_floor", 0)) == 100

    def test_inventory_lists_required_surfaces(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        surfaces = data.get("surfaces")
        assert isinstance(surfaces, list)
        assert surfaces
        ids = {s["id"] for s in surfaces if isinstance(s, dict) and "id" in s}
        missing = REQUIRED_SURFACE_IDS - ids
        assert not missing, f"inventory missing surfaces: {sorted(missing)}"

    def test_inventory_paths_exist_and_target_at_least_floor(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        floor = int(data["target_floor"])
        for surface in data["surfaces"]:
            sid = surface["id"]
            target = surface.get("target_min")
            if target == "100_of_files":
                assert floor == 100, sid
            else:
                assert int(target) >= floor, sid
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

    def test_frontend_thresholds_match_vitest_config(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        fe = next(s for s in data["surfaces"] if s["id"] == "frontend")
        assert int(fe["target_min"]) == 100
        current = fe.get("current_thresholds") or {}
        vitest = (ROOT / "apps/frontend/vitest.config.ts").read_text(encoding="utf-8")
        for key in ("lines", "statements", "functions", "branches"):
            m = re.search(rf"{key}:\s*(\d+)", vitest)
            assert m, key
            assert int(current[key]) == int(m.group(1)), key

    def test_shared_js_thresholds_match_vitest_config(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        shared = next(s for s in data["surfaces"] if s["id"] == "shared-js")
        current = shared.get("current_thresholds") or {}
        vitest = (ROOT / "packages/shared/vitest.config.ts").read_text(encoding="utf-8")
        for key in ("lines", "statements", "functions", "branches"):
            m = re.search(rf"{key}:\s*(\d+)", vitest)
            assert m, key
            assert int(current[key]) == int(m.group(1)), key

    def test_approved_omits_documented(self) -> None:
        """TC-EV080-010 — intentional non-surfaces are the approved omit set."""
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        nons = data.get("intentional_non_surfaces") or []
        ids = {n["id"] for n in nons if isinstance(n, dict) and "id" in n}
        missing = REQUIRED_APPROVED_OMITS - ids
        assert not missing, f"missing approved omits: {sorted(missing)}"
        for n in nons:
            assert n.get("reason"), f"{n.get('id')}: need reason"

    def test_frontend_executable_excludes_listed_for_removal(self) -> None:
        """Executable FE excludes must be tracked for M3 purge — not approved."""
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        fe = next(s for s in data["surfaces"] if s["id"] == "frontend")
        to_remove = set(fe.get("executable_excludes_to_remove") or [])
        approved = set(fe.get("approved_excludes") or [])
        missing = FE_EXECUTABLE_EXCLUDES - to_remove
        assert not missing, (
            f"FE executable excludes not listed for removal: {sorted(missing)}"
        )
        overlap = FE_EXECUTABLE_EXCLUDES & approved
        assert not overlap, (
            f"executable paths must not be approved excludes: {sorted(overlap)}"
        )

    def test_scripts_counts_documented(self) -> None:
        data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
        py = next(s for s in data["surfaces"] if s["id"] == "scripts-python")
        sh = next(s for s in data["surfaces"] if s["id"] == "scripts-shell-bats")
        assert int(py.get("script_py_file_count") or 0) >= 1
        assert int(sh.get("shell_file_count_at_inventory") or 0) >= 1
        actual_py = len(list(ROOT.glob("scripts/**/*.py")))
        actual_sh = len(list(ROOT.glob("scripts/**/*.sh")))
        assert int(py["script_py_file_count"]) == actual_py
        assert int(sh["shell_file_count_at_inventory"]) == actual_sh
