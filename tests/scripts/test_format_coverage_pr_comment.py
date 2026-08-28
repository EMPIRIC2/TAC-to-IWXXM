"""EV-080 M4 — 100% coverage for scripts/ci/format_coverage_pr_comment.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

import pytest
from scripts.ci import format_coverage_pr_comment as mod

ROOT = Path(__file__).resolve().parents[2]


def test_pct_from_rate_branches() -> None:
    assert mod._pct_from_rate(None) is None
    assert mod._pct_from_rate("0.5") == 50.0
    assert mod._pct_from_rate("not-a-number") is None


def test_parse_cobertura_and_vitest(tmp_path: Path) -> None:
    root = Element("coverage", {"line-rate": "0.982", "branch-rate": "0.91"})
    SubElement(root, "packages")
    xml_path = tmp_path / "coverage.xml"
    xml_path.write_bytes(tostring(root))
    line, branch = mod.parse_cobertura(xml_path)
    assert line == 98.2
    assert branch == 91.0

    summary = tmp_path / "coverage-summary.json"
    summary.write_text(
        json.dumps({"total": {"lines": {"pct": 96.5}}}), encoding="utf-8"
    )
    assert mod.parse_vitest_summary(summary) == 96.5
    summary.write_text(json.dumps({"total": {}}), encoding="utf-8")
    assert mod.parse_vitest_summary(summary) is None


def test_package_label_paths(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    backend = root / "apps" / "backend" / "coverage.xml"
    backend.parent.mkdir(parents=True)
    backend.touch()
    assert mod.package_label(backend, root) == "backend"

    pkg = root / "packages" / "tac2iwxxm" / "coverage.xml"
    pkg.parent.mkdir(parents=True)
    pkg.touch()
    assert mod.package_label(pkg, root) == "tac2iwxxm"

    fe = root / "apps" / "frontend" / "coverage-summary.json"
    fe.parent.mkdir(parents=True)
    fe.touch()
    assert mod.package_label(fe, root) == "frontend"

    weird = root / "misc" / "coverage.xml"
    weird.parent.mkdir(parents=True)
    weird.touch()
    assert mod.package_label(weird, root) == "misc"


def test_collect_rows_dedupes_and_formats(tmp_path: Path) -> None:
    root = tmp_path / "tree"
    be = root / "apps" / "backend"
    be.mkdir(parents=True)
    xml = Element("coverage", {"line-rate": "1.0", "branch-rate": "0.5"})
    SubElement(xml, "packages")
    (be / "coverage.xml").write_bytes(tostring(xml))
    dup = root / "backend" / "coverage.xml"
    dup.parent.mkdir(parents=True)
    dup.write_bytes(tostring(xml))

    fe = root / "frontend"
    fe.mkdir()
    (fe / "coverage-summary.json").write_text(
        json.dumps({"total": {"lines": {"pct": 88.0}}}), encoding="utf-8"
    )
    rows = mod.collect_rows(root)
    labels = [r[0] for r in rows]
    assert "backend" in labels
    assert "frontend" in labels
    assert labels.count("backend") == 1


def test_main_empty_and_populated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert mod.main([str(tmp_path / "missing")]) == 0
    out = capsys.readouterr().out
    assert mod.MARKER in out
    assert "no coverage artifacts" in out

    root = tmp_path / "artifacts"
    be = root / "apps" / "backend"
    be.mkdir(parents=True)
    xml = Element("coverage", {"line-rate": "0.5"})
    SubElement(xml, "packages")
    (be / "coverage.xml").write_bytes(tostring(xml))

    monkeypatch.setenv("GITHUB_RUN_ID", "12345")
    monkeypatch.setenv("GITHUB_REPOSITORY", "org/repo")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.example")
    assert mod.main([str(root)]) == 0
    out = capsys.readouterr().out
    assert "https://github.example/org/repo/actions/runs/12345" in out

    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    assert mod.main([str(root)]) == 0
    out = capsys.readouterr().out
    assert "https://github.example/org/repo/actions" in out
    assert "/runs/" not in out.split("actions")[-1]


def test_package_label_packages_index_error(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    # "packages/" substring without a top-level "packages" path segment (ValueError).
    nested = root / "my-packages" / "coverage.xml"
    nested.parent.mkdir(parents=True)
    nested.write_text("", encoding="utf-8")
    assert mod.package_label(nested, root) == "my-packages"


def test_collect_rows_skips_duplicate_frontend_label(tmp_path: Path) -> None:
    root = tmp_path / "tree"
    be = root / "apps" / "backend"
    be.mkdir(parents=True)
    xml = Element("coverage", {"line-rate": "1.0"})
    SubElement(xml, "packages")
    (be / "coverage.xml").write_bytes(tostring(xml))

    fe1 = root / "apps" / "frontend" / "coverage-summary.json"
    fe1.parent.mkdir(parents=True)
    fe1.write_text(json.dumps({"total": {"lines": {"pct": 90.0}}}), encoding="utf-8")

    fe2 = root / "frontend" / "coverage-summary.json"
    fe2.parent.mkdir(parents=True)
    fe2.write_text(json.dumps({"total": {"lines": {"pct": 80.0}}}), encoding="utf-8")

    rows = mod.collect_rows(root)
    assert sum(1 for label, *_ in rows if label == "frontend") == 1


def test_main_with_rows(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "artifacts"
    be = root / "apps" / "backend"
    be.mkdir(parents=True)
    xml = Element("coverage", {"line-rate": "0.75", "branch-rate": "0.5"})
    SubElement(xml, "packages")
    (be / "coverage.xml").write_bytes(tostring(xml))
    assert mod.main(["script", str(root)]) == 0
    out = capsys.readouterr().out
    assert "`backend`" in out
    assert "75.00%" in out


def test_main_entrypoint_subprocess(tmp_path: Path) -> None:

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/ci/format_coverage_pr_comment.py"),
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
