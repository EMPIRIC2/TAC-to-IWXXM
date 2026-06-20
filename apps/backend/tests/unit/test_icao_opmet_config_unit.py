"""Unit tests for src.config.icao_opmet."""

from __future__ import annotations

import pytest

from src.config import icao_opmet as cfg


@pytest.mark.parametrize(
    "code,expected",
    [
        ("KJFK", "NAM"),
        ("CYVR", "NAM"),
        ("MMMX", "NAM"),
        ("FAOR", "AFI"),
        ("EGLL", "EUR"),
        ("RJTT", "APAC"),
        ("OMDB", "MID"),
        ("SBGR", "SAM"),
    ],
)
def test_get_icao_region_known_prefixes(code, expected):
    assert cfg.get_icao_region(code) == expected


@pytest.mark.parametrize("code", ["", "ABC", "ABCDE", None])
def test_get_icao_region_rejects_invalid_codes(code):
    with pytest.raises(ValueError):
        cfg.get_icao_region(code)


@pytest.mark.parametrize(
    "code,expected",
    [
        ("QZZZ", "NAM"),
        ("NZZZ", "APAC"),
        ("SZZZ", "SAM"),
        ("HZZZ", "AFI"),
        ("DZZZ", "MID"),
        ("EZZZ", "EUR"),
    ],
)
def test_get_icao_region_fallback_by_first_letter(code, expected):
    assert cfg.get_icao_region(code) == expected


def test_get_translation_centre_info_contains_expected_keys():
    info = cfg.get_translation_centre_info()
    assert "translationCentreName" in info
    assert "supportedIwxxmVersions" in info
    assert info["supportedProducts"] == ["METAR", "SPECI"]


def test_should_log_statistics_reflects_module_flag(monkeypatch):
    monkeypatch.setattr(cfg, "ENABLE_STATISTICS", True)
    assert cfg.should_log_statistics() is True
    monkeypatch.setattr(cfg, "ENABLE_STATISTICS", False)
    assert cfg.should_log_statistics() is False


def test_should_send_webhooks_requires_enabled_and_urls(monkeypatch):
    monkeypatch.setattr(cfg, "ENABLE_WEBHOOKS", False)
    monkeypatch.setattr(cfg, "WEBHOOK_URLS", ["https://example.test"])
    assert cfg.should_send_webhooks() is False

    monkeypatch.setattr(cfg, "ENABLE_WEBHOOKS", True)
    monkeypatch.setattr(cfg, "WEBHOOK_URLS", [])
    assert cfg.should_send_webhooks() is False

    monkeypatch.setattr(cfg, "ENABLE_WEBHOOKS", True)
    monkeypatch.setattr(cfg, "WEBHOOK_URLS", ["https://example.test"])
    assert cfg.should_send_webhooks() is True
