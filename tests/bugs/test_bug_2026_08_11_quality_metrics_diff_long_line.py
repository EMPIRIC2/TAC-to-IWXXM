"""BUG-2026-08-11 — Quality metrics display XML must pretty-print after C14N.

Staging showed unified diffs as one ~3k-character C14N line. The FE helper
``qualityMetricsDisplayXml`` must pipe C14N through ``prettyPrintXml`` so
line-oriented diffs stay human-readable.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DISPLAY = ROOT / "apps" / "frontend" / "src" / "utils" / "qualityMetricsDisplayXml.ts"
DETAIL = (
    ROOT
    / "apps"
    / "frontend"
    / "src"
    / "app"
    / "components"
    / "QualityMetricsDetail.tsx"
)


def test_bug_2026_08_11_display_xml_pretty_prints_c14n() -> None:
    src = DISPLAY.read_text(encoding="utf-8")
    assert "prettyPrintXml" in src
    assert "c14nXml" in src
    # Must not return bare C14N without pretty-print.
    assert "return c14nXml(" not in src.replace(" ", "")


def test_bug_2026_08_11_detail_uses_display_helper_for_diff() -> None:
    src = DETAIL.read_text(encoding="utf-8")
    assert "qualityMetricsDisplayXml" in src
    assert "unifiedLineDiff" in src
