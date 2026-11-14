"""Success / failure / validation coverage for dissemination router helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from src.routers import dissemination_router_helpers as helpers


def test_client_id_success_with_host() -> None:
    req = SimpleNamespace(client=SimpleNamespace(host="10.0.0.1"), headers={})
    assert helpers.client_id(req) == "10.0.0.1"


def test_client_id_validation_anonymous() -> None:
    req = SimpleNamespace(client=None, headers={})
    assert helpers.client_id(req) == "anonymous"


def test_profiles_service_for_optional_auth_none() -> None:
    assert helpers.profiles_service_for_optional_auth(None) is None


def test_profiles_service_for_optional_auth_success() -> None:
    svc = helpers.profiles_service_for_optional_auth({"sub": "11111111-1111-1111-1111-111111111111"})
    assert svc is not None


def test_merge_template_params_success() -> None:
    merged = helpers.merge_template_params({"a": 1, "b": 2}, {"b": 9, "c": 3})
    assert merged == {"a": 1, "b": 9, "c": 3}


def test_require_sink_validation_missing() -> None:
    with pytest.raises(HTTPException) as exc:
        helpers.require_sink(None)
    assert exc.value.status_code == 422


def test_require_sink_failure_unknown() -> None:
    with pytest.raises(HTTPException) as exc:
        helpers.require_sink("ftp")
    assert exc.value.status_code == 400


def test_require_sink_success() -> None:
    assert helpers.require_sink("wis2") == "wis2"
    assert helpers.require_sink("postgres") == "postgres"


@pytest.mark.asyncio
async def test_read_preflight_failure_bad_json() -> None:
    from starlette.requests import Request

    scope = {"type": "http", "method": "POST", "path": "/", "headers": [], "client": ("1.1.1.1", 1)}
    req = Request(scope)
    req._body = b"{not-json"
    with pytest.raises(HTTPException) as exc:
        await helpers.read_preflight(req)
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_read_preflight_success() -> None:
    from starlette.requests import Request

    scope = {"type": "http", "method": "POST", "path": "/", "headers": [], "client": ("1.1.1.1", 1)}
    req = Request(scope)
    req._body = b'{"sink_type":"wis2"}'
    parsed = await helpers.read_preflight(req)
    assert parsed.sink_type == "wis2"
