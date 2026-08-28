"""EV-080 M4 — 100% coverage for scripts/ci/collect_quality_pr_stats.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from scripts.ci import collect_quality_pr_stats as mod

ROOT = Path(__file__).resolve().parents[2]


def test_bump_and_rows_from_agg() -> None:
    agg: dict[tuple[str, str], list[int]] = {}
    mod._bump(agg, "metar", "annex3", "match")
    mod._bump(agg, "metar", "annex3", "soft_diff")
    rows = mod._rows_from_agg(agg)
    assert rows == [
        {
            "product": "METAR",
            "profile": "annex3",
            "match": 1,
            "soft_diff": 1,
            "fail": 0,
            "skip": 0,
        }
    ]


def test_collect_golden_pack_missing_manifest(tmp_path: Path) -> None:
    assert (
        mod.collect_golden_pack(tmp_path / "missing.json", default_profile="annex3")
        == {}
    )


def test_collect_golden_pack_all_outcome_branches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "match.tac").write_text("METAR KJFK 010000Z=\n", encoding="utf-8")
    (pack / "match.golden.xml").write_text("<a/>\n", encoding="utf-8")
    (pack / "fail.tac").write_text("METAR KJFK 010000Z=\n", encoding="utf-8")
    (pack / "fail.golden.xml").write_text("<b/>\n", encoding="utf-8")
    (pack / "bad.tac").write_text("METAR KJFK 010000Z=\n", encoding="utf-8")
    (pack / "bad.golden.xml").write_text("<c/>\n", encoding="utf-8")
    (pack / "soft.tac").write_text("METAR KJFK 010000Z=\n", encoding="utf-8")
    manifest = {
        "profile": "annex3",
        "iwxxm_version": "2025-2",
        "cases": [
            "not-a-dict",
            {"product": "METAR", "tac": None},
            {"product": "METAR", "tac": "missing.tac", "golden": "x.xml"},
            {"product": "METAR", "tac": "soft.tac", "soft_compare": True},
            {"product": "METAR", "tac": "match.tac", "golden": "match.golden.xml"},
            {"product": "METAR", "tac": "fail.tac", "golden": "fail.golden.xml"},
            {"product": "METAR", "tac": "bad.tac", "golden": "bad.golden.xml"},
            {"product": "TAF", "tac": "match.tac"},
            {"product": "TAF", "tac": "match.tac", "golden": "missing.golden.xml"},
        ],
    }
    (pack / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    import metar_shared.xml_canonical as xml_canonical
    import tac2iwxxm

    def _convert(tac: str, **_k: object) -> SimpleNamespace:
        if "bad" in tac or tac.startswith("METAR KJFK 010000Z="):
            # fail path for bad.tac via exception below
            pass
        return SimpleNamespace(ok=True, xml="<a/>")

    def _canonicalize(s: str) -> str:
        if "<b/>" in s:
            return "<converted/>"
        if "<c/>" in s:
            raise RuntimeError("boom")
        return s.strip()

    monkeypatch.setattr(tac2iwxxm, "convert", _convert)
    monkeypatch.setattr(xml_canonical, "canonicalize_xml", _canonicalize)

    counts = mod.collect_golden_pack(pack / "manifest.json", default_profile="annex3")
    assert counts[("METAR", "annex3")][0] == 1  # match
    assert counts[("METAR", "annex3")][1] == 1  # soft_diff
    assert counts[("METAR", "annex3")][2] >= 2  # fail + exception
    assert counts[("TAF", "annex3")][3] >= 2  # skip branches


def test_collect_golden_pack_convert_not_ok(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "x.tac").write_text("METAR KJFK 010000Z=\n", encoding="utf-8")
    (pack / "x.golden.xml").write_text("<a/>\n", encoding="utf-8")
    (pack / "manifest.json").write_text(
        json.dumps(
            {"cases": [{"product": "METAR", "tac": "x.tac", "golden": "x.golden.xml"}]}
        ),
        encoding="utf-8",
    )
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm, "convert", lambda *_a, **_k: SimpleNamespace(ok=False, xml=None)
    )
    counts = mod.collect_golden_pack(pack / "manifest.json", default_profile="annex3")
    assert counts[("METAR", "annex3")][2] == 1


def test_collect_quality_matrix_inventory_branches(tmp_path: Path) -> None:
    assert mod.collect_quality_matrix_inventory(tmp_path / "missing") == {}

    qm = tmp_path / "quality_matrices"
    assert mod.collect_quality_matrix_inventory(qm) == {}

    td = qm / "testdata" / "convert" / "metar_speci"
    td.mkdir(parents=True)
    (td / "bad.yml").write_text("not: [valid\n", encoding="utf-8")
    (td / "scalar.yml").write_text("just a string\n", encoding="utf-8")
    (td / "no_cases.yml").write_text("meta: {}\n", encoding="utf-8")
    (td / "full.yml").write_text(
        """
meta:
  product: METAR_SPECI
  profile: annex3
product: ignored
cases:
- not-a-dict
- status: ok
  meta:
    product: METAR
    profile: annex3
- status: pass
  meta: {product: SPECI, profile: iwxxm_us}
- status: needs-fixture
  meta: {product: TAF, profile: annex3}
- status: oos
- status: skipped
  meta: {product: SIGMET, profile: annex3}
- status: soft
  meta: {product: AIRMET, profile: annex3}
- status: soft-diff
  meta: {product: SWXA, profile: annex3}
- status: fail
  meta: {product: VAA, profile: annex3}
- status: weird
  meta: {product: TCA, profile: annex3}
""",
        encoding="utf-8",
    )
    counts = mod.collect_quality_matrix_inventory(qm)
    assert counts[("METAR", "annex3")][0] >= 1
    assert counts[("METAR", "annex3")][3] >= 1
    assert counts[("SPECI", "iwxxm_us")][0] >= 1
    assert counts[("TAF", "annex3")][3] >= 1
    assert counts[("SIGMET", "annex3")][3] >= 1
    assert counts[("AIRMET", "annex3")][1] >= 1
    assert counts[("SWXA", "annex3")][1] >= 1
    assert counts[("VAA", "annex3")][2] >= 1
    assert counts[("TCA", "annex3")][1] >= 1


def test_collect_quality_matrix_inventory_yaml_import_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    qm = tmp_path / "quality_matrices"
    td = qm / "testdata" / "x"
    td.mkdir(parents=True)
    (td / "a.yml").write_text("cases: []\n", encoding="utf-8")

    real_import = __import__

    def _fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "yaml":
            raise ImportError("no yaml")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _fake_import)
    assert mod.collect_quality_matrix_inventory(qm) == {}


def test_main_writes_summaries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        mod,
        "collect_golden_pack",
        lambda *_a, **_k: {("METAR", "annex3"): [1, 0, 0, 0]},
    )
    monkeypatch.setattr(
        mod,
        "collect_quality_matrix_inventory",
        lambda *_a, **_k: {("TAF", "annex3"): [0, 0, 1, 0]},
    )
    out = tmp_path / "out"
    rc = mod.main(["--repo-root", str(ROOT), "--out", str(out)])
    assert rc == 0
    assert (out / "annex3-golden" / "quality-summary.json").is_file()
    assert (out / "iwxxm_us-golden" / "quality-summary.json").is_file()
    assert (out / "quality-matrix" / "quality-summary.json").is_file()


def test_main_entrypoint_subprocess() -> None:

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/ci/collect_quality_pr_stats.py"),
            "--repo-root",
            str(ROOT),
            "--out",
            str(ROOT / "artifacts" / "test-quality-out"),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0
