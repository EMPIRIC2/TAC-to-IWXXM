"""QA-gap QG-weekly-api-validation-automation: weekly catalog automation inventory.

Documents what convert/validate automation exists on the git index vs what evolve
``EV-weekly-validation-catalog-gha`` must land (tracked weekly GHA + staging/DO
convert/validate severity catalog probes). Does not edit workflow YAML.

Local untracked evolve WIP is ignored — inventory uses ``git ls-files`` only.

[Corpus: tests] [Corpus: deploy]
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path
from types import ModuleType

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
SMOKE = ROOT / "scripts" / "deploy" / "staging_smoke.sh"
WEEKLY_SCRIPT = ROOT / "scripts" / "ci" / "weekly_validation_catalog.py"
WEEKLY_WORKFLOW = WORKFLOWS / "weekly-validation-catalog.yml"

_KNOWN_SCHEDULED = frozenset(
    {
        "load-tests.yml",
        "mutation.yml",
        "pypi-nightly.yml",
        "vendor-sync.yml",
    }
)


def _git_tracked(rel: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", rel],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _tracked_workflow_names() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", ".github/workflows/*.yml"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {Path(line).name for line in result.stdout.splitlines() if line.strip()}


def _scheduled_tracked_workflow_names() -> set[str]:
    names: set[str] = set()
    for name in _tracked_workflow_names():
        path = WORKFLOWS / name
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            continue
        on = doc.get("on") or doc.get(True)
        if isinstance(on, dict) and on.get("schedule"):
            names.add(name)
    return names


def _smoke_has_post_probe(path: str) -> bool:
    """True when staging_smoke POSTs the given API path (not OPTIONS-only)."""
    text = SMOKE.read_text(encoding="utf-8")
    for match in re.finditer(r"curl[^\n]+", text):
        line = match.group(0)
        if path not in line:
            continue
        if re.search(r"-X\s+POST\b", line) or re.search(r"--request\s+POST\b", line):
            return True
    return False


def _load_weekly_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "weekly_validation_catalog_qg",
        WEEKLY_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_qg_weekly_catalog_scheduled_workflow_inventory() -> None:
    """Known schedules remain; weekly validation catalog is tracked (EV land)."""
    scheduled = _scheduled_tracked_workflow_names()
    assert scheduled >= _KNOWN_SCHEDULED, (
        f"expected scheduled workflows {_KNOWN_SCHEDULED - scheduled} missing; got {scheduled}"
    )
    assert "weekly-validation-catalog.yml" in scheduled, (
        "weekly-validation-catalog.yml must be tracked with an on.schedule entry"
    )
    assert _git_tracked(".github/workflows/weekly-validation-catalog.yml")
    assert _git_tracked("scripts/ci/weekly_validation_catalog.py")


def test_qg_staging_smoke_convert_cors_only_baseline() -> None:
    """Staging smoke stays CORS/health-only; weekly GHA owns convert/validate catalogs.

    Follow-up (optional): extend staging_smoke with POST probes — not required while
    ``weekly-validation-catalog.yml`` covers staging/DO severity catalogs.
    """
    smoke = SMOKE.read_text(encoding="utf-8")
    assert "/api/v1/convert" in smoke
    assert "OPTIONS" in smoke or "-X OPTIONS" in smoke
    assert not _smoke_has_post_probe("/api/v1/convert")
    assert "/api/v1/validate" not in smoke
    assert "severity" not in smoke.lower()
    assert "validation-catalog" not in smoke.lower()


def test_qg_weekly_validation_catalog_automation_present() -> None:
    """Weekly catalog GHA + probe script are present and scheduled (G2/G3 land)."""
    assert _git_tracked(".github/workflows/weekly-validation-catalog.yml")
    assert _git_tracked("scripts/ci/weekly_validation_catalog.py")
    assert WEEKLY_WORKFLOW.is_file()
    assert WEEKLY_SCRIPT.is_file()
    workflow = WEEKLY_WORKFLOW.read_text(encoding="utf-8")
    assert "schedule:" in workflow
    assert "0 0 * * 0" in workflow
    assert "weekly_validation_catalog.py" in workflow
    assert "environment: staging" in workflow


def test_qg_weekly_script_counts_validate_level_when_tracked() -> None:
    """ValidateIssueModel uses ``level``; weekly count_severities must read it (G5)."""
    assert _git_tracked("scripts/ci/weekly_validation_catalog.py"), (
        "stage/commit scripts/ci/weekly_validation_catalog.py so inventory can assert track"
    )
    assert WEEKLY_SCRIPT.is_file()
    module = _load_weekly_script()
    counts = module.count_severities(
        [
            {"level": "error", "message": "xsd fail"},
            {"level": "warning", "message": "schematron soft"},
            {"severity": "info", "message": "note"},
        ]
    )
    assert counts["error"] == 1, (
        "count_severities ignores ValidateIssueModel.level — weekly validate "
        "probes will report unknown/zero errors"
    )
    assert counts["warning"] == 1
    assert counts["info"] == 1
