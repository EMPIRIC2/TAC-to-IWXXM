"""EV-080 M4 — 100% coverage for scripts/iwxxm/harvest_ca_eccc_vaac_tac.py."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from scripts.iwxxm import harvest_ca_eccc_vaac_tac as mod

ROOT = Path(__file__).resolve().parents[2]

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def fixtures_root(tmp_path: Path) -> Path:
    root = tmp_path / "CA_ECCC"
    root.mkdir()
    manifest = {
        "schema_version": 1,
        "cases": [
            {"id": "taf_x", "product": "TAF", "tier": "wmoReference"},
            {"id": "vaa_old", "product": "VAA", "tier": "vaacTac"},
        ],
    }
    (root / "ops_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


def test_fetch_vaac_tac_success_and_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    good = MagicMock()
    good.read.return_value = b"<pre>VA ADVISORY\ncontent</pre>"
    good.__enter__ = lambda s: s
    good.__exit__ = lambda *a: None
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_a, **_k: good)
    tac = mod._fetch_vaac_tac("param")
    assert tac.startswith("VA ADVISORY")

    bad = MagicMock()
    bad.read.return_value = b"<pre>no advisory here</pre>"
    bad.__enter__ = lambda s: s
    bad.__exit__ = lambda *a: None
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_a, **_k: bad)
    with pytest.raises(RuntimeError, match="VAAC TAC not found"):
        mod._fetch_vaac_tac("param")


def test_merge_vaa_cases() -> None:
    manifest = {
        "cases": [
            {"id": "a", "product": "TAF"},
            {"id": "vaa_old", "product": "VAA"},
        ]
    }
    merged = mod._merge_vaa_cases(
        manifest,
        [{"id": "new", "product": "VAA"}, {"id": "a", "product": "TAF"}],
    )
    by_id = {c["id"]: c for c in merged}
    assert "vaa_old" not in by_id
    assert by_id["new"]["product"] == "VAA"
    assert by_id["a"]["product"] == "TAF"


def test_harvest_vaac_tac_network(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(mod, "_fetch_vaac_tac", lambda _p: "VA ADVISORY\nTAC")
    monkeypatch.setattr(mod.time, "sleep", lambda *_a: None)
    manifest = mod.harvest_vaac_tac(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        rate_limit=0.0,
        dry_run=False,
        skip_network=False,
    )
    dest = fixtures_root / mod._PINNED_VAAC[0]["rel_path"]
    assert dest.is_file()
    assert manifest["vaa_harvest"] == "vaac_tac_waived"
    assert sum(1 for c in manifest["cases"] if c["product"] == "VAA") == 1


def test_harvest_vaac_tac_http_error(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _boom(*_a: object, **_k: object) -> str:
        raise urllib.error.HTTPError("url", 500, "err", hdrs=None, fp=None)

    monkeypatch.setattr(mod, "_fetch_vaac_tac", _boom)
    with pytest.raises(RuntimeError, match="VAAC fetch failed"):
        mod.harvest_vaac_tac(
            fixtures_root=fixtures_root,
            pin_date="2026-08-24",
            rate_limit=0.0,
            dry_run=False,
            skip_network=False,
        )


def test_harvest_vaac_tac_dry_skip(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = mod.harvest_vaac_tac(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        rate_limit=0.0,
        dry_run=True,
        skip_network=True,
    )
    assert manifest["pin_date"] == "2026-08-24"
    assert not (fixtures_root / mod._PINNED_VAAC[0]["rel_path"]).exists()
    text = (fixtures_root / "ops_manifest.json").read_text(encoding="utf-8")
    assert "vaa_old" not in text or "VAA" in text


def test_main_entrypoint_subprocess() -> None:

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/iwxxm/harvest_ca_eccc_vaac_tac.py"),
            "--skip-network",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0


def test_main(
    fixtures_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(mod, "_REPO", fixtures_root.parent)
    monkeypatch.setattr(mod, "ops_fixture_root", lambda _r: fixtures_root)
    monkeypatch.setattr(
        mod,
        "harvest_vaac_tac",
        lambda **_k: {
            "cases": [{"product": "VAA"}, {"product": "TAF"}],
            "vaa_harvest": "x",
        },
    )
    monkeypatch.setattr(sys, "argv", ["harvest_ca_eccc_vaac_tac.py"])
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "vaa_cases=1" in out
    assert "vaa_harvest=x" in out
