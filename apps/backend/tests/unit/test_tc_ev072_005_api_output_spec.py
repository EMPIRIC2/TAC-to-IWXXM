"""TC-EV072-005 - API convert exposes CA_ECCC output spec per aerodrome product (EV-072 M1)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from tac2iwxxm.exchange_output import ca_msc_filename, format_ca_wmo_ahl, issued_at_from_yygggg

from tac2iwxxm import parse_ahl

_PRODUCT_CASES = (
    pytest.param(
        "METAR",
        "SAUL31 CYUL 231800",
        "A_LACN",
        "METAR",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0"\n'
        '    gml:id="metar.ca.basic.cyul"\n'
        '    reportStatus="NORMAL"\n'
        '    permissibleUsage="OPERATIONAL"\n'
        '    translationCentreDesignator="CWAO"\n'
        '    translationCentreName="Environment and Climate Change Canada">\n'
        '  <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
        "</iwxxm:METAR>",
        id="metar",
    ),
    pytest.param(
        "SPECI",
        "SPUL31 CYUL 231800",
        "A_LPCN",
        "SPECI",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<iwxxm:SPECI xmlns:iwxxm="http://icao.int/iwxxm/3.0"\n'
        '    gml:id="speci.ca.basic.cyul"\n'
        '    reportStatus="NORMAL"\n'
        '    permissibleUsage="OPERATIONAL"\n'
        '    translationCentreDesignator="CWAO"\n'
        '    translationCentreName="Environment and Climate Change Canada">\n'
        '  <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
        "</iwxxm:SPECI>",
        id="speci",
    ),
    pytest.param(
        "TAF",
        "FTUL31 CYUL 231800",
        "A_LTCN",
        "TAF",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<iwxxm:TAF xmlns:iwxxm="http://icao.int/iwxxm/3.0"\n'
        '    gml:id="taf.ca.basic.cyul"\n'
        '    reportStatus="NORMAL"\n'
        '    permissibleUsage="OPERATIONAL"\n'
        '    translationCentreDesignator="CWAO"\n'
        '    translationCentreName="Environment and Climate Change Canada">\n'
        '  <iwxxm:baseForecast nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
        "</iwxxm:TAF>",
        id="taf",
    ),
    pytest.param(
        "AIRMET",
        "WAUL31 CYUL 231800",
        "A_LWCN",
        "AIRMET",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<iwxxm:AIRMET xmlns:iwxxm="http://icao.int/iwxxm/3.0"\n'
        '    gml:id="airmet.ca.basic.cyul"\n'
        '    reportStatus="NORMAL"\n'
        '    permissibleUsage="OPERATIONAL"\n'
        '    translationCentreDesignator="CWAO"\n'
        '    translationCentreName="Environment and Climate Change Canada">\n'
        '  <iwxxm:analysis nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
        "</iwxxm:AIRMET>",
        id="airmet",
    ),
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(api_module.app)


@pytest.mark.parametrize(("product", "ahl", "designator", "report_line", "golden_xml"), _PRODUCT_CASES)
def test_tc_ev072_005_convert_metadata_includes_ca_output_spec(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    product: str,
    ahl: str,
    designator: str,
    report_line: str,
    golden_xml: str,
) -> None:
    """Convert with semantic_profile=CA_ECCC returns product-appropriate output_spec."""

    def fake_convert(tac: str, **kwargs):
        return golden_xml, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    monkeypatch.setattr(
        api_module, "tac_lint_fn", lambda *a, **k: type("R", (), {"ok": True, "issues": [], "fixes": []})()
    )

    bulletin = f"{ahl}\n{report_line} CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012=\n"
    if product == "TAF":
        bulletin = f"{ahl}\nTAF CYUL 231800Z 2319/2418 24010KT P6SM BKN020=\n"
    elif product == "AIRMET":
        bulletin = (
            f"{ahl}\n"
            "CZUL AIRMET 1 VALID 221400/221800 CWEG-\n"
            "CZUL MONTREAL FIR FRQ TCU ISOL TS OBS N OF S50 TOP ABV FL300 MOV E 20KT NC=\n"
        )

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, bulletin),
            "product": (None, product),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, "3.0.0"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    metadata = response.json()["metadata"]
    assert metadata["semantic_profile"] == "ca_eccc"
    spec = metadata["output_spec"]
    parts = parse_ahl(ahl)
    issued = issued_at_from_yygggg(parts.yygggg)
    assert spec["semantic_profile"] == "CA_ECCC"
    assert spec["wmo_header_designator"] == designator
    assert spec["suggested_filename"] == ca_msc_filename(parts, issued_at=issued)
    assert spec["wmo_ahl_header"] == format_ca_wmo_ahl(parts, product=product)
    for value in spec.values():
        assert isinstance(value, str)
        assert "EV-" not in value
        assert "TC-" not in value
