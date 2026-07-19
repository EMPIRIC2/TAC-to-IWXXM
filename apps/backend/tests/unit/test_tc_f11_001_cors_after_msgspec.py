"""T5.6 / TC-F11-001: H0c CORS re-check after msgspec high-churn HTTP (ADR-026).

Msgspec response encode must not introduce new CORS knobs; high-churn POST routes
still answer browser OPTIONS preflight under existing ``METAR_CORS_ORIGINS`` /
``config.*.api.corsOrigins``.
"""

from __future__ import annotations

import inspect

import pytest
from fastapi.testclient import TestClient
from metar_shared import METAR_CORS_ORIGINS_ENV

from src import api as api_module

HIGH_CHURN_PATHS = (
    "/api/v1/convert",
    "/api/v1/convert-zip",
    "/api/v1/convert-bulletin",
    "/api/v1/validate",
    "/api/v1/lint-tac",
    "/api/v1/decode-tac",
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(api_module.app)


@pytest.fixture
def allowed_origin() -> str:
    origins = list(api_module.allowed_origins)
    assert origins, "backend must configure at least one CORS origin"
    return origins[0]


@pytest.mark.parametrize("path", HIGH_CHURN_PATHS)
def test_high_churn_options_preflight_allows_post(client: TestClient, allowed_origin: str, path: str) -> None:
    """Browser preflight for msgspec high-churn routes remains POST-capable."""
    response = client.options(
        path,
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code in {200, 204}, response.text[:300]
    allow_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allow_methods.upper() or allow_methods == "*"
    assert response.headers.get("access-control-allow-origin") == allowed_origin


def test_msgspec_http_introduces_no_new_cors_env_knobs() -> None:
    """ADR-026 / T5.6: msgspec encode path must not add CORS-specific env vars."""
    import msgspec_http

    helper_src = inspect.getsource(msgspec_http)
    assert "METAR_CORS" not in helper_src
    assert "CORS" not in helper_src.upper()
    assert METAR_CORS_ORIGINS_ENV == "METAR_CORS_ORIGINS"


def test_cors_origins_still_driven_by_existing_knobs() -> None:
    """get_cors_origins remains the single origin resolver (no msgspec-specific branch)."""
    src = inspect.getsource(api_module.get_cors_origins)
    assert "msgspec" not in src.lower()
    assert METAR_CORS_ORIGINS_ENV in src or "METAR_CORS_ORIGINS" in src
