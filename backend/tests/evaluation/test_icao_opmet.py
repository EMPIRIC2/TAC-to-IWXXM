"""
Tests for ICAO OPMET Data Exchange compliance features.

Tests Translation Centre configuration, ICAO region mapping,
and statistics endpoints.
"""
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.config.icao_opmet import (
    ICAO_LOCATION_INDICATOR,
    TRANSLATION_CENTRE_DESIGNATOR,
    TRANSLATION_CENTRE_NAME,
    get_icao_region,
    get_translation_centre_info,
)
from src.schemas.icao_opmet import ICAORegion
from src.utilities.security import verify_supabase_token


class TestICAORegionMapping:
    """Test ICAO region determination from airport codes."""

    def test_north_american_k_prefix(self):
        """Test K-prefix airports map to NAM region (Continental USA)."""
        assert get_icao_region("KJFK") == "NAM"
        assert get_icao_region("KLAX") == "NAM"
        assert get_icao_region("KORD") == "NAM"
        assert get_icao_region("KATL") == "NAM"

    def test_north_american_c_prefix(self):
        """Test C-prefix airports map to NAM region (Canada)."""
        assert get_icao_region("CYYZ") == "NAM"
        assert get_icao_region("CYVR") == "NAM"
        assert get_icao_region("CYUL") == "NAM"

    def test_north_american_m_prefix(self):
        """Test M-prefix airports map to NAM region (Central America/Mexico)."""
        assert get_icao_region("MMUN") == "NAM"
        assert get_icao_region("MMMX") == "NAM"

    def test_european_airports(self):
        """Test European airport codes map to EUR region."""
        assert get_icao_region("EGLL") == "EUR"  # London Heathrow
        assert get_icao_region("LFPG") == "EUR"  # Paris CDG
        assert get_icao_region("EDDF") == "EUR"  # Frankfurt
        assert get_icao_region("LEMD") == "EUR"  # Madrid
        assert get_icao_region("LIRF") == "EUR"  # Rome

    def test_asia_pacific_airports(self):
        """Test Asia-Pacific airport codes map to APAC region."""
        assert get_icao_region("RJAA") == "APAC"  # Tokyo Narita
        assert get_icao_region("RJTT") == "APAC"  # Tokyo Haneda
        assert get_icao_region("WSSS") == "APAC"  # Singapore
        assert get_icao_region("ZBAA") == "APAC"  # Beijing Capital
        assert get_icao_region("VHHH") == "APAC"  # Hong Kong

    def test_middle_east_airports(self):
        """Test Middle East airport codes map to MID region."""
        assert get_icao_region("OMDB") == "MID"  # Dubai
        assert get_icao_region("OEJN") == "MID"  # Jeddah
        assert get_icao_region("OTBD") == "MID"  # Doha
        assert get_icao_region("OIII") == "MID"  # Tehran

    def test_africa_airports(self):
        """Test African airport codes map to AFI region."""
        assert get_icao_region("FAOR") == "AFI"  # Johannesburg
        assert get_icao_region("HECA") == "AFI"  # Cairo
        assert get_icao_region("GMMN") == "AFI"  # Casablanca
        assert get_icao_region("FKKD") == "AFI"  # Kinshasa

    def test_south_american_airports(self):
        """Test South American airport codes map to SAM region."""
        assert get_icao_region("SBGR") == "SAM"  # Sao Paulo
        assert get_icao_region("SCEL") == "SAM"  # Santiago
        assert get_icao_region("SABE") == "SAM"  # Buenos Aires
        assert get_icao_region("SKBO") == "SAM"  # Bogota

    def test_greenland_airports(self):
        """Test Greenland airports map to NAM region (BG prefix)."""
        assert get_icao_region("BGBW") == "NAM"
        assert get_icao_region("BGGH") == "NAM"

    def test_invalid_airport_code_raises_error(self):
        """Test that invalid airport codes raise ValueError."""
        with pytest.raises(ValueError, match="Invalid ICAO airport code"):
            get_icao_region("ABC")  # Too short

        with pytest.raises(ValueError, match="Invalid ICAO airport code"):
            get_icao_region("ABCDE")  # Too long

        with pytest.raises(ValueError, match="Invalid ICAO airport code"):
            get_icao_region("")  # Empty string

    def test_case_insensitive(self):
        """Test region mapping is case-insensitive."""
        assert get_icao_region("kjfk") == "NAM"
        assert get_icao_region("KJFK") == "NAM"
        assert get_icao_region("KjFk") == "NAM"


class TestTranslationCentreConfiguration:
    """Test Translation Centre configuration and metadata."""

    def test_centre_info_structure(self):
        """Test Translation Centre info returns correct structure."""
        info = get_translation_centre_info()

        assert isinstance(info, dict)
        assert "translationCentreName" in info
        assert "translationCentreDesignator" in info
        assert "icaoLocationIndicator" in info
        assert "supportedIwxxmVersions" in info
        assert "supportedProducts" in info

    def test_centre_configuration_is_optional(self):
        """Test Translation Centre configuration is optional (None by default)."""
        # Translation Centre details are not set by default (not an official TC)
        # They can be configured via environment variables
        assert TRANSLATION_CENTRE_NAME is None or isinstance(TRANSLATION_CENTRE_NAME, str)
        assert TRANSLATION_CENTRE_DESIGNATOR is None or isinstance(TRANSLATION_CENTRE_DESIGNATOR, str)

    def test_icao_location_indicator_optional(self):
        """Test ICAO location indicator is optional (None by default)."""
        # ICAO location indicator can be configured via environment variable
        if ICAO_LOCATION_INDICATOR is not None:
            assert len(ICAO_LOCATION_INDICATOR) == 4

    def test_supported_iwxxm_versions(self):
        """Test supported IWXXM versions list."""
        info = get_translation_centre_info()
        versions = info["supportedIwxxmVersions"]

        assert "2025-2" in versions
        assert "2023-1" in versions
        assert len(versions) == 2  # Only 2 supported versions

    def test_supported_products(self):
        """Test supported aviation products."""
        info = get_translation_centre_info()
        products = info["supportedProducts"]

        assert "METAR" in products
        assert "SPECI" in products


class TestICAOOPMETEndpoints:
    """Test ICAO OPMET statistics API endpoints."""

    @pytest.fixture(autouse=True)
    def mock_db_pool(self):
        """Mock database session for all tests in this class."""
        from unittest.mock import AsyncMock

        # Create mock engine
        mock_engine = AsyncMock()
        mock_session = AsyncMock()

        # Mock execute() to return a result object with scalars() method
        mock_result = AsyncMock()
        # Default return empty dict for query results
        mock_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_result.scalars = AsyncMock(return_value=[])
        mock_result.first = AsyncMock(return_value=None)

        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.close = AsyncMock()

        # Create a proper async context manager mock for get_db_session
        mock_get_session_cm = AsyncMock()
        mock_get_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_session_cm.__aexit__ = AsyncMock(return_value=None)

        # Patch the get_db_session function to return our mock context manager
        with patch('src.services.database.get_db_session', return_value=mock_get_session_cm):
            yield

    @pytest.fixture
    def client(self):
        """Create test client with admin authentication override."""

        from src.api import app

        async def override_verify_token_admin():
            return {"sub": "admin-user-id", "aud": "test-project", "role": "admin"}

        app.dependency_overrides[verify_supabase_token] = override_verify_token_admin
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_centre_info_endpoint(self, client):
        """Test /api/v1/translation/centre-info endpoint."""
        response = client.get("/api/v1/translation/centre-info")

        assert response.status_code == 200
        data = response.json()

        # Translation Centre configuration is optional
        assert "centre_name" in data
        assert "centre_designator" in data
        assert "icao_location_indicator" in data
        assert "supported_iwxxm_versions" in data
        assert "supported_products" in data

        # Supported versions should include current versions
        if data["supported_iwxxm_versions"]:
            assert "2025-2" in data["supported_iwxxm_versions"]
            assert "2023-1" in data["supported_iwxxm_versions"]

        # METAR should be supported if product list is populated
        if data["supported_products"]:
            assert "METAR" in data["supported_products"]

    def test_airport_region_endpoint(self, client):
        """Test /api/v1/translation/airport-region/{code} endpoint."""
        response = client.get("/api/v1/translation/airport-region/KJFK")

        assert response.status_code == 200
        data = response.json()

        assert data["airport_code"] == "KJFK"
        assert data["icao_region"] == "NAM"
        assert "North American" in data["region_name"]

    def test_airport_region_invalid_code(self, client):
        """Test airport region endpoint with invalid code."""
        response = client.get("/api/v1/translation/airport-region/ABC")

        assert response.status_code == 400
        assert "Invalid ICAO airport code" in response.json()["detail"]

    def test_health_endpoint(self, client):
        """Test /api/v1/translation/health endpoint."""
        response = client.get("/api/v1/translation/health")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "translation-statistics"
        assert data["status"] == "healthy"
        assert isinstance(data["statistics_enabled"], bool)
        assert "retention_policy" in data
        assert "supported_regions" in data
        assert "supported_versions" in data

    def test_translation_centre_headers_optional(self, client):
        """Test that Translation Centre headers are present when configured."""
        response = client.get("/health")

        # Health endpoint should always return success
        assert response.status_code == 200

        # Headers may or may not be present depending on configuration
        # If TRANSLATION_CENTRE_DESIGNATOR is set, header should be present
        if TRANSLATION_CENTRE_DESIGNATOR:
            assert "x-translation-centre" in response.headers
            assert response.headers["x-translation-centre"] == TRANSLATION_CENTRE_DESIGNATOR

        if ICAO_LOCATION_INDICATOR:
            assert "x-icao-location-indicator" in response.headers
            assert response.headers["x-icao-location-indicator"] == ICAO_LOCATION_INDICATOR

    def test_statistics_endpoint_requires_date_range(self, client):
        """Test statistics endpoint validates date parameters."""
        # Missing parameters
        response = client.post("/api/v1/translation/statistics", json={})
        assert response.status_code == 422  # Validation error

    def test_statistics_endpoint_validates_date_range(self, client):
        """Test statistics endpoint rejects invalid date ranges."""
        # End date before start date
        response = client.post(
            "/api/v1/translation/statistics",
            json={
                "start_date": "2026-02-13T00:00:00Z",
                "end_date": "2026-02-01T00:00:00Z",
            }
        )
        assert response.status_code == 400
        assert "end_date must be after start_date" in response.json()["detail"]

    def test_statistics_endpoint_validates_max_range(self, client):
        """Test statistics endpoint rejects excessive date ranges."""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)  # 364 days (> 90 day limit)

        response = client.post(
            "/api/v1/translation/statistics",
            json={
                "start_date": start_date.isoformat() + "Z",
                "end_date": end_date.isoformat() + "Z",
            }
        )
        assert response.status_code == 400
        assert "cannot exceed 90 days" in response.json()["detail"]

    def test_recent_statistics_endpoint(self, client):
        """Test /api/v1/translation/statistics/recent endpoint."""
        response = client.get("/api/v1/translation/statistics/recent?hours=24")

        # Should return 200 even with no data (placeholder implementation)
        assert response.status_code == 200
        data = response.json()

        assert "period_start" in data
        assert "period_end" in data
        assert "total_translations" in data
        assert "success_rate" in data

    def test_statistics_by_region_endpoint(self, client):
        """Test /api/v1/translation/statistics/by-region endpoint."""
        from unittest.mock import AsyncMock

        from src.services.statistics import StatisticsService

        # Mock the service method directly to return expected data
        expected_data = {
            'AFI': {'total_translations': 10, 'successful_translations': 9},
            'APAC': {'total_translations': 20, 'successful_translations': 18},
            'ESAF': {'total_translations': 12, 'successful_translations': 11},
            'EUR': {'total_translations': 30, 'successful_translations': 27},
            'MID': {'total_translations': 15, 'successful_translations': 14},
            'NAM': {'total_translations': 50, 'successful_translations': 48},
            'NAT': {'total_translations': 18, 'successful_translations': 17},
            'SAM': {'total_translations': 25, 'successful_translations': 23},
            'WAFR': {'total_translations': 8, 'successful_translations': 7},
        }

        with patch.object(StatisticsService, 'get_statistics_by_region', new_callable=AsyncMock, return_value=expected_data):
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=1)

            response = client.get(
                f"/api/v1/translation/statistics/by-region"
                f"?start_date={start_date.isoformat()}Z"
                f"&end_date={end_date.isoformat()}Z"
            )

            assert response.status_code == 200
            data = response.json()

            # Should return stats for all regions
            assert isinstance(data, dict)
            for region in ICAORegion:
                assert region.value in data


class TestICAORegionEnum:
    """Test ICAORegion enum values."""

    def test_all_regions_defined(self):
        """Test all ICAO regions are defined in enum."""
        expected_regions = {"AFI", "APAC", "ESAF", "EUR", "MID", "NAM", "NAT", "SAM", "WAFR"}
        actual_regions = {region.value for region in ICAORegion}

        assert expected_regions == actual_regions

    def test_region_enum_values(self):
        """Test individual region enum values."""
        assert ICAORegion.NAM.value == "NAM"
        assert ICAORegion.EUR.value == "EUR"
        assert ICAORegion.APAC.value == "APAC"
        assert ICAORegion.MID.value == "MID"
        assert ICAORegion.AFI.value == "AFI"
        assert ICAORegion.SAM.value == "SAM"
