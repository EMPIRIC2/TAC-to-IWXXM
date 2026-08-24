"""TC-EV073-009 — CA_ECCC convert + validate with IWXXM_CA (EV-073 M2 / #1042)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from iwxxm_validate import rust_available
from iwxxm_validate.ca_eccc_bundle import CA_ECCC_IWXXM_VERSION, ca_eccc_bundle_available
from tac2iwxxm.ca_ops_corpus import extract_iwxxm_from_collect

from src import api as api_module

REPO_ROOT = Path(__file__).resolve().parents[4]
CA_FIXTURES = REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "profiles" / "CA_ECCC"


@pytest.fixture
def client() -> TestClient:
    return TestClient(api_module.app)


@pytest.mark.integration
def test_tc_ev073_009_ca_eccc_convert_validate_with_extensions(client: TestClient) -> None:
    if not ca_eccc_bundle_available():
        pytest.skip("CA_ECCC vendor bundle not present")
    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    manifest = json.loads((CA_FIXTURES / "manifest.json").read_text(encoding="utf-8"))
    case = next(c for c in manifest["cases"] if c["id"] == "metar_basic")
    tac_path = CA_FIXTURES / case["tac"]
    bulletin = f"SAUL31 CYUL 231800\n{tac_path.read_text(encoding='utf-8').strip()}"

    convert_resp = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, CA_ECCC_IWXXM_VERSION),
            "extensions": (None, "IWXXM_CA"),
            "exchange_output": (None, "true"),
            "lint": (None, "false"),
        },
    )
    assert convert_resp.status_code == 200, convert_resp.text[:800]
    collect_results = [row for row in convert_resp.json()["results"] if "MeteorologicalBulletin" in row["content"]]
    assert collect_results, convert_resp.text[:800]
    collect_xml = collect_results[0]["content"]
    inner_xml = extract_iwxxm_from_collect(collect_xml)
    assert inner_xml

    validate_resp = client.post(
        "/api/v1/validate",
        files={
            "xml_content": (None, inner_xml),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, CA_ECCC_IWXXM_VERSION),
            "product": (None, "METAR"),
            "extensions": (None, "IWXXM_CA"),
            "layers": (None, "ALL"),
            "stop_on_error": (None, "false"),
        },
    )
    assert validate_resp.status_code == 200, validate_resp.text[:800]
    body = validate_resp.json()
    stages = body.get("package_stages") or []
    ca_stage = next((stage for stage in stages if stage.get("stage") == "ca_xsd"), None)
    assert ca_stage is not None, body
    assert ca_stage.get("ok") is True, ca_stage
