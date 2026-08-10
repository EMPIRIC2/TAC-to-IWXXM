"""Unit tests for scripts/ci/collect_quality_pr_stats.py (EV-052 / TC-EV052-005)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ci" / "collect_quality_pr_stats.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("collect_quality_pr_stats", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.unit
def test_collect_golden_pack_soft_diff_match_skip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load_module()
    pack = tmp_path / "annex3_golden"
    pack.mkdir()
    (pack / "ok.tac").write_text(
        "METAR KJFK 010000Z 00000KT 10SM CLR 10/00 A2992=\n", encoding="utf-8"
    )
    (pack / "ok.golden.xml").write_text("<iwxxm:METAR/>\n", encoding="utf-8")
    (pack / "soft.tac").write_text(
        "METAR KJFK 010000Z 00000KT 10SM CLR 10/00 A2992=\n", encoding="utf-8"
    )
    manifest = {
        "schema_version": 1,
        "profile": "annex3",
        "cases": [
            {
                "id": "ok",
                "product": "METAR",
                "tac": "ok.tac",
                "golden": "ok.golden.xml",
            },
            {
                "id": "soft",
                "product": "METAR",
                "tac": "soft.tac",
                "soft_compare": True,
            },
            {
                "id": "missing",
                "product": "TAF",
                "tac": "missing.tac",
                "golden": "missing.golden.xml",
            },
        ],
    }
    (pack / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    class _Result:
        ok = True
        xml = "<iwxxm:METAR/>\n"

    import metar_shared.xml_canonical as xml_canonical
    import tac2iwxxm

    monkeypatch.setattr(tac2iwxxm, "convert", lambda *a, **k: _Result())
    monkeypatch.setattr(xml_canonical, "canonicalize_xml", lambda s: s.strip())

    counts = mod.collect_golden_pack(pack / "manifest.json", default_profile="annex3")
    # list[int]: match, soft_diff, fail, skip
    assert counts[("METAR", "annex3")][0] == 1
    assert counts[("METAR", "annex3")][1] == 1
    assert counts[("TAF", "annex3")][3] == 1


@pytest.mark.unit
def test_write_summary_schema(tmp_path: Path) -> None:
    mod = _load_module()
    counts = {("METAR", "annex3"): [2, 1, 0, 3]}
    out = tmp_path / "quality-summary.json"
    mod._write_summary(out, "annex3-golden", counts)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["source"] == "annex3-golden"
    assert data["rows"] == [
        {
            "product": "METAR",
            "profile": "annex3",
            "match": 2,
            "soft_diff": 1,
            "fail": 0,
            "skip": 3,
        }
    ]


@pytest.mark.unit
def test_collect_quality_matrix_inventory_per_case(tmp_path: Path) -> None:
    mod = _load_module()
    qm = tmp_path / "quality_matrices"
    td = qm / "testdata" / "convert" / "metar_speci"
    td.mkdir(parents=True)
    (td / "sample.yml").write_text(
        """
rule_id: sample
engine: convert
cases:
- bucket: happy
  case_id: "01"
  status: ready
  tac: "METAR KJFK 010000Z="
  meta:
    product: METAR
    profile: annex3
- bucket: happy
  case_id: "02"
  status: needs-fixture
  meta:
    product: METAR
    profile: annex3
    reason: scaffold
- bucket: sad
  case_id: "01"
  status: oos
  meta:
    product: SPECI
    profile: iwxxm_us
    cite: child-issue
""",
        encoding="utf-8",
    )
    counts = mod.collect_quality_matrix_inventory(qm)
    assert counts[("METAR", "annex3")][0] == 1  # ready → match (inventory)
    assert counts[("METAR", "annex3")][3] == 1  # needs-fixture → skip
    assert counts[("SPECI", "iwxxm_us")][3] == 1  # oos → skip
