"""Tests for packages/shared Python exports."""

from __future__ import annotations

import metar_shared
from metar_shared.constants import METAR_CORS_ORIGINS_ENV, VITE_API_BASE_URL_ENV
from metar_shared.env import parse_comma_separated_origins


def test_constants_export_cors_and_vite_names() -> None:
    assert METAR_CORS_ORIGINS_ENV == "METAR_CORS_ORIGINS"
    assert VITE_API_BASE_URL_ENV == "VITE_API_BASE_URL"


def test_parse_comma_separated_origins_trims_and_splits() -> None:
    assert parse_comma_separated_origins("https://a.test, https://b.test") == [
        "https://a.test",
        "https://b.test",
    ]


def test_parse_comma_separated_origins_empty_values() -> None:
    assert parse_comma_separated_origins(None) == []
    assert parse_comma_separated_origins("") == []
    assert parse_comma_separated_origins("   ") == []


def test_package_all_exports_are_importable() -> None:
    for name in metar_shared.__all__:
        assert hasattr(metar_shared, name)
