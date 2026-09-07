"""T4.4 / TC-F14-001: PyPI publish workflow structural gate (pypi-release-checklist)."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pypi-publish.yml"

EXPECTED_PACKAGES = frozenset({"tac-validate", "iwxxm-validate", "tac2iwxxm"})
EXPECTED_TAG_PREFIXES = frozenset(
    {"tac-validate-v*", "iwxxm-validate-v*", "tac2iwxxm-v*"}
)


def _load_workflow() -> dict:
    assert WORKFLOW.is_file(), f"missing publish workflow: {WORKFLOW}"
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    # PyYAML treats bare key ``on:`` as boolean True.
    if True in data and "on" not in data:
        data["on"] = data.pop(True)
    return data


def test_pypi_publish_workflow_oidc_and_matrix() -> None:
    """
    Checklist gate when TestPyPI / act is not configured (T4.4).

    Asserts select→fromJSON matrices, tag filters, and ``id-token: write`` on publish.
    """
    wf = _load_workflow()
    assert wf.get("name") == "PyPI Publish"

    on = wf["on"]
    tags = set(on["push"]["tags"])
    assert tags == EXPECTED_TAG_PREFIXES
    assert "workflow_dispatch" in on

    jobs = wf["jobs"]
    assert set(jobs) >= {"select", "build", "build-native", "smoke", "publish"}

    select = jobs["select"]
    assert "pure_matrix" in select["outputs"]
    assert "native_matrix" in select["outputs"]
    select_run = "\n".join(
        str(step.get("run", "")) for step in select["steps"] if isinstance(step, dict)
    )
    for pkg in EXPECTED_PACKAGES:
        assert pkg in select_run

    build = jobs["build"]
    assert "fromJSON(needs.select.outputs.pure_matrix)" in str(
        build["strategy"]["matrix"]["include"]
    )

    native = jobs["build-native"]
    assert native["if"] == "needs.select.outputs.has_native == 'true'"
    assert "fromJSON(needs.select.outputs.native_matrix)" in str(
        native["strategy"]["matrix"]["include"]
    )
    assert "PyO3/maturin-action@" in str(native["steps"])
    # Native packages (no pure-only tac-validate in select native_matrix).
    assert "tac2iwxxm" in select_run
    assert "iwxxm-validate" in select_run
    assert "native='[]'" in select_run or 'native="[]"' in select_run

    publish = jobs["publish"]
    assert publish["permissions"]["id-token"] == "write"
    assert publish["environment"]["name"] == "pypi"
    assert "should_publish" in str(publish["if"])

    # Trusted publishing: no password / API token wiring in the publish step.
    publish_steps = publish["steps"]
    publish_step = next(
        s for s in publish_steps if "pypi-publish" in str(s.get("uses", ""))
    )
    with_block = publish_step.get("with") or {}
    assert "password" not in with_block
    assert "user" not in with_block
    assert "secrets.PYPI_API_TOKEN" not in WORKFLOW.read_text(encoding="utf-8")


def test_pypi_publish_workflow_dispatch_dry_run_default() -> None:
    """``workflow_dispatch.publish`` defaults to false (dry-run / checklist path)."""
    wf = _load_workflow()
    inputs = wf["on"]["workflow_dispatch"]["inputs"]
    assert inputs["publish"]["default"] is False
    assert set(inputs["package"]["options"]) == EXPECTED_PACKAGES
