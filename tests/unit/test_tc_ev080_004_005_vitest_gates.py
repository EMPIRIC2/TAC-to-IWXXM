"""TC-EV080-004 / TC-EV080-005 — Vitest coverage thresholds at 100% (EV-080 / ADR-007).

[Corpus: adr/ADR-007] [Corpus: tests]
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FE_VITEST = ROOT / "apps/frontend/vitest.config.ts"
SHARED_VITEST = ROOT / "packages/shared/vitest.config.ts"

# Executable FE modules that must not be excluded from coverage measurement.
FORBIDDEN_FE_EXCLUDES = (
    "tacEditorSpans.ts",
    "TacEditor.tsx",
    "liveAssist.ts",
    "useLiveWorkbenchAssist.ts",
    "gunzip.ts",
    "App.tsx",
)


def _threshold_block(text: str) -> str:
    m = re.search(r"thresholds:\s*\{([^}]+)\}", text, re.DOTALL)
    assert m, "expected thresholds block"
    return m.group(1)


@pytest.mark.unit
class TestTcEv080004VitestThresholds:
    """FE + shared Vitest thresholds are 100 on all four metrics."""

    def test_frontend_thresholds_100(self) -> None:
        text = FE_VITEST.read_text(encoding="utf-8")
        block = _threshold_block(text)
        for metric in ("lines", "functions", "branches", "statements"):
            assert re.search(rf"{metric}:\s*100\b", block), f"FE {metric} != 100"

    def test_shared_thresholds_100(self) -> None:
        text = SHARED_VITEST.read_text(encoding="utf-8")
        block = _threshold_block(text)
        for metric in ("lines", "functions", "branches", "statements"):
            assert re.search(rf"{metric}:\s*100\b", block), f"shared {metric} != 100"


@pytest.mark.unit
class TestTcEv080005NoExecutableFeExcludes:
    """Executable FE modules are not listed in coverage.exclude."""

    def test_no_forbidden_executable_excludes(self) -> None:
        text = FE_VITEST.read_text(encoding="utf-8")
        # Only inspect the coverage.exclude array.
        m = re.search(r"coverage:\s*\{.*?exclude:\s*\[(.*?)\]", text, re.DOTALL)
        assert m, "expected coverage.exclude array"
        exclude_block = m.group(1)
        for name in FORBIDDEN_FE_EXCLUDES:
            assert name not in exclude_block, (
                f"executable exclude still present: {name}"
            )
        assert "src/fixtures/**" in exclude_block
        assert "src/generated/**" in exclude_block
