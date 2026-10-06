"""BUG-2026-10-04 - the live map scrolls upward and only draws continent chips.

The converter map must draw points and polygons, skip the region chips, and
must not pan the view when a report opens. Hover may open the card.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_MAP = (_ROOT / "apps/frontend/src/app/components/LiveWorldMap.tsx").read_text(
    encoding="utf-8"
)
_CONVERTER = (_ROOT / "apps/frontend/src/app/components/FileConverter.tsx").read_text(
    encoding="utf-8"
)
_PANES = (_ROOT / "apps/frontend/src/app/components/LiveConvertPaneGrid.tsx").read_text(
    encoding="utf-8"
)


def test_bug_2026_10_04_map_draws_features_without_clusters_or_upward_pan() -> None:
    assert "clusterPlaces" not in _MAP
    assert "panBy" not in _MAP
    assert "autoPan: false" in _MAP
    assert "L.polygon" in _MAP
    assert "live-map-tac" in _MAP
    assert "live-map-station" in _MAP
    assert "decodeTac" not in _MAP
    assert "mouseover" in _MAP
    assert "onOpenPlace" in _MAP
    assert "onOpenPlace" in _CONVERTER
    assert "scrollIntoView" in _CONVERTER
    assert "convert-weather-map" in _CONVERTER
    assert "min-h-[100dvh]" in _CONVERTER
    assert "min-h-[100dvh]" in _PANES
