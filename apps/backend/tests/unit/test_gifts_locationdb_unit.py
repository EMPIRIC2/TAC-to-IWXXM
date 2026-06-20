"""Unit tests for GiftsLocationDBAdapter – 0% coverage target."""

from unittest.mock import MagicMock, patch

from src.utilities.gifts_locationdb_adapter import GiftsLocationDBAdapter


def _make_adapter(openaip_service=None):
    """Helper to create adapter with mocked sub-components."""
    with (
        patch("src.utilities.gifts_locationdb_adapter.AirportRecordBuilder") as MockBuilder,
        patch("src.utilities.gifts_locationdb_adapter.get_airport_validator", return_value=None),
    ):
        mock_builder_instance = MagicMock()
        MockBuilder.return_value = mock_builder_instance
        adapter = GiftsLocationDBAdapter(openaip_service=openaip_service or MagicMock())
        adapter.record_builder = mock_builder_instance
    return adapter


class TestGiftsLocationDBAdapterInit:
    def test_init_creates_openaip_service_if_none(self):
        with (
            patch("src.utilities.gifts_locationdb_adapter.OpenAIPService") as MockService,
            patch("src.utilities.gifts_locationdb_adapter.AirportRecordBuilder"),
            patch("src.utilities.gifts_locationdb_adapter.get_airport_validator", return_value=None),
        ):
            adapter = GiftsLocationDBAdapter(openaip_service=None)
            MockService.assert_called_once()

    def test_init_uses_provided_service(self):
        mock_service = MagicMock()
        with (
            patch("src.utilities.gifts_locationdb_adapter.AirportRecordBuilder"),
            patch("src.utilities.gifts_locationdb_adapter.get_airport_validator", return_value=None),
        ):
            adapter = GiftsLocationDBAdapter(openaip_service=mock_service)
            assert adapter.openaip_service is mock_service

    def test_init_handles_missing_validator(self):
        with (
            patch("src.utilities.gifts_locationdb_adapter.AirportRecordBuilder"),
            patch(
                "src.utilities.gifts_locationdb_adapter.get_airport_validator",
                side_effect=Exception("not available"),
            ),
        ):
            adapter = GiftsLocationDBAdapter(openaip_service=MagicMock())
            assert adapter.airport_validator is None


class TestGiftsLocationDBAdapterGet:
    def test_get_returns_gifts_string(self):
        mock_service = MagicMock()
        mock_service.get_airport.return_value = {"name": "JFK"}

        adapter = _make_adapter(openaip_service=mock_service)
        adapter.record_builder.build_record.return_value = {"icao": "KJFK"}
        adapter.record_builder.get_gifts_format.return_value = "JFK Airport|JFK|KJFK|40.64,-73.78"

        result = adapter.get("KJFK")
        assert result == "JFK Airport|JFK|KJFK|40.64,-73.78"

    def test_get_none_when_no_data(self):
        mock_service = MagicMock()
        mock_service.get_airport.return_value = None

        adapter = _make_adapter(openaip_service=mock_service)
        adapter.record_builder.build_record.return_value = {"icao": "XXXX"}
        adapter.record_builder.get_gifts_format.return_value = None

        result = adapter.get("XXXX")
        assert result is None

    def test_get_empty_icao_returns_none(self):
        adapter = _make_adapter()
        result = adapter.get("")
        assert result is None

    def test_get_none_icao_returns_none(self):
        adapter = _make_adapter()
        result = adapter.get(None)
        assert result is None

    def test_get_normalises_icao_to_upper(self):
        mock_service = MagicMock()
        mock_service.get_airport.return_value = None

        adapter = _make_adapter(openaip_service=mock_service)
        adapter.record_builder.build_record.return_value = {}
        adapter.record_builder.get_gifts_format.return_value = "Airport|AAA|AAAA|0,0"

        adapter.get("kjfk")
        call_args = adapter.record_builder.build_record.call_args
        assert call_args[0][0] == "KJFK"


class TestGiftsLocationDBAdapterValidate:
    def test_validate_airport_true_when_found(self):
        mock_service = MagicMock()
        mock_service.get_airport.return_value = {"name": "Airport"}

        adapter = _make_adapter(openaip_service=mock_service)
        adapter.record_builder.build_record.return_value = {}
        adapter.record_builder.get_gifts_format.return_value = "Some|AAA|AAAA|0,0"

        assert adapter.validate_airport("AAAA") is True

    def test_validate_airport_false_when_not_found(self):
        mock_service = MagicMock()
        mock_service.get_airport.return_value = None

        adapter = _make_adapter(openaip_service=mock_service)
        adapter.record_builder.build_record.return_value = {}
        adapter.record_builder.get_gifts_format.return_value = None

        assert adapter.validate_airport("XXXX") is False
