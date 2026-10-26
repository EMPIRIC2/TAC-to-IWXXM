"""BUG-2026-08-11 - Quality metrics long-line XML diffs.

The Quality metrics tab was removed with its display helper and detail view.
Those paths stay absent so this report still has a repro.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_REMOVED = (
    "apps/frontend/src/utils/qualityMetricsDisplayXml.ts",
    "apps/frontend/src/app/components/QualityMetricsDetail.tsx",
)


def test_bug_2026_08_11_quality_metrics_display_paths_absent() -> None:
    present = [rel for rel in _REMOVED if (ROOT / rel).exists()]
    assert present == []
