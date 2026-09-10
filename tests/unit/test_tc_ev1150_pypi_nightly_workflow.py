"""TC-EV1150 / ADR-043: PyPI nightly TestPyPI workflow structural gate."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pypi-nightly.yml"

EXPECTED_PACKAGES = frozenset({"tac-validate", "iwxxm-validate", "tac2iwxxm"})


def _load_workflow() -> dict:
    assert WORKFLOW.is_file(), f"missing nightly workflow: {WORKFLOW}"
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    if True in data and "on" not in data:
        data["on"] = data.pop(True)
    return data


def test_pypi_nightly_workflow_schedule_and_testpypi() -> None:
    wf = _load_workflow()
    assert wf.get("name") == "PyPI Nightly (TestPyPI)"
    on = wf["on"]
    assert "schedule" in on
    assert "workflow_dispatch" in on
    cron = on["schedule"][0]["cron"]
    assert cron == "0 7 * * *"

    job = wf["jobs"]["nightly"]
    assert job["environment"]["name"] == "testpypi"
    assert job["permissions"]["id-token"] == "write"

    matrix_pkgs = {row["package"] for row in job["strategy"]["matrix"]["include"]}
    assert matrix_pkgs == EXPECTED_PACKAGES

    steps_blob = str(job["steps"])
    assert "bump_calver.py" in steps_blob
    assert "test.pypi.org" in steps_blob
    assert "continue-on-error" in WORKFLOW.read_text(encoding="utf-8")
    # No long-lived TestPyPI password in the workflow file.
    assert "secrets.PYPI_API_TOKEN" not in WORKFLOW.read_text(encoding="utf-8")
    assert "password" not in (
        next(
            s.get("with") or {}
            for s in job["steps"]
            if "pypi-publish" in str(s.get("uses", ""))
        )
    )
