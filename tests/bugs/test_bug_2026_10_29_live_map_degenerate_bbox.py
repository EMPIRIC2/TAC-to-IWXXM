"""BUG-2026-10-29 - live map must not request a zero-area bbox.

Staging FE called ``/api/v1/live-map`` with west==east and south==north
(Leaflet collapsed bounds at setView center). Guard in liveMap.ts before fetch.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_LIVE_MAP = (_ROOT / "apps/frontend/src/utils/liveMap.ts").read_text(encoding="utf-8")


def test_bug_2026_10_29_live_map_sanitizes_degenerate_bounds() -> None:
    assert "DEFAULT_LIVE_MAP_BOUNDS" in _LIVE_MAP
    assert "isUsableMapBounds" in _LIVE_MAP
    assert "sanitizeMapBounds" in _LIVE_MAP
    assert (
        "sanitizeMapBounds"
        in _LIVE_MAP.split("export async function fetchLivePlaces")[1][:800]
    )
    assert "sanitizeMapBounds" in _LIVE_MAP.split("export function boundsOf")[1][:600]
