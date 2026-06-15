"""T5.8 product regression smoke — F2–F4 post-move (REQ-016).

Verifies IWXXM validation (F2), airport data services (F3), and IWXXM version
handling (F4) remain functional after backend move to apps/backend/. Behavior
parity only — no feature rewrites.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.config.iwxxm_versions import get_namespace_uri, resolve_schema_file
from src.schemas.airport import get_airport_validator
from src.services.openaip_service import OpenAIPService
from src.utilities.airport_record_builder import AirportRecordBuilder
from src.utilities.security import verify_supabase_token

pytestmark = [pytest.mark.integration, pytest.mark.smoke]

SAMPLE_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
KNOWN_ICAO = "KJFK"
BACKEND_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def smoke_client() -> Iterator[TestClient]:
    """Authenticated in-process client for product smoke checks."""

    async def _auth_user() -> dict[str, str]:
        return {"sub": "smoke-user", "aud": "test"}

    app.dependency_overrides[verify_supabase_token] = _auth_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestF2ValidationSmoke:
    """F2: IWXXM validation routers and comprehensive validate endpoint."""

    def test_validation_layers_discovery(self, smoke_client: TestClient) -> None:
        response = smoke_client.get("/api/v1/validation/layers")
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload, dict)
        layers_raw = payload.get("layers")
        assert isinstance(layers_raw, list)
        layers: list[Any] = layers_raw
        assert len(layers) == 7
        layer_names = {
            layer["layer"] for layer in layers if isinstance(layer, dict)
        }
        assert "airport_icao" in layer_names
        assert "xml_schema" in layer_names

    def test_comprehensive_validate_known_good_metar(
        self, smoke_client: TestClient
    ) -> None:
        response = smoke_client.post(
            "/api/v1/validate",
            data={
                "manual_text": SAMPLE_METAR,
                "iwxxm_version": "2025-2",
                "layers": ["AIRPORT_ICAO", "TAC_SYNTAX"],
                "stop_on_error": "false",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload, dict)
        assert payload["is_valid"] is True
        layers_passed = payload.get("layers_passed")
        assert isinstance(layers_passed, list)
        assert "AIRPORT_ICAO" in layers_passed
        assert "TAC_SYNTAX" in layers_passed

    def test_validation_router_tac_validate(self, smoke_client: TestClient) -> None:
        response = smoke_client.post(
            "/api/v1/validation/validate",
            json={"content": SAMPLE_METAR},
        )
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload, dict)
        assert payload["passed"] is True
        assert payload["total_issues"] == 0


class TestF3AirportDataSmoke:
    """F3: Airport database, OpenAIP service, and enrichment helpers."""

    def test_airport_validator_loads_from_apps_backend(self) -> None:
        validator = get_airport_validator()
        assert validator.count() > 0
        assert validator.validate_icao(KNOWN_ICAO) is True
        airport = validator.get_airport(KNOWN_ICAO)
        assert airport is not None
        assert airport.icao == KNOWN_ICAO

    def test_openaip_service_initializes_post_move(self) -> None:
        service = OpenAIPService()
        assert service.cache_file.parent.name == "data"
        assert "apps/backend" in str(service.cache_file)

    def test_airport_record_builder_uses_legacy_airports_json(self) -> None:
        airports_json = BACKEND_ROOT / "src" / "data" / "airports.json"
        assert airports_json.is_file(), "apps/backend airport data must be present"
        builder = AirportRecordBuilder()
        record = builder.build_record(KNOWN_ICAO)
        assert record["icao"] == KNOWN_ICAO
        assert record.get("name")

    def test_translation_airport_region_endpoint(
        self, smoke_client: TestClient
    ) -> None:
        response = smoke_client.get(
            f"/api/v1/translation/airport-region/{KNOWN_ICAO}"
        )
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload, dict)
        assert payload["airport_code"] == KNOWN_ICAO
        assert payload["icao_region"] == "NAM"


class TestF4VersionHandlingSmoke:
    """F4: Multi-version IWXXM support and schema resolution."""

    def test_versions_endpoint_lists_supported(self, smoke_client: TestClient) -> None:
        response = smoke_client.get("/api/v1/versions")
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload, dict)
        supported = payload.get("supported_versions")
        assert isinstance(supported, list)
        versions = {
            entry["version"] for entry in supported if isinstance(entry, dict)
        }
        assert "2025-2" in versions
        assert "2023-1" in versions
        assert payload["default_version"] == "2025-2"

    @pytest.mark.parametrize("version", ["2025-2", "2023-1"])
    def test_convert_emits_version_specific_namespace(
        self, smoke_client: TestClient, version: str
    ) -> None:
        response = smoke_client.post(
            "/api/v1/convert",
            data={"manual_text": SAMPLE_METAR, "iwxxm_version": version},
        )
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload, dict)
        results = payload.get("results")
        assert isinstance(results, list) and results
        first = results[0]
        assert isinstance(first, dict)
        content = first.get("content")
        assert isinstance(content, str)
        expected_ns = get_namespace_uri(version)
        assert expected_ns in content

    @pytest.mark.parametrize("version", ["2025-2", "2023-1"])
    def test_vendor_schema_paths_resolve_post_move(self, version: str) -> None:
        xsd_path = resolve_schema_file(version, "xsd")
        assert xsd_path.is_file()
        codelists_dir = resolve_schema_file(version, "codelists")
        assert codelists_dir.is_dir()
