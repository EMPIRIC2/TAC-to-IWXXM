"""BUG-2026-10-04 - the live map scrolls upward and only draws continent chips.

The Live map must draw points and polygons, skip the region chips, and
must not pan the view when a report opens. Hover may open the card.
Convert Results no longer hosts an embedded map tab.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
_FE = _ROOT / "apps/frontend/src"
_MAP = "\n".join(
    (
        (_FE / "app/components/LiveWorldMap.tsx").read_text(encoding="utf-8"),
        (_FE / "app/components/LiveWorldMapView.tsx").read_text(encoding="utf-8"),
        (_FE / "hooks/useLiveWorldMap.ts").read_text(encoding="utf-8"),
        (_FE / "utils/liveWorldMapHelpers.tsx").read_text(encoding="utf-8"),
    )
)
_STATION_POPUP = (_FE / "app/components/StationPopup.tsx").read_text(encoding="utf-8")
_CONVERTER = "\n".join(
    (
        (_FE / "app/components/FileConverter.tsx").read_text(encoding="utf-8"),
        (_FE / "app/components/FileConverterChromeToolbar.tsx").read_text(
            encoding="utf-8"
        ),
        (_FE / "hooks/useFileConverterPart2.ts").read_text(encoding="utf-8"),
    )
)
_VISUALS = (_FE / "app/components/DecodeVisualsPage.tsx").read_text(encoding="utf-8")
_DRAWER = (_FE / "utils/convertResultsDrawer.ts").read_text(encoding="utf-8")
_PANES = (_FE / "app/components/LiveConvertPaneGrid.tsx").read_text(encoding="utf-8")


def test_bug_2026_10_04_map_draws_features_without_clusters_or_upward_pan() -> None:
    assert "clusterPlaces" not in _MAP
    assert "panBy" not in _MAP
    assert "autoPan: false" in _MAP
    assert "L.polygon" in _MAP
    assert "StationPopup" in _MAP
    assert "live-map-tac" in _STATION_POPUP
    assert "live-map-station" in _STATION_POPUP
    assert "decodeTac" not in _MAP
    assert "mouseover" in _MAP
    assert "onOpenPlace" in _MAP
    assert "onOpenPlace" in _VISUALS
    assert "LiveWorldMap" in _VISUALS
    assert "scrollIntoView" in _CONVERTER
    assert "convert-weather-map" not in _CONVERTER
    assert "convert-results-tab-map" not in _CONVERTER
    assert (
        "ConvertResultsTab = 'iwxxm' | 'console' | 'decoder' | 'downloads'" in _DRAWER
    )
    assert "{ id: 'map', label: 'Map' }" not in _DRAWER
    assert "convert-panes-toggle" in _CONVERTER
    assert "min-h-[100dvh]" not in _CONVERTER
    assert "min-h-[100dvh]" not in _PANES
    assert "min-h-[24rem]" in _MAP
