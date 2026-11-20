"""Router HTTP tests for live-check (validation and mapped errors).

[Corpus: product §F6] [Corpus: tests §TC-LIVE-FEEDS] [Corpus: api]
"""

from __future__ import annotations

from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from live_check_test_support import (
    ALLOW as _ALLOW,
)
from live_check_test_support import (
    TAC as _TAC,
)
from live_check_test_support import (
    XML as _XML,
)
from live_check_test_support import (
    FakeResponse as _FakeResponse,
)
from live_check_test_support import (
    ok_convert as _ok_convert,
)
from src.routers import live_check as live_check_router
from src.services.live_check import LiveCheckService, set_live_check_service


def _clear_service() -> None:
    set_live_check_service(None)


def setup_function() -> None:
    _clear_service()


def teardown_function() -> None:
    _clear_service()


def test_router_success_and_failure() -> None:
    def http_get(url: str, *, params=None, headers=None):
        return _FakeResponse(_TAC)

    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.8.8", 0))],
    ):
        svc = LiveCheckService(
            http_get=http_get,  # type: ignore[arg-type]
            convert_fn=_ok_convert,
            allowlist=_ALLOW,
        )
        set_live_check_service(svc)
        app = FastAPI()
        app.include_router(live_check_router.router)
        client = TestClient(app)

        ok = client.get("/api/v1/live-check", params={"icao": "KJFK", "provider": "noaa"})
        assert ok.status_code == 200
        body = ok.json()
        assert body["icao"] == "KJFK"
        assert body["profile"] == "iwxxm_us"
        assert body["source_tac"] == _TAC
        assert body["our_iwxxm"] == _XML

        bad = client.get(
            "/api/v1/live-check",
            params={"icao": "KJFK", "provider": "sadis"},
        )
        assert bad.status_code == 400
        assert "allowlisted" in bad.json()["detail"]


def test_router_query_validation_and_mapped_errors() -> None:
    def http_get(url: str, *, params=None, headers=None):
        return _FakeResponse("EGLL 231751Z 18012KT=")

    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.8.8", 0))],
    ):
        svc = LiveCheckService(
            http_get=http_get,  # type: ignore[arg-type]
            convert_fn=_ok_convert,
            allowlist=_ALLOW,
            knmi_api_key="",
        )
        set_live_check_service(svc)
        app = FastAPI()
        app.include_router(live_check_router.router)
        client = TestClient(app)

        too_short = client.get("/api/v1/live-check", params={"icao": "JFK"})
        assert too_short.status_code == 422

        too_long = client.get("/api/v1/live-check", params={"icao": "KJFKX"})
        assert too_long.status_code == 422

        bad_product = client.get(
            "/api/v1/live-check",
            params={"icao": "KJFK", "product": "SIGMET", "provider": "noaa"},
        )
        assert bad_product.status_code == 400
        assert "METAR or TAF" in bad_product.json()["detail"]

        knmi_taf = client.get(
            "/api/v1/live-check",
            params={"icao": "EHRD", "product": "TAF", "provider": "knmi"},
        )
        assert knmi_taf.status_code == 400
        assert "METAR only" in knmi_taf.json()["detail"]

        missing = client.get(
            "/api/v1/live-check",
            params={"icao": "KJFK", "provider": "noaa"},
        )
        assert missing.status_code == 404
        assert "noaa returned no" in missing.json()["detail"]

        knmi = client.get(
            "/api/v1/live-check",
            params={"icao": "EHRD", "provider": "knmi"},
        )
        assert knmi.status_code == 503
        assert "not configured" in knmi.json()["detail"]
