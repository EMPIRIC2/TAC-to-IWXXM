"""TC-EV073-005 - API convert COLLECT output mode (EV-073 M1 / #1032)."""

from __future__ import annotations

import pytest
from dissemination.collect_namespaces import is_collect_bulletin
from fastapi.testclient import TestClient
from src import api as api_module
from tac2iwxxm.exchange_output import ca_msc_filename, issued_at_from_yygggg

from tac2iwxxm import parse_ahl

_BULLETIN = """\
SAUL31 CYUL 231800
METAR CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012=
"""

_CA_IWXXM_VERSION = "3.0.0"

_INNER_METAR = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0"\n'
    '    gml:id="metar.ca.basic.cyul"\n'
    '    reportStatus="NORMAL"\n'
    '    permissibleUsage="OPERATIONAL">\n'
    '  <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
    "</iwxxm:METAR>"
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(api_module.app)


def test_tc_ev073_005_exchange_output_wraps_collect(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CA_ECCC convert with exchange_output=true returns COLLECT-wrapped XML."""

    def fake_convert(tac: str, **kwargs):
        return _INNER_METAR, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    monkeypatch.setattr(
        api_module, "tac_lint_fn", lambda *a, **k: type("R", (), {"ok": True, "issues": [], "fixes": []})()
    )

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _BULLETIN),
            "product": (None, "METAR"),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, _CA_IWXXM_VERSION),
            "exchange_output": (None, "true"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload["metadata"].get("exchange_output") is True
    xml = payload["results"][0]["content"]
    assert xml
    assert is_collect_bulletin(xml)
    parts = parse_ahl("SAUL31 CYUL 231800")
    issued = issued_at_from_yygggg(parts.yygggg)
    expected_filename = ca_msc_filename(parts, issued_at=issued)
    assert expected_filename in xml


def test_tc_ev073_005_exchange_output_off_returns_inner_product(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default convert path keeps inner IWXXM product (no COLLECT wrap)."""

    def fake_convert(tac: str, **kwargs):
        return _INNER_METAR, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    monkeypatch.setattr(
        api_module, "tac_lint_fn", lambda *a, **k: type("R", (), {"ok": True, "issues": [], "fixes": []})()
    )

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _BULLETIN),
            "product": (None, "METAR"),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, _CA_IWXXM_VERSION),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    xml = response.json()["results"][0]["content"]
    assert xml
    assert not is_collect_bulletin(xml)
    assert "iwxxm:METAR" in xml
