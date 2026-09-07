"""TC-EV071-008 - API convert exposes CA_ECCC output spec (EV-071 M2 / #1032)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from tac2iwxxm.exchange_output import ca_msc_filename, format_ca_wmo_ahl, issued_at_from_yygggg

from tac2iwxxm import parse_ahl

_BULLETIN = """\
SAUL31 CYUL 231800
METAR CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012=
"""

_CA_GOLDEN = (  # minimal CA METAR shell for monkeypatched convert
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0"\n'
    '    gml:id="metar.ca.basic.cyul"\n'
    '    reportStatus="NORMAL"\n'
    '    permissibleUsage="OPERATIONAL"\n'
    '    translationCentreDesignator="CWAO"\n'
    '    translationCentreName="Environment and Climate Change Canada">\n'
    '  <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
    "</iwxxm:METAR>"
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(api_module.app)


def test_tc_ev071_008_convert_metadata_includes_ca_output_spec(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Convert with semantic_profile=CA_ECCC returns operator-visible output_spec fields."""

    def fake_convert(tac: str, **kwargs):
        return _CA_GOLDEN, None

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
            "iwxxm_version": (None, "3.0.0"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    metadata = response.json()["metadata"]
    assert metadata["semantic_profile"] == "ca_eccc"
    spec = metadata["output_spec"]
    parts = parse_ahl("SAUL31 CYUL 231800")
    issued = issued_at_from_yygggg(parts.yygggg)
    assert spec["semantic_profile"] == "CA_ECCC"
    assert spec["wmo_header_designator"] == "A_LACN"
    assert "file_naming_pattern" in spec
    assert spec["suggested_filename"] == ca_msc_filename(parts, issued_at=issued)
    assert spec["wmo_ahl_header"] == format_ca_wmo_ahl(parts, product="METAR")
    assert "translation_centre_designator" in spec
    assert "translation_centre_name" in spec
    for value in spec.values():
        assert isinstance(value, str)
        assert "EV-" not in value
        assert "TC-" not in value
