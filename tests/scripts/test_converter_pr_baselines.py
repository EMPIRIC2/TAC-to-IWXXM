"""EV-080 M4 — 100% coverage for scripts/bench/converter_pr_baselines.py."""

from __future__ import annotations

import time
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from scripts.bench import converter_pr_baselines as mod

ROOT = Path(__file__).resolve().parents[2]


def test_ceiling_p95_s() -> None:
    assert mod.ceiling_p95_s(0.001, 1.2, 0.0002) == pytest.approx(0.0012)


def test_p95_branches() -> None:
    with pytest.raises(ValueError, match="no samples"):
        mod._p95([])
    assert mod._p95([1.0]) == 1.0
    assert mod._p95([1.0, 2.0, 3.0, 4.0, 5.0]) > 4.0


def test_resolve_tac_inline_and_fixture(tmp_path: Path) -> None:
    assert mod._resolve_tac({"tac": "  inline  "}, tmp_path) == "inline"
    fixture = tmp_path / "f.tac"
    fixture.write_text("from-file\n", encoding="utf-8")
    assert mod._resolve_tac({"fixture": "f.tac"}, tmp_path) == "from-file"
    with pytest.raises(ValueError, match="needs tac or fixture"):
        mod._resolve_tac({}, tmp_path)


def test_load_converter_pr_baselines(tmp_path: Path) -> None:
    data = {
        "version": 1,
        "status": "test",
        "ratio_limit": 1.2,
        "absolute_floor_s": 0.0002,
        "iwxxm_version": "2025-2",
        "profile": "annex3",
        "warmup": 1,
        "iterations": 2,
        "products": {
            "metar": {
                "product": "METAR",
                "tac": "METAR KJFK 010000Z=",
                "baseline_p50_s": 0.001,
                "baseline_p95_s": 0.002,
            }
        },
    }
    path = tmp_path / "baseline.yaml"
    path.write_text(yaml.dump(data), encoding="utf-8")
    loaded = mod.load_converter_pr_baselines(path)
    assert loaded.products["metar"].tac == "METAR KJFK 010000Z="
    assert (
        loaded.products["metar"].ceiling_p95_s > loaded.products["metar"].baseline_p95_s
    )


def test_measure_convert_p95_and_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baselines = mod.load_converter_pr_baselines()

    def ok_convert(*_a: object, **_k: object) -> SimpleNamespace:
        return SimpleNamespace(ok=True, xml="<x/>")

    p50, p95 = mod.measure_convert_p95(
        "METAR KJFK 010000Z=",
        product="METAR",
        profile=baselines.profile,
        iwxxm_version=baselines.iwxxm_version,
        warmup=1,
        iterations=3,
        convert_fn=ok_convert,
    )
    assert p50 <= p95

    def fail_convert(*_a: object, **_k: object) -> SimpleNamespace:
        return SimpleNamespace(ok=False)

    with pytest.raises(RuntimeError, match="warmup convert failed"):
        mod.measure_convert_p95(
            "METAR KJFK 010000Z=",
            product="METAR",
            profile=baselines.profile,
            iwxxm_version=baselines.iwxxm_version,
            warmup=1,
            iterations=1,
            convert_fn=fail_convert,
        )

    calls = {"n": 0}

    def flaky_convert(*_a: object, **_k: object) -> SimpleNamespace:
        calls["n"] += 1
        if calls["n"] <= 2:
            return SimpleNamespace(ok=True, xml="<x/>")
        return SimpleNamespace(ok=False)

    with pytest.raises(RuntimeError, match="convert failed"):
        mod.measure_convert_p95(
            "METAR KJFK 010000Z=",
            product="METAR",
            profile=baselines.profile,
            iwxxm_version=baselines.iwxxm_version,
            warmup=1,
            iterations=3,
            convert_fn=flaky_convert,
        )

    updated = mod.record_baselines_dict(
        baselines,
        status="ci_recorded",
        recorded_host="test",
        convert_fn=ok_convert,
    )
    assert updated["status"] == "ci_recorded"
    assert updated["products"]["metar"]["baseline_p95_s"] > 0


def test_measure_convert_p95_slow_path() -> None:
    baselines = mod.load_converter_pr_baselines()
    pb = baselines.products["metar"]

    def slow(*_a: object, **_k: object) -> SimpleNamespace:
        time.sleep(0.002)
        return SimpleNamespace(ok=True, xml="<x/>")

    _p50, p95 = mod.measure_convert_p95(
        pb.tac,
        product=pb.product,
        profile=baselines.profile,
        iwxxm_version=baselines.iwxxm_version,
        warmup=1,
        iterations=3,
        convert_fn=slow,
    )
    assert p95 >= 0.002
