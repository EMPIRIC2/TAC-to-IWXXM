"""Lock: stage pushes always run bugs + package matrix + quality packs.

Standing docs: [Corpus: tests] docs/test-plan.md CI row (path filters on
family quality packs deferred for push; PR path filters remain).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
CI_CD = WORKFLOWS / "ci-cd.yml"
TESTER_REGRESSION = WORKFLOWS / "tester-regression.yml"

# Family quality / smoke workflows that must always run on stage/main push.
QUALITY_PUSH_ALWAYS = (
    "ahl-com-quality.yml",
    "airmet-quality.yml",
    "codelist-uri-drift.yml",
    "iwxxm-us-compat-smoke.yml",
    "metar-quality.yml",
    "product-order-smoke.yml",
    "quality-matrices.yml",
    "report-state-matrix-smoke.yml",
    "sigmet-quality.yml",
    "speci-quality.yml",
    "swxa-quality.yml",
    "taf-quality.yml",
    "tc-sigmet-quality.yml",
    "tca-quality.yml",
    "va-sigmet-quality.yml",
    "vaa-quality.yml",
    "wmo-quality.yml",
)

REQUIRED_MATRIX = frozenset(
    {
        "shared",
        "auth",
        "backend",
        "frontend",
        "tac2iwxxm",
        "tac-decoding",
        "reference-lookup",
        "iwxxm-validate",
        "tac-validate",
        "dissemination",
        "workflows",
        "worker",
        "bugs",
    }
)


def _on(doc: dict[str, Any]) -> dict[str, Any]:
    triggers = doc.get("on")
    if triggers is None:
        triggers = doc.get(True)
    assert isinstance(triggers, dict), "workflow must define on:"
    return triggers


def _load(path: Path) -> dict[str, Any]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(doc, dict)
    return doc


def test_ci_cd_push_stage_has_no_path_filter() -> None:
    doc = _load(CI_CD)
    push = _on(doc)["push"]
    assert isinstance(push, dict)
    assert "stage" in push.get("branches", [])
    assert "paths" not in push
    assert "paths-ignore" not in push


def test_ci_cd_test_matrix_includes_bugs_and_packages() -> None:
    packages = set(_load(CI_CD)["jobs"]["test"]["strategy"]["matrix"]["package"])
    missing = sorted(REQUIRED_MATRIX - packages)
    assert not missing, f"Test matrix missing packages: {missing}"


def test_ci_cd_bugs_job_runs_tests_bugs_tree() -> None:
    text = CI_CD.read_text(encoding="utf-8")
    assert "matrix.package == 'bugs'" in text or 'matrix.package == "bugs"' in text
    assert "pytest tests/bugs" in text
    assert "not live and not live_api" in text
    # Offline live_tac_eval regressions live under tests/bugs/ — recursive collect.
    assert "tests/regression/caribbean_tester" in text


def test_tester_regression_always_on_stage_push() -> None:
    doc = _load(TESTER_REGRESSION)
    push = _on(doc)["push"]
    assert isinstance(push, dict)
    assert "stage" in push.get("branches", [])
    assert "paths" not in push
    assert "paths-ignore" not in push


def test_quality_packs_push_stage_without_path_filter() -> None:
    for name in QUALITY_PUSH_ALWAYS:
        path = WORKFLOWS / name
        assert path.is_file(), f"missing workflow {name}"
        doc = _load(path)
        push = _on(doc)["push"]
        assert isinstance(push, dict), f"{name}: push must be a mapping"
        branches = push.get("branches") or []
        assert "stage" in branches, f"{name}: push.branches must include stage"
        assert "paths" not in push, f"{name}: push must not path-filter (stage tip)"
        assert "paths-ignore" not in push, f"{name}: no paths-ignore on push"
