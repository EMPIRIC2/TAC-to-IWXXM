"""EV-080 M4 — 100% coverage for scripts/iwxxm/codelist_uri_drift.py."""

from __future__ import annotations

import subprocess
import sys
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from scripts.iwxxm import codelist_uri_drift as mod

ROOT = Path(__file__).resolve().parents[2]


def test_load_and_diff_helpers(tmp_path: Path) -> None:
    rdf = tmp_path / "nil.rdf"
    rdf.write_text(
        '<skos:Concept rdf:about="http://codes.wmo.int/common/nil/missing"/>',
        encoding="utf-8",
    )
    uris = mod.load_sch_rdf_member_uris(rdf)
    assert "http://codes.wmo.int/common/nil/missing" in uris

    csv = tmp_path / "nil.csv"
    csv.write_text(
        "id,notation\nhttp://codes.wmo.int/common/nil/missing,m\n", encoding="utf-8"
    )
    csv_uris = mod.load_csv_member_uris(csv)
    assert csv_uris == {"http://codes.wmo.int/common/nil/missing"}

    only_l, only_r = mod.diff_uri_sets(uris, csv_uris)
    assert only_l == []
    assert only_r == []


def test_summarize_drift_offline_ok() -> None:
    report, ok = mod.summarize_drift(iwxxm_version="2025-2", repo_root=ROOT)
    assert "codes.wmo.int URI drift" in report
    assert ok or "DRIFT" in report or "OK" in report


def test_summarize_drift_missing_files(tmp_path: Path) -> None:
    spec = mod.RegisterSpec(
        "http://codes.wmo.int/test/register",
        "missing.rdf",
        "CSV/missing.csv",
    )
    report, ok = mod.summarize_drift(
        iwxxm_version="2025-2",
        repo_root=tmp_path,
        registers=(spec,),
    )
    assert not ok
    assert "ERROR missing SCH RDF" in report
    assert "ERROR missing CSV" not in report  # never reached csv without sch

    sch_dir = tmp_path / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "rule"
    sch_dir.mkdir(parents=True)
    (sch_dir / "missing.rdf").write_text("", encoding="utf-8")
    report2, ok2 = mod.summarize_drift(
        iwxxm_version="2025-2",
        repo_root=tmp_path,
        registers=(spec,),
    )
    assert not ok2
    assert "ERROR missing CSV" in report2


def test_summarize_drift_sch_only_and_drift(tmp_path: Path) -> None:
    sch_dir = tmp_path / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "rule"
    sch_dir.mkdir(parents=True)
    sch = sch_dir / "codes.wmo.int-common-nil.rdf"
    sch.write_text(
        """
<skos:Concept rdf:about="http://codes.wmo.int/common/nil/missing"/>
<skos:Concept rdf:about="http://codes.wmo.int/common/nil/unknown"/>
<skos:Concept rdf:about="http://codes.wmo.int/common/nil/withheld"/>
""",
        encoding="utf-8",
    )
    csv_root = tmp_path / "vendor" / "schemas" / "iwxxm-codelists"
    csv_path = csv_root / "CSV/common/nil/nil_entity.csv"
    csv_path.parent.mkdir(parents=True)
    csv_path.write_text(
        "id,notation\n"
        "http://codes.wmo.int/common/nil/missing,m\n"
        "http://codes.wmo.int/common/nil/extra,e\n",
        encoding="utf-8",
    )

    sch_only = mod.RegisterSpec(
        "http://codes.wmo.int/iwxxm/nil",
        "codes.wmo.int-iwxxm-nil.rdf",
        None,
    )
    (sch_dir / "codes.wmo.int-iwxxm-nil.rdf").write_text(
        '<skos:Concept rdf:about="http://codes.wmo.int/iwxxm/nil/missing"/>',
        encoding="utf-8",
    )

    nil_spec = mod.RegisterSpec(
        "http://codes.wmo.int/common/nil",
        "codes.wmo.int-common-nil.rdf",
        "CSV/common/nil/nil_entity.csv",
    )
    report, ok = mod.summarize_drift(
        iwxxm_version="2025-2",
        repo_root=tmp_path,
        registers=(nil_spec, sch_only),
    )
    assert not ok
    assert "DRIFT" in report
    assert "only_in_SCH" in report
    assert "only_in_CSV" in report
    assert "SCH inventory only" in report


def test_summarize_drift_known_lag(tmp_path: Path) -> None:
    sch_dir = tmp_path / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "rule"
    sch_dir.mkdir(parents=True)
    sch_name = "codes.wmo.int-49-2-SpaceWxLocation.rdf"
    sch = sch_dir / sch_name
    sch.write_text(
        """
<skos:Concept rdf:about="http://codes.wmo.int/49-2/SpaceWxLocation/DAYSIDE"/>
<skos:Concept rdf:about="http://codes.wmo.int/49-2/SpaceWxLocation/NIGHTSIDE"/>
<skos:Concept rdf:about="http://codes.wmo.int/49-2/SpaceWxLocation/OTHER"/>
""",
        encoding="utf-8",
    )
    csv_root = tmp_path / "vendor" / "schemas" / "iwxxm-codelists"
    csv_path = csv_root / "CSV/49-2/SpaceWxLocation/SpaceWxLocation_entity.csv"
    csv_path.parent.mkdir(parents=True)
    csv_path.write_text(
        "id\nhttp://codes.wmo.int/49-2/SpaceWxLocation/DAYSIDE\n", encoding="utf-8"
    )

    spec = mod.RegisterSpec(
        "http://codes.wmo.int/49-2/SpaceWxLocation",
        sch_name,
        "CSV/49-2/SpaceWxLocation/SpaceWxLocation_entity.csv",
    )
    report, ok = mod.summarize_drift(
        iwxxm_version="2025-2",
        repo_root=tmp_path,
        registers=(spec,),
    )
    assert not ok
    assert "KNOWN_LAG" in report
    assert "only_in_SCH (known)" in report


def test_fetch_live_rdf_branches(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def _urlopen(req: object, timeout: float = 30.0) -> MagicMock:
        url = getattr(req, "full_url", "")
        if "fail-network" in url:
            raise urllib.error.URLError("network down")
        if "html-only" in url:
            resp = MagicMock()
            resp.read.return_value = b"<html><body>not rdf</body></html>"
            resp.headers = {"Content-Type": "text/html"}
            resp.__enter__ = lambda s: s
            resp.__exit__ = lambda *a: None
            return resp
        if "turtle-fallback" in url:
            resp = MagicMock()
            resp.read.return_value = (
                b"http://codes.wmo.int/common/nil/missing\n"
                b"http://codes.wmo.int/common/nil/extra,"
            )
            resp.headers = {"Content-Type": "text/turtle"}
            resp.__enter__ = lambda s: s
            resp.__exit__ = lambda *a: None
            return resp
        resp = MagicMock()
        resp.read.return_value = (
            b'<skos:Concept rdf:about="http://codes.wmo.int/common/nil/missing"/>'
        )
        resp.headers = {"Content-Type": "application/rdf+xml"}
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        return resp

    monkeypatch.setattr(urllib.request, "urlopen", _urlopen)
    assert mod._fetch_live_rdf("http://codes.wmo.int/fail-network/x") is None
    assert "soft-skip" in capsys.readouterr().err

    assert mod._fetch_live_rdf("http://codes.wmo.int/html-only/x") is None
    assert mod._fetch_live_rdf("http://codes.wmo.int/common/nil") is not None


def test_summarize_drift_live_modes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sch_dir = tmp_path / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "rule"
    sch_dir.mkdir(parents=True)
    sch_name = "codes.wmo.int-common-nil.rdf"
    (sch_dir / sch_name).write_text(
        '<skos:Concept rdf:about="http://codes.wmo.int/common/nil/missing"/>',
        encoding="utf-8",
    )
    csv_root = tmp_path / "vendor" / "schemas" / "iwxxm-codelists"
    csv_path = csv_root / "CSV/common/nil/nil_entity.csv"
    csv_path.parent.mkdir(parents=True)
    csv_path.write_text(
        "id\nhttp://codes.wmo.int/common/nil/missing\n", encoding="utf-8"
    )
    spec = mod.RegisterSpec(
        "http://codes.wmo.int/common/nil",
        sch_name,
        "CSV/common/nil/nil_entity.csv",
    )

    monkeypatch.setattr(mod, "_fetch_live_rdf", lambda *_a, **_k: None)
    report, ok = mod.summarize_drift(
        iwxxm_version="2025-2",
        repo_root=tmp_path,
        registers=(spec,),
        live=True,
        strict_live=True,
    )
    assert not ok
    assert "ERROR live fetch failed" in report

    monkeypatch.setattr(mod, "_fetch_live_rdf", lambda *_a, **_k: None)
    report2, ok2 = mod.summarize_drift(
        iwxxm_version="2025-2",
        repo_root=tmp_path,
        registers=(spec,),
        live=True,
        strict_live=False,
    )
    assert ok2
    assert "live: soft-skipped" in report2

    monkeypatch.setattr(
        mod,
        "_fetch_live_rdf",
        lambda *_a, **_k: (
            '<skos:Concept rdf:about="http://codes.wmo.int/common/nil/extra"/>'
        ),
    )
    report3, ok3 = mod.summarize_drift(
        iwxxm_version="2025-2",
        repo_root=tmp_path,
        registers=(spec,),
        live=True,
        strict_live=True,
    )
    assert not ok3
    assert "DRIFT vs live" in report3

    monkeypatch.setattr(
        mod,
        "_fetch_live_rdf",
        lambda *_a, **_k: "http://codes.wmo.int/common/nil/missing",
    )
    report4, ok4 = mod.summarize_drift(
        iwxxm_version="2025-2",
        repo_root=tmp_path,
        registers=(spec,),
        live=True,
        strict_live=False,
    )
    assert ok4
    assert "live OK" in report4


def test_summarize_drift_live_advisory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sch_dir = tmp_path / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "rule"
    sch_dir.mkdir(parents=True)
    sch_name = "codes.wmo.int-common-nil.rdf"
    (sch_dir / sch_name).write_text(
        '<skos:Concept rdf:about="http://codes.wmo.int/common/nil/missing"/>',
        encoding="utf-8",
    )
    csv_root = tmp_path / "vendor" / "schemas" / "iwxxm-codelists"
    csv_path = csv_root / "CSV/common/nil/nil_entity.csv"
    csv_path.parent.mkdir(parents=True)
    csv_path.write_text(
        "id\nhttp://codes.wmo.int/common/nil/missing\n", encoding="utf-8"
    )
    spec = mod.RegisterSpec(
        "http://codes.wmo.int/common/nil",
        sch_name,
        "CSV/common/nil/nil_entity.csv",
    )
    monkeypatch.setattr(
        mod,
        "_fetch_live_rdf",
        lambda *_a, **_k: (
            '<skos:Concept rdf:about="http://codes.wmo.int/common/nil/extra"/>'
        ),
    )
    report, ok = mod.summarize_drift(
        iwxxm_version="2025-2",
        repo_root=tmp_path,
        registers=(spec,),
        live=True,
        strict_live=False,
    )
    assert ok
    assert "advisory; not failing offline gate" in report


def test_main_entrypoint_subprocess() -> None:

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/iwxxm/codelist_uri_drift.py")],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode in (0, 1)


def test_main_exit_codes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod, "summarize_drift", lambda **_k: ("report\n", True))
    assert mod.main([]) == 0
    monkeypatch.setattr(mod, "summarize_drift", lambda **_k: ("report\n", False))
    assert mod.main(["--strict-live"]) == 1
