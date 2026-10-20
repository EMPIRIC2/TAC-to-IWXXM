"""Lock OpenAPI path templates that tests call with concrete ids.

Unit and e2e tests request ``/api/v1/stations/kjfk`` rather than the
template ``/api/v1/stations/{icao}``. This module names those templates
and checks the OpenAPI document still defines them. [Corpus: api] [Corpus: tests]
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = ROOT / "apps" / "frontend" / "openapi" / "openapi.json"

TEMPLATE_PATHS = (
    "/api/v1/dissemination/mappings/{mapping_id}",
    "/api/v1/dissemination/mappings/{name}",
    "/api/v1/dissemination/plans/{plan_id}",
    "/api/v1/dissemination/plans/{plan_id}/execute",
    "/api/v1/dissemination/plans/{slug}",
    "/api/v1/profiles/conversion-templates/{template_id}",
    "/api/v1/profiles/library-assets/{asset_id}",
    "/api/v1/profiles/overlays/{overlay_id}",
    "/api/v1/profiles/presets/{preset_id}",
    "/api/v1/profiles/rule-packs/{pack_id}",
    "/api/v1/profiles/templates/{template_id}",
    "/api/v1/quality-metrics/{stem}",
    "/api/v1/stations/{icao}",
    "/api/v1/work-sessions/{session_id}",
    "/api/v1/work-sessions/{session_id}/restore",
)


def test_openapi_document_defines_template_paths() -> None:
    """Each template path is a key on the OpenAPI paths object."""
    payload: object = json.loads(OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    paths = payload.get("paths")
    assert isinstance(paths, dict)
    missing = [path for path in TEMPLATE_PATHS if path not in paths]
    assert not missing, f"OpenAPI document dropped template paths: {missing}"
