"""T6.6 / E10-35: hard publish gates (HTTP always; lib when ``IWXXM_VALIDATE_HARD_PERF=1``).

Soft benches (T3.5 / T5.3) force ``hard=False``. This module exercises the publish
path: HTTP 1.0x must pass; lib 0.85x hard-fails under the env flip (see
``docs/sessions/S014-package-publish-validation/reports/t66-hard-publish-gates.md``).
"""

from __future__ import annotations

import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path

import msgspec
import pytest
from iwxxm_validate import rust_available, validate, validate_iwxxm
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
IWXXM_VERSION = "2023-1"
LIB_ITERATIONS = 11
HTTP_ITERATIONS = 51


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


def _p95(fn: Callable[[], object], iterations: int) -> float:
    fn()
    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return _percentile(samples, 95.0)


def _load_xml() -> str:
    if not VENDOR_METAR.is_file():
        pytest.skip(f"IWXXM fixture missing: {VENDOR_METAR}")
    return VENDOR_METAR.read_text(encoding="utf-8")


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


def _http_payloads() -> tuple[_PydResponse, _MsgResponse]:
    xml = (
        "<?xml version='1.0' encoding='utf-8'?>"
        "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2023-1'>"
        "<iwxxm:observationTime>2023-09-23T17:51:00Z</iwxxm:observationTime>"
        "</iwxxm:METAR>"
    )
    pyd = _PydResponse(
        results=[_PydResult(content=xml, size_bytes=len(xml))],
        total_processed=1,
        successful=1,
        failed=0,
    )
    msg = _MsgResponse(
        results=[
            _MsgResult(name="bench", content=xml, source="manual", size_bytes=len(xml))
        ],
        errors=[],
        total_processed=1,
        successful=1,
        failed=0,
    )
    return pyd, msg


def test_t66_http_hard_gates_pass() -> None:
    """Hard: msgspec encode / helper <= 1.0x pydantic map (E10-35 / T6.6)."""
    baselines = load_baselines()
    pyd, msg = _http_payloads()

    def pydantic_map() -> None:
        pyd.model_dump_json()

    def msgspec_encode() -> None:
        json_encoder.encode(msg)

    def helper_encode() -> None:
        msgspec_json_response(msg)

    pyd_p95 = _p95(pydantic_map, HTTP_ITERATIONS)
    msg_p95 = _p95(msgspec_encode, HTTP_ITERATIONS)
    helper_p95 = _p95(helper_encode, HTTP_ITERATIONS)

    apply_gate(
        check_ratio(
            msg_p95,
            pyd_p95,
            ratio=baselines.http_msgspec_ratio,
            label="t66_http_msgspec_vs_pydantic_map",
        ),
        hard=True,
    )
    apply_gate(
        check_ratio(
            helper_p95,
            baselines.http_pydantic_map_p95_s,
            ratio=baselines.http_msgspec_ratio,
            label="t66_http_helper_vs_committed_pydantic_baseline",
        ),
        hard=True,
    )


def test_t66_lib_hard_gates_under_env_flip() -> None:
    """Hard lib 0.85x only when publish env is set (does not fail default CI)."""
    if not hard_perf_enabled():
        pytest.skip(
            f"Set {HARD_PERF_ENV}=1 for T6.6 lib hard-fail "
            "(see t66-hard-publish-gates.md)"
        )
    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (maturin --release)")

    xml = _load_xml()

    def lxml_xsd() -> None:
        validate(xml, iwxxm_version=IWXXM_VERSION, profile="annex3", levels=("xsd",))

    def native_xsd() -> None:
        validate_iwxxm(
            xml, iwxxm_version=IWXXM_VERSION, profile="annex3", levels=("xsd",)
        )

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

    apply_gate(
        check_ratio(
            _p95(native_xsd, LIB_ITERATIONS),
            _p95(lxml_xsd, LIB_ITERATIONS),
            ratio=0.85,
            label="t66_native_xsd_vs_lxml",
        ),
        hard=True,
    )
    apply_gate(
        check_ratio(
            _p95(native_all, LIB_ITERATIONS),
            _p95(lxml_all, LIB_ITERATIONS),
            ratio=0.85,
            label="t66_native_validate_vs_lxml",
        ),
        hard=True,
    )


def test_t66_report_exists() -> None:
    report = (
        REPO_ROOT
        / "docs"
        / "sessions"
        / "S014-package-publish-validation"
        / "reports"
        / "t66-hard-publish-gates.md"
    )
    assert report.is_file()
    text = report.read_text(encoding="utf-8")
    assert "0.85" in text
    assert "PARTIAL" in text or "PASS" in text
