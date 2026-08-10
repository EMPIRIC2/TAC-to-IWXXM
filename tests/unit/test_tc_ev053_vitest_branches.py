"""TC-EV053-001 / T1.3 — Vitest branches ≥95; FileConverter in coverage set.

[Corpus: tests] [Corpus: adr/ADR-007] EV-053 / #968
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FRONTEND_VITEST = ROOT / "apps" / "frontend" / "vitest.config.ts"


def _vitest_thresholds(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    out: dict[str, int] = {}
    for key in ("lines", "functions", "branches", "statements"):
        m = re.search(rf"{key}:\s*(\d+)", text)
        assert m, f"missing {key} threshold in {path}"
        out[key] = int(m.group(1))
    return out


@pytest.mark.unit
class TestTcEv053VitestBranches:
    """AC1 — config enforces branches ≥95 with FileConverter included."""

    def test_all_thresholds_at_least_95(self) -> None:
        thresholds = _vitest_thresholds(FRONTEND_VITEST)
        for metric, value in thresholds.items():
            assert value >= 95, f"{metric}={value} < 95"

    def test_fileconverter_not_in_coverage_exclude(self) -> None:
        text = FRONTEND_VITEST.read_text(encoding="utf-8")
        # Isolate coverage.exclude block (before thresholds).
        block = text.split("coverage:")[1].split("thresholds:")[0]
        assert "src/app/components/FileConverter.tsx" not in block
        assert "branches: 84" not in text
