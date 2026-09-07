"""T1.1-T1.2 / TC-F11-002: F11 layer cost matrix harness contract + timings."""

from __future__ import annotations

from pathlib import Path

import pytest
from scripts.bench import validation_stack as harness

REPO = Path(__file__).resolve().parents[2]
REPORT = (
    REPO
    / "docs"
    / "sessions"
    / "S014-package-publish-validation"
    / "reports"
    / "layer-cost-matrix.md"
)


def test_layers_cover_f11_matrix_scope() -> None:
    assert harness.LAYERS == (
        "lint",
        "convert_ir",
        "xsd",
        "schematron",
        "http_dto_pydantic",
        "http_dto_msgspec",
    )


def test_fixtures_cover_single_bulletin_golden() -> None:
    assert harness.FIXTURES == ("single_metar", "bulletin", "golden_iwxxm")


def test_load_fixtures_non_empty() -> None:
    loaded = harness.load_fixtures()
    assert set(loaded) == set(harness.FIXTURES)
    assert loaded["single_metar"].tac
    assert "METAR" in loaded["single_metar"].tac
    assert loaded["bulletin"].tac
    assert loaded["bulletin"].tac.count("METAR") >= 2
    assert loaded["golden_iwxxm"].xml
    assert "iwxxm:METAR" in loaded["golden_iwxxm"].xml
    for fid in harness.FIXTURES:
        assert loaded[fid].path.is_file()
        assert loaded[fid].path.is_relative_to(REPO)


def test_run_matrix_timings_shape() -> None:
    matrix = harness.run_matrix(iterations=5)
    assert matrix.implemented is True
    assert len(matrix.cells) == len(harness.LAYERS) * len(harness.FIXTURES)
    by_key = {(c.layer, c.fixture): c for c in matrix.cells}

    # TAC-only layers blocked on golden XML.
    assert by_key[("lint", "golden_iwxxm")].status == "blocked"
    assert by_key[("convert_ir", "golden_iwxxm")].status == "blocked"

    # Timed TAC path for single METAR.
    for layer in ("lint", "convert_ir", "xsd", "schematron"):
        cell = by_key[(layer, "single_metar")]
        assert cell.status == "ok"
        assert cell.p50_s is not None
        assert cell.p95_s is not None
        assert cell.p95_s >= cell.p50_s >= 0.0

    # HTTP encode paths always have XML (fixture or convert).
    for layer in ("http_dto_pydantic", "http_dto_msgspec"):
        for fid in harness.FIXTURES:
            cell = by_key[(layer, fid)]
            assert cell.status == "ok"
            assert cell.p50_s is not None
            assert cell.p95_s is not None


def test_matrix_as_dict_keys() -> None:
    payload = harness.matrix_as_dict(harness.run_matrix(iterations=3))
    assert payload["implemented"] is True
    assert payload["layers"] == list(harness.LAYERS)
    assert payload["fixtures"] == list(harness.FIXTURES)
    assert len(payload["cells"]) == len(harness.LAYERS) * len(harness.FIXTURES)


def test_makefile_bench_target_points_at_harness() -> None:
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    assert "bench-validation-stack:" in makefile
    assert "scripts/bench/validation_stack.py" in makefile


def test_write_report_and_main() -> None:
    assert harness.IMPLEMENTED is True
    matrix = harness.run_matrix(iterations=5)
    path = harness.write_layer_cost_report(matrix, path=REPORT)
    assert path == REPORT
    text = path.read_text(encoding="utf-8")
    assert "Layer cost matrix" in text
    assert "schematron" in text
    assert "Dominant layer" in text
    assert "xslt2" in text or "SCHEMATRON_SKIPPED" in text
    assert harness.main([]) == 0


@pytest.mark.parametrize("layer", harness.LAYERS)
def test_measure_layer_on_single_metar(layer: harness.LayerId) -> None:
    fixture = harness.load_fixtures()["single_metar"]
    timing = harness.measure_layer(layer, fixture, iterations=3)
    assert timing.layer == layer
    assert timing.status == "ok"
    assert timing.p50_s is not None
    assert timing.p95_s is not None
