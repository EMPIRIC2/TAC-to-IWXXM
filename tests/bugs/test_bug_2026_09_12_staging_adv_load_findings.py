"""Repro/guards for EV-staging-adv-load-e2e findings (F-ADV-LOAD-01/02/03)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def test_f_adv_load_02_locustfile_exports_user_classes() -> None:
    """Locust entrypoint must import HttpUser classes (F-ADV-LOAD-02)."""
    locustfile = REPO_ROOT / "apps/backend/tests/load/locustfile.py"
    text = locustfile.read_text(encoding="utf-8")
    assert "from tests.load.scenarios import" in text
    assert "PublicApiUser" in text
    assert "ConversionApiUser" in text


def test_f_adv_load_01_staging_api_replicas_and_ingress_timeouts() -> None:
    """Staging API should run ≥2 replicas with longer ingress timeouts (F-ADV-LOAD-01)."""
    resources = yaml.safe_load_all(
        (REPO_ROOT / "deploy/doks/overlays/staging/patch-resources.yaml").read_text(
            encoding="utf-8"
        )
    )
    api_patch = next(
        doc
        for doc in resources
        if doc and doc.get("metadata", {}).get("name") == "metar-api"
    )
    assert api_patch["spec"]["replicas"] >= 2

    ingress = yaml.safe_load(
        (REPO_ROOT / "deploy/doks/overlays/staging/patch-ingress-api.yaml").read_text(
            encoding="utf-8"
        )
    )
    annotations = ingress["metadata"]["annotations"]
    assert int(annotations["nginx.ingress.kubernetes.io/proxy-read-timeout"]) >= 120
    assert int(annotations["nginx.ingress.kubernetes.io/proxy-send-timeout"]) >= 120
    assert annotations["kubernetes.io/ingress.class"] == "nginx"


@pytest.mark.asyncio
async def test_f_adv_load_03_validation_router_honors_iwxxm_content_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``content_type=iwxxm`` must not run TAC airport_icao on XML (F-ADV-LOAD-03)."""
    from src.routers import validation as validation_router
    from src.schemas.validation import ValidationLayer
    from src.services.validation_orchestrator import ComprehensiveValidationResult

    class FakeOrch:
        def validate(self, xml_content, *, iwxxm_version, layers=None):
            assert "iwxxm:METAR" in xml_content or "METAR" in xml_content
            assert ValidationLayer.AIRPORT_ICAO not in (layers or [])
            return ComprehensiveValidationResult(
                is_valid=True,
                layers_run=[ValidationLayer.XML_WELLFORMED],
                layers_passed=[ValidationLayer.XML_WELLFORMED],
                layers_failed=[],
                all_issues=[],
                issues_by_layer={},
                version=iwxxm_version,
            )

    monkeypatch.setattr(
        validation_router, "get_validation_orchestrator", lambda: FakeOrch()
    )
    request = validation_router.ValidationRequest(
        content='<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>',
        content_type="iwxxm",
        layers=[ValidationLayer.XML_WELLFORMED],
    )
    result = await validation_router.validate_content(request)
    assert result.layers_validated == [ValidationLayer.XML_WELLFORMED]
    assert ValidationLayer.AIRPORT_ICAO not in result.layers_validated
