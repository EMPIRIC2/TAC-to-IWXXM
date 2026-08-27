"""T2.5.2 - per-file ≥95% coverage gate (EV-047 / D-S056-cov95)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ci" / "check_per_file_coverage.py"


def _load_mod() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_per_file_coverage", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cov_mod() -> ModuleType:
    return _load_mod()


@pytest.mark.unit
def test_script_exists() -> None:
    assert SCRIPT.is_file()


@pytest.mark.unit
def test_file_percent_skips_empty(cov_mod: ModuleType) -> None:
    assert cov_mod.file_percent({"num_statements": 0, "percent_covered": 100.0}) is None


@pytest.mark.unit
def test_file_percent_reads_value(cov_mod: ModuleType) -> None:
    assert (
        cov_mod.file_percent({"num_statements": 10, "percent_covered": 94.96}) == 94.96
    )


@pytest.mark.unit
def test_files_below_floor_lists_under_95(cov_mod: ModuleType) -> None:
    report = {
        "files": {
            "pkg/a.py": {"summary": {"num_statements": 10, "percent_covered": 100.0}},
            "pkg/b.py": {"summary": {"num_statements": 20, "percent_covered": 94.96}},
            "pkg/empty.py": {
                "summary": {"num_statements": 0, "percent_covered": 100.0}
            },
        }
    }
    below = cov_mod.files_below_floor(report, min_pct=95.0)
    assert below == [("pkg/b.py", 94.96)]


@pytest.mark.unit
def test_check_report_ok_and_fail(cov_mod: ModuleType) -> None:
    ok = {
        "files": {"a.py": {"summary": {"num_statements": 1, "percent_covered": 95.0}}}
    }
    assert cov_mod.check_report(ok, min_pct=95.0) == 0
    bad = {
        "files": {"a.py": {"summary": {"num_statements": 1, "percent_covered": 94.9}}}
    }
    assert cov_mod.check_report(bad, min_pct=95.0) == 1


@pytest.mark.unit
def test_main_reads_json(cov_mod: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "coverage.json"
    path.write_text(
        json.dumps(
            {
                "files": {
                    "x.py": {"summary": {"num_statements": 2, "percent_covered": 100.0}}
                }
            }
        ),
        encoding="utf-8",
    )
    assert cov_mod.main([str(path)]) == 0
    path.write_text(
        json.dumps(
            {
                "files": {
                    "x.py": {"summary": {"num_statements": 2, "percent_covered": 90.0}}
                }
            }
        ),
        encoding="utf-8",
    )
    assert cov_mod.main([str(path), "--min-pct", "95"]) == 1


@pytest.mark.unit
def test_main_missing_file(cov_mod: ModuleType, tmp_path: Path) -> None:
    assert cov_mod.main([str(tmp_path / "missing.json")]) == 2
