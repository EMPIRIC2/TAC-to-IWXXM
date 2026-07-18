"""
Layer cost matrix harness stubs (F11 / TC-F11-002 / T1.1).

Measures (once T1.2 implements ``measure_layer``): TAC lint, convert IR, XSD,
Schematron, and HTTP DTO encode (pydantic map vs msgspec) on single METAR,
bulletin, and golden IWXXM fixtures.

Until T1.2, ``run_matrix`` returns a structured stub with ``status="stub"``
and null timings; ``main`` exits 1 so ``make bench-validation-stack`` stays
fail-clear.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Literal

RepoRoot = Path(__file__).resolve().parents[2]
_FIXTURES = RepoRoot / "packages" / "tac2iwxxm" / "tests" / "fixtures"

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

# T1.2 flips this after real timing + matrix report land.
IMPLEMENTED: Final[bool] = False

DEFAULT_IWXXM_VERSION: Final[str] = "2025-2"
DEFAULT_PROFILE: Final[str] = "annex3"
DEFAULT_PRODUCT: Final[str] = "METAR"


@dataclass(frozen=True, slots=True)
class BenchFixture:
    """Loaded fixture payload for a layer-cost run."""

    id: FixtureId
    tac: str | None
    xml: str | None
    path: Path


@dataclass(frozen=True, slots=True)
class LayerTiming:
    """p50/p95 seconds for one layer x fixture cell (None while stubbed)."""

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


def measure_layer(
    layer: LayerId,
    fixture: BenchFixture,
    *,
    iterations: int = 21,
    iwxxm_version: str = DEFAULT_IWXXM_VERSION,
    profile: str = DEFAULT_PROFILE,
) -> LayerTiming:
    """
    Time one validation-stack layer on one fixture (stub until T1.2).

    Parameters
    ----------
    layer :
        Layer id from ``LAYERS``.
    fixture :
        Loaded ``BenchFixture``.
    iterations :
        Sample count for p50/p95 (used by T1.2 implementation).
    iwxxm_version :
        IWXXM release line for convert/validate layers.
    profile :
        ``annex3`` or ``iwxxm_us``.

    Returns
    -------
    LayerTiming
        Stub cell with null timings while ``IMPLEMENTED`` is False.
    """
    _ = (iterations, iwxxm_version, profile, fixture)
    if layer not in LAYERS:
        msg = f"unknown layer: {layer!r}"
        raise ValueError(msg)
    return LayerTiming(
        layer=layer,
        fixture=fixture.id,
        p50_s=None,
        p95_s=None,
        status="stub",
        note="T1.2: implement measure_layer timings",
    )


def run_matrix(
    *,
    iterations: int = 21,
    iwxxm_version: str = DEFAULT_IWXXM_VERSION,
    profile: str = DEFAULT_PROFILE,
) -> LayerCostMatrix:
    """
    Run (or stub) every layer x fixture cell for the layer cost matrix.

    Returns
    -------
    LayerCostMatrix
        Structured grid; timings remain null until T1.2.
    """
    fixtures = load_fixtures()
    cells: list[LayerTiming] = []
    for layer in LAYERS:
        for fid in FIXTURES:
            # XML-only layers skip TAC fixtures at measure time in T1.2; stubs
            # still emit a cell so the matrix shape is stable for tests.
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


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry for ``make bench-validation-stack``.

    Returns
    -------
    int
        ``1`` while stubbed (T1.1); ``0`` after T1.2 writes timings.
    """
    _ = argv
    matrix = run_matrix()
    print(
        f"layer-cost harness: implemented={matrix.implemented} "
        f"cells={len(matrix.cells)} version={matrix.iwxxm_version}"
    )
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
