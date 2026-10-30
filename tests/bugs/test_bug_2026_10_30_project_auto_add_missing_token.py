"""BUG-2026-10-30 — Project auto-add must not fail when PROJECT_TOKEN is unset.

Repo secret PROJECT_TOKEN was missing; actions/add-to-project then failed with
``Input required and not supplied: github-token`` on every issues event.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "project-auto-add.yml"


def test_bug_2026_10_30_project_auto_add_workflow_exists() -> None:
    assert WORKFLOW.is_file()


def test_bug_2026_10_30_project_auto_add_skips_when_token_unset() -> None:
    """Guard: empty PROJECT_TOKEN must skip add-to-project (no hard fail)."""
    raw = WORKFLOW.read_text(encoding="utf-8")
    doc = yaml.safe_load(raw)
    assert isinstance(doc, dict)
    jobs = doc.get("jobs") or {}
    job = jobs.get("add-to-project")
    assert isinstance(job, dict), "expected add-to-project job"
    steps = job.get("steps") or []
    assert steps, "expected steps"

    # Must probe the secret without feeding an empty token into the action.
    assert any(
        "PROJECT_TOKEN" in str(step.get("env") or {})
        or "PROJECT_TOKEN" in str(step.get("run") or "")
        for step in steps
    ), "expected a step that reads PROJECT_TOKEN before add-to-project"

    add_steps = [
        step
        for step in steps
        if isinstance(step, dict)
        and str(step.get("uses") or "").startswith("actions/add-to-project@")
    ]
    assert len(add_steps) == 1, "expected exactly one add-to-project step"
    add = add_steps[0]
    assert "if:" in raw or add.get("if"), "add-to-project must be conditional"
    assert "has_token" in raw or "secrets.PROJECT_TOKEN != ''" in raw.replace(
        " ", ""
    ).replace('"', "").replace("'", "")
    # Soft-skip path must warn, not error-exit, when unset.
    assert "::warning::" in raw
    assert "github-token:" in raw
    assert "secrets.PROJECT_TOKEN" in raw


def test_bug_2026_10_30_project_auto_add_still_targets_project_7() -> None:
    raw = WORKFLOW.read_text(encoding="utf-8")
    assert "https://github.com/orgs/EMPIRIC2/projects/7" in raw
