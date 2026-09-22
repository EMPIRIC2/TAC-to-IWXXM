"""EV-ci-runtime-failures — mutation dual-cadence matrix shape (TC-F34-005)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MUTATION_WORKFLOW = ROOT / ".github" / "workflows" / "mutation.yml"


def test_mutation_workflow_dual_cadence_markers() -> None:
    raw = MUTATION_WORKFLOW.read_text(encoding="utf-8")
    assert "Daily subset" in raw
    assert (
        'dow}" == "7"' in raw
        or '${dow}" == "7"' in raw
        or '[[ "${dow}" == "7" ]]' in raw
    )
    assert "rotate 3 Python" in raw
    assert "pnpm/action-setup@v4" in raw
    assert "version: 9" not in raw
