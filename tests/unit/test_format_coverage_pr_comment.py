"""Unit tests for scripts/ci/format_coverage_pr_comment.py (EV-036)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ci" / "format_coverage_pr_comment.py"


@pytest.mark.unit
def test_format_coverage_pr_comment_parses_xml_and_vitest(tmp_path: Path) -> None:
    backend = tmp_path / "apps" / "backend"
    backend.mkdir(parents=True)
    root = Element("coverage", {"line-rate": "0.982", "branch-rate": "0.91"})
    SubElement(root, "packages")
    (backend / "coverage.xml").write_bytes(tostring(root))

    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "coverage-summary.json").write_text(
        json.dumps({"total": {"lines": {"pct": 96.5}}}),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    out = proc.stdout
    assert "<!-- EV-036-coverage-comment -->" in out
    assert "## Coverage summary (EV-036 / EV-080)" in out
    assert "100%" in out
    assert "`backend`" in out
    assert "98.20%" in out
    assert "91.00%" in out
    assert "`frontend`" in out
    assert "96.50%" in out
    assert "Codecov not used" in out


@pytest.mark.unit
def test_format_coverage_pr_comment_empty_dir(tmp_path: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "no coverage artifacts" in proc.stdout
