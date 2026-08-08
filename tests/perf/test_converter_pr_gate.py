"""TC-EV047-005..008 — converter PR hard gate vs committed baselines."""

from __future__ import annotations

import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import yaml
from scripts.bench.converter_pr_baselines import (
    DEFAULT_BASELINES,
    ceiling_p95_s,
    load_converter_pr_baselines,
    measure_convert_p95,
)

REPO = Path(__file__).resolve().parents[2]


def test_tc_ev047_baseline_file_schema() -> None:
    """TC-EV047-006/008 — committed baseline YAML schema + ceilings."""
    assert DEFAULT_BASELINES.is_file()
    data = yaml.safe_load(DEFAULT_BASELINES.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert data["metric"] == "convert_only_wall_p95_s"
    assert float(data["ratio_limit"]) == pytest.approx(1.20)
    assert float(data["absolute_floor_s"]) == pytest.approx(0.000200)
    for key in ("metar", "speci", "taf", "sigmet"):
        assert key in data["products"]
        assert float(data["products"][key]["baseline_p95_s"]) > 0
    baselines = load_converter_pr_baselines()
    metar = baselines.products["metar"]
    expected = ceiling_p95_s(
        metar.baseline_p95_s, baselines.ratio_limit, baselines.absolute_floor_s
    )
    assert metar.ceiling_p95_s == pytest.approx(expected)


def test_tc_ev047_convert_under_ceiling() -> None:
    """TC-EV047-006 — current convert stays under committed ceilings (green path).

    Skipped while ``status: laptop_seed`` (D-S056-04-plan=2) — re-enable after T1.3
    CI re-record sets ``status: ci_recorded``.
    """
    baselines = load_converter_pr_baselines()
    if baselines.status != "ci_recorded":
        pytest.skip(
            f"baseline status={baselines.status!r}; green path waits for CI re-record (T1.3)"
        )
    for pb in baselines.products.values():
        _p50, p95 = measure_convert_p95(
            pb.tac,
            product=pb.product,
            profile=baselines.profile,
            iwxxm_version=baselines.iwxxm_version,
            warmup=baselines.warmup,
            iterations=baselines.iterations,
        )
        assert p95 <= pb.ceiling_p95_s, (
            f"{pb.key}: convert p95 {p95:.6g}s exceeds ceiling {pb.ceiling_p95_s:.6g}s "
            f"(baseline {pb.baseline_p95_s:.6g}s; status={baselines.status})"
        )


def test_tc_ev047_artificial_slowdown_exceeds_ceiling() -> None:
    """TC-EV047-005 — deliberate slowdown turns the gate red."""
    baselines = load_converter_pr_baselines()
    pb = baselines.products["metar"]
    delay = max(pb.ceiling_p95_s * 2, 0.002)

    def slow_convert(*_a: Any, **_k: Any) -> SimpleNamespace:
        time.sleep(delay)
        return SimpleNamespace(ok=True, xml="<x/>")

    _p50, p95 = measure_convert_p95(
        pb.tac,
        product=pb.product,
        profile=baselines.profile,
        iwxxm_version=baselines.iwxxm_version,
        warmup=1,
        iterations=3,
        convert_fn=slow_convert,
    )
    assert p95 > pb.ceiling_p95_s


def test_tc_ev047_makefile_has_baseline_refresh_target() -> None:
    """TC-EV047-006 — explicit refresh target (no silent auto-raise)."""
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    assert "perf-converter-baseline" in makefile


def test_tc_ev047_ci_job_locked_name() -> None:
    """TC-EV047-007 — CI job display name matches ruleset context."""
    workflow = (REPO / ".github" / "workflows" / "ci-cd.yml").read_text(
        encoding="utf-8"
    )
    assert "name: Converter perf (tac2iwxxm)" in workflow
    assert "converter-perf:" in workflow
    script = (REPO / "scripts" / "deploy" / "apply_gh_branch_rulesets.sh").read_text(
        encoding="utf-8"
    )
    assert "Converter perf (tac2iwxxm)" in script
