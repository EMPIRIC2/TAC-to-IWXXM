"""TC-1036 — parameterized ops harvest harness + paired TAC + datamart probe.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tac2iwxxm.ca_ops_corpus import load_ops_manifest, ops_fixture_root

_REPO = Path(__file__).resolve().parents[3]
_FIXTURES = ops_fixture_root(_REPO)
_MANIFEST = _FIXTURES / "ops_manifest.json"
_PROBE = _FIXTURES / "ops_datamart_probe.json"
_HARVEST_OPS = _REPO / "scripts" / "iwxxm" / "harvest_ops_corpus.py"
_PROBE_SCRIPT = _REPO / "scripts" / "iwxxm" / "probe_msc_datamart_drift.py"


def test_tc_1036_001_parameterized_harvest_entrypoint_exists() -> None:
    assert _HARVEST_OPS.is_file()
    text = _HARVEST_OPS.read_text(encoding="utf-8")
    assert "--profile" in text
    assert "--product" in text
    assert "CA_ECCC" in text


def test_tc_1036_002_unsupported_profile_fails_closed() -> None:
    proc = subprocess.run(
        [sys.executable, str(_HARVEST_OPS), "--profile", "AU_BOM", "--dry-run"],
        cwd=_REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert "unsupported profile" in proc.stderr.lower()


def test_tc_1036_003_metar_ops_paired_tac_iwxxm() -> None:
    manifest = load_ops_manifest(_MANIFEST)
    metar = [case for case in manifest["cases"] if case["product"] == "METAR"]
    assert len(metar) >= 5
    for case in metar:
        assert case.get("ops_tac"), case["id"]
        assert case.get("ops_xml"), case["id"]
        assert (_FIXTURES / case["ops_tac"]).is_file()
        assert (_FIXTURES / case["ops_xml"]).is_file()
        assert case.get("pair_kind") == "encoder_reference_tac_iwxxm"


def test_tc_1036_004_metar_speci_datamart_blocker_documented() -> None:
    manifest = load_ops_manifest(_MANIFEST)
    note = manifest.get("metar_speci_datamart_blocker") or ""
    assert "404" in note
    assert "metar" in note.lower()
    probe = json.loads(_PROBE.read_text(encoding="utf-8"))
    assert probe["products"]["metar"]["http_status"] == 404
    assert probe["products"]["speci"]["http_status"] == 404
    assert probe["products"]["taf"]["http_status"] == 200


def test_tc_1036_005_offline_datamart_probe_script_green() -> None:
    proc = subprocess.run(
        [sys.executable, str(_PROBE_SCRIPT)],
        cwd=_REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "OK" in proc.stdout
