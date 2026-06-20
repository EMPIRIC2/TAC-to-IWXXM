"""Unit tests for OpenAIPService – 0% coverage target."""

import builtins
import json
from datetime import datetime, timedelta

import pytest

from src.services.openaip_service import OpenAIPService


def _make_cache_file(tmp_path, airports: dict, fetched_at=None):
    """Write a fake openaip_cache.json to tmp_path."""
    if fetched_at is None:
        fetched_at = datetime.utcnow().isoformat()
    data = {
        "_metadata": {"fetched_at": fetched_at},
        "airports": airports,
    }
    cache_file = tmp_path / "openaip_cache.json"
    cache_file.write_text(json.dumps(data))
    return cache_file


class TestOpenAIPServiceInit:
    def test_loads_cache_from_file(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK"}})
        svc = OpenAIPService(cache_file=cache_file)
        assert "KJFK" in svc._cache

    def test_missing_cache_file_yields_empty_cache(self, tmp_path):
        svc = OpenAIPService(cache_file=tmp_path / "nonexistent.json")
        assert svc._cache is None or svc._cache == {}

    def test_bad_json_cache_file_handled(self, tmp_path):
        cache_file = tmp_path / "bad.json"
        cache_file.write_text("{{NOT JSON")
        svc = OpenAIPService(cache_file=cache_file)
        assert svc._cache == {} or svc._cache is None

    def test_default_cache_path_used_when_none(self):
        # Just confirm no exception when constructing (even if cache doesn't exist)
        svc = OpenAIPService()
        assert svc.cache_file is not None


class TestOpenAIPServiceGetAirport:
    def test_get_existing_airport_from_file_cache(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK", "country": "US"}})
        svc = OpenAIPService(cache_file=cache_file)
        result = svc.get_airport("KJFK")
        assert result is not None
        assert result["name"] == "JFK"

    def test_get_airport_case_insensitive(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK"}})
        svc = OpenAIPService(cache_file=cache_file)
        assert svc.get_airport("kjfk") is not None

    def test_get_missing_airport_returns_none_without_api_key(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {})
        svc = OpenAIPService(cache_file=cache_file)
        result = svc.get_airport("XXXX")
        assert result is None

    def test_get_airport_uses_live_cache_if_set(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {})
        svc = OpenAIPService(cache_file=cache_file)
        from datetime import datetime

        svc._live_cache["EGLL"] = {
            "data": {"name": "Heathrow"},
            "_cached_at": datetime.utcnow().isoformat(),
        }
        result = svc.get_airport("EGLL")
        assert result is not None

    def test_live_cache_without_timestamp_falls_through_to_api(self, tmp_path, monkeypatch):
        cache_file = _make_cache_file(tmp_path, {})
        svc = OpenAIPService(cache_file=cache_file, api_key="token")
        svc._live_cache["EGLL"] = {
            "data": {"name": "stale-without-ts"},
        }

        monkeypatch.setattr(svc, "_fetch_from_api", lambda _icao: {"name": "fresh-api"})

        result = svc.get_airport("EGLL")

        assert result == {"name": "fresh-api"}

    def test_handles_flat_airports_format(self, tmp_path):
        """Cache file without _metadata wrapping (flat dict of airports)."""
        cache_file = tmp_path / "flat_cache.json"
        cache_file.write_text(json.dumps({"EDDF": {"name": "Frankfurt"}}))
        svc = OpenAIPService(cache_file=cache_file)
        result = svc.get_airport("EDDF")
        assert result is not None


class TestOpenAIPServiceCacheStale:
    def test_cache_considered_fresh_by_default(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK"}})
        svc = OpenAIPService(cache_file=cache_file)
        # Service should have loaded the cache
        assert svc._cache_timestamp is not None

    def test_old_cache_does_not_crash(self, tmp_path):
        old_time = (datetime.utcnow() - timedelta(days=365)).isoformat()
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK"}}, fetched_at=old_time)
        svc = OpenAIPService(cache_file=cache_file)
        # Should still return data from old cache
        assert svc.get_airport("KJFK") is not None


class TestOpenAIPServiceLiveAPI:
    def test_fetch_from_api_success_via_get_airport(self, tmp_path, monkeypatch):
        cache_file = _make_cache_file(tmp_path, {})
        svc = OpenAIPService(cache_file=cache_file, api_key="token")

        class _Resp:
            status_code = 200

            @staticmethod
            def json():
                return {"items": [{"icaoCode": "KJFK", "name": "John F Kennedy"}]}

        class _Requests:
            @staticmethod
            def get(url, headers, params, timeout):
                assert "api.openaip.net" in url
                assert headers["Authorization"] == "Bearer token"
                assert params["icaoCode"] == "KJFK"
                assert timeout == 5
                return _Resp()

        monkeypatch.setitem(__import__("sys").modules, "requests", _Requests)

        result = svc.get_airport("KJFK")
        assert result is not None
        assert result["icaoCode"] == "KJFK"
        assert "KJFK" in svc._live_cache

    def test_fetch_from_api_non_200_returns_none(self, tmp_path, monkeypatch):
        cache_file = _make_cache_file(tmp_path, {})
        svc = OpenAIPService(cache_file=cache_file, api_key="token")

        class _Resp:
            status_code = 404

            @staticmethod
            def json():
                return {}

        class _Requests:
            @staticmethod
            def get(url, headers, params, timeout):
                return _Resp()

        monkeypatch.setitem(__import__("sys").modules, "requests", _Requests)

        assert svc.get_airport("XXXX") is None

    def test_fetch_from_api_empty_items_returns_none(self, tmp_path, monkeypatch):
        cache_file = _make_cache_file(tmp_path, {})
        svc = OpenAIPService(cache_file=cache_file, api_key="token")

        class _Resp:
            status_code = 200

            @staticmethod
            def json():
                return {"items": []}

        class _Requests:
            @staticmethod
            def get(url, headers, params, timeout):
                return _Resp()

        monkeypatch.setitem(__import__("sys").modules, "requests", _Requests)

        assert svc.get_airport("XXXX") is None

    def test_fetch_from_api_exception_returns_none(self, tmp_path, monkeypatch):
        cache_file = _make_cache_file(tmp_path, {})
        svc = OpenAIPService(cache_file=cache_file, api_key="token")

        class _Requests:
            @staticmethod
            def get(url, headers, params, timeout):
                raise RuntimeError("network")

        monkeypatch.setitem(__import__("sys").modules, "requests", _Requests)

        assert svc.get_airport("XXXX") is None

    def test_fetch_from_api_import_error_returns_none(self, tmp_path, monkeypatch):
        cache_file = _make_cache_file(tmp_path, {})
        svc = OpenAIPService(cache_file=cache_file, api_key="token")

        real_import = builtins.__import__

        def _fake_import(name, *args, **kwargs):
            if name == "requests":
                raise ImportError("requests missing")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fake_import)

        assert svc._fetch_from_api("KJFK") is None


class TestOpenAIPServiceHelpers:
    def test_validate_airport_true_and_false(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK"}})
        svc = OpenAIPService(cache_file=cache_file)
        assert svc.validate_airport("KJFK") is True
        assert svc.validate_airport("XXXX") is False

    def test_get_all_airports_returns_cache_dict(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK"}, "KLAX": {"name": "LAX"}})
        svc = OpenAIPService(cache_file=cache_file)
        airports = svc.get_all_airports()
        assert set(airports.keys()) == {"KJFK", "KLAX"}

    def test_cache_freshness_none_when_timestamp_missing(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK"}})
        svc = OpenAIPService(cache_file=cache_file)
        svc._cache_timestamp = None
        assert svc.cache_freshness() is None

    def test_is_cache_stale_true_when_timestamp_missing(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK"}})
        svc = OpenAIPService(cache_file=cache_file)
        svc._cache_timestamp = None
        assert svc.is_cache_stale() is True

    def test_suggest_refresh_message_when_stale(self, tmp_path):
        old_time = (datetime.utcnow() - timedelta(days=30)).isoformat()
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK"}}, fetched_at=old_time)
        svc = OpenAIPService(cache_file=cache_file)
        message = svc.suggest_refresh()
        assert "Refresh with" in message

    def test_suggest_refresh_empty_when_fresh(self, tmp_path):
        cache_file = _make_cache_file(tmp_path, {"KJFK": {"name": "JFK"}})
        svc = OpenAIPService(cache_file=cache_file)
        assert svc.suggest_refresh() == ""

    def test_expired_live_cache_falls_through_to_api(self, tmp_path, monkeypatch):
        cache_file = _make_cache_file(tmp_path, {})
        svc = OpenAIPService(cache_file=cache_file, api_key="token")

        svc._live_cache["EGLL"] = {
            "data": {"name": "old"},
            "_cached_at": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
        }

        monkeypatch.setattr(svc, "_fetch_from_api", lambda _icao: {"name": "new"})
        result = svc.get_airport("EGLL")

        assert result == {"name": "new"}
