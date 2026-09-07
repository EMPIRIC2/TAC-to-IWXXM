"""Coverage for scripts/ci/check_per_file_coverage.py (Batch A)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import scripts.ci.check_per_file_coverage as cov_mod


@pytest.mark.unit
def test_file_percent_none_when_percent_missing() -> None:
    assert cov_mod.file_percent({"num_statements": 5}) is None


@pytest.mark.unit
def test_files_below_floor_skips_non_dict_entries() -> None:
    report = {
        "files": {
            "bad.py": "not-a-dict",
            "empty_summary.py": {"summary": "nope"},
            "ok.py": {"summary": {"num_statements": 1, "percent_covered": 100.0}},
        }
    }
    assert cov_mod.files_below_floor(report, min_pct=100.0) == []


@pytest.mark.unit
def test_main_rejects_non_object_root(tmp_path: Path) -> None:
    path = tmp_path / "coverage.json"
    path.write_text(json.dumps([]), encoding="utf-8")
    assert cov_mod.main([str(path)]) == 2


@pytest.mark.unit
def test_check_report_ok_message(capsys: pytest.CaptureFixture[str]) -> None:
    report = {
        "files": {"a.py": {"summary": {"num_statements": 1, "percent_covered": 100.0}}}
    }
    assert cov_mod.check_report(report, min_pct=100.0) == 0
    assert "per-file coverage OK" in capsys.readouterr().out


@pytest.mark.unit
def test_main_missing_coverage_json(tmp_path: Path) -> None:
    assert cov_mod.main([str(tmp_path / "missing.json")]) == 2


@pytest.mark.unit
def test_file_percent_none_when_no_statements() -> None:
    assert cov_mod.file_percent({"num_statements": 0, "percent_covered": 50.0}) is None


@pytest.mark.unit
def test_files_below_floor_skips_missing_percent() -> None:
    report = {
        "files": {
            "partial.py": {"summary": {"num_statements": 3}},
        }
    }
    assert cov_mod.files_below_floor(report, min_pct=100.0) == []


@pytest.mark.unit
def test_main_success_returns_check_report(tmp_path: Path) -> None:
    path = tmp_path / "coverage.json"
    path.write_text(
        '{"files": {"a.py": {"summary": {"num_statements": 1, "percent_covered": 100.0}}}}',
        encoding="utf-8",
    )
    assert cov_mod.main([str(path), "--min-pct", "100"]) == 0


@pytest.mark.unit
def test_check_report_fail_message(capsys: pytest.CaptureFixture[str]) -> None:
    report = {
        "files": {"a.py": {"summary": {"num_statements": 1, "percent_covered": 50.0}}}
    }
    assert cov_mod.check_report(report, min_pct=100.0) == 1
    err = capsys.readouterr().err
    assert "per-file coverage FAIL" in err
    assert "50.00%" in err
