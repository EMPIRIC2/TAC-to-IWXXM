"""
TC-EV052-009 — committed OpenAPI snapshot must match FastAPI ``app.openapi()``.

EV-052 / M4 / D-S061-openapi-src: refresh via ``make openapi-refresh``.
"""

from __future__ import annotations

import json
from pathlib import Path

from src import api as api_module

_REPO_ROOT = Path(__file__).resolve().parents[4]
OPENAPI_SNAPSHOT = _REPO_ROOT / "apps" / "frontend" / "openapi" / "openapi.json"


def test_openapi_snapshot_exists() -> None:
    """Committed snapshot path locked for openapi-typescript input."""
    assert OPENAPI_SNAPSHOT.is_file(), f"Missing {OPENAPI_SNAPSHOT.relative_to(_REPO_ROOT)}; run: make openapi-refresh"


def test_openapi_snapshot_matches_live_schema() -> None:
    """Snapshot must equal live OpenAPI (sorted JSON) — CI drift gate."""
    live = api_module.app.openapi()
    expected = json.dumps(live, indent=2, sort_keys=True) + "\n"
    loaded = OPENAPI_SNAPSHOT.read_text(encoding="utf-8")
    assert loaded == expected, (
        "OpenAPI snapshot drift; run: make openapi-refresh "
        "(then regenerate FE types with pnpm --filter @metar/frontend openapi:generate)"
    )


def test_high_churn_schemas_present_in_snapshot() -> None:
    """Convert + validate response schemas must be in the committed snapshot."""
    schema = json.loads(OPENAPI_SNAPSHOT.read_text(encoding="utf-8"))
    comps = schema.get("components", {}).get("schemas", {})
    for name in (
        "ConversionResponse",
        "ConversionResult",
        "ValidateResponse",
        "LintTacResponse",
    ):
        assert name in comps, f"missing schema {name} in OpenAPI snapshot"
