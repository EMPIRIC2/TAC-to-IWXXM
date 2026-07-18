"""T1.1 / TC-F11-002: contract stubs for F11 layer cost matrix harness."""

from __future__ import annotations

from pathlib import Path

import pytest
from scripts.bench import validation_stack as harness

REPO = Path(__file__).resolve().parents[2]


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
    assert loaded["single_metar"].tac and "METAR" in loaded["single_metar"].tac
    assert loaded["bulletin"].tac and loaded["bulletin"].tac.count("METAR") >= 2
    assert loaded["golden_iwxxm"].xml and "iwxxm:METAR" in loaded["golden_iwxxm"].xml
    for fid in harness.FIXTURES:
        assert loaded[fid].path.is_file()
        assert loaded[fid].path.is_relative_to(REPO)


def test_run_matrix_stub_shape() -> None:
    matrix = harness.run_matrix()
    assert matrix.implemented is False
    assert len(matrix.cells) == len(harness.LAYERS) * len(harness.FIXTURES)
    by_key = {(c.layer, c.fixture): c for c in matrix.cells}
    for layer in harness.LAYERS:
        for fid in harness.FIXTURES:
            cell = by_key[(layer, fid)]
            assert cell.status == "stub"
            assert cell.p50_s is None
            assert cell.p95_s is None
            assert "T1.2" in cell.note


def test_matrix_as_dict_keys() -> None:
    payload = harness.matrix_as_dict(harness.run_matrix())
    assert payload["implemented"] is False
    assert payload["layers"] == list(harness.LAYERS)
    assert payload["fixtures"] == list(harness.FIXTURES)
    assert len(payload["cells"]) == len(harness.LAYERS) * len(harness.FIXTURES)


def test_makefile_bench_target_points_at_harness() -> None:
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    assert "bench-validation-stack:" in makefile
    assert "scripts/bench/validation_stack.py" in makefile


def test_main_fail_clear_while_stubbed() -> None:
    assert harness.IMPLEMENTED is False
    assert harness.main([]) == 1


@pytest.mark.parametrize("layer", harness.LAYERS)
def test_measure_layer_stub_per_layer(layer: harness.LayerId) -> None:
    fixture = harness.load_fixtures()["single_metar"]
    timing = harness.measure_layer(layer, fixture)
    assert timing.layer == layer
    assert timing.status == "stub"
    assert timing.p50_s is None and timing.p95_s is None
