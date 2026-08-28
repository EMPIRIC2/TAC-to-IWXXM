"""EV-080 coverage fills for scripts/vendor/tip_diff_iwxxm.py."""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest
import scripts.vendor.tip_diff_iwxxm as tip_mod
from scripts.vendor.tip_diff_iwxxm import (
    _collect,
    _file_sha256,
    main,
    summarize,
)


def test_iwxxm_product_dir_layouts(tmp_path: Path) -> None:
    versioned = tmp_path / "2023-1" / "IWXXM"
    versioned.mkdir(parents=True)
    assert tip_mod._iwxxm_product_dir("2023-1", tmp_path) == versioned

    flat = tmp_path / "IWXXM"
    flat.mkdir()
    assert tip_mod._iwxxm_product_dir("flat", tmp_path) == flat

    with pytest.raises(SystemExit, match="No IWXXM tree"):
        tip_mod._iwxxm_product_dir("missing", tmp_path)


def test_file_sha256_and_collect_kinds(tmp_path: Path) -> None:
    f = tmp_path / "a.bin"
    f.write_bytes(b"data")
    assert _file_sha256(f) == hashlib.sha256(b"data").hexdigest()

    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "schema.xsd").write_text("<x/>", encoding="utf-8")
    rule = tree / "rule" / "rules.sch"
    rule.parent.mkdir(parents=True)
    rule.write_text("sch", encoding="utf-8")
    (tree / "rule" / "meta.rdf").write_text("rdf", encoding="utf-8")
    ex = tree / "examples" / "metar-A3-1.tac"
    ex.parent.mkdir(parents=True)
    ex.write_text("METAR", encoding="utf-8")
    (tree / "examples" / "metar-A3-1.xml").write_text("<x/>", encoding="utf-8")
    (tree / "readme.txt").write_text("other", encoding="utf-8")

    maps = _collect(tree)
    assert "schema.xsd" in maps["xsd"]
    assert any("rule" in k for k in maps["sch"])
    assert "examples/metar-A3-1" in maps["example"]
    assert "readme.txt" in maps["other"]
    assert dict(_collect(tmp_path / "missing")) == {}


def test_summarize_removed_and_changed_truncation(tmp_path: Path) -> None:
    root = tmp_path / "iwxxm"
    old_tree = root / "2023-1" / "IWXXM"
    new_tree = root / "2025-2" / "IWXXM"
    old_tree.mkdir(parents=True)
    new_tree.mkdir(parents=True)
    for i in range(85):
        (old_tree / f"gone-{i}.xsd").write_text("old", encoding="utf-8")
    (old_tree / "mut.xsd").write_text("v1", encoding="utf-8")
    (new_tree / "mut.xsd").write_text("v2", encoding="utf-8")
    report = summarize("2023-1", "2025-2", root=root)
    assert "+5 more" in report

    added_root = tmp_path / "added"
    (added_root / "2023-1" / "IWXXM").mkdir(parents=True)
    (added_root / "2025-2" / "IWXXM").mkdir(parents=True)
    (added_root / "2023-1" / "IWXXM" / "shared.xsd").write_text("s", encoding="utf-8")
    for i in range(85):
        (added_root / "2025-2" / "IWXXM" / f"extra-{i}.xsd").write_text(
            "e", encoding="utf-8"
        )
    assert "+5 more" in summarize("2023-1", "2025-2", root=added_root)

    outside = tmp_path / "outside"
    (outside / "2023-1" / "IWXXM").mkdir(parents=True)
    (outside / "2025-2" / "IWXXM").mkdir(parents=True)
    with patch.object(tip_mod, "_REPO_ROOT", tmp_path / "norepo"):
        rel_report = summarize("2023-1", "2025-2", root=outside)
    assert "2023-1" in rel_report


def test_summarize_changed_truncation(tmp_path: Path) -> None:
    root = tmp_path / "changed"
    old_tree = root / "2023-1" / "IWXXM"
    new_tree = root / "2025-2" / "IWXXM"
    old_tree.mkdir(parents=True)
    new_tree.mkdir(parents=True)
    for i in range(85):
        (old_tree / f"c{i}.xsd").write_text(f"v1-{i}", encoding="utf-8")
        (new_tree / f"c{i}.xsd").write_text(f"v2-{i}", encoding="utf-8")
    report = summarize("2023-1", "2025-2", root=root)
    assert "content-changed" in report
    assert "+5 more" in report


def test_main(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    root = tmp_path / "iwxxm"
    (root / "2023-1" / "IWXXM").mkdir(parents=True)
    (root / "2025-2" / "IWXXM").mkdir(parents=True)
    (root / "2023-1" / "IWXXM" / "a.xsd").write_text("a", encoding="utf-8")
    (root / "2025-2" / "IWXXM" / "a.xsd").write_text("a", encoding="utf-8")
    assert main(["--from", "2023-1", "--to", "2025-2", "--root", str(root)]) == 0
    assert "IWXXM tip-diff" in capsys.readouterr().out
