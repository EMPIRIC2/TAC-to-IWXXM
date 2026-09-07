"""TC-F21 amended by F31 - Auth restored; convert stays public; sessions JWT-gated."""

from __future__ import annotations

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient


def _iter_route_paths(routes, prefix: str = "") -> list[str]:
    paths: list[str] = []
    for route in routes:
        if isinstance(route, APIRoute):
            paths.append(f"{prefix}{route.path}" if route.path is not None else prefix)
        elif type(route).__name__ == "_IncludedRouter":
            ctx = getattr(route, "include_context", None)
            nested_prefix = prefix + (getattr(ctx, "prefix", "") or "")
            paths.extend(_iter_route_paths(route.original_router.routes, nested_prefix))
        elif hasattr(route, "routes") and route.routes:
            mount_path = getattr(route, "path", "") or ""
            paths.extend(_iter_route_paths(route.routes, f"{prefix}{mount_path}"))
    return paths


@pytest.mark.unit
def test_auth_routes_present_without_admin() -> None:
    from src.api import app

    paths = set(_iter_route_paths(app.routes))
    assert "/auth/login" in paths
    assert "/auth/me" in paths
    assert not any("/admin" in p for p in paths)


@pytest.mark.unit
def test_work_sessions_routes_present() -> None:
    """F31 / M2 - work-sessions mounted under /api/v1 (JWT-gated)."""
    from src.api import app

    paths = set(_iter_route_paths(app.routes))
    assert any("/work-sessions" in p for p in paths)


@pytest.mark.unit
def test_auth_login_not_route_missing() -> None:
    from src.api import app

    client = TestClient(app)
    response = client.post(
        "/auth/login",
        json={"email": "a@b.co", "password": "x"},
    )
    assert response.status_code != 404


@pytest.mark.unit
def test_work_sessions_list_requires_jwt() -> None:
    """TC-F31-003 - session list is 401/403 without Bearer (not a silent public 200)."""
    from src.api import app

    client = TestClient(app)
    response = client.get("/api/v1/work-sessions")
    assert response.status_code in (401, 403)


@pytest.mark.unit
def test_convert_succeeds_without_authorization() -> None:
    """Public convert must not require Authorization (F21 Amended / F31)."""
    from src import api as api_module

    api_module.app.dependency_overrides.clear()

    client = TestClient(api_module.app)
    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 121851Z 09014KT 10SM FEW250 22/14 A3015=",
            "product": "METAR",
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "validate_output": "false",
        },
    )
    assert response.status_code != 401
    assert response.status_code != 403
    assert response.status_code == 200, response.text


@pytest.mark.unit
def test_lint_and_validate_succeed_without_authorization() -> None:
    """TC-EV031-003 deepen - lint-tac / validate stay JWT-free (F21 Amended)."""
    from src import api as api_module

    api_module.app.dependency_overrides.clear()
    client = TestClient(api_module.app)
    metar = "METAR KJFK 121851Z 09014KT 10SM FEW250 22/14 A3015="

    lint = client.post(
        "/api/v1/lint-tac",
        files={
            "manual_text": (None, metar),
            "product": (None, "METAR"),
        },
    )
    assert lint.status_code not in {401, 403}
    assert lint.status_code == 200, lint.text

    validate = client.post(
        "/api/v1/validate",
        files={
            "iwxxm_xml": (
                None,
                (
                    '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0" '
                    'xmlns:gml="http://www.opengis.net/gml/3.2" gml:id="x"/>'
                ),
            ),
            "version": (None, "2025-2"),
        },
    )
    assert validate.status_code not in {401, 403}
