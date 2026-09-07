"""EV-080 M4 — 100% coverage for scripts/iwxxm/harvest_ca_eccc_ops.py."""

from __future__ import annotations

import subprocess
import sys
import urllib.error
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from scripts.iwxxm import harvest_ca_eccc_ops as mod

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def fixtures_root(tmp_path: Path) -> Path:
    root = tmp_path / "CA_ECCC"
    met_dir = root / "METAR" / "valid"
    met_dir.mkdir(parents=True)
    (met_dir / "metar_basic.tac").write_text(
        "METAR CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012=\n", encoding="utf-8"
    )
    (met_dir / "metar_auto.tac").write_text(
        "METAR CYUL 231800Z AUTO 24010KT 9999 FEW240 22/12 A3012=\n", encoding="utf-8"
    )
    (met_dir / "metar_lwis.tac").write_text("METAR CYUL 231800Z=\n", encoding="utf-8")
    (met_dir / "metar_sawr.tac").write_text("METAR CYUL 231800Z=\n", encoding="utf-8")
    (met_dir / "metar_vis_sm.tac").write_text("METAR CYUL 231800Z=\n", encoding="utf-8")
    return root


def test_fetch_url(monkeypatch: pytest.MonkeyPatch) -> None:
    resp = MagicMock()
    resp.read.return_value = b"<xml/>"
    resp.__enter__ = lambda s: s
    resp.__exit__ = lambda *a: None
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_a, **_k: resp)
    assert mod._fetch_url("https://example.test/x") == b"<xml/>"


def test_bootstrap_encoder_reference(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda tac, **_k: SimpleNamespace(ok=True, xml=f"<xml>{tac[:8]}</xml>"),
    )
    cases = mod._bootstrap_encoder_reference(fixtures_root, dry_run=False)
    assert len(cases) == len(mod._ENCODER_REFERENCE)
    assert (fixtures_root / "METAR/ops/metar_basic_ops.xml").is_file()

    dry = mod._bootstrap_encoder_reference(fixtures_root, dry_run=True)
    assert len(dry) == len(mod._ENCODER_REFERENCE)


def test_bootstrap_encoder_reference_failure(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda *_a, **_k: SimpleNamespace(ok=False, xml=None, issues=["bad"]),
    )
    with pytest.raises(RuntimeError, match="encoder reference failed"):
        mod._bootstrap_encoder_reference(fixtures_root, dry_run=False)


def test_harvest_network_and_manifest(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    resp = MagicMock()
    resp.read.return_value = b"<collect/>"
    resp.__enter__ = lambda s: s
    resp.__exit__ = lambda *a: None
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_a, **_k: resp)
    monkeypatch.setattr(mod.time, "sleep", lambda *_a: None)

    manifest = mod.harvest(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        datamart_base=mod.DEFAULT_BASE,
        rate_limit=0.0,
        dry_run=False,
        skip_network=False,
    )
    assert len(manifest["cases"]) == len(mod._PINNED_FETCHES) + len(
        mod._ENCODER_REFERENCE
    )
    assert (fixtures_root / "ops_manifest.json").is_file()
    sigmet = next(c for c in manifest["cases"] if c["id"] == "sigmet_czeg_15_001")
    assert sigmet["sigmet_kind"] == "weather"


def test_harvest_http_error(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _boom(*_a: object, **_k: object) -> None:
        raise urllib.error.HTTPError("url", 404, "missing", hdrs=None, fp=None)

    monkeypatch.setattr(mod, "_fetch_url", _boom)
    with pytest.raises(RuntimeError, match="fetch failed"):
        mod.harvest(
            fixtures_root=fixtures_root,
            pin_date="2026-08-24",
            datamart_base=mod.DEFAULT_BASE,
            rate_limit=0.0,
            dry_run=False,
            skip_network=False,
        )


def test_harvest_skip_network_and_dry_run(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<xml/>"),
    )
    manifest = mod.harvest(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        datamart_base="https://other.example",
        rate_limit=0.0,
        dry_run=True,
        skip_network=True,
    )
    assert manifest["datamart_base"] == "https://other.example"
    assert not (fixtures_root / "ops_manifest.json").exists()
    assert len(manifest["cases"]) == len(mod._ENCODER_REFERENCE)


def test_harvest_dry_run_with_network_plan(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<xml/>"),
    )
    manifest = mod.harvest(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        datamart_base="https://other.example",
        rate_limit=0.0,
        dry_run=True,
        skip_network=False,
    )
    assert len(manifest["cases"]) == len(mod._PINNED_FETCHES) + len(
        mod._ENCODER_REFERENCE
    )


def test_main_entrypoint_subprocess() -> None:

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/iwxxm/harvest_ca_eccc_ops.py"),
            "--skip-network",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0


def test_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "CA_ECCC"
    root.mkdir()
    monkeypatch.setattr(mod, "_REPO", tmp_path)
    monkeypatch.setattr(mod, "ops_fixture_root", lambda _r: root)
    monkeypatch.setattr(
        mod,
        "harvest",
        lambda **_k: {"cases": [{"id": "x"}], "manifest_sha256": "abc123def456"},
    )
    monkeypatch.setattr(sys, "argv", ["harvest_ca_eccc_ops.py"])
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "cases=1" in out
    assert "checksum=abc123def456" in out
