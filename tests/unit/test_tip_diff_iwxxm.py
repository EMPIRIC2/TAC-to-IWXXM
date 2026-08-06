"""Unit tests for vendor tip-diff summary (#852 / TC-EV038-005)."""

from __future__ import annotations

from pathlib import Path

from scripts.vendor.tip_diff_iwxxm import _collect, _diff_maps, summarize


def test_collect_and_diff_example_stems(tmp_path: Path) -> None:
    old = tmp_path / "old" / "IWXXM"
    new = tmp_path / "new" / "IWXXM"
    (old / "examples").mkdir(parents=True)
    (new / "examples").mkdir(parents=True)
    (old / "a.xsd").write_text("<xs/>", encoding="utf-8")
    (new / "a.xsd").write_text("<xs/>", encoding="utf-8")
    (new / "b.xsd").write_text("<xs2/>", encoding="utf-8")
    (old / "examples" / "metar-A3-1.tac").write_text("METAR", encoding="utf-8")
    (new / "examples" / "metar-A3-1.tac").write_text("METAR", encoding="utf-8")
    (new / "examples" / "vona-A7-1.tac").write_text("VONA", encoding="utf-8")

    old_m = _collect(old)
    new_m = _collect(new)
    added, removed, changed = _diff_maps(old_m["xsd"], new_m["xsd"])
    assert added == ["b.xsd"]
    assert removed == []
    assert changed == []

    ex_added, _, _ = _diff_maps(old_m["example"], new_m["example"])
    assert "examples/vona-A7-1" in ex_added


def test_summarize_real_vendor_trees() -> None:
    """Smoke: pinned 2023-1 → 2025-2 trees produce a non-empty report."""
    report = summarize("2023-1", "2025-2", root=Path("vendor/schemas/iwxxm"))
    assert "IWXXM tip-diff: 2023-1 → 2025-2" in report
    assert "## XSD" in report
    assert "## Example stems" in report
