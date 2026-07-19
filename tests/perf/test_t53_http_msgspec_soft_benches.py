"""T5.3 / E10-35: soft HTTP bench - msgspec encode <= 1.0x pydantic map baseline.

Soft until publish (T6.6): over-ceiling results warn only unless
``IWXXM_VALIDATE_HARD_PERF=1``.
"""

from __future__ import annotations

import sys
import time
import warnings
from collections.abc import Callable, Sequence
from pathlib import Path

import msgspec
import pytest
from pydantic import BaseModel, Field
from scripts.bench.perf_gates import (
    HARD_PERF_ENV,
    apply_gate,
    check_ratio,
    hard_perf_enabled,
    load_baselines,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = REPO_ROOT / "apps" / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from msgspec_http import json_encoder, msgspec_json_response  # noqa: E402

ITERATIONS = 51


class _PydResult(BaseModel):
    name: str = "bench"
    content: str
    source: str = "manual"
    size_bytes: int = Field(ge=0)


class _PydResponse(BaseModel):
    results: list[_PydResult]
    errors: list[str] = Field(default_factory=list)
    total_processed: int = Field(ge=0)
    successful: int = Field(ge=0)
    failed: int = Field(ge=0)


class _MsgResult(msgspec.Struct, frozen=True):
    name: str
    content: str
    source: str
    size_bytes: int


class _MsgResponse(msgspec.Struct, frozen=True):
    results: list[_MsgResult]
    errors: list[str]
    total_processed: int
    successful: int
    failed: int


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
    fn()  # warmup
    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return _percentile(samples, 95.0)


def _sample_xml() -> str:
    return (
        "<?xml version='1.0' encoding='utf-8'?>"
        "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2023-1'>"
        "<iwxxm:observationTime>2023-09-23T17:51:00Z</iwxxm:observationTime>"
        "</iwxxm:METAR>"
    )


def _payloads() -> tuple[_PydResponse, _MsgResponse]:
    xml = _sample_xml()
    pyd = _PydResponse(
        results=[
            _PydResult(
                name="manual_input.txt",
                content=xml,
                source="manual",
                size_bytes=len(xml),
            )
        ],
        errors=[],
        total_processed=1,
        successful=1,
        failed=0,
    )
    msg = _MsgResponse(
        results=[
            _MsgResult(
                name="manual_input.txt",
                content=xml,
                source="manual",
                size_bytes=len(xml),
            )
        ],
        errors=[],
        total_processed=1,
        successful=1,
        failed=0,
    )
    return pyd, msg


def test_http_msgspec_gate_baselines_wired() -> None:
    """T1.3 ceilings + 1.0x HTTP ratio available for T5.3 / T6.6."""
    baselines = load_baselines()
    assert baselines.http_msgspec_ratio == pytest.approx(1.0)
    assert baselines.http_msgspec_hard_ceiling_p95_s == pytest.approx(
        1.0 * baselines.http_pydantic_map_p95_s
    )
    assert HARD_PERF_ENV == "IWXXM_VALIDATE_HARD_PERF"
    assert hard_perf_enabled() is False


def test_soft_bench_msgspec_vs_same_run_pydantic_map() -> None:
    """Soft: msgspec encode p95 <= 1.0x same-run pydantic model_dump_json (E10-35)."""
    pyd, msg = _payloads()

    def pydantic_map() -> None:
        pyd.model_dump_json()

    def msgspec_encode() -> None:
        json_encoder.encode(msg)

    pyd_p95 = _p95(pydantic_map)
    msg_p95 = _p95(msgspec_encode)
    check = check_ratio(
        msg_p95,
        pyd_p95,
        ratio=1.0,
        label="http_msgspec_vs_pydantic_map",
    )
    apply_gate(check, hard=False)


def test_soft_bench_msgspec_helper_vs_committed_ceiling() -> None:
    """Soft: ``msgspec_json_response`` path vs committed T1.3 HTTP ceiling."""
    baselines = load_baselines()
    _, msg = _payloads()

    def helper_encode() -> None:
        msgspec_json_response(msg)

    helper_p95 = _p95(helper_encode)
    check = check_ratio(
        helper_p95,
        baselines.http_pydantic_map_p95_s,
        ratio=baselines.http_msgspec_ratio,
        label="http_msgspec_helper_vs_committed_pydantic_baseline",
    )
    apply_gate(check, hard=False)


def test_soft_bench_helper_with_pydantic_alias_dump() -> None:
    """OpenAPI alias models dump then msgspec-encode (T5.2 path) stays <= 1.0x map."""
    pyd, _ = _payloads()

    def pydantic_map() -> None:
        pyd.model_dump_json()

    def helper_via_alias() -> None:
        msgspec_json_response(pyd)

    pyd_p95 = _p95(pydantic_map)
    helper_p95 = _p95(helper_via_alias)
    # Helper includes model_dump + encode; soft-check vs dump_json alone may warn -
    # still useful signal; hard gate at T6.6 uses Struct encode vs committed ceiling.
    check = check_ratio(
        helper_p95,
        pyd_p95,
        ratio=1.0,
        label="http_msgspec_helper_alias_vs_pydantic_dump_json",
    )
    apply_gate(check, hard=False)


def test_http_hard_mode_raises_on_over_ceiling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(HARD_PERF_ENV, "1")
    check = check_ratio(1.1, 1.0, ratio=1.0, label="forced_http_over")
    assert check.ok is False
    with pytest.raises(AssertionError, match="HARD PERF"):
        apply_gate(check)


def test_http_soft_mode_warns_on_over_ceiling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(HARD_PERF_ENV, raising=False)
    check = check_ratio(1.1, 1.0, ratio=1.0, label="forced_http_over_soft")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        apply_gate(check, hard=False)
    assert any("SOFT PERF" in str(w.message) for w in caught)
