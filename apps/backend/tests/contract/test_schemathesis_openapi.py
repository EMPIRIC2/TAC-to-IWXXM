"""TC-F34-001 - Schemathesis OpenAPI property suite against backend ASGI (F34 / #727).

Loads the live FastAPI OpenAPI document in-process (no network). Auth-protected
product routes use ``verify_supabase_token`` dependency override (published OpenAPI
intentionally has no Bearer scheme - F21 / ADR-031). Hypothesis budget:
``max_examples`` ≤ 25 (``D-S069-01-budget`` / TC-F34-007).

Exclusions (explicit - not silent large skips):
- ``/api/v1/work-sessions*`` - needs Postgres session store
- ``/api/v1/eval/*`` - needs job/persistence store
- ``/auth/*`` - needs live Supabase Auth proxy

Those surfaces stay covered by unit/integration tests.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
import schemathesis
from schemathesis import checks as st_checks

# Before importing the app (statistics / CORS side effects).
os.environ.setdefault("ENABLE_STATISTICS", "false")

from src.api import app
from src.utilities.security import verify_supabase_token

# TC-F34-007 / AC7 - do not raise without AskQuestion.
_MAX_EXAMPLES = int(os.environ.get("SCHEMATHESIS_MAX_EXAMPLES", "25"))
if _MAX_EXAMPLES > 25:
    raise RuntimeError(
        f"SCHEMATHESIS_MAX_EXAMPLES={_MAX_EXAMPLES} exceeds locked ceiling 25 (TC-F34-007 / D-S069-01-budget)"
    )

_EXCLUDED_PATH_PREFIXES: tuple[str, ...] = (
    "/api/v1/work-sessions",
    "/api/v1/eval",
    "/auth/",
)


def _path_excluded(path: str) -> bool:
    """Return True when *path* is intentionally out of Schemathesis scope."""
    return any(path == prefix or path.startswith(prefix) for prefix in _EXCLUDED_PATH_PREFIXES)


@pytest.fixture
def schemathesis_app() -> Iterator[object]:
    """ASGI app with JWT gate overridden so protected routes are exercised."""

    async def override_verify_token() -> dict[str, str]:
        return {"sub": "test-user-id", "aud": "test-project", "role": "user"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def api_schema(schemathesis_app: object) -> object:
    """Schemathesis schema from backend OpenAPI with budget + path filters."""
    config = schemathesis.Config.from_dict(
        {
            "generation": {"max-examples": _MAX_EXAMPLES},
            # Documented placeholder 501 on /api/v1/ingest-collect is expected (not a bug).
            "checks": {
                "not_a_server_error": {
                    "expected-statuses": ["2xx", "4xx", "501"],
                }
            },
        }
    )
    schema = schemathesis.openapi.from_asgi("/openapi.json", schemathesis_app, config=config)
    # Prefer filter over pytest.skip so excluded ops are not collected.
    return (
        schema.exclude(path_regex=r"^/api/v1/work-sessions")
        .exclude(path_regex=r"^/api/v1/eval")
        .exclude(path_regex=r"^/auth")
    )


schema = schemathesis.pytest.from_fixture("api_schema")


@pytest.mark.schemathesis
@schema.parametrize()
def test_openapi_no_unexpected_server_error(case: object) -> None:
    """Property: schema-valid requests must not yield unexpected 5xx (TC-F34-001)."""
    path = getattr(case, "path", "") or ""
    if _path_excluded(path):
        pytest.skip(f"excluded path {path}")

    case.call_and_validate(checks=(st_checks.not_a_server_error,))
