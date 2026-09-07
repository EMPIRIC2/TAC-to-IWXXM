"""Unit coverage for scripts/security/filter-opengrep-baseline.py."""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from tests.scripts.conftest import REPO_ROOT, load_script


@pytest.fixture
def filt():
    return load_script(
        "security/filter-opengrep-baseline.py", "opengrep_baseline_filter"
    )


@pytest.mark.unit
def test_rel_normalizes_absolute(filt, tmp_path: Path) -> None:
    root = tmp_path
    nested = root / "apps" / "x.py"
    nested.parent.mkdir(parents=True)
    nested.write_text("x\n", encoding="utf-8")
    assert filt._rel(str(nested), root) == "apps/x.py"
    assert filt._rel("./apps/x.py", root) == "apps/x.py"


@pytest.mark.unit
def test_filter_all_baselined(filt, tmp_path: Path) -> None:
    report = tmp_path / "og.json"
    abs_path = str((tmp_path / "a.py").resolve())
    (tmp_path / "a.py").write_text("x\n", encoding="utf-8")
    report.write_text(
        json.dumps(
            {
                "results": [
                    {"check_id": "r1", "path": abs_path},
                    {"check_id": "r1", "path": "a.py"},
                ]
            }
        ),
        encoding="utf-8",
    )
    baseline = tmp_path / "base.txt"
    baseline.write_text("# c\nr1\ta.py\nbadline\n", encoding="utf-8")
    with patch.object(
        sys, "argv", ["x", str(report), str(baseline), "1", str(tmp_path)]
    ):
        assert filt.main() == 0


@pytest.mark.unit
def test_filter_new_finding(filt, tmp_path: Path) -> None:
    report = tmp_path / "og.json"
    report.write_text(
        json.dumps({"results": [{"check_id": "r2", "path": "b.py"}]}),
        encoding="utf-8",
    )
    baseline = tmp_path / "base.txt"
    baseline.write_text("r1\ta.py\n", encoding="utf-8")
    with patch.object(
        sys, "argv", ["x", str(report), str(baseline), "0", str(tmp_path)]
    ):
        assert filt.main() == 1


@pytest.mark.unit
def test_filter_usage_and_tool_error(filt, tmp_path: Path) -> None:
    with patch.object(sys, "argv", ["x"]):
        assert filt.main() == 2
    report = tmp_path / "missing.json"
    baseline = tmp_path / "base.txt"
    baseline.write_text("", encoding="utf-8")
    with patch.object(
        sys, "argv", ["x", str(report), str(baseline), "3", str(tmp_path)]
    ):
        assert filt.main() == 3
    with patch.object(sys, "argv", ["x", str(report), str(baseline)]):
        assert filt.main() == 0


@pytest.mark.unit
def test_filter_missing_baseline_file(filt, tmp_path: Path) -> None:
    report = tmp_path / "og.json"
    report.write_text(json.dumps({"results": []}), encoding="utf-8")
    missing = tmp_path / "no-baseline.txt"
    with patch.object(
        sys, "argv", ["x", str(report), str(missing), "0", str(tmp_path)]
    ):
        assert filt.main() == 0


@pytest.mark.unit
def test_filter_main_entrypoint() -> None:
    path = REPO_ROOT / "scripts/security/filter-opengrep-baseline.py"
    with patch.object(sys, "argv", [str(path)]), pytest.raises(SystemExit) as exc:
        runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 2
