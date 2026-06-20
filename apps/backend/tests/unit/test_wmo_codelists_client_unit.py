"""Unit tests for WMOCodelistCache – 0% coverage target."""
import builtins
import importlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.clients import wmo_codelists_client as wmo_module
from src.clients.wmo_codelists_client import (
    WMOCodelistCache,
    WMOCodelistInfo,
    WMOCodelistsClient,
)


class TestWMOCodelistCacheInit:
    def test_creates_cache_dir(self, tmp_path):
        cache_dir = tmp_path / "nested" / "cache"
        assert not cache_dir.exists()
        cache = WMOCodelistCache(cache_dir=cache_dir)
        assert cache_dir.exists()

    def test_default_ttl(self, tmp_path):
        cache = WMOCodelistCache(cache_dir=tmp_path)
        assert cache.ttl == timedelta(seconds=604800)

    def test_custom_ttl(self, tmp_path):
        cache = WMOCodelistCache(cache_dir=tmp_path, ttl_seconds=3600)
        assert cache.ttl == timedelta(seconds=3600)

    def test_loads_existing_metadata(self, tmp_path):
        metadata = {"my_list": {"cached_at": datetime.now().isoformat()}}
        (tmp_path / "cache_metadata.json").write_text(json.dumps(metadata))
        cache = WMOCodelistCache(cache_dir=tmp_path)
        assert "my_list" in cache._metadata

    def test_ignores_bad_metadata(self, tmp_path):
        (tmp_path / "cache_metadata.json").write_text("{{NOT JSON")
        cache = WMOCodelistCache(cache_dir=tmp_path)  # should not raise
        assert cache._metadata == {}


class TestWMOCodelistCacheGet:
    def _write_entry(self, tmp_path, name, values, cached_at=None):
        if cached_at is None:
            cached_at = datetime.now().isoformat()
        metadata = {name: {"cached_at": cached_at}}
        (tmp_path / "cache_metadata.json").write_text(json.dumps(metadata))
        (tmp_path / f"{name}.json").write_text(json.dumps({"values": list(values)}))

    def test_get_fresh_entry(self, tmp_path):
        self._write_entry(tmp_path, "test_list", {"A", "B"})
        cache = WMOCodelistCache(cache_dir=tmp_path)
        result = cache.get("test_list")
        assert result == {"A", "B"}

    def test_get_expired_entry_returns_none(self, tmp_path):
        old_time = (datetime.now() - timedelta(days=10)).isoformat()
        self._write_entry(tmp_path, "old_list", {"X"}, cached_at=old_time)
        cache = WMOCodelistCache(cache_dir=tmp_path)
        assert cache.get("old_list") is None

    def test_get_missing_metadata_returns_none(self, tmp_path):
        cache = WMOCodelistCache(cache_dir=tmp_path)
        assert cache.get("nonexistent") is None

    def test_get_missing_file_returns_none(self, tmp_path):
        # Metadata present but no value file
        metadata = {"orphan": {"cached_at": datetime.now().isoformat()}}
        (tmp_path / "cache_metadata.json").write_text(json.dumps(metadata))
        cache = WMOCodelistCache(cache_dir=tmp_path)
        assert cache.get("orphan") is None

    def test_get_bad_value_file_returns_none(self, tmp_path):
        metadata = {"broken": {"cached_at": datetime.now().isoformat()}}
        (tmp_path / "cache_metadata.json").write_text(json.dumps(metadata))
        (tmp_path / "broken.json").write_text("{{BAD JSON")
        cache = WMOCodelistCache(cache_dir=tmp_path)
        assert cache.get("broken") is None


class TestWMOCodelistCacheSet:
    def test_set_creates_file_and_metadata(self, tmp_path):
        cache = WMOCodelistCache(cache_dir=tmp_path)
        cache.set("my_list", {"V1", "V2"})

        assert (tmp_path / "my_list.json").exists()
        assert "my_list" in cache._metadata

    def test_set_then_get_roundtrip(self, tmp_path):
        cache = WMOCodelistCache(cache_dir=tmp_path)
        cache.set("roundtrip", {"X", "Y", "Z"})
        result = cache.get("roundtrip")
        assert result == {"X", "Y", "Z"}

    def test_set_overwrites_expired(self, tmp_path):
        old_time = (datetime.now() - timedelta(days=10)).isoformat()
        meta = {"stale": {"cached_at": old_time}}
        (tmp_path / "cache_metadata.json").write_text(json.dumps(meta))
        cache = WMOCodelistCache(cache_dir=tmp_path)
        # Expired returns None
        assert cache.get("stale") is None
        # After set, returns fresh value
        cache.set("stale", {"NEW"})
        assert cache.get("stale") == {"NEW"}


class TestWMOCodelistInfo:
    def test_default_values(self):
        info = WMOCodelistInfo(name="test", url="http://example.com")
        assert info.values == set()
        assert info.source == "local"
        assert info.version is None
        assert info.last_updated is None


class TestWMOCodelistsClientInit:
    """Test WMOCodelistsClient initialization."""

    def test_init_creates_parser_and_cache(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=False,
        )

        assert client.enable_online is False
        assert client.registry_url == "https://codes.wmo.int"
        assert client.parser is not None
        assert client.cache is not None

    def test_init_with_custom_registry_url(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=True,
            registry_url="http://custom.example.com",
        )

        assert client.enable_online is True
        assert client.registry_url == "http://custom.example.com"

    def test_init_creates_cache_dir_if_missing(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        # cache_dir does NOT exist yet

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        assert cache_dir.exists()


class TestWMOCodelistsClientValidateMethods:
    """Test validate_* methods."""

    def test_validate_weather_phenomenon_delegates_to_validate_code(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        with patch.object(client, "_validate_code", return_value=True) as mock_validate:
            result = client.validate_weather_phenomenon("NSW")
            assert result is True
            mock_validate.assert_called_once_with("AerodromePresentOrForecastWeather", "NSW")

    def test_validate_weather_phenomenon_custom_codelist(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        with patch.object(client, "_validate_code", return_value=False) as mock_validate:
            result = client.validate_weather_phenomenon("X", codelist="CustomWeather")
            assert result is False
            mock_validate.assert_called_once_with("CustomWeather", "X")

    def test_validate_cloud_type(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        with patch.object(client, "_validate_code", return_value=True) as mock_validate:
            result = client.validate_cloud_type("CB")
            assert result is True
            mock_validate.assert_called_once_with("CloudType", "CB")

    def test_validate_cloud_amount(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        with patch.object(client, "_validate_code", return_value=True) as mock_validate:
            result = client.validate_cloud_amount("OVC")
            assert result is True
            mock_validate.assert_called_once_with("CloudAmount", "OVC")

    def test_validate_visibility_type(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        with patch.object(client, "_validate_code", return_value=True) as mock_validate:
            result = client.validate_visibility_type("FORECAST")
            assert result is True
            mock_validate.assert_called_once_with("MeasurementOrFactType", "FORECAST")


class TestWMOCodelistsClientValidateCode:
    """Test _validate_code with fallback paths."""

    def test_validate_code_parser_success(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        client.parser = MagicMock()
        client.parser.validate_code.return_value = True

        result = client._validate_code("TestList", "CODE1")
        assert result is True
        client.parser.validate_code.assert_called_once_with("TestList", "CODE1")

    def test_validate_code_cache_fallback(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Set up cache with values
        cache_metadata = {"TestList": {"cached_at": datetime.now().isoformat()}}
        (cache_dir / "cache_metadata.json").write_text(json.dumps(cache_metadata))
        (cache_dir / "TestList.json").write_text(
            json.dumps({"values": ["CODE2", "CODE3"]})
        )

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        # Parser returns False, but cache has the code
        client.parser = MagicMock()
        client.parser.validate_code.return_value = False

        result = client._validate_code("TestList", "CODE2")
        assert result is True

    def test_validate_code_cache_miss(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        # Parser and cache both fail, online disabled
        client.parser = MagicMock()
        client.parser.validate_code.return_value = False
        client.enable_online = False

        result = client._validate_code("UnknownList", "CODE")
        assert result is False

    def test_validate_code_online_fallback(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=True,
        )

        client.parser = MagicMock()
        client.parser.validate_code.return_value = False

        # Mock _fetch_codelist_online to return codes
        with patch.object(
            client, "_fetch_codelist_online", return_value={"CODE4", "CODE5"}
        ):
            result = client._validate_code("RemoteList", "CODE4")
            assert result is True
            # Should cache the values
            assert client.cache.get("RemoteList") == {"CODE4", "CODE5"}

    def test_validate_code_online_returns_none(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=True,
        )

        client.parser = MagicMock()
        client.parser.validate_code.return_value = False

        # Mock _fetch_codelist_online to return None
        with patch.object(client, "_fetch_codelist_online", return_value=None):
            result = client._validate_code("BadRemoteList", "CODE")
            assert result is False


class TestWMOCodelistsClientOnline:
    """Test _fetch_codelist_online with XML parsing."""

    def test_fetch_codelist_online_success(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=True,
        )

        # Mock XML response
        rdf_xml = """<?xml version="1.0"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:skos="http://www.w3.org/2004/02/skos/core#">
            <skos:Concept rdf:about="http://example.com/list/CODE1"/>
            <skos:Concept rdf:about="http://example.com/list/CODE2"/>
        </rdf:RDF>
        """

        with patch("src.clients.wmo_codelists_client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = rdf_xml.encode()
            mock_requests.get.return_value = mock_response

            result = client._fetch_codelist_online("TestList")
            assert result == {"CODE1", "CODE2"}

    def test_fetch_codelist_online_no_requests(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=True,
        )

        # Simulate requests unavailable
        with patch("src.clients.wmo_codelists_client.REQUESTS_AVAILABLE", False):
            result = client._fetch_codelist_online("TestList")
            assert result is None

    def test_fetch_codelist_online_http_error(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=True,
        )

        with patch("src.clients.wmo_codelists_client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_requests.get.return_value = mock_response

            result = client._fetch_codelist_online("NotFound")
            assert result is None

    def test_fetch_codelist_online_request_timeout(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=True,
        )

        with patch("src.clients.wmo_codelists_client.requests") as mock_requests:
            mock_requests.get.side_effect = TimeoutError("timeout")

            result = client._fetch_codelist_online("SlowList")
            assert result is None

    def test_fetch_codelist_online_malformed_xml(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=True,
        )

        with patch("src.clients.wmo_codelists_client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"<invalid xml"
            mock_requests.get.return_value = mock_response

            result = client._fetch_codelist_online("BadXML")
            assert result is None


class TestWMOCodelistsClientGetCodelistInfo:
    """Test get_codelist_info with fallback paths."""

    def test_get_codelist_info_from_local_parser(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        client.parser = MagicMock()
        client.parser.get_codes.return_value = {"L1", "L2"}

        info = client.get_codelist_info("LocalList")
        assert info.name == "LocalList"
        assert info.values == {"L1", "L2"}
        assert info.source == "local"

    def test_get_codelist_info_from_cache(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Set up cache
        cache_metadata = {"CachedList": {"cached_at": datetime.now().isoformat()}}
        (cache_dir / "cache_metadata.json").write_text(json.dumps(cache_metadata))
        (cache_dir / "CachedList.json").write_text(
            json.dumps({"values": ["C1", "C2"]})
        )

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        client.parser = MagicMock()
        client.parser.get_codes.return_value = None

        info = client.get_codelist_info("CachedList")
        assert info.name == "CachedList"
        assert info.values == {"C1", "C2"}
        assert info.source == "cache"

    def test_get_codelist_info_from_online(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=True,
        )

        client.parser = MagicMock()
        client.parser.get_codes.return_value = None

        with patch.object(
            client, "_fetch_codelist_online", return_value={"O1", "O2"}
        ):
            info = client.get_codelist_info("OnlineList")
            assert info.name == "OnlineList"
            assert info.values == {"O1", "O2"}
            assert info.source == "online"
            assert info.last_updated is not None

    def test_get_codelist_info_not_found(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        client.parser = MagicMock()
        client.parser.get_codes.return_value = None

        info = client.get_codelist_info("NotFound")
        assert info.name == "NotFound"
        assert info.source == "unknown"
        assert info.values == set()


class TestWMOCodelistsClientListAndStatistics:
    """Test list_available_codelists and get_statistics."""

    def test_list_available_codelists(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Set up cache with one list
        cache_metadata = {"CachedList": {"cached_at": datetime.now().isoformat()}}
        (cache_dir / "cache_metadata.json").write_text(json.dumps(cache_metadata))

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        client.parser = MagicMock()
        client.parser.list_codelists.return_value = ["LocalList1", "LocalList2"]

        result = client.list_available_codelists()
        assert "LocalList1" in result
        assert "LocalList2" in result
        assert "CachedList" in result
        assert len(result) == 3

    def test_list_available_codelists_empty_cache(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
        )

        client.parser = MagicMock()
        client.parser.list_codelists.return_value = ["OnlyLocal"]

        result = client.list_available_codelists()
        assert result == ["OnlyLocal"]

    def test_get_statistics(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Set up cache with one list
        cache_metadata = {"CachedList": {"cached_at": datetime.now().isoformat()}}
        (cache_dir / "cache_metadata.json").write_text(json.dumps(cache_metadata))

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=True,
            registry_url="http://test.example.com",
        )

        client.parser = MagicMock()
        client.parser.list_codelists.return_value = ["L1", "L2", "L3"]

        stats = client.get_statistics()
        assert stats["local_codelists"] == 3
        assert stats["cached_codelists"] == 1
        assert stats["total_unique"] == 4
        assert stats["online_enabled"] is True
        assert stats["registry_url"] == "http://test.example.com"

    def test_get_statistics_empty(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()

        # Mock CodeListParser to avoid validation settings initialization
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=False,
        )

        client.parser = MagicMock()
        client.parser.list_codelists.return_value = []

        stats = client.get_statistics()
        assert stats["local_codelists"] == 0
        assert stats["cached_codelists"] == 0
        assert stats["total_unique"] == 0
        assert stats["online_enabled"] is False


class TestWMOCodelistCacheEdgeBranches:
    def test_save_metadata_write_failure_is_swallowed(self, tmp_path, monkeypatch):
        cache = WMOCodelistCache(cache_dir=tmp_path)

        def _fail_open(*_args, **_kwargs):
            raise OSError("no write")

        monkeypatch.setattr("builtins.open", _fail_open)

        # Should not raise when metadata write fails.
        cache._save_metadata()

    def test_set_write_failure_is_swallowed(self, tmp_path, monkeypatch):
        cache = WMOCodelistCache(cache_dir=tmp_path)

        def _fail_open(*_args, **_kwargs):
            raise OSError("no write")

        monkeypatch.setattr("builtins.open", _fail_open)

        # Should not raise when cache file write fails.
        cache.set("broken", {"A"})

    def test_clear_expired_removes_only_expired_and_updates_metadata(self, tmp_path):
        cache = WMOCodelistCache(cache_dir=tmp_path, ttl_seconds=60)
        now = datetime.now()
        old = (now - timedelta(hours=2)).isoformat()
        fresh = now.isoformat()
        cache._metadata = {
            "old_list": {"cached_at": old},
            "fresh_list": {"cached_at": fresh},
        }

        (tmp_path / "old_list.json").write_text(json.dumps({"values": ["A"]}), encoding="utf-8")
        (tmp_path / "fresh_list.json").write_text(json.dumps({"values": ["B"]}), encoding="utf-8")

        removed = cache.clear_expired()

        assert removed == 1
        assert "old_list" not in cache._metadata
        assert "fresh_list" in cache._metadata
        assert not (tmp_path / "old_list.json").exists()
        assert (tmp_path / "fresh_list.json").exists()

    def test_clear_expired_without_expired_entries_does_nothing(self, tmp_path):
        cache = WMOCodelistCache(cache_dir=tmp_path, ttl_seconds=60)
        cache._metadata = {
            "fresh_only": {"cached_at": datetime.now().isoformat()},
        }
        (tmp_path / "fresh_only.json").write_text(json.dumps({"values": ["X"]}), encoding="utf-8")

        removed = cache.clear_expired()

        assert removed == 0
        assert "fresh_only" in cache._metadata
        assert (tmp_path / "fresh_only.json").exists()


class TestWMOCodelistsClientAdditionalBranches:
    def test_init_uses_default_cache_dir_when_none_provided(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        codelists_dir.mkdir()
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(codelists_dir=codelists_dir, cache_dir=None)

        assert client.cache.cache_dir == codelists_dir / "cache"
        assert (codelists_dir / "cache").exists()

    def test_fetch_online_skips_concepts_without_about_attribute(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(codelists_dir=codelists_dir, cache_dir=cache_dir, enable_online=True)

        rdf_xml = """<?xml version=\"1.0\"?>
        <rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"
                 xmlns:skos=\"http://www.w3.org/2004/02/skos/core#\">
            <skos:Concept />
            <skos:Concept rdf:about=\"http://example.com/list/CODE1\"/>
        </rdf:RDF>
        """

        with patch("src.clients.wmo_codelists_client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = rdf_xml.encode()
            mock_requests.get.return_value = mock_response

            result = client._fetch_codelist_online("TestList")

        assert result == {"CODE1"}

    def test_fetch_online_200_with_no_codes_returns_none(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(codelists_dir=codelists_dir, cache_dir=cache_dir, enable_online=True)

        rdf_xml = """<?xml version=\"1.0\"?>
        <rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"
                 xmlns:skos=\"http://www.w3.org/2004/02/skos/core#\">
        </rdf:RDF>
        """

        with patch("src.clients.wmo_codelists_client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = rdf_xml.encode()
            mock_requests.get.return_value = mock_response

            assert client._fetch_codelist_online("EmptyList") is None

    def test_get_codelist_info_returns_unknown_when_online_disabled(self, tmp_path, monkeypatch):
        codelists_dir = Path(tmp_path) / "codelists"
        cache_dir = Path(tmp_path) / "cache"
        codelists_dir.mkdir()
        cache_dir.mkdir()
        mock_parser = MagicMock()
        monkeypatch.setattr("src.clients.wmo_codelists_client.CodeListParser", lambda x: mock_parser)

        client = WMOCodelistsClient(
            codelists_dir=codelists_dir,
            cache_dir=cache_dir,
            enable_online=False,
        )
        client.parser = MagicMock()
        client.parser.get_codes.return_value = None

        info = client.get_codelist_info("UnknownList")

        assert info.source == "unknown"
        assert info.values == set()


class TestWMOCodelistsModuleImportFallback:
    def test_module_reload_without_requests_sets_flag_false(self, monkeypatch):
        original_import = builtins.__import__

        def _import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "requests":
                raise ImportError("requests unavailable")
            return original_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", _import)
        reloaded = importlib.reload(wmo_module)

        try:
            assert reloaded.REQUESTS_AVAILABLE is False
        finally:
            monkeypatch.setattr(builtins, "__import__", original_import)
            importlib.reload(wmo_module)
