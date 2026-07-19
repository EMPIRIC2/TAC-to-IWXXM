"""T3.5 / E10-35: soft benches for native ``validate_iwxxm`` vs lxml; hard-gate path.

Soft until publish (T6.6): over-ceiling results warn only unless
``IWXXM_VALIDATE_HARD_PERF=1``.
"""

from __future__ import annotations

import time
import warnings
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest
import yaml
from iwxxm_validate import rust_available, validate, validate_iwxxm
from scripts.bench.perf_gates import (
    HARD_PERF_ENV,
    apply_gate,
    check_ratio,
    hard_perf_enabled,
    load_baselines,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS = (
    REPO_ROOT / "docs" / "sessions" / "S014-package-publish-validation" / "reports"
)
GOLDEN_XML = (
    REPO_ROOT
    / "packages"
    / "tac2iwxxm"
    / "tests"
    / "fixtures"
    / "annex3_golden"
    / "metar_basic.golden.xml"
)
VENDOR_METAR = (
    REPO_ROOT
    / "vendor"
    / "schemas"
    / "iwxxm"
    / "2023-1"
    / "IWXXM"
    / "examples"
    / "metar-A3-1.xml"
)

# Fair head-to-head: 2023-1 where both engines evaluate Schematron (lxml may skip XSLT2).
IWXXM_VERSION = "2023-1"
ITERATIONS = 11


def _percentile(samples: Sequence[float], pct: float) -> float:
    ordered = sorted(samples)
    if len(ordered) == 1:
        return ordered[0]
    rank = (pct / 100.0) * (len(ordered) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(ordered) - 1)
    if lo == hi:
        return ordered[lo]
    frac = rank - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def _p95(fn: Callable[[], object], iterations: int = ITERATIONS) -> float:
    fn()  # warmup (schema compile / first load)
    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return _percentile(samples, 95.0)


def _load_xml() -> str:
    path = VENDOR_METAR if VENDOR_METAR.is_file() else GOLDEN_XML
    if not path.is_file():
        pytest.skip(f"IWXXM fixture missing: {path}")
    return path.read_text(encoding="utf-8")


def test_hard_gate_path_wired_for_publish() -> None:
    """Assert E10-35 hard-gate path exists for T6.6 (ceilings + env flip)."""
    baselines = load_baselines()
    assert baselines.lib_path_ratio == pytest.approx(0.85)
    assert baselines.lib_path_hard_ceiling_p95_s == pytest.approx(
        0.85 * baselines.lib_path_lxml_p95_s
    )
    assert HARD_PERF_ENV == "IWXXM_VALIDATE_HARD_PERF"
    # Soft by default in build
    assert hard_perf_enabled() is False

    plan = (
        REPO_ROOT
        / "docs"
        / "sessions"
        / "S014-package-publish-validation"
        / "reports"
        / "execution-plan.md"
    ).read_text(encoding="utf-8")
    assert "T6.6" in plan
    assert "0.85" in plan


def test_soft_bench_native_vs_lxml_xsd() -> None:
    """Soft: native XSD p95 <= 0.85x same-run lxml XSD p95 (E10-35)."""
    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    xml = _load_xml()

    def lxml_xsd() -> None:
        validate(xml, iwxxm_version=IWXXM_VERSION, profile="annex3", levels=("xsd",))

    def native_xsd() -> None:
        validate_iwxxm(
            xml, iwxxm_version=IWXXM_VERSION, profile="annex3", levels=("xsd",)
        )

    lxml_p95 = _p95(lxml_xsd)
    native_p95 = _p95(native_xsd)
    check = check_ratio(native_p95, lxml_p95, ratio=0.85, label="native_xsd_vs_lxml")
    apply_gate(check, hard=False)


def test_soft_bench_native_vs_lxml_schematron() -> None:
    """Soft: native Schematron p95 <= 0.85x lxml Schematron p95 (may warn — real SCH vs skip)."""
    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    xml = _load_xml()

    def lxml_sch() -> None:
        validate(
            xml, iwxxm_version=IWXXM_VERSION, profile="annex3", levels=("schematron",)
        )

    def native_sch() -> None:
        validate_iwxxm(
            xml, iwxxm_version=IWXXM_VERSION, profile="annex3", levels=("schematron",)
        )

    lxml_p95 = _p95(lxml_sch)
    native_p95 = _p95(native_sch)
    # lxml often hits SCHEMATRON_SKIPPED (cheap); native evaluates real rules — soft warn expected.
    check = check_ratio(
        native_p95, lxml_p95, ratio=0.85, label="native_schematron_vs_lxml"
    )
    apply_gate(check, hard=False)


def test_soft_bench_native_vs_lxml_validate_combined() -> None:
    """Soft: full validate_iwxxm p95 <= 0.85x lxml validate p95 on golden IWXXM."""
    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    xml = _load_xml()

    def lxml_all() -> None:
        validate(
            xml,
            iwxxm_version=IWXXM_VERSION,
            profile="annex3",
            levels=("xsd", "schematron"),
        )

    def native_all() -> None:
        validate_iwxxm(
            xml,
            iwxxm_version=IWXXM_VERSION,
            profile="annex3",
            levels=("xsd", "schematron"),
        )

    lxml_p95 = _p95(lxml_all)
    native_p95 = _p95(native_all)
    check = check_ratio(
        native_p95, lxml_p95, ratio=0.85, label="native_validate_vs_lxml"
    )
    apply_gate(check, hard=False)


def test_soft_bench_vs_committed_lib_path_ceiling() -> None:
    """Soft: native full validate p95 vs committed T1.3 lib_path_hard ceiling."""
    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    baselines = load_baselines()
    xml = _load_xml()

    def native_all() -> None:
        validate_iwxxm(
            xml,
            iwxxm_version=IWXXM_VERSION,
            profile="annex3",
            levels=("xsd", "schematron"),
        )

    native_p95 = _p95(native_all)
    # Composed lib_path baseline includes lint+convert; validate-only is a subset —
    # still soft-check against the hard ceiling as an early signal for T6.6.
    check = check_ratio(
        native_p95,
        baselines.lib_path_lxml_p95_s,
        ratio=baselines.lib_path_ratio,
        label="native_validate_vs_committed_lib_path_baseline",
    )
    apply_gate(check, hard=False)


def test_hard_mode_raises_on_over_ceiling(monkeypatch: pytest.MonkeyPatch) -> None:
    """Publish path: ``IWXXM_VALIDATE_HARD_PERF=1`` turns ratio miss into AssertionError."""
    monkeypatch.setenv(HARD_PERF_ENV, "1")
    assert hard_perf_enabled() is True
    check = check_ratio(1.0, 1.0, ratio=0.85, label="forced_over")
    assert check.ok is False
    with pytest.raises(AssertionError, match="HARD PERF"):
        apply_gate(check)


def test_soft_mode_warns_on_over_ceiling(monkeypatch: pytest.MonkeyPatch) -> None:
    """Build path: over-ceiling emits SOFT PERF warning (does not fail the test)."""
    monkeypatch.delenv(HARD_PERF_ENV, raising=False)
    check = check_ratio(1.0, 1.0, ratio=0.85, label="forced_over_soft")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        apply_gate(check, hard=False)
    assert any("SOFT PERF" in str(w.message) for w in caught)


def test_t35_records_native_observed_in_baselines_yaml() -> None:
    """Baselines YAML documents native soft-bench fields for T6.6 re-baseline."""
    data = yaml.safe_load((REPORTS / "perf-baselines.yaml").read_text(encoding="utf-8"))
    assert "native_soft_bench" in data
    native = data["native_soft_bench"]
    assert native["iwxxm_version"] == "2023-1"
    assert "validate_combined_note" in native
