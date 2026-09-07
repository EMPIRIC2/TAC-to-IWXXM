"""EV-080 M4 — 100% coverage for scripts/iwxxm/iwxxm_us_compat_gate.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.iwxxm import iwxxm_us_compat_gate as mod

ROOT = Path(__file__).resolve().parents[2]


def test_load_manifest_us_pin_errors(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="missing vendor manifest"):
        mod.load_manifest_us_pin(tmp_path / "missing.json")

    bad = tmp_path / "manifest.json"
    bad.write_text(json.dumps({"bundles": {}}), encoding="utf-8")
    with pytest.raises(SystemExit, match=r"missing bundles\.iwxxm-us"):
        mod.load_manifest_us_pin(bad)


def test_build_gate_report_with_and_without_source(tmp_path: Path) -> None:
    manifest = {
        "bundles": {
            "iwxxm-us": {
                "tag": "3.0",
                "local_path": "vendor/schemas/iwxxm-us",
            }
        }
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    report = mod.build_gate_report(default_version="2025-2", manifest_path=path)
    assert "2025-2" in report
    assert mod.LAG_POLICY_ID in report
    assert "iwxxm-us source:" not in report

    manifest["bundles"]["iwxxm-us"]["source_url"] = "https://example.test/tgz"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    report2 = mod.build_gate_report(default_version="2025-2", manifest_path=path)
    assert "iwxxm-us source: https://example.test/tgz" in report2


def test_default_version_from_sot() -> None:
    version = mod._default_version_from_sot()
    assert version


def test_run_smoke_branches(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mod, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr("subprocess.call", lambda *_a, **_k: 1)
    assert mod._run_smoke() == 1

    calls: list[list[str]] = []

    def _call(cmd: list[str], cwd: Path | None = None) -> int:
        calls.append(cmd)
        return 0

    monkeypatch.setattr("subprocess.call", _call)
    assert mod._run_smoke() == 0
    assert len(calls) == 1

    annex = (
        tmp_path / "packages/tac2iwxxm/tests/test_tc_f6_020_021_metar_speci_annex3.py"
    )
    annex.parent.mkdir(parents=True)
    annex.write_text("# stub\n", encoding="utf-8")
    calls.clear()
    assert mod._run_smoke() == 0
    assert len(calls) == 2


def test_main_without_smoke(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(mod, "_default_version_from_sot", lambda: "2025-2")
    monkeypatch.setattr(
        mod,
        "build_gate_report",
        lambda **_k: "gate report\n",
    )
    assert mod.main([]) == 0
    assert capsys.readouterr().out == "gate report\n"


def test_main_with_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod, "_default_version_from_sot", lambda: "2025-2")
    monkeypatch.setattr(mod, "build_gate_report", lambda **_k: "")
    monkeypatch.setattr(mod, "_run_smoke", lambda: 0)
    assert mod.main(["--smoke"]) == 0


def test_main_entrypoint_subprocess() -> None:
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/iwxxm/iwxxm_us_compat_gate.py")],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0
