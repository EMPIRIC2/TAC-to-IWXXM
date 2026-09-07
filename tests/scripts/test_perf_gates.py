"""Coverage for scripts/bench/perf_gates.py (remaining branches)."""

from __future__ import annotations

import warnings
from pathlib import Path

import pytest
import yaml
from scripts.bench.perf_gates import (
    HARD_PERF_ENV,
    RatioCheck,
    apply_gate,
    check_ratio,
    hard_perf_enabled,
    load_baselines,
)


@pytest.mark.unit
def test_load_baselines_custom_path(tmp_path: Path) -> None:
    path = tmp_path / "perf.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "gates": {"lib_path_ratio": 0.85, "http_msgspec_ratio": 1.0},
                "baselines_p95_s": {
                    "lib_path_lxml": 0.1,
                    "http_pydantic_map": 0.2,
                },
                "ceilings_p95_s": {
                    "lib_path_hard": 0.085,
                    "http_msgspec_hard": 0.2,
                },
            }
        ),
        encoding="utf-8",
    )
    baselines = load_baselines(path)
    assert baselines.lib_path_ratio == 0.85
    assert baselines.lib_path_lxml_p95_s == 0.1


@pytest.mark.unit
@pytest.mark.parametrize(
    "value",
    ["1", "true", "TRUE", "yes", "YES"],
)
def test_hard_perf_enabled_truthy(value: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(HARD_PERF_ENV, value)
    assert hard_perf_enabled() is True


@pytest.mark.unit
def test_hard_perf_enabled_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(HARD_PERF_ENV, raising=False)
    assert hard_perf_enabled() is False


@pytest.mark.unit
def test_check_ratio_rejects_non_positive_baseline() -> None:
    with pytest.raises(ValueError, match="baseline must be positive"):
        check_ratio(1.0, 0.0, ratio=0.85, label="lib")


@pytest.mark.unit
def test_ratio_check_message() -> None:
    check = RatioCheck(
        ok=False,
        candidate_p95_s=0.2,
        baseline_p95_s=0.1,
        ratio=0.85,
        ceiling_p95_s=0.085,
        observed_ratio=2.0,
        label="lib",
    )
    assert "lib:" in check.message
    assert "observed ratio=2" in check.message


@pytest.mark.unit
def test_apply_gate_ok_is_noop() -> None:
    ok = check_ratio(0.05, 0.1, ratio=0.85, label="lib")
    apply_gate(ok, hard=False)


@pytest.mark.unit
def test_apply_gate_soft_warns() -> None:
    bad = check_ratio(0.2, 0.1, ratio=0.85, label="lib")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        apply_gate(bad, hard=False)
    assert any("SOFT PERF" in str(w.message) for w in caught)


@pytest.mark.unit
def test_apply_gate_hard_raises() -> None:
    bad = check_ratio(0.2, 0.1, ratio=0.85, label="lib")
    with pytest.raises(AssertionError, match="HARD PERF"):
        apply_gate(bad, hard=True)


@pytest.mark.unit
def test_apply_gate_uses_env_when_hard_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(HARD_PERF_ENV, "1")
    bad = check_ratio(0.2, 0.1, ratio=0.85, label="lib")
    with pytest.raises(AssertionError, match="HARD PERF"):
        apply_gate(bad)
