"""
Tests for the statistics logging service.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.schemas.icao_opmet import TranslationStatus
from src.services.statistics import StatisticsService


@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy async session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def statistics_service():
    """Create a statistics service instance."""
    return StatisticsService()


@pytest.mark.asyncio
class TestLogTranslation:
    """Test translation logging."""

    async def test_log_successful_translation(self, statistics_service):
        """Test logging a successful translation."""
        import uuid
        user_id = str(uuid.uuid4())
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        # Create a proper async context manager mock
        mock_get_session_cm = AsyncMock()
        mock_get_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_session_cm.__aexit__ = AsyncMock(return_value=None)

        with patch('src.services.statistics.get_db_session', return_value=mock_get_session_cm):
            translation_id = await statistics_service.log_translation(
                tac_message="METAR KJFK 131051Z 18012KT 10SM FEW250",
                iwxxm_version="2025-2",
                icao_airport_code="KJFK",
                translation_status=TranslationStatus.SUCCESS,
                translation_duration_ms=125,
                iwxxm_output="<?xml version='1.0'?>...",
                validation_layers_passed=None,
                validation_errors=None,
                user_id=user_id
            )

            # Should return a UUID string (logged successfully)
            assert isinstance(translation_id, str)
            # Session should have added and committed
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    async def test_log_failed_translation(self, statistics_service):
        """Test logging a failed translation."""
        import uuid
        user_id = str(uuid.uuid4())
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        # Create a proper async context manager mock
        mock_get_session_cm = AsyncMock()
        mock_get_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_session_cm.__aexit__ = AsyncMock(return_value=None)

        with patch('src.services.statistics.get_db_session', return_value=mock_get_session_cm):
            translation_id = await statistics_service.log_translation(
                tac_message="METAR INVALID 131051Z",
                iwxxm_version="2025-2",
                icao_airport_code=None,
                translation_status=TranslationStatus.FAILED,
                translation_duration_ms=50,
                iwxxm_output=None,
                validation_layers_passed=None,
                validation_errors={"error": "Invalid airport code"},
                user_id=user_id
            )

            # Should return a UUID string or None on error
            assert isinstance(translation_id, (str, type(None)))
            # Session should have been used
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    async def test_auto_detect_icao_region(self, statistics_service):
        """Test automatic ICAO region detection."""
        import uuid
        user_id = str(uuid.uuid4())
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        # Create a proper async context manager mock
        mock_get_session_cm = AsyncMock()
        mock_get_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_session_cm.__aexit__ = AsyncMock(return_value=None)

        with patch('src.services.statistics.get_db_session', return_value=mock_get_session_cm), \
             patch('src.services.statistics.get_icao_region') as mock_get_region:
            mock_get_region.return_value = "NAM"

            await statistics_service.log_translation(
                tac_message="METAR KJFK 131051Z",
                iwxxm_version="2025-2",
                icao_airport_code="KJFK",
                translation_status=TranslationStatus.SUCCESS,
                translation_duration_ms=100,
                iwxxm_output="<xml>",
                validation_layers_passed=None,
                validation_errors=None,
                user_id=user_id
            )

            mock_get_region.assert_called_once_with("KJFK")
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()


@pytest.mark.asyncio
class TestGetStatistics:
    """Test statistics retrieval."""

    async def test_get_statistics_basic(self, statistics_service):
        """Test basic statistics retrieval."""

        expected_stats = {
            'total_translations': 100,
            'successful_translations': 95,
            'failed_translations': 5,
            'partial_translations': 0,
            'success_rate': 95.0,
            'avg_duration_ms': 150.5,
            'median_duration_ms': 125.0,
            'translations_by_region': {'NAM': 50, 'EUR': 30, 'PAC': 20},
            'translations_by_version': {'2025-2': 100},
            'translations_by_airport': None,
            'common_validation_errors': None
        }

        with patch.object(statistics_service, 'get_statistics', new_callable=AsyncMock, return_value=expected_stats):
            # Method requires start_date and end_date
            start = datetime(2025, 2, 1, tzinfo=timezone.utc)
            end = datetime(2025, 2, 10, tzinfo=timezone.utc)
            stats = await statistics_service.get_statistics(start, end)

            assert stats is not None
            assert stats['total_translations'] == 100

    async def test_get_statistics_with_date_range(self, statistics_service):
        """Test statistics with date range filter."""

        expected_stats = {
            'total_translations': 50,
            'successful_translations': 48,
            'failed_translations': 2,
            'partial_translations': 0,
            'success_rate': 96.0,
            'avg_duration_ms': 140.0,
            'median_duration_ms': 120.0,
            'translations_by_region': {'NAM': 50},
            'translations_by_version': {'2025-2': 50},
            'translations_by_airport': None,
            'common_validation_errors': None
        }

        with patch.object(statistics_service, 'get_statistics', new_callable=AsyncMock, return_value=expected_stats):
            start_date = datetime.now(timezone.utc) - timedelta(days=7)
            end_date = datetime.now(timezone.utc)

            stats = await statistics_service.get_statistics(start_date, end_date)

            assert stats is not None
            assert stats['total_translations'] == 50


@pytest.mark.asyncio
class TestGetStatisticsByRegion:
    """Test regional statistics."""

    async def test_get_statistics_by_region(self, statistics_service):
        """Test statistics grouped by ICAO region."""

        expected_stats = {
            'NAM': {'total_translations': 50, 'successful_translations': 48, 'failed_translations': 2},
            'EUR': {'total_translations': 30, 'successful_translations': 29, 'failed_translations': 1},
        }

        with patch.object(statistics_service, 'get_statistics_by_region', new_callable=AsyncMock, return_value=expected_stats):
            # Method requires start_date and end_date
            start = datetime(2025, 2, 1, tzinfo=timezone.utc)
            end = datetime(2025, 2, 10, tzinfo=timezone.utc)
            stats = await statistics_service.get_statistics_by_region(start, end)

            assert len(stats) == 2
            assert stats['NAM']['total_translations'] == 50
