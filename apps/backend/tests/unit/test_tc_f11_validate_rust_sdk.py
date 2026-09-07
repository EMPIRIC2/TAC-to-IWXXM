"""T3.8a / F11.4 / F13: /validate uses validate_iwxxm; no double heavy-layer run."""

from __future__ import annotations

from typing import Any, ClassVar
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from iwxxm_validate import Issue, ValidationReport, validate_iwxxm
from src import api as api_module
from src.utilities.security import verify_supabase_token


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_validate_route_binds_validate_iwxxm_sdk() -> None:
    """F13: backend thin wrapper must bind the Rust-preferring SDK entrypoint."""
    assert api_module.iwxxm_validate_fn is validate_iwxxm


def test_validate_calls_sdk_once_without_orchestrator_xsd_schematron(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    F11.4: package XSD+Schematron must not be re-run by the legacy orchestrator.

    Spec: feature-list F11 §4; execution-plan T3.8a.
    """
    sdk_calls: list[dict[str, Any]] = []
    heavy_in_orch: list[str] = []

    def fake_sdk(
        xml: str,
        *,
        iwxxm_version: str,
        profile: str = "annex3",
        levels=None,
        product: str | None = None,
    ) -> ValidationReport:
        sdk_calls.append(
            {
                "xml": xml,
                "iwxxm_version": iwxxm_version,
                "profile": profile,
                "levels": levels,
                "product": product,
            }
        )
        return ValidationReport(
            ok=True,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=[],
        )

    monkeypatch.setattr(api_module, "iwxxm_validate_fn", fake_sdk)

    class _FakeResult:
        is_valid = True
        version = "2023-1"
        layers_run: ClassVar[list[Any]] = []
        layers_passed: ClassVar[list[Any]] = []
        layers_failed: ClassVar[list[Any]] = []
        all_issues: ClassVar[list[Any]] = []
        issues_by_layer: ClassVar[dict[Any, list[Any]]] = {}
        stopped_at_layer = None

    def fake_complete(*, tac_text, xml_content, version, layers, stop_on_error=False):
        for layer in layers:
            name = getattr(layer, "name", str(layer))
            if name in ("XML_SCHEMA", "SCHEMATRON"):
                heavy_in_orch.append(name)
        return _FakeResult()

    orch = MagicMock()
    orch.validate_complete.side_effect = fake_complete
    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: orch)

    xml = """<?xml version="1.0"?><root xmlns="http://icao.int/iwxxm/2023-1"/>"""
    response = client.post(
        "/api/v1/validate",
        files={
            "xml_content": (None, xml),
            "iwxxm_version": (None, "2023-1"),
            "profile": (None, "annex3"),
            "layers": (None, "ALL"),
        },
    )
    assert response.status_code == 200, response.text
    assert len(sdk_calls) == 1
    assert sdk_calls[0]["profile"] == "annex3"
    assert set(sdk_calls[0]["levels"] or ()) >= {"xsd", "schematron"}
    assert heavy_in_orch == [], f"orchestrator must skip heavy layers, got {heavy_in_orch}"
    orch.validate_complete.assert_called_once()

    body = response.json()
    assert body["package_ok"] is True
    assert "package_issues" in body


def test_validate_import_surface_exports_validate_iwxxm() -> None:
    """Guard: iwxxm_validate public API exposes validate_iwxxm for backend bind."""
    import iwxxm_validate

    assert callable(iwxxm_validate.validate_iwxxm)
    assert Issue is not None
