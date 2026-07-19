"""T1.3 / E10-35: absolute hard-gate baselines recorded from layer-cost matrix."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPORTS = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "sessions"
    / "S014-package-publish-validation"
    / "reports"
)
BASELINES_YAML = REPORTS / "perf-baselines.yaml"
BASELINES_MD = REPORTS / "perf-baselines.md"
MATRIX_MD = REPORTS / "layer-cost-matrix.md"


def test_perf_baselines_yaml_exists_with_gate_fields() -> None:
    assert BASELINES_YAML.is_file()
    data = yaml.safe_load(BASELINES_YAML.read_text(encoding="utf-8"))
    assert data["gates"]["lib_path_ratio"] == 0.85
    assert data["gates"]["http_msgspec_ratio"] == 1.0
    baselines = data["baselines_p95_s"]
    for key in (
        "lint",
        "convert_ir",
        "xsd",
        "schematron",
        "http_pydantic_map",
        "lib_path_lxml",
    ):
        assert key in baselines
        assert isinstance(baselines[key], float)
        assert baselines[key] > 0.0
    ceilings = data["ceilings_p95_s"]
    assert ceilings["lib_path_hard"] == pytest.approx(0.85 * baselines["lib_path_lxml"])
    assert ceilings["http_msgspec_hard"] == pytest.approx(
        1.0 * baselines["http_pydantic_map"]
    )
    assert "schematron_xslt2_skipped_d_s008_t21_sch" in data["caveats"]


def test_perf_baselines_markdown_and_matrix_linked() -> None:
    assert BASELINES_MD.is_file()
    assert MATRIX_MD.is_file()
    md = BASELINES_MD.read_text(encoding="utf-8")
    assert "0.85" in md
    assert "1.0" in md
    assert "lib_path_lxml_baseline_p95_s" in md
    assert "http_pydantic_map_baseline_p95_s" in md
    assert "layer-cost-matrix.md" in md
