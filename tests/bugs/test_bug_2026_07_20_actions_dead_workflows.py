"""BUG-2026-07-20 — drop always-red / dead GitHub Actions workflows.

Guards the P0+P1 cleanup: no legacy smoke/coverage workflows, and the
full-stack E2E workflow must not schedule the obsolete Performance
Benchmarks job that ``cd backend`` (path removed in the monorepo).
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_bug_2026_07_20_dead_workflows_removed() -> None:
    assert not (WORKFLOWS / "smoke-tests-deploy.yml").exists()
    assert not (WORKFLOWS / "test-coverage-95.yml").exists()


def test_bug_2026_07_20_e2e_no_schedule_or_legacy_benchmarks() -> None:
    path = WORKFLOWS / "e2e-tests.yml"
    assert path.is_file()
    raw = path.read_text(encoding="utf-8")
    # PyYAML may parse the key `on` as boolean True
    doc = yaml.safe_load(raw)
    assert isinstance(doc, dict)

    triggers = doc.get("on")
    if triggers is None:
        triggers = doc.get(True)
    assert isinstance(triggers, dict), "e2e-tests.yml must have an `on:` trigger map"
    assert "schedule" not in triggers, "E2E cron disabled until monorepo rewrite"

    jobs = doc.get("jobs") or {}
    assert "performance-benchmarks" not in jobs
    assert "cd backend" not in raw
    # Job display name must not reappear
    assert "\n    name: Performance Benchmarks\n" not in raw
