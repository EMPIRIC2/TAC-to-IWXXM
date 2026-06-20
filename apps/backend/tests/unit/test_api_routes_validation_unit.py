"""Route-level unit tests for api.py validate and metadata endpoints."""

from __future__ import annotations

import builtins
import io
from types import SimpleNamespace

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient

from src import api as api_module
from src.schemas.validation import ValidationLayer, ValidationLevel
from src.utilities.conversion import ConversionError
from src.utilities.security import verify_supabase_token


@pytest.fixture
def client(monkeypatch):
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_get_supported_versions_response_shape(client, monkeypatch):
    from src.config import iwxxm_versions as versions_module

    monkeypatch.setattr(versions_module, "DEFAULT_VERSION", "2025-2")
    monkeypatch.setattr(
        versions_module,
        "SUPPORTED_VERSIONS",
        {
            "2023-1": {
                "name": "IWXXM 2023-1",
                "status": "previous",
                "release_date": "2023-06-02",
                "wmo_amendment": 78,
            },
            "2025-2": {
                "name": "IWXXM 2025-2",
                "status": "latest",
                "release_date": "2025-11-25",
                "wmo_amendment": 82,
            },
        },
    )
    monkeypatch.setattr(versions_module, "DEPRECATED_VERSIONS", {"2021-2": {}, "2018": {}})

    response = client.get("/api/v1/versions")

    assert response.status_code == 200
    payload = response.json()
    assert payload["default_version"] == "2025-2"
    assert payload["supported_versions"][0]["version"] == "2025-2"
    assert "2021-2" in payload["deprecated_versions"]


def test_get_schema_status_includes_rc_metadata(client, monkeypatch):
    from src.config import iwxxm_versions as versions_module

    monkeypatch.setattr(versions_module, "DEFAULT_VERSION", "2025-2")
    monkeypatch.setattr(
        versions_module,
        "get_versions_by_channel",
        lambda channel: {
            "stable": ["2025-2", "2023-1"],
            "rc": ["2025-2RC1"],
            "all": ["2025-2", "2025-2RC1", "2023-1"],
        }[channel],
    )
    monkeypatch.setattr(
        versions_module,
        "get_all_versions_with_metadata",
        lambda: {
            "2025-2": {
                "name": "IWXXM 2025-2",
                "status": "latest",
                "discovery_metadata": {
                    "channel": "stable",
                    "discovered": "2025-11-25T00:00:00Z",
                    "source_url": "https://example/stable",
                    "mirrored": True,
                },
            },
            "2025-2RC1": {
                "name": "IWXXM 2025-2 RC1",
                "status": "rc",
                "promoted_to_stable": None,
                "discovery_metadata": {
                    "channel": "rc",
                    "discovered": "2026-02-10T00:00:00Z",
                    "source_url": "https://example/rc",
                    "mirrored": False,
                },
            },
        },
    )

    response = client.get("/api/v1/schema-status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["stable"] == ["2025-2", "2023-1"]
    assert payload["rc"] == ["2025-2RC1"]
    assert "promoted_to_stable" in payload["metadata"]["2025-2RC1"]
    assert "promoted_to_stable" not in payload["metadata"]["2025-2"]


@pytest.mark.asyncio
async def test_parse_optional_files_filters_non_upload_values():
    upload = UploadFile(filename="a.txt", file=io.BytesIO(b"x"))

    class _Form:
        def getlist(self, _name):
            return [upload, "", None, 123]

    class _Req:
        async def form(self):
            return _Form()

    files = await api_module.parse_optional_files(_Req())
    assert len(files) == 1
    assert files[0].filename == "a.txt"


@pytest.mark.asyncio
async def test_validate_comprehensive_json_body_maps_level_to_layers(monkeypatch):
    captured = {}

    def fake_normalize(version):
        return version

    def fake_get_version_config(_version):
        return {"name": "IWXXM"}

    class _Orchestrator:
        def validate_complete(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                is_valid=True,
                version=kwargs["version"],
                layers_run=[ValidationLayer.SCHEMATRON],
                layers_passed=[ValidationLayer.SCHEMATRON],
                layers_failed=[],
                all_issues=[],
                issues_by_layer={},
                stopped_at_layer=None,
            )

    from src.config import iwxxm_versions as versions_module

    monkeypatch.setattr(versions_module, "normalize_version", fake_normalize)
    monkeypatch.setattr(versions_module, "get_version_config", fake_get_version_config)
    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _Orchestrator())

    request_body = api_module.ValidateRequest(
        iwxxm_xml="<iwxxm:METAR/>",
        version="2025-2",
        validation_level="schematron",
        stop_on_error=False,
    )
    response = await api_module.validate_comprehensive(
        request_body=request_body,
        user={"sub": "test-user", "aud": "test-aud"},
    )

    assert response["is_valid"] is True
    assert captured["layers"] == [ValidationLayer.SCHEMATRON]
    assert captured["stop_on_error"] is not False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "level,expected",
    [
        ("schema", [ValidationLayer.XML_WELLFORMED, ValidationLayer.XML_SCHEMA]),
        ("icao_opmet", [ValidationLayer.WMO_CODELISTS, ValidationLayer.GML_REFERENCES]),
        ("unexpected", [ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX]),
    ],
)
async def test_validate_comprehensive_json_level_mapping_variants(monkeypatch, level, expected):
    captured = {}

    from src.config import iwxxm_versions as versions_module

    monkeypatch.setattr(versions_module, "normalize_version", lambda version: version)
    monkeypatch.setattr(versions_module, "get_version_config", lambda _version: {"name": "IWXXM"})

    class _Orchestrator:
        def validate_complete(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                is_valid=True,
                version=kwargs["version"],
                layers_run=kwargs["layers"],
                layers_passed=kwargs["layers"],
                layers_failed=[],
                all_issues=[],
                issues_by_layer={},
                stopped_at_layer=None,
            )

    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _Orchestrator())

    request_body = api_module.ValidateRequest(
        iwxxm_xml="<iwxxm:METAR/>",
        version="2025-2",
        validation_level=level,
        stop_on_error=True,
    )

    response = await api_module.validate_comprehensive(
        request_body=request_body,
        user={"sub": "test-user", "aud": "test-aud"},
    )

    assert response["is_valid"] is True
    assert captured["layers"] == expected


def test_validate_comprehensive_invalid_version_returns_400(client, monkeypatch):
    from src.config import iwxxm_versions as versions_module

    monkeypatch.setattr(versions_module, "normalize_version", lambda v: v)

    def raise_invalid(_version):
        raise ValueError("bad version")

    monkeypatch.setattr(versions_module, "get_version_config", raise_invalid)

    response = client.post(
        "/api/v1/validate",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK", "iwxxm_version": "bad"},
    )

    assert response.status_code == 400
    assert "bad version" in response.json()["detail"]


def test_validate_comprehensive_conversion_error_returns_400(client, monkeypatch):
    from src.config import iwxxm_versions as versions_module

    monkeypatch.setattr(versions_module, "normalize_version", lambda v: v)
    monkeypatch.setattr(versions_module, "get_version_config", lambda _v: {"ok": True})

    def fail_convert(*_args, **_kwargs):
        raise ConversionError("failed conversion")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_convert)

    response = client.post(
        "/api/v1/validate",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK", "iwxxm_version": "2025-2"},
    )

    assert response.status_code == 400
    assert "Failed to convert TAC to XML" in response.json()["detail"]


def test_validate_comprehensive_invalid_layer_returns_400(client, monkeypatch):
    from src.config import iwxxm_versions as versions_module

    monkeypatch.setattr(versions_module, "normalize_version", lambda v: v)
    monkeypatch.setattr(versions_module, "get_version_config", lambda _v: {"ok": True})

    response = client.post(
        "/api/v1/validate",
        data={
            "xml_content": "<iwxxm:METAR/>",
            "iwxxm_version": "2025-2",
            "layers": ["NOT_A_LAYER"],
        },
    )

    assert response.status_code == 400
    assert "Invalid validation layer" in response.json()["detail"]


def test_validate_comprehensive_unexpected_exception_returns_500(client, monkeypatch):
    from src.config import iwxxm_versions as versions_module

    monkeypatch.setattr(versions_module, "normalize_version", lambda v: v)
    monkeypatch.setattr(versions_module, "get_version_config", lambda _v: {"ok": True})

    class _BoomOrchestrator:
        def validate_complete(self, **_kwargs):
            raise RuntimeError("orchestrator boom")

    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _BoomOrchestrator())

    response = client.post(
        "/api/v1/validate",
        data={"xml_content": "<iwxxm:METAR/>", "iwxxm_version": "2025-2", "layers": ["ALL"]},
    )

    assert response.status_code == 500
    assert "Validation failed" in response.json()["detail"]


def test_validate_comprehensive_formats_issue_payload(client, monkeypatch):
    from src.config import iwxxm_versions as versions_module

    monkeypatch.setattr(versions_module, "normalize_version", lambda v: v)
    monkeypatch.setattr(versions_module, "get_version_config", lambda _v: {"ok": True})

    issue = SimpleNamespace(
        layer=ValidationLayer.XML_SCHEMA,
        level=ValidationLevel.ERROR,
        message="schema issue",
        location="line 1",
        code="SCHEMA_FAIL",
    )

    class _Orchestrator:
        def validate_complete(self, **kwargs):
            return SimpleNamespace(
                is_valid=False,
                version=kwargs["version"],
                layers_run=[ValidationLayer.XML_SCHEMA],
                layers_passed=[],
                layers_failed=[ValidationLayer.XML_SCHEMA],
                all_issues=[issue],
                issues_by_layer={ValidationLayer.XML_SCHEMA: [issue]},
                stopped_at_layer=ValidationLayer.XML_SCHEMA,
            )

    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _Orchestrator())

    response = client.post(
        "/api/v1/validate",
        data={"xml_content": "<iwxxm:METAR/>", "iwxxm_version": "2025-2", "layers": ["ALL"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_valid"] is False
    assert payload["total_issues"] == 1
    assert payload["issues"][0]["code"] == "SCHEMA_FAIL"
    assert payload["stopped_at_layer"] == "XML_SCHEMA"


def test_get_supported_versions_import_fallback(monkeypatch):
    """Cover fallback import path in get_supported_versions()."""
    original_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "src.config.iwxxm_versions":
            raise ImportError("force fallback")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import)

    payload = api_module.get_supported_versions()

    assert "default_version" in payload
    assert isinstance(payload["supported_versions"], list)


def test_get_schema_status_import_fallback(monkeypatch):
    """Cover fallback import path in get_schema_status()."""
    original_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "src.config.iwxxm_versions":
            raise ImportError("force fallback")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import)

    payload = api_module.get_schema_status()

    assert "default" in payload
    assert "metadata" in payload


@pytest.mark.asyncio
async def test_validate_comprehensive_comprehensive_level_and_import_fallback(monkeypatch):
    """Cover comprehensive mapping and validate endpoint fallback import branch."""
    captured = {}
    original_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "src.config.iwxxm_versions":
            raise ImportError("force fallback")
        return original_import(name, globals, locals, fromlist, level)

    class _Orchestrator:
        def validate_complete(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                is_valid=True,
                version=kwargs["version"],
                layers_run=kwargs["layers"],
                layers_passed=kwargs["layers"],
                layers_failed=[],
                all_issues=[],
                issues_by_layer={},
                stopped_at_layer=None,
            )

    monkeypatch.setattr(builtins, "__import__", _import)
    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _Orchestrator())

    response = await api_module.validate_comprehensive(
        request_body=api_module.ValidateRequest(
            iwxxm_xml="<iwxxm:METAR/>",
            version="2025-2",
            validation_level="comprehensive",
            stop_on_error=False,
        ),
        user={"sub": "test-user", "aud": "test-aud"},
    )

    assert response["is_valid"] is True
    assert captured["layers"]
    assert ValidationLayer.AIRPORT_ICAO in captured["layers"]
