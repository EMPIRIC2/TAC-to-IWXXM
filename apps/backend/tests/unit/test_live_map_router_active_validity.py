"""Active reports validity stamps on live-map slim payload."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import cast

from src.routers import live_map as live_map_router

_places_for_browser = cast(
    Callable[[Sequence[Mapping[str, object]]], list[dict[str, object]]],
    vars(live_map_router)["_places_for_browser"],
)


def test_places_for_browser_passes_valid_from_to() -> None:
    """Optional validity stamps stay on the public list; IWXXM stays off."""
    places = _places_for_browser(
        [
            {
                "place_key": "KJFK",
                "product": "taf",
                "latitude": 40.64,
                "longitude": -73.78,
                "geometry": {"kind": "point"},
                "reports": [
                    {
                        "observed_at": "2026-11-13T12:00:00+00:00",
                        "tac": "TAF KJFK",
                        "iwxxm": "<iwxxm/>",
                        "issues": ["x"],
                        "valid_from": "2026-11-13T12:00:00Z",
                        "valid_to": "2026-11-14T12:00:00Z",
                    }
                ],
            }
        ]
    )
    reports = cast(list[dict[str, object]], places[0]["reports"])
    assert reports[0] == {
        "observed_at": "2026-11-13T12:00:00+00:00",
        "tac": "TAF KJFK",
        "valid_from": "2026-11-13T12:00:00Z",
        "valid_to": "2026-11-14T12:00:00Z",
    }


def test_places_for_browser_omits_blank_validity() -> None:
    """Blank validity stamps are not emitted."""
    places = _places_for_browser(
        [
            {
                "place_key": "KJFK",
                "product": "metar",
                "latitude": 40.64,
                "longitude": -73.78,
                "geometry": {"kind": "point"},
                "reports": [
                    {
                        "observed_at": "2026-11-13T12:00:00+00:00",
                        "tac": "METAR KJFK",
                        "valid_from": "  ",
                        "valid_to": "",
                    }
                ],
            }
        ]
    )
    reports = cast(list[dict[str, object]], places[0]["reports"])
    assert reports[0] == {
        "observed_at": "2026-11-13T12:00:00+00:00",
        "tac": "METAR KJFK",
    }
