"""BUG-2026-11-10 — IWXXM downloads are .xml; ZIP pairs TAC .txt/.tac.

Behavioral UI repro lives in:
``apps/frontend/src/test/bug-2026-11-10-download-ext-xml-tac.test.tsx``
(frontend ``npm test``). This module locks the wiring contract for CI ``bugs``.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_FILENAME = ROOT / "apps" / "frontend" / "src" / "utils" / "outputFilename.ts"
OUTPUT_FILENAME_TEST = (
    ROOT / "apps" / "frontend" / "src" / "utils" / "outputFilename.test.ts"
)
FILE_CONVERTER = (
    ROOT / "apps" / "frontend" / "src" / "app" / "components" / "FileConverter.tsx"
)
UI_REPRO = (
    ROOT
    / "apps"
    / "frontend"
    / "src"
    / "test"
    / "bug-2026-11-10-download-ext-xml-tac.test.tsx"
)


def test_bug_2026_11_10_helpers_exported() -> None:
    """TAC/IWXXM extension helpers and ZIP pair aligner must exist."""
    src = OUTPUT_FILENAME.read_text(encoding="utf-8")
    assert "export function toIwxxmDownloadName" in src
    assert "export function toTacSourceName" in src
    assert "export function alignConversionZipPairs" in src


def test_bug_2026_11_10_unit_tests_cover_success_and_failure() -> None:
    """Unit suite must assert success mapping and failure/collision modes."""
    src = OUTPUT_FILENAME_TEST.read_text(encoding="utf-8")
    assert "toTacSourceName" in src
    assert "alignConversionZipPairs" in src
    assert "failure" in src.lower() or "collision" in src.lower()
    assert "bulletin_report_1.xml" in src
    assert "never returns .xml" in src or "not.toMatch(/\\.xml$/i)" in src


def test_bug_2026_11_10_fileconverter_zip_includes_tac_and_xml() -> None:
    """Download-all must align pairs and write TAC + IWXXM members."""
    src = FILE_CONVERTER.read_text(encoding="utf-8")
    assert "alignConversionZipPairs" in src
    assert "toTacSourceName" in src
    assert "zip.file(tacName, file.originalContent)" in src
    assert "zip.file(xmlName, file.convertedContent)" in src


def test_bug_2026_11_10_ui_repro_exists() -> None:
    """Vitest UI regression must live under apps/frontend/src/test."""
    assert UI_REPRO.is_file()
    src = UI_REPRO.read_text(encoding="utf-8")
    assert "bulletin_report_1.xml" in src
    assert "METARYUD.txt" in src
