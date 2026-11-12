"""100% coverage for scripts/ci/filter_osv_severity.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.ci import filter_osv_severity as mod


def test_cvss_numeric_and_enum() -> None:
    assert mod._cvss({"severity": 9.1}) == 9.1
    assert mod._cvss({"severity": "CRITICAL"}) == 9.5
    assert mod._cvss({"severity": "LOW"}) == 2.0
    assert mod._cvss({}) == 0.0


def test_filter_osv_missing_report_clean_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["filter_osv_severity.py", str(tmp_path / "missing.json"), "10.0", "0"],
    )
    assert mod.main() == 0


def test_filter_osv_missing_report_propagates_scanner_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["filter_osv_severity.py", str(tmp_path / "missing.json"), "10.0", "2"],
    )
    assert mod.main() == 2


def test_filter_osv_critical_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = tmp_path / "osv.json"
    report.write_text(
        json.dumps(
            {
                "results": [
                    {"vulnerabilities": [{"id": "CVE-TEST", "severity": "CRITICAL"}]}
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        ["filter_osv_severity.py", str(report), "9.0", "0"],
    )
    assert mod.main() == 1


def test_filter_osv_low_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = tmp_path / "osv.json"
    report.write_text(
        json.dumps(
            {"results": [{"vulnerabilities": [{"id": "CVE-LOW", "severity": "LOW"}]}]}
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        ["filter_osv_severity.py", str(report), "9.0", "0"],
    )
    assert mod.main() == 0


def test_filter_osv_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["filter_osv_severity.py"])
    assert mod.main() == 2


def test_filter_osv_main_entrypoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Execute the ``__main__`` guard for scripts coverage."""
    import runpy

    report = tmp_path / "osv.json"
    report.write_text(json.dumps({"results": []}), encoding="utf-8")
    path = Path(mod.__file__).resolve()
    monkeypatch.setattr(
        "sys.argv",
        [str(path), str(report), "10.0", "0"],
    )
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0
