"""Unit tests for ICAO OPMET statistics router."""

from __future__ import annotations

from datetime import UTC, datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from src.routers import icao_opmet as router_module
from src.schemas.icao_opmet import ICAORegion, TranslationStatisticsRequest


@pytest.fixture
def valid_stats_payload() -> dict:
    start = datetime(2026, 2, 1, tzinfo=UTC)
    end = datetime(2026, 2, 2, tzinfo=UTC)
    return {
        "period_start": start,
        "period_end": end,
        "total_translations": 100,
        "successful_translations": 90,
        "failed_translations": 8,
        "partial_translations": 2,
        "success_rate": 90.0,
        "average_duration_ms": 150.0,
        "median_duration_ms": 120.0,
        "translations_by_region": {ICAORegion.NAM: 60, ICAORegion.EUR: 40},
        "translations_by_version": {"2025-2": 95, "2023-1": 5},
        "translations_by_airport": {"KJFK": 10},
        "validation_layer_success_rates": {},
        "common_validation_errors": [{"layer": "XML_SCHEMA", "count": 2}],
    }


@pytest.mark.asyncio
async def test_get_centre_info_parses_online_since(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        router_module,
        "get_translation_centre_info",
        lambda: {
            "translationCentreName": "Centre Name",
            "translationCentreDesignator": "NOAA-MDL",
            "icaoLocationIndicator": "KWBC",
            "supportedIwxxmVersions": ["2025-2"],
            "supportedProducts": ["METAR"],
            "serviceOnlineSince": "2026-01-01T00:00:00Z",
            "technicalContact": "test@example.com",
        },
    )

    response = await router_module.get_centre_info()

    assert response.centre_name == "Centre Name"
    assert response.online_since is not None
    assert response.contact_email == "test@example.com"


@pytest.mark.asyncio
async def test_get_translation_statistics_validates_date_order() -> None:
    req = TranslationStatisticsRequest(
        start_date=datetime(2026, 2, 2, tzinfo=UTC),
        end_date=datetime(2026, 2, 1, tzinfo=UTC),
    )

    with pytest.raises(HTTPException, match="end_date must be after start_date"):
        await router_module.get_translation_statistics(req)


@pytest.mark.asyncio
async def test_get_translation_statistics_validates_max_range() -> None:
    req = TranslationStatisticsRequest(
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        end_date=datetime(2026, 6, 1, tzinfo=UTC),
    )

    with pytest.raises(HTTPException, match="Date range cannot exceed"):
        await router_module.get_translation_statistics(req)


@pytest.mark.asyncio
async def test_get_translation_statistics_success(
    monkeypatch: pytest.MonkeyPatch,
    valid_stats_payload: dict,
) -> None:
    req = TranslationStatisticsRequest(
        start_date=datetime(2026, 2, 1, tzinfo=UTC),
        end_date=datetime(2026, 2, 2, tzinfo=UTC),
        icao_region=ICAORegion.NAM,
        iwxxm_version="2025-2",
        airport_code="KJFK",
        include_airport_breakdown=True,
        include_error_details=True,
    )

    async def fake_get_statistics(**kwargs):
        assert kwargs["icao_region"] == "NAM"
        assert kwargs["iwxxm_version"] == "2025-2"
        assert kwargs["airport_code"] == "KJFK"
        assert kwargs["include_airport_breakdown"] is True
        assert kwargs["include_error_details"] is True
        return valid_stats_payload

    monkeypatch.setattr(router_module, "statistics_service", SimpleNamespace(get_statistics=fake_get_statistics))

    response = await router_module.get_translation_statistics(req)

    assert response.total_translations == 100
    assert response.success_rate == 90.0


@pytest.mark.asyncio
async def test_get_recent_statistics_success(
    monkeypatch: pytest.MonkeyPatch,
    valid_stats_payload: dict,
) -> None:
    async def fake_get_statistics(**kwargs):
        assert kwargs["icao_region"] == "EUR"
        assert kwargs["iwxxm_version"] == "2023-1"
        assert kwargs["include_airport_breakdown"] is False
        assert kwargs["include_error_details"] is False
        return valid_stats_payload

    monkeypatch.setattr(router_module, "statistics_service", SimpleNamespace(get_statistics=fake_get_statistics))

    response = await router_module.get_recent_statistics(
        hours=12,
        icao_region=ICAORegion.EUR,
        iwxxm_version="2023-1",
    )

    assert response.failed_translations == 8


@pytest.mark.asyncio
async def test_get_statistics_by_region_success(monkeypatch: pytest.MonkeyPatch) -> None:
    start = datetime(2026, 2, 1, tzinfo=UTC)
    end = datetime(2026, 2, 2, tzinfo=UTC)

    async def fake_by_region(**kwargs):
        assert kwargs["start_date"] == start
        assert kwargs["end_date"] == end
        return {"NAM": {"total": 10, "success_rate": 100.0}}

    monkeypatch.setattr(router_module, "statistics_service", SimpleNamespace(get_statistics_by_region=fake_by_region))

    response = await router_module.get_statistics_by_region(start, end)
    assert response["NAM"]["total"] == 10


@pytest.mark.asyncio
async def test_get_airport_region_success_and_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(router_module, "get_icao_region", lambda code: "NAM")

    response = await router_module.get_airport_region("kjfk")

    assert response["airport_code"] == "KJFK"
    assert response["region_name"] == "North American"

    def raise_bad(_code):
        raise ValueError("invalid airport")

    monkeypatch.setattr(router_module, "get_icao_region", raise_bad)

    with pytest.raises(HTTPException, match="invalid airport"):
        await router_module.get_airport_region("bad")


@pytest.mark.asyncio
async def test_statistics_health(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(router_module, "SUPPORTED_IWXXM_VERSIONS", ["2025-2", "2023-1"])

    health = await router_module.statistics_health()

    assert health["service"] == "translation-statistics"
    assert "NAM" in health["supported_regions"]
    assert "2025-2" in health["supported_versions"]
