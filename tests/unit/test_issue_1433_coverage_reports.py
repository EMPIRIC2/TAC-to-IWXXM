"""#1433 — publish coverage reports for four packages.

[Corpus: tests] [Corpus: product]

The sticky coverage comment and ``coverage-xml-*`` artifacts must include
``tac2iwxxm``, ``tac-validate``, ``auth``, and ``workflows`` at the existing
100% floor.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
CI_YML = ROOT / ".github" / "workflows" / "ci-cd.yml"
MAKEFILE = ROOT / "Makefile"

REQUIRED_PACKAGES = ("tac2iwxxm", "tac-validate", "auth", "workflows")
XML_PATHS = {
    "tac2iwxxm": "packages/tac2iwxxm/coverage.xml",
    "tac-validate": "packages/tac-validate/coverage.xml",
    "auth": "packages/auth/coverage.xml",
    "workflows": "packages/workflows/coverage.xml",
}
PYPROJECTS = {
    "tac2iwxxm": "packages/tac2iwxxm/pyproject.toml",
    "tac-validate": "packages/tac-validate/pyproject.toml",
    "auth": "packages/auth/pyproject.toml",
    "workflows": "packages/workflows/pyproject.toml",
}


def _upload_step(workflow: dict) -> dict:
    steps = workflow["jobs"]["test"]["steps"]
    return next(
        step
        for step in steps
        if step.get("name") == "Upload package coverage XML artifact"
    )


def _format_step(workflow: dict) -> dict:
    steps = workflow["jobs"]["coverage-pr-comment"]["steps"]
    return next(
        step for step in steps if step.get("name") == "Format coverage markdown"
    )


def _workflows_recipe(makefile: str) -> str:
    match = re.search(
        r"^test-unit-workflows:\n(?P<body>(?:\t.*\n)+)",
        makefile,
        re.MULTILINE,
    )
    assert match, "test-unit-workflows recipe missing"
    return match.group("body")


@pytest.mark.unit
def test_coverage_artifact_includes_four_packages() -> None:
    workflow = yaml.safe_load(CI_YML.read_text(encoding="utf-8"))
    step = _upload_step(workflow)
    condition = str(step["if"])
    paths = str(step["with"]["path"])
    for package in REQUIRED_PACKAGES:
        assert f'"{package}"' in condition
        assert XML_PATHS[package] in paths
    assert step["with"]["name"] == "coverage-xml-${{ matrix.package }}"

    comment = workflow["jobs"]["coverage-pr-comment"]
    download = next(
        step
        for step in comment["steps"]
        if step.get("name") == "Download coverage artifacts"
    )
    assert download["with"]["pattern"] == "coverage-xml-*"
    require = _format_step(workflow)["run"]
    assert "--require tac2iwxxm,tac-validate,auth,workflows" in require


@pytest.mark.unit
def test_workflows_make_target_writes_xml_at_100() -> None:
    body = _workflows_recipe(MAKEFILE.read_text(encoding="utf-8"))
    assert "--cov-report=xml:packages/workflows/coverage.xml" in body
    assert "--cov-report=json:packages/workflows/coverage.json" in body
    assert "--cov-fail-under=100" in body
    assert "check_per_file_coverage.py packages/workflows/coverage.json" in body


@pytest.mark.unit
def test_four_package_floors_stay_at_100() -> None:
    for package, rel in PYPROJECTS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert re.search(r"fail_under\s*=\s*100\b", text), package
    checker = (ROOT / "scripts/ci/check_per_file_coverage.py").read_text(
        encoding="utf-8"
    )
    assert "default=100.0" in checker
    workflow = CI_YML.read_text(encoding="utf-8")
    for package, xml_path in XML_PATHS.items():
        if package == "workflows":
            continue
        assert f"--cov-report=xml:{xml_path}" in workflow
    assert "--cov-fail-under=100" in workflow
    lowered = [
        int(value)
        for value in re.findall(r"--cov-fail-under=(\d+)", workflow)
        if int(value) < 100
    ]
    assert not lowered
