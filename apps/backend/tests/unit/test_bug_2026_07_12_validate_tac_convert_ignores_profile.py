"""Repro: /api/v1/validate TAC auto-convert ignores profile.

Bug: docs/bug-reports/BUG-2026-07-12-validate-tac-convert-ignores-profile.md
Review: PR #711 / 18-pr-review PRR-018
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

METAR = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_validate_tac_auto_convert_forwards_profile(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Form profile must reach convert_metar_tac_with_metadata when xml_content is omitted."""
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append({"tac": tac, **kwargs})
        return (
            '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>',
            None,
        )

    def fake_iwxxm_validate(xml: str, *, iwxxm_version: str, profile: str = "annex3", levels=None, product=None):
        from iwxxm_validate import ValidationReport

        return ValidationReport(
            ok=True,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=[],
        )

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    monkeypatch.setattr(api_module, "iwxxm_validate_fn", fake_iwxxm_validate)

    class _LayerResult:
        def __init__(self) -> None:
            self.is_valid = True
            self.version = "2025-2"
            self.layers_run = []
            self.layers_passed = []
            self.layers_failed = []
            self.all_issues = []
            self.issues_by_layer = {}
            self.stopped_at_layer = None

    class _Orch:
        def validate_complete(self, **_kwargs):
            return _LayerResult()

    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _Orch())

    response = client.post(
        "/api/v1/validate",
        files={
            "manual_text": (None, METAR),
            "profile": (None, "iwxxm_us"),
            "iwxxm_version": (None, "2025-2"),
            "layers": (None, "XML_WELLFORMED"),
        },
    )
    assert response.status_code == 200, response.text
    assert seen, "expected convert_metar_tac_with_metadata to be called"
    assert seen[0].get("profile") == "iwxxm_us"
