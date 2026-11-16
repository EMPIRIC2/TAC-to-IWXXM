"""BUG-2026-11-10 — Map send to converter must keep results drawer open.

Map Send now lives on the Live map page (App → pendingMapTac). FileConverter
must still keep the Results drawer open after a handoff and must not host a
Results Map tab. Behavioral UI repro:
``apps/frontend/src/app/components/FileConverter.test.tsx``
(``loads a Live map handoff into the TAC panes and scrolls up``).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILE_CONVERTER = (
    ROOT / "apps" / "frontend" / "src" / "app" / "components" / "FileConverter.tsx"
)
APP = ROOT / "apps" / "frontend" / "src" / "app" / "App.tsx"
UI_REPRO = (
    ROOT / "apps" / "frontend" / "src" / "app" / "components" / "FileConverter.test.tsx"
)
DRAWER_TABS = ROOT / "apps" / "frontend" / "src" / "utils" / "convertResultsDrawer.ts"


def test_bug_2026_11_10_map_send_does_not_close_results_drawer() -> None:
    """Live map Send must not collapse Results; Convert has no embedded Map tab."""
    converter = FILE_CONVERTER.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    tabs = DRAWER_TABS.read_text(encoding="utf-8")
    assert "convert-weather-map" not in converter
    assert "onOpenPlace={(place: LivePlace)" not in converter
    assert "setPendingMapTac" in app
    assert "setCurrentView('converter')" in app
    assert (
        "setResultsDrawerOpen(false)"
        not in app.split("handleMapOpenPlace", 1)[1].split(
            "const handleRequestLogin",
            1,
        )[0]
    )
    assert "ConvertResultsTab = 'iwxxm' | 'console' | 'decoder' | 'downloads'" in tabs


def test_bug_2026_11_10_map_send_ui_repro_asserts_drawer_open() -> None:
    """Vitest must assert drawer shell stays open after Live map handoff."""
    assert UI_REPRO.is_file()
    src = UI_REPRO.read_text(encoding="utf-8")
    assert "convert-results-drawer-shell" in src
    assert "queryByTestId('convert-results-tab-map')" in src
    assert "loads a Live map handoff into the TAC panes and scrolls up" in src
