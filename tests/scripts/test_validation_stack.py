"""EV-080 M4 — 100% coverage for scripts/bench/validation_stack.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from scripts.bench import validation_stack as mod

ROOT = Path(__file__).resolve().parents[2]


def test_percentile_and_fmt_seconds() -> None:
    with pytest.raises(ValueError, match="empty samples"):
        mod._percentile([], 50.0)
    assert mod._percentile([2.0], 50.0) == 2.0
    assert mod._percentile([1.0, 2.0, 3.0, 4.0], 95.0) > 3.0
    assert mod._fmt_seconds(None) == "—"
    assert "us" in mod._fmt_seconds(0.0000005)
    assert "ms" in mod._fmt_seconds(0.01)
    assert mod._fmt_seconds(2.5).endswith("s")


def test_load_fixtures_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        mod,
        "_fixture_paths",
        lambda: {"single_metar": tmp_path / "missing.tac"},
    )
    with pytest.raises(FileNotFoundError, match="bench fixture missing"):
        mod.load_fixtures()

    empty = tmp_path / "empty.tac"
    empty.write_text("   \n", encoding="utf-8")
    monkeypatch.setattr(
        mod,
        "_fixture_paths",
        lambda: {"single_metar": empty},
    )
    with pytest.raises(ValueError, match="bench fixture empty"):
        mod.load_fixtures()


def test_resolve_xml_and_blocked_layers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    golden = mod.BenchFixture(
        id="golden_iwxxm",
        tac=None,
        xml="<xml/>",
        path=Path("x"),
    )
    assert mod.measure_layer("lint", golden, iterations=1).status == "blocked"
    assert mod.measure_layer("convert_ir", golden, iterations=1).status == "blocked"

    no_payload = mod.BenchFixture(id="single_metar", tac=None, xml=None, path=Path("x"))
    blocked = mod.measure_layer("xsd", no_payload, iterations=1)
    assert blocked.status == "blocked"
    assert blocked.note == "no tac or xml"

    tac_only = mod.BenchFixture(
        id="single_metar", tac="METAR KJFK 010000Z=", xml=None, path=Path("x")
    )

    def _bad_convert(*_a: object, **_k: object) -> SimpleNamespace:
        return SimpleNamespace(ok=False, xml=None)

    import tac2iwxxm

    monkeypatch.setattr(tac2iwxxm, "convert", _bad_convert)
    monkeypatch.setattr(
        mod,
        "convert",
        _bad_convert,
        raising=False,
    )
    blocked2 = mod.measure_layer("xsd", tac_only, iterations=1)
    assert blocked2.status == "blocked"
    assert "convert failed" in blocked2.note


def test_measure_layer_unknown_raises() -> None:
    fixture = mod.load_fixtures()["single_metar"]
    with pytest.raises(ValueError, match="unknown layer"):
        mod.measure_layer("not-a-layer", fixture)  # type: ignore[arg-type]


def test_run_matrix_and_report(tmp_path: Path) -> None:
    import importlib

    importlib.invalidate_caches()
    # Ensure real tac_validate package (not Suite stubs) is importable.
    sys.modules.pop("tac_validate", None)
    for key in list(sys.modules):
        if key.startswith("tac_validate."):
            sys.modules.pop(key, None)
    matrix = mod.run_matrix(iterations=3)
    assert matrix.implemented is True
    assert len(matrix.cells) == len(mod.LAYERS) * len(mod.FIXTURES)

    payload = mod.matrix_as_dict(matrix)
    assert payload["layers"] == list(mod.LAYERS)

    report = mod.write_layer_cost_report(matrix, path=tmp_path / "report.md")
    text = report.read_text(encoding="utf-8")
    assert "Layer cost matrix" in text
    assert "Dominant layer" in text
    assert "Mean p95 by layer" in text


def test_write_report_no_ok_cells(tmp_path: Path) -> None:
    cells = tuple(
        mod.LayerTiming(layer, fid, None, None, "blocked", note="x")
        for layer in mod.LAYERS
        for fid in mod.FIXTURES
    )
    matrix = mod.LayerCostMatrix(
        cells=cells,
        implemented=True,
        iwxxm_version="2025-2",
        profile="annex3",
    )
    text = mod.write_layer_cost_report(matrix, path=tmp_path / "empty.md").read_text(
        encoding="utf-8"
    )
    assert "No timed cells" in text
    assert "blocked / n/a" in text


def test_main_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    sys.modules.pop("tac_validate", None)
    for key in list(sys.modules):
        if key.startswith("tac_validate."):
            sys.modules.pop(key, None)
    matrix = mod.run_matrix(iterations=2)
    monkeypatch.setattr(mod, "run_matrix", lambda **_k: matrix)
    monkeypatch.setattr(
        mod, "write_layer_cost_report", lambda m, path=None: tmp_path / "r.md"
    )
    assert mod.main([]) == 0


def test_percentile_lo_equals_hi() -> None:
    assert mod._percentile([1.0, 2.0], 100.0) == 2.0


def test_main_not_implemented(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    matrix = mod.LayerCostMatrix(
        cells=(),
        implemented=False,
        iwxxm_version="2025-2",
        profile="annex3",
    )
    monkeypatch.setattr(mod, "run_matrix", lambda **_k: matrix)
    monkeypatch.setattr(
        mod, "write_layer_cost_report", lambda m, path=None: tmp_path / "r.md"
    )
    assert mod.main([]) == 1


def test_measure_layer_unhandled_assertion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(mod, "LAYERS", (*mod.LAYERS, "orphan"))
    fixture = mod.load_fixtures()["single_metar"]
    with pytest.raises(AssertionError, match="unhandled layer"):
        mod.measure_layer("orphan", fixture)  # type: ignore[arg-type]


def test_main_entrypoint_subprocess() -> None:
    import sys

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/bench/validation_stack.py")],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0
