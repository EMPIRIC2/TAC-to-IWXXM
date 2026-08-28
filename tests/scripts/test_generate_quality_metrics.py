"""EV-080 M4 — 100% coverage for scripts/ci/generate_quality_metrics.py."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest
from scripts.ci import generate_quality_metrics as mod

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class _Peer:
    stem: str
    disposition: str = "registered"
    catalog_id: str = "cat1"
    product: str | None = "METAR"
    deferral_reason: str | None = None


def test_helpers() -> None:
    assert mod._product_key(" METAR ") == "metar"
    issue = SimpleNamespace(
        severity="error",
        code="X",
        message="m",
        location="loc",
        start=0,
        end=1,
        layer="xsd",
    )
    lint = mod._serialize_lint_issues([issue])
    assert lint[0]["location"] == "loc"
    val = mod._serialize_validate_issues([issue])
    assert val[0]["layer"] == "xsd"
    assert mod._error_count([{"severity": "error"}, {"severity": "warn"}]) == 1


def test_build_summaries_all_branches() -> None:
    files = [
        {
            "product": "metar",
            "deferred": True,
            "match_status": "deferred",
            "residual_count": 0,
            "lint_error_count": 0,
            "validate_error_count": 0,
        },
        {
            "product": "metar",
            "deferred": False,
            "match_status": "equal",
            "residual_count": 1,
            "lint_error_count": 1,
            "validate_error_count": 1,
        },
        {
            "product": "metar",
            "deferred": False,
            "match_status": "unequal",
            "residual_count": 0,
            "lint_error_count": 0,
            "validate_error_count": 0,
        },
    ]
    summaries = mod._build_summaries(files)
    by = {s["product"]: s for s in summaries}
    assert by["metar"]["deferred_gaps"] == 1
    assert by["metar"]["match_pass"] == 1
    assert by["metar"]["match_fail"] == 1
    assert by["metar"]["residual_nonempty"] == 1
    assert by["metar"]["lint_fail"] == 1
    assert by["metar"]["validate_fail"] == 1


def test_generate_corpus_metrics_branches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    deferred = _Peer("deferred-stem", disposition="deferred", deferral_reason="later")
    active = _Peer("metar-A3-1", catalog_id="metar_a3_1", product="METAR")
    vendor = tmp_path / "vendor"
    vendor.mkdir()
    (vendor / "metar-A3-1.xml").write_text("<converted/>\n", encoding="utf-8")
    monkeypatch.setattr(mod, "_VENDOR_EXAMPLES", vendor)
    monkeypatch.setattr(mod, "_FIXTURES", tmp_path / "fixtures")
    monkeypatch.setattr(mod, "_OUT_DIR", tmp_path / "out")
    monkeypatch.setattr(mod, "_OUT_PATH", tmp_path / "out" / "corpus_metrics.json")

    tac_dir = tmp_path / "fixtures" / "annex3_golden"
    tac_dir.mkdir(parents=True)
    tac_file = tac_dir / "metar_a3_1.tac"
    tac_file.write_text("METAR KJFK 010000Z=\n", encoding="utf-8")

    def _annex3_path(peer: _Peer) -> Path:
        return tac_file

    fake_inventory = SimpleNamespace(
        OFFICIAL_TAC_PEERS=(deferred, active),
        annex3_path=_annex3_path,
    )
    sys.modules.pop("wmo_official_tac_inventory", None)
    monkeypatch.setitem(
        sys.modules,
        "wmo_official_tac_inventory",
        fake_inventory,
    )

    convert_calls: list[str] = []

    def _convert(tac: str, **_k: object) -> SimpleNamespace:
        convert_calls.append(tac)
        return SimpleNamespace(ok=True, xml="<converted/>")

    monkeypatch.setitem(
        sys.modules,
        "tac2iwxxm",
        SimpleNamespace(
            convert=_convert,
            decode_tac=lambda *_a, **_k: SimpleNamespace(residuals=[]),
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "tac_validate",
        SimpleNamespace(lint=lambda *_a, **_k: SimpleNamespace(issues=[])),
    )
    import types as types_mod

    iwxxm_pkg = types_mod.ModuleType("iwxxm_validate")
    iwxxm_pkg.__path__ = []  # type: ignore[attr-defined]
    c14n_mod = types_mod.ModuleType("iwxxm_validate.c14n")
    c14n_mod.c14n_equal = lambda a, b: True  # type: ignore[attr-defined]
    sys.modules["iwxxm_validate"] = iwxxm_pkg
    sys.modules["iwxxm_validate.c14n"] = c14n_mod
    iwxxm_pkg.validate_for_quality_metrics = lambda *_a, **_k: SimpleNamespace(
        issues=[]
    )  # type: ignore[attr-defined]

    monkeypatch.setattr(mod, "_ensure_imports", lambda: None)

    doc = mod.generate_corpus_metrics()
    assert len(doc["files"]) == 2
    assert doc["details"]["deferred-stem"]["deferred"] is True
    assert doc["details"]["metar-A3-1"]["match_status"] == "equal"


def test_generate_corpus_metrics_vendor_and_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sys

    peer = _Peer("metar-A3-1", catalog_id="metar_a3_1", product="METAR")
    monkeypatch.setattr(mod, "_FIXTURES", tmp_path / "fixtures")
    vendor = tmp_path / "vendor"
    vendor.mkdir()
    (vendor / "metar-A3-1.xml").write_text("<vendor/>\n", encoding="utf-8")
    monkeypatch.setattr(mod, "_VENDOR_EXAMPLES", vendor)

    tac_file = tmp_path / "fixtures" / "annex3_golden" / "metar_a3_1.tac"
    tac_file.parent.mkdir(parents=True)
    tac_file.write_text("METAR KJFK 010000Z=\n", encoding="utf-8")

    fake_inventory = SimpleNamespace(
        OFFICIAL_TAC_PEERS=(peer,),
        annex3_path=lambda _p: tac_file,
    )
    monkeypatch.setitem(sys.modules, "wmo_official_tac_inventory", fake_inventory)

    monkeypatch.setitem(
        sys.modules,
        "tac2iwxxm",
        SimpleNamespace(
            convert=lambda *_a, **_k: SimpleNamespace(ok=False, xml=None),
            decode_tac=lambda *_a, **_k: SimpleNamespace(residuals=[]),
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "tac_validate",
        SimpleNamespace(lint=lambda *_a, **_k: SimpleNamespace(issues=[])),
    )
    monkeypatch.setitem(
        sys.modules,
        "iwxxm_validate",
        SimpleNamespace(
            validate_for_quality_metrics=lambda *_a, **_k: SimpleNamespace(issues=[]),
            c14n_equal=lambda *_a, **_k: False,
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "iwxxm_validate.c14n",
        SimpleNamespace(c14n_equal=lambda *_a, **_k: False),
    )

    doc = mod.generate_corpus_metrics()
    assert doc["details"]["metar-A3-1"]["match_status"] == "convert_fail"
    assert doc["details"]["metar-A3-1"]["validate_issues"] == []


def test_generate_corpus_metrics_missing_official_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sys

    peer = _Peer("metar-A3-1", catalog_id="missing_cat", product="METAR")
    monkeypatch.setattr(mod, "_FIXTURES", tmp_path / "fixtures")
    monkeypatch.setattr(mod, "_VENDOR_EXAMPLES", tmp_path / "vendor")
    tac_file = tmp_path / "fixtures" / "annex3_golden" / "x.tac"
    tac_file.parent.mkdir(parents=True)
    tac_file.write_text("METAR KJFK 010000Z=\n", encoding="utf-8")

    fake_inventory = SimpleNamespace(
        OFFICIAL_TAC_PEERS=(peer,),
        annex3_path=lambda _p: tac_file,
    )
    monkeypatch.setitem(sys.modules, "wmo_official_tac_inventory", fake_inventory)
    monkeypatch.setitem(
        sys.modules,
        "tac2iwxxm",
        SimpleNamespace(
            convert=lambda *_a, **_k: SimpleNamespace(ok=True, xml="<x/>"),
            decode_tac=lambda *_a, **_k: SimpleNamespace(residuals=[]),
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "tac_validate",
        SimpleNamespace(lint=lambda *_a, **_k: SimpleNamespace(issues=[])),
    )
    monkeypatch.setitem(
        sys.modules,
        "iwxxm_validate",
        SimpleNamespace(
            validate_for_quality_metrics=lambda *_a, **_k: SimpleNamespace(issues=[]),
            c14n_equal=lambda *_a, **_k: True,
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "iwxxm_validate.c14n",
        SimpleNamespace(c14n_equal=lambda *_a, **_k: True),
    )

    with pytest.raises(FileNotFoundError, match="No official XML"):
        mod.generate_corpus_metrics()


def test_generate_corpus_metrics_golden_fallback_and_unequal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    peer = _Peer("metar-A3-1", catalog_id="metar_a3_1", product="METAR")
    monkeypatch.setattr(mod, "_FIXTURES", tmp_path / "fixtures")
    monkeypatch.setattr(mod, "_VENDOR_EXAMPLES", tmp_path / "vendor")
    tac_file = tmp_path / "fixtures" / "annex3_golden" / "metar_a3_1.tac"
    tac_file.parent.mkdir(parents=True)
    tac_file.write_text("METAR KJFK 010000Z=\n", encoding="utf-8")
    golden = tmp_path / "fixtures" / "annex3_golden" / "metar_a3_1.golden.xml"
    golden.write_text("<golden/>\n", encoding="utf-8")

    fake_inventory = SimpleNamespace(
        OFFICIAL_TAC_PEERS=(peer,),
        annex3_path=lambda _p: tac_file,
    )
    sys.modules.pop("wmo_official_tac_inventory", None)
    monkeypatch.setitem(sys.modules, "wmo_official_tac_inventory", fake_inventory)
    monkeypatch.setitem(
        sys.modules,
        "tac2iwxxm",
        SimpleNamespace(
            convert=lambda *_a, **_k: SimpleNamespace(ok=True, xml="<converted/>"),
            decode_tac=lambda *_a, **_k: SimpleNamespace(residuals=[]),
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "tac_validate",
        SimpleNamespace(lint=lambda *_a, **_k: SimpleNamespace(issues=[])),
    )
    import types as types_mod

    iwxxm_pkg = types_mod.ModuleType("iwxxm_validate")
    iwxxm_pkg.__path__ = []  # type: ignore[attr-defined]
    c14n_mod = types_mod.ModuleType("iwxxm_validate.c14n")
    c14n_mod.c14n_equal = lambda *_a, **_k: False  # type: ignore[attr-defined]
    sys.modules["iwxxm_validate"] = iwxxm_pkg
    sys.modules["iwxxm_validate.c14n"] = c14n_mod
    iwxxm_pkg.validate_for_quality_metrics = lambda *_a, **_k: SimpleNamespace(
        issues=[]
    )  # type: ignore[attr-defined]
    monkeypatch.setattr(mod, "_ensure_imports", lambda: None)

    doc = mod.generate_corpus_metrics()
    assert doc["details"]["metar-A3-1"]["match_status"] == "unequal"
    assert "<golden/>" in doc["details"]["metar-A3-1"]["official_xml"]


def test_main_entrypoint_subprocess() -> None:
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/ci/generate_quality_metrics.py")],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0


def test_main_writes_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        mod,
        "generate_corpus_metrics",
        lambda: {
            "generated_at": "2026-01-01T00:00:00Z",
            "iwxxm_pin": "2025-2",
            "summaries": [
                {
                    "product": "metar",
                    "match_pass": 1,
                    "match_fail": 0,
                    "deferred_gaps": 0,
                }
            ],
            "files": [{"deferred": False}, {"deferred": True}],
            "details": {},
        },
    )
    monkeypatch.setattr(mod, "_OUT_DIR", tmp_path)
    monkeypatch.setattr(mod, "_OUT_PATH", tmp_path / "corpus_metrics.json")
    monkeypatch.setattr(mod, "_REPO_ROOT", tmp_path)
    assert mod.main() == 0
    assert (tmp_path / "corpus_metrics.json").is_file()
