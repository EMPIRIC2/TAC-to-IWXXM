"""Unit tests for OpenAIPClient – 0% coverage target."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.clients.openaip_client import Airport, OpenAIPClient

# ---------------------------------------------------------------------------
# Airport dataclass helpers
# ---------------------------------------------------------------------------


def make_airport_feature(icao="KJFK", name="Test Airport", country="US", elevation=9.14, elevation_unit="m"):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-73.7789, 40.6398]},
        "properties": {
            "icaoCode": icao,
            "name": name,
            "country": country,
            "elevation": elevation,
            "elevationUnit": elevation_unit,
        },
    }


class TestAirportDataclass:
    def test_lat_lon_from_geojson(self):
        a = Airport(
            icao_code="KJFK",
            name="JFK",
            country="US",
            geometry={"type": "Point", "coordinates": [-73.7789, 40.6398]},
        )
        lat, lon = a.lat_lon
        assert abs(lat - 40.6398) < 0.001
        assert abs(lon - (-73.7789)) < 0.001

    def test_lat_lon_no_geometry(self):
        a = Airport(icao_code="XXXX", name="X", country="XX")
        assert a.lat_lon is None
        assert a.latitude is None
        assert a.longitude is None

    def test_lat_lon_non_point_geometry(self):
        a = Airport(icao_code="XXXX", name="X", country="XX", geometry={"type": "Polygon", "coordinates": []})
        assert a.lat_lon is None

    def test_lat_lon_point_with_insufficient_coordinates(self):
        a = Airport(
            icao_code="XXXX",
            name="X",
            country="XX",
            geometry={"type": "Point", "coordinates": [-73.7789]},
        )
        assert a.lat_lon is None


class TestOpenAIPClientLocal:
    def test_init_defaults(self):
        client = OpenAIPClient()
        assert client.data_path == Path("data/open-aip")
        assert client._cache == {}
        assert not client._loaded

    def test_init_custom_path(self, tmp_path):
        client = OpenAIPClient(data_path=tmp_path)
        assert client.data_path == tmp_path

    def test_load_local_data_geojson(self, tmp_path):
        feature_collection = {
            "type": "FeatureCollection",
            "features": [make_airport_feature("KJFK"), make_airport_feature("EGLL", country="GB")],
        }
        geojson_file = tmp_path / "gb_apt.geojson"
        geojson_file.write_text(json.dumps(feature_collection))

        client = OpenAIPClient(data_path=tmp_path)
        client._load_local_data()

        assert "KJFK" in client._cache
        assert "EGLL" in client._cache
        assert client._loaded is True

    def test_load_local_data_feet_conversion(self, tmp_path):
        feature = make_airport_feature("KJFK", elevation=30.0, elevation_unit="ft")
        geojson_file = tmp_path / "us_apt.geojson"
        geojson_file.write_text(json.dumps({"type": "FeatureCollection", "features": [feature]}))

        client = OpenAIPClient(data_path=tmp_path)
        client._load_local_data()
        airport = client._cache.get("KJFK")
        assert airport is not None
        assert abs(airport.elevation - 30.0 * 0.3048) < 0.001

    def test_load_local_data_already_loaded(self, tmp_path):
        client = OpenAIPClient(data_path=tmp_path)
        client._loaded = True
        # Should not scan directory again
        client._load_local_data()
        assert client._loaded is True

    def test_load_local_data_skips_bad_file(self, tmp_path):
        bad_file = tmp_path / "bad_apt.geojson"
        bad_file.write_text("NOT JSON {{{")
        client = OpenAIPClient(data_path=tmp_path)
        # Should not raise
        client._load_local_data()
        assert client._loaded is True

    def test_load_local_data_no_icao(self, tmp_path):
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0, 0]},
            "properties": {"name": "No ICAO"},
        }
        geojson_file = tmp_path / "xx_apt.geojson"
        geojson_file.write_text(json.dumps({"type": "FeatureCollection", "features": [feature]}))
        client = OpenAIPClient(data_path=tmp_path)
        client._load_local_data()
        assert len(client._cache) == 0

    def test_get_airport_from_cache(self, tmp_path):
        feature_collection = {
            "type": "FeatureCollection",
            "features": [make_airport_feature("KJFK")],
        }
        geojson_file = tmp_path / "us_apt.geojson"
        geojson_file.write_text(json.dumps(feature_collection))

        client = OpenAIPClient(data_path=tmp_path)
        airport = client.get_airport_by_icao("KJFK")
        assert airport is not None
        assert airport.icao_code == "KJFK"

    def test_get_airport_case_insensitive(self, tmp_path):
        feature_collection = {"type": "FeatureCollection", "features": [make_airport_feature("KJFK")]}
        (tmp_path / "us_apt.geojson").write_text(json.dumps(feature_collection))
        client = OpenAIPClient(data_path=tmp_path)
        assert client.get_airport_by_icao("kjfk") is not None

    def test_get_airport_not_found(self, tmp_path):
        client = OpenAIPClient(data_path=tmp_path)
        assert client.get_airport_by_icao("XXXX") is None

    def test_parse_feature_minimal(self):
        client = OpenAIPClient()
        feature = {
            "type": "Feature",
            "geometry": None,
            "properties": {"icaoCode": "ABCD", "name": "Mini", "country": "AB"},
        }
        airport = client._parse_feature(feature)
        assert airport is not None
        assert airport.icao_code == "ABCD"

    def test_parse_feature_no_icao_returns_none(self):
        client = OpenAIPClient()
        airport = client._parse_feature({"type": "Feature", "geometry": None, "properties": {}})
        assert airport is None

    def test_parse_feature_uses_icao_fallback_and_iata(self):
        client = OpenAIPClient()
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [7.0, 48.0]},
            "properties": {
                "icao": "eddf",
                "iata": "FRA",
                "name": "Frankfurt",
                "country": "DE",
                "elevation": "364",
            },
        }

        airport = client._parse_feature(feature)

        assert airport is not None
        assert airport.icao_code == "EDDF"
        assert airport.iata_code == "FRA"
        assert airport.elevation == 364.0
        assert airport.source == "openaip"

    def test_search_airports_filters_country_bbox_and_limit(self, tmp_path):
        klax_feature = make_airport_feature("KLAX", country="US")
        klax_feature["geometry"] = {
            "type": "Point",
            "coordinates": [-118.4085, 33.9416],
        }
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                make_airport_feature("KJFK", country="US"),
                klax_feature,
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [2.55, 49.01]},
                    "properties": {
                        "icaoCode": "LFPG",
                        "name": "CDG",
                        "country": "FR",
                    },
                },
            ],
        }
        (tmp_path / "airports_apt.geojson").write_text(json.dumps(feature_collection))

        client = OpenAIPClient(data_path=tmp_path)

        us_results = client.search_airports(country="us")
        bbox_results = client.search_airports(bbox=(-80.0, 39.0, -70.0, 42.0), limit=5)
        limited_results = client.search_airports(limit=1)

        assert {airport.icao_code for airport in us_results} == {"KJFK", "KLAX"}
        assert [airport.icao_code for airport in bbox_results] == ["KJFK"]
        assert len(limited_results) == 1

    def test_search_airports_bbox_skips_missing_coordinates(self):
        client = OpenAIPClient()
        client._cache = {
            "TEST": Airport(icao_code="TEST", name="NoCoords", country="US", geometry=None),
            "KJFK": Airport(
                icao_code="KJFK",
                name="JFK",
                country="US",
                geometry={"type": "Point", "coordinates": [-73.7789, 40.6398]},
            ),
        }
        client._loaded = True

        results = client.search_airports(bbox=(-80.0, 39.0, -70.0, 42.0))

        assert {airport.icao_code for airport in results} == {"TEST", "KJFK"}

    def test_get_statistics_aggregates_loaded_airports(self):
        client = OpenAIPClient()
        client._cache = {
            "KJFK": Airport(
                icao_code="KJFK",
                name="JFK",
                country="US",
                elevation=10.0,
                geometry={"type": "Point", "coordinates": [-73.7789, 40.6398]},
            ),
            "KLAX": Airport(
                icao_code="KLAX",
                name="LAX",
                country="US",
                elevation=None,
                geometry=None,
            ),
            "LFPG": Airport(
                icao_code="LFPG",
                name="CDG",
                country="FR",
                elevation=119.0,
                geometry={"type": "Point", "coordinates": [2.55, 49.01]},
            ),
        }
        client._loaded = True

        stats = client.get_statistics()

        assert stats == {
            "total_airports": 3,
            "countries": 2,
            "with_elevation": 2,
            "with_coordinates": 2,
            "data_source": "local_cache",
        }


class _FakeResponse:
    def __init__(self, payload, should_raise=False):
        self._payload = payload
        self._should_raise = should_raise

    def raise_for_status(self):
        if self._should_raise:
            raise RuntimeError("request failed")

    def json(self):
        return self._payload


class _FakeAsyncClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params=None, headers=None):
        self.calls.append({"url": url, "params": params, "headers": headers})
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class TestDownloadOpenAIPData:
    @pytest.mark.asyncio
    async def test_download_requires_api_key(self, tmp_path):
        from src.clients.openaip_client import download_openaip_data

        with pytest.raises(ValueError, match="API key required"):
            await download_openaip_data(tmp_path)

    @pytest.mark.asyncio
    async def test_download_openaip_data_writes_default_country_files(self, tmp_path):
        from src.clients.openaip_client import download_openaip_data

        responses = [
            _FakeResponse({"type": "FeatureCollection", "features": [{"id": country}]})
            for country in ["US", "CA", "GB", "DE", "FR", "AU", "JP"]
        ]
        fake_client = _FakeAsyncClient(responses)

        async def fake_sleep(_seconds):
            return None

        with (
            patch("src.clients.openaip_client.httpx.AsyncClient", return_value=fake_client),
            patch("src.clients.openaip_client.asyncio.sleep", side_effect=fake_sleep) as sleep_mock,
        ):
            await download_openaip_data(tmp_path, api_key="secret")

        assert sleep_mock.await_count == 7
        assert len(fake_client.calls) == 7
        assert fake_client.calls[0]["params"] == {"country": "US"}
        assert fake_client.calls[0]["headers"] == {"x-openaip-api-key": "secret"}
        assert (tmp_path / "US_apt.geojson").exists()
        assert json.loads((tmp_path / "JP_apt.geojson").read_text())["features"][0]["id"] == "JP"

    @pytest.mark.asyncio
    async def test_download_openaip_data_continues_after_failure(self, tmp_path):
        from src.clients.openaip_client import download_openaip_data

        fake_client = _FakeAsyncClient(
            [
                _FakeResponse({"type": "FeatureCollection", "features": [{"id": "US"}]}),
                RuntimeError("network down"),
                _FakeResponse({"type": "FeatureCollection", "features": [{"id": "GB"}]}, should_raise=True),
            ]
        )

        async def fake_sleep(_seconds):
            return None

        with (
            patch("src.clients.openaip_client.httpx.AsyncClient", return_value=fake_client),
            patch("src.clients.openaip_client.asyncio.sleep", side_effect=fake_sleep),
        ):
            await download_openaip_data(tmp_path, countries=["US", "CA", "GB"], api_key="secret")

        assert (tmp_path / "US_apt.geojson").exists()
        assert not (tmp_path / "CA_apt.geojson").exists()
        assert not (tmp_path / "GB_apt.geojson").exists()
