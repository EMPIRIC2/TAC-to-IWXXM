"""BUG-2026-08-07 / #904 - Download must use current Output filename after convert.

Behavioral UI repro lives in:
``apps/frontend/src/test/bug-2026-08-07-output-filename-download-stale.test.tsx``
(frontend ``npm test``). This module locks the wiring contract for CI ``bugs``.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILENAME = ROOT / "apps" / "frontend" / "src" / "utils" / "outputFilename.ts"
FILE_CONVERTER = (
    ROOT / "apps" / "frontend" / "src" / "app" / "components" / "FileConverter.tsx"
)


def test_bug_2026_08_07_manual_download_helper_exported() -> None:
    """Helper derives download XML name from the *current* field (not baked name)."""
    src = OUTPUT_FILENAME.read_text(encoding="utf-8")
    assert "export function manualDownloadXmlName" in src


def test_bug_2026_08_07_fileconverter_download_uses_current_field() -> None:
    """Single + ZIP download paths must call the current-field helper for manuals."""
    src = FILE_CONVERTER.read_text(encoding="utf-8")
    assert "manualDownloadXmlName" in src
    # Stale pattern: download attribute from convert-time originalName alone.
    assert "a.download = file.originalName.replace" not in src
