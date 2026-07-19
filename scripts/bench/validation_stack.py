"""
Layer cost matrix harness (F11 / TC-F11-002 / T1.1-T1.2).

Measures TAC lint, convert IR, XSD, Schematron, and HTTP DTO encode
(pydantic map vs msgspec) on single METAR, bulletin, and golden IWXXM fixtures.
"""

from __future__ import annotations

import statistics
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Literal

import msgspec
from iwxxm_validate import validate
from pydantic import BaseModel, Field
from tac_validate import lint

from tac2iwxxm import convert

RepoRoot = Path(__file__).resolve().parents[2]
_FIXTURES = RepoRoot / "packages" / "tac2iwxxm" / "tests" / "fixtures"
_REPORT_PATH = (
    RepoRoot
    / "docs"
    / "sessions"
    / "S014-package-publish-validation"
    / "reports"
    / "layer-cost-matrix.md"
)

LayerId = Literal[
    "lint",
    "convert_ir",
    "xsd",
    "schematron",
    "http_dto_pydantic",
    "http_dto_msgspec",
]
FixtureId = Literal["single_metar", "bulletin", "golden_iwxxm"]

LAYERS: Final[tuple[LayerId, ...]] = (
    "lint",
    "convert_ir",
    "xsd",
    "schematron",
    "http_dto_pydantic",
    "http_dto_msgspec",
)
FIXTURES: Final[tuple[FixtureId, ...]] = (
    "single_metar",
    "bulletin",
    "golden_iwxxm",
)

IMPLEMENTED: Final[bool] = True

DEFAULT_IWXXM_VERSION: Final[str] = "2025-2"
DEFAULT_PROFILE: Final[str] = "annex3"
DEFAULT_PRODUCT: Final[str] = "METAR"

_MSGSPEC_ENCODER = msgspec.json.Encoder()


@dataclass(frozen=True, slots=True)
class BenchFixture:
    """Loaded fixture payload for a layer-cost run."""

    id: FixtureId
    tac: str | None
    xml: str | None
    path: Path


@dataclass(frozen=True, slots=True)
class LayerTiming:
    """p50/p95 seconds for one layer x fixture cell."""

    layer: LayerId
    fixture: FixtureId
    p50_s: float | None
    p95_s: float | None
    status: Literal["stub", "ok", "blocked"]
    note: str = ""


@dataclass(frozen=True, slots=True)
class LayerCostMatrix:
    """Full layer x fixture timing grid for TC-F11-002."""

    cells: tuple[LayerTiming, ...]
    implemented: bool
    iwxxm_version: str
    profile: str


class _HttpDtoResult(BaseModel):
    """Minimal ConversionResponse-shaped payload for encode benches."""

    name: str = "bench"
    content: str
    source: str = "manual"
    size_bytes: int = Field(ge=0)


class _HttpDtoResponse(BaseModel):
    """Pydantic HTTP DTO stand-in for convert response encode cost."""

    results: list[_HttpDtoResult]
    errors: list[str] = Field(default_factory=list)
    total_processed: int = Field(ge=0)
    successful: int = Field(ge=0)
    failed: int = Field(ge=0)


class _MsgspecDtoResult(msgspec.Struct, frozen=True):
    name: str
    content: str
    source: str
    size_bytes: int


class _MsgspecDtoResponse(msgspec.Struct, frozen=True):
    results: list[_MsgspecDtoResult]
    errors: list[str]
    total_processed: int
    successful: int
    failed: int


def _fixture_paths() -> Mapping[FixtureId, Path]:
    return {
        "single_metar": _FIXTURES / "annex3_golden" / "metar_basic.tac",
        "bulletin": _FIXTURES / "metar_multi_ahl.txt",
        "golden_iwxxm": _FIXTURES / "annex3_golden" / "metar_basic.golden.xml",
    }


def load_fixtures() -> dict[FixtureId, BenchFixture]:
    """
    Load single-METAR TAC, multi-report bulletin, and golden IWXXM XML.

    Returns
    -------
    dict[FixtureId, BenchFixture]
        Non-empty payloads for each required fixture id.

    Raises
    ------
    FileNotFoundError
        If a pinned fixture path is missing.
    ValueError
        If a fixture file is empty.
    """
    loaded: dict[FixtureId, BenchFixture] = {}
    for fid, path in _fixture_paths().items():
        if not path.is_file():
            raise FileNotFoundError(f"bench fixture missing: {path}")
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError(f"bench fixture empty: {path}")
        if fid == "golden_iwxxm":
            loaded[fid] = BenchFixture(id=fid, tac=None, xml=text, path=path)
        else:
            loaded[fid] = BenchFixture(id=fid, tac=text, xml=None, path=path)
    return loaded


def _percentile(samples: Sequence[float], pct: float) -> float:
    """Return nearest-rank percentile (``pct`` in 0..100)."""
    if not samples:
        msg = "empty samples"
        raise ValueError(msg)
    ordered = sorted(samples)
    if len(ordered) == 1:
        return ordered[0]
    # statistics.quantiles needs n>=2; use inclusive rank for p50/p95.
    rank = (pct / 100.0) * (len(ordered) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(ordered) - 1)
    if lo == hi:
        return ordered[lo]
    frac = rank - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def _time_call(fn: Callable[[], Any], iterations: int) -> tuple[float, float]:
    samples: list[float] = []
    # Warmup once so first-import / schema compile is not the only sample.
    fn()
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return _percentile(samples, 50.0), _percentile(samples, 95.0)


def _resolve_xml(
    fixture: BenchFixture,
    *,
    iwxxm_version: str,
    profile: str,
) -> tuple[str | None, str]:
    if fixture.xml:
        return fixture.xml, "fixture xml"
    if not fixture.tac:
        return None, "no tac or xml"
    result = convert(
        fixture.tac,
        product=DEFAULT_PRODUCT,
        profile=profile,
        iwxxm_version=iwxxm_version,
    )
    if not result.ok or not result.xml:
        return None, "convert failed for xml layers"
    return result.xml, "converted from tac"


def _http_payload(xml: str) -> tuple[_HttpDtoResponse, _MsgspecDtoResponse]:
    pydantic_model = _HttpDtoResponse(
        results=[
            _HttpDtoResult(
                name="bench.xml",
                content=xml,
                source="manual",
                size_bytes=len(xml.encode("utf-8")),
            )
        ],
        errors=[],
        total_processed=1,
        successful=1,
        failed=0,
    )
    msgspec_model = _MsgspecDtoResponse(
        results=[
            _MsgspecDtoResult(
                name="bench.xml",
                content=xml,
                source="manual",
                size_bytes=len(xml.encode("utf-8")),
            )
        ],
        errors=[],
        total_processed=1,
        successful=1,
        failed=0,
    )
    return pydantic_model, msgspec_model


def measure_layer(
    layer: LayerId,
    fixture: BenchFixture,
    *,
    iterations: int = 21,
    iwxxm_version: str = DEFAULT_IWXXM_VERSION,
    profile: str = DEFAULT_PROFILE,
) -> LayerTiming:
    """
    Time one validation-stack layer on one fixture.

    Parameters
    ----------
    layer :
        Layer id from ``LAYERS``.
    fixture :
        Loaded ``BenchFixture``.
    iterations :
        Sample count for p50/p95 after one warmup call.
    iwxxm_version :
        IWXXM release line for convert/validate layers.
    profile :
        ``annex3`` or ``iwxxm_us``.

    Returns
    -------
    LayerTiming
        Timed cell, or ``blocked`` when the fixture cannot feed the layer.
    """
    if layer not in LAYERS:
        msg = f"unknown layer: {layer!r}"
        raise ValueError(msg)

    if layer == "lint":
        if not fixture.tac:
            return LayerTiming(
                layer=layer,
                fixture=fixture.id,
                p50_s=None,
                p95_s=None,
                status="blocked",
                note="lint requires TAC; golden IWXXM is XML-only",
            )

        def _lint() -> None:
            lint(fixture.tac or "", product=DEFAULT_PRODUCT)

        p50, p95 = _time_call(_lint, iterations)
        return LayerTiming(layer, fixture.id, p50, p95, "ok")

    if layer == "convert_ir":
        if not fixture.tac:
            return LayerTiming(
                layer=layer,
                fixture=fixture.id,
                p50_s=None,
                p95_s=None,
                status="blocked",
                note="convert_ir requires TAC; golden IWXXM is XML-only",
            )

        def _convert() -> None:
            convert(
                fixture.tac or "",
                product=DEFAULT_PRODUCT,
                profile=profile,
                iwxxm_version=iwxxm_version,
            )

        p50, p95 = _time_call(_convert, iterations)
        return LayerTiming(layer, fixture.id, p50, p95, "ok")

    xml, xml_note = _resolve_xml(
        fixture, iwxxm_version=iwxxm_version, profile=profile
    )
    if xml is None:
        return LayerTiming(
            layer=layer,
            fixture=fixture.id,
            p50_s=None,
            p95_s=None,
            status="blocked",
            note=xml_note,
        )

    if layer == "xsd":

        def _xsd() -> None:
            validate(
                xml,
                iwxxm_version=iwxxm_version,
                profile=profile,
                levels=("xsd",),
            )

        p50, p95 = _time_call(_xsd, iterations)
        return LayerTiming(layer, fixture.id, p50, p95, "ok", note=xml_note)

    if layer == "schematron":

        def _sch() -> None:
            validate(
                xml,
                iwxxm_version=iwxxm_version,
                profile=profile,
                levels=("schematron",),
            )

        p50, p95 = _time_call(_sch, iterations)
        return LayerTiming(layer, fixture.id, p50, p95, "ok", note=xml_note)

    pydantic_model, msgspec_model = _http_payload(xml)
    if layer == "http_dto_pydantic":

        def _pyd() -> None:
            pydantic_model.model_dump_json()

        p50, p95 = _time_call(_pyd, iterations)
        return LayerTiming(layer, fixture.id, p50, p95, "ok", note=xml_note)

    if layer == "http_dto_msgspec":

        def _msg() -> None:
            _MSGSPEC_ENCODER.encode(msgspec_model)

        p50, p95 = _time_call(_msg, iterations)
        return LayerTiming(layer, fixture.id, p50, p95, "ok", note=xml_note)

    msg = f"unhandled layer: {layer!r}"
    raise AssertionError(msg)


def run_matrix(
    *,
    iterations: int = 21,
    iwxxm_version: str = DEFAULT_IWXXM_VERSION,
    profile: str = DEFAULT_PROFILE,
) -> LayerCostMatrix:
    """
    Run every layer x fixture cell for the layer cost matrix.

    Returns
    -------
    LayerCostMatrix
        Structured grid with p50/p95 when measurable.
    """
    fixtures = load_fixtures()
    cells: list[LayerTiming] = []
    for layer in LAYERS:
        for fid in FIXTURES:
            cells.append(
                measure_layer(
                    layer,
                    fixtures[fid],
                    iterations=iterations,
                    iwxxm_version=iwxxm_version,
                    profile=profile,
                )
            )
    return LayerCostMatrix(
        cells=tuple(cells),
        implemented=IMPLEMENTED,
        iwxxm_version=iwxxm_version,
        profile=profile,
    )


def matrix_as_dict(matrix: LayerCostMatrix) -> dict[str, Any]:
    """Serialize ``LayerCostMatrix`` for reports / JSON dumps."""
    return {
        "implemented": matrix.implemented,
        "iwxxm_version": matrix.iwxxm_version,
        "profile": matrix.profile,
        "layers": list(LAYERS),
        "fixtures": list(FIXTURES),
        "cells": [asdict(cell) for cell in matrix.cells],
    }


def _fmt_seconds(value: float | None) -> str:
    if value is None:
        return "—"
    if value < 0.001:
        return f"{value * 1e6:.1f} us"
    if value < 1.0:
        return f"{value * 1e3:.2f} ms"
    return f"{value:.3f} s"


def write_layer_cost_report(
    matrix: LayerCostMatrix,
    path: Path | None = None,
) -> Path:
    """
    Write markdown p50/p95 matrix under the S014 session reports dir.

    Parameters
    ----------
    matrix :
        Completed ``LayerCostMatrix``.
    path :
        Output path (default: session ``layer-cost-matrix.md``).

    Returns
    -------
    Path
        Path written.
    """
    out = path or _REPORT_PATH
    out.parent.mkdir(parents=True, exist_ok=True)

    ok_cells = [c for c in matrix.cells if c.status == "ok" and c.p95_s is not None]
    dominant = max(ok_cells, key=lambda c: c.p95_s or 0.0) if ok_cells else None

    lines: list[str] = [
        "# Layer cost matrix (F11 / TC-F11-002)",
        "",
        f"- **IWXXM version**: `{matrix.iwxxm_version}`",
        f"- **Profile**: `{matrix.profile}`",
        f"- **Implemented**: `{matrix.implemented}`",
        "- **Iterations**: 21 timed samples + 1 warmup per cell",
        "- **Generated by**: `scripts/bench/validation_stack.py` (T1.2)",
        "",
        "## p95 by layer x fixture (seconds)",
        "",
        "| Layer | single_metar | bulletin | golden_iwxxm |",
        "|-------|-------------:|---------:|-------------:|",
    ]
    for layer in LAYERS:
        row = [layer]
        for fid in FIXTURES:
            cell = next(c for c in matrix.cells if c.layer == layer and c.fixture == fid)
            if cell.status != "ok":
                row.append(cell.status)
            else:
                row.append(f"{cell.p95_s:.6f}" if cell.p95_s is not None else "—")
        lines.append("| " + " | ".join(row) + " |")

    lines.extend(
        [
            "",
            "## p50 by layer x fixture (seconds)",
            "",
            "| Layer | single_metar | bulletin | golden_iwxxm |",
            "|-------|-------------:|---------:|-------------:|",
        ]
    )
    for layer in LAYERS:
        row = [layer]
        for fid in FIXTURES:
            cell = next(c for c in matrix.cells if c.layer == layer and c.fixture == fid)
            if cell.status != "ok":
                row.append(cell.status)
            else:
                row.append(f"{cell.p50_s:.6f}" if cell.p50_s is not None else "—")
        lines.append("| " + " | ".join(row) + " |")

    lines.extend(["", "## Human-readable p95", ""])
    for layer in LAYERS:
        for fid in FIXTURES:
            cell = next(c for c in matrix.cells if c.layer == layer and c.fixture == fid)
            lines.append(
                f"- **{layer}** / **{fid}**: {_fmt_seconds(cell.p95_s)} "
                f"({cell.status}"
                f"{'; ' + cell.note if cell.note else ''})"
            )

    lines.extend(["", "## Dominant layer", ""])
    if dominant is None:
        lines.append("_No timed cells — cannot identify dominant layer._")
    else:
        lines.append(
            f"**{dominant.layer}** on **{dominant.fixture}** leads p95 at "
            f"**{_fmt_seconds(dominant.p95_s)}** "
            f"({'Schematron identified as dominant' if dominant.layer == 'schematron' else 'evidence contradicts Schematron-as-dominant assumption'})."
        )
    lines.extend(
        [
            "",
            "### Caveat — Schematron path",
            "",
            "Current `iwxxm-validate` lxml isoschematron **skips** XSLT2 Schematron for "
            "`2025-2` (`SCHEMATRON_SKIPPED` / D-S008-T21-sch). Timed `schematron` cells "
            "therefore measure the skip/early-return path, **not** full SVRL evaluation. "
            "Treat Schematron dominance as **unverified until F13 Rust Schematron** "
            "(T3.3/T3.5) re-runs this matrix.",
            "",
        ]
    )

    # Mean p95 across fixtures per layer (ok cells only) for a clearer summary.
    lines.extend(["", "## Mean p95 by layer (ok cells)", ""])
    for layer in LAYERS:
        vals = [
            c.p95_s
            for c in matrix.cells
            if c.layer == layer and c.status == "ok" and c.p95_s is not None
        ]
        if not vals:
            lines.append(f"- **{layer}**: blocked / n/a")
        else:
            mean = statistics.fmean(vals)
            lines.append(f"- **{layer}**: {_fmt_seconds(mean)} (n={len(vals)})")

    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry for ``make bench-validation-stack``.

    Returns
    -------
    int
        ``0`` after timings + report write; ``1`` on failure.
    """
    _ = argv
    matrix = run_matrix()
    report = write_layer_cost_report(matrix)
    print(
        f"layer-cost harness: implemented={matrix.implemented} "
        f"cells={len(matrix.cells)} version={matrix.iwxxm_version}"
    )
    print(f"wrote {report}")
    if not matrix.implemented:
        print(
            "error: timings not implemented yet "
            "(execution plan T1.2 — write p50/p95 + layer-cost-matrix.md)",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
