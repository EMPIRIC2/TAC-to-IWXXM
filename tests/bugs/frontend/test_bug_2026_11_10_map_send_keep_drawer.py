"""BUG-2026-11-10 — Map send to converter must keep results drawer open.

Behavioral UI repro lives in
``apps/frontend/src/app/components/FileConverter.test.tsx``
(``loads a map report into the TAC panes and scrolls up``). This module locks
the wiring contract for CI ``bugs``.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILE_CONVERTER = (
    ROOT / "apps" / "frontend" / "src" / "app" / "components" / "FileConverter.tsx"
)
UI_REPRO = (
    ROOT / "apps" / "frontend" / "src" / "app" / "components" / "FileConverter.test.tsx"
)


def test_bug_2026_11_10_map_send_does_not_close_results_drawer() -> None:
    """Map onOpenPlace must not collapse the Convert results drawer."""
    src = FILE_CONVERTER.read_text(encoding="utf-8")
    on_open = src.split("onOpenPlace={(place: LivePlace) => {", 1)[1].split(
        "}}",
        1,
    )[0]
    assert "setResultsDrawerOpen(false)" not in on_open
    assert "setManualInput(tac)" in on_open
    assert "setConverterOpen(true)" in on_open


def test_bug_2026_11_10_map_send_ui_repro_asserts_drawer_open() -> None:
    """Vitest must assert drawer shell and Map panel stay open after handoff."""
    assert UI_REPRO.is_file()
    src = UI_REPRO.read_text(encoding="utf-8")
    assert "convert-results-drawer-shell" in src
    assert "convert-results-panel-map" in src
    assert "BUG-2026-11-10 map-send-keep-drawer" in src
