"""TC-F6-030 T2 / T3.3: POST /convert-bulletin multi-result schema (Q6=A, Q7=C)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

FIXTURE_TEXT = """\
SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z 19010KT 10SM SCT040 21/13 A3010=
"""


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _multipart_bulletin(
    client: TestClient,
    *,
    manual_text: str,
    product: str = "METAR",
    profile: str = "annex3",
    lint: str = "true",
):
    return client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, manual_text),
            "product": (None, product),
            "profile": (None, profile),
            "lint": (None, lint),
        },
    )


def test_convert_bulletin_route_multi_result_schema(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Partial-success multi-result shape: bulletin_meta + results[] (Q6=A, Q7=C)."""

    def fake_convert(tac: str, **kwargs):
        return f"<iwxxm:METAR>{tac[:20]}</iwxxm:METAR>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = _multipart_bulletin(client, manual_text=FIXTURE_TEXT)
    assert response.status_code == 200
    payload = response.json()

    meta = payload["bulletin_meta"]
    assert meta["ahl"] == "SAUS31 KZNY 121200"
    assert meta["report_count"] == 2
    assert meta["tt"] == "SA"
    assert meta["aa"] == "US"
    assert meta["cccc"] == "KZNY"
    assert meta["yygggg"] == "121200"

    results = payload["results"]
    assert len(results) == 2
    assert results[0]["report_index"] == 0
    assert results[0]["ok"] is True
    assert results[0]["tac_input"].startswith("METAR KJFK")
    assert results[0]["xml"]
    assert results[0]["issues"] == []
    assert isinstance(results[0]["fixes"], list)
    assert results[1]["report_index"] == 1
    assert results[1]["ok"] is True


def test_convert_bulletin_partial_success_on_per_report_failure(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """HTTP 200 when split succeeds even if some reports fail (Q6=A)."""
    calls = {"n": 0}

    def fake_convert(tac: str, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return "<iwxxm:METAR>ok</iwxxm:METAR>", None
        raise api_module.ConversionError("parse boom")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = _multipart_bulletin(client, manual_text=FIXTURE_TEXT, lint="false")
    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["ok"] is True
    assert results[1]["ok"] is False
    assert results[1]["xml"] is None
    assert any(i["code"] == "parse_failed" for i in results[1]["issues"])


def test_convert_bulletin_empty_bulletin_400(client: TestClient) -> None:
    response = _multipart_bulletin(client, manual_text="SAUS31 KZNY 121200\n")
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "empty_bulletin"


def test_convert_bulletin_split_failed_422(client: TestClient) -> None:
    response = _multipart_bulletin(
        client,
        manual_text="METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=\n",
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "bulletin_split_failed"


def test_convert_bulletin_requires_product(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert-bulletin",
        files={"manual_text": (None, FIXTURE_TEXT)},
    )
    assert response.status_code == 422


SPECI_CCA_TEXT = """\
SPUS31 KZNY 121230 CCA
SPECI KJFK 121225Z 18008KT 10SM FEW250 22/14 A3012=
"""


def test_convert_bulletin_speci_ahl_bbb_report_status(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """EV-029 T3.2: SPECI AHL CCA → bulletin_meta.report_status + convert kwarg."""
    seen: dict[str, object] = {}

    def fake_convert(tac: str, **kwargs):
        seen.update(kwargs)
        return f'<iwxxm:SPECI reportStatus="CORRECTION">{tac[:20]}</iwxxm:SPECI>', None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = _multipart_bulletin(
        client,
        manual_text=SPECI_CCA_TEXT,
        product="SPECI",
        lint="false",
    )
    assert response.status_code == 200
    payload = response.json()
    meta = payload["bulletin_meta"]
    assert meta["tt"] == "SP"
    assert meta["bbb"] == "CCA"
    assert meta["report_status"] == "CORRECTION"
    assert seen.get("product") == "SPECI"
    assert seen.get("report_status") == "CORRECTION"
    assert payload["results"][0]["ok"] is True
    assert "iwxxm:SPECI" in (payload["results"][0]["xml"] or "")


TAF_CCA_TEXT = """\
FCUS31 KJFK 121200 CCA
TAF KJFK 121130Z 1212/1312 18010KT P6SM FEW050=
"""


def test_convert_bulletin_taf_ahl_bbb_report_status(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """EV-029 T4.2: TAF AHL CCA → bulletin_meta.report_status + convert kwarg."""
    seen: dict[str, object] = {}

    def fake_convert(tac: str, **kwargs):
        seen.update(kwargs)
        return f'<iwxxm:TAF reportStatus="CORRECTION">{tac[:20]}</iwxxm:TAF>', None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = _multipart_bulletin(
        client,
        manual_text=TAF_CCA_TEXT,
        product="TAF",
        lint="false",
    )
    assert response.status_code == 200
    payload = response.json()
    meta = payload["bulletin_meta"]
    assert meta["tt"] == "FC"
    assert meta["bbb"] == "CCA"
    assert meta["report_status"] == "CORRECTION"
    assert seen.get("product") == "TAF"
    assert seen.get("report_status") == "CORRECTION"
    assert payload["results"][0]["ok"] is True
    assert "iwxxm:TAF" in (payload["results"][0]["xml"] or "")


SIGMET_CCA_TEXT = """\
WSUK31 EGRR 121200 CCA
YUDD SIGMET 2 VALID 101200/101600 YUSO-
YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=
"""


def test_convert_bulletin_sigmet_ahl_bbb_report_status(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """EV-029 T5.2: SIGMET AHL CCA → bulletin_meta.report_status + convert kwarg."""
    seen: dict[str, object] = {}

    def fake_convert(tac: str, **kwargs):
        seen.update(kwargs)
        return f'<iwxxm:SIGMET reportStatus="CORRECTION">{tac[:20]}</iwxxm:SIGMET>', None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = _multipart_bulletin(
        client,
        manual_text=SIGMET_CCA_TEXT,
        product="SIGMET",
        lint="false",
    )
    assert response.status_code == 200
    payload = response.json()
    meta = payload["bulletin_meta"]
    assert meta["tt"] == "WS"
    assert meta["bbb"] == "CCA"
    assert meta["report_status"] == "CORRECTION"
    assert seen.get("product") == "SIGMET"
    assert seen.get("report_status") == "CORRECTION"
    assert payload["results"][0]["ok"] is True
    assert "iwxxm:SIGMET" in (payload["results"][0]["xml"] or "")


VA_SIGMET_CCA_TEXT = """\
WVUK31 EGRR 121200 CCA
EGGX SIGMET 4 VALID 251600/252000 EGRR-
EGGX SHANWICK OCEANIC FIR VA ERUPTION MT HEKLA PSN N6359 W01940
VA CLD OBS AT 1600Z WI N6000 W01150 - N5900 W01300 - N6000 W01600 - N6000 W01150 SFC/FL550 NC=
"""


def test_convert_bulletin_va_sigmet_ahl_bbb_report_status(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """EV-029 T6.2: WV AHL CCA → bulletin_meta.report_status + convert kwarg."""
    seen: dict[str, object] = {}

    def fake_convert(tac: str, **kwargs):
        seen.update(kwargs)
        return (
            f'<iwxxm:VolcanicAshSIGMET reportStatus="CORRECTION">{tac[:20]}</iwxxm:VolcanicAshSIGMET>',
            None,
        )

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = _multipart_bulletin(
        client,
        manual_text=VA_SIGMET_CCA_TEXT,
        product="SIGMET",
        lint="false",
    )
    assert response.status_code == 200
    payload = response.json()
    meta = payload["bulletin_meta"]
    assert meta["tt"] == "WV"
    assert meta["bbb"] == "CCA"
    assert meta["report_status"] == "CORRECTION"
    assert seen.get("product") == "SIGMET"
    assert seen.get("report_status") == "CORRECTION"
    assert payload["results"][0]["ok"] is True
    assert "iwxxm:VolcanicAshSIGMET" in (payload["results"][0]["xml"] or "")


TC_SIGMET_CCA_TEXT = """\
WCUK31 EGRR 121200 CCA
YUCC SIGMET 3 VALID 251600/252200 YUDO-
YUCC AMSWELL FIR TC GLORIA PSN N2706 W07306 CB OBS AT 1600Z WI 250NM OF TC CENTRE TOP FL500 NC
FCST AT 2200Z TC CENTRE PSN N2740 W07345=
"""


def test_convert_bulletin_tc_sigmet_ahl_bbb_report_status(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """EV-029 T7.2: WC AHL CCA → bulletin_meta.report_status + convert kwarg."""
    seen: dict[str, object] = {}

    def fake_convert(tac: str, **kwargs):
        seen.update(kwargs)
        return (
            f'<iwxxm:TropicalCycloneSIGMET reportStatus="CORRECTION">{tac[:20]}</iwxxm:TropicalCycloneSIGMET>',
            None,
        )

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = _multipart_bulletin(
        client,
        manual_text=TC_SIGMET_CCA_TEXT,
        product="SIGMET",
        lint="false",
    )
    assert response.status_code == 200
    payload = response.json()
    meta = payload["bulletin_meta"]
    assert meta["tt"] == "WC"
    assert meta["bbb"] == "CCA"
    assert meta["report_status"] == "CORRECTION"
    assert seen.get("product") == "SIGMET"
    assert seen.get("report_status") == "CORRECTION"
    assert payload["results"][0]["ok"] is True
    assert "iwxxm:TropicalCycloneSIGMET" in (payload["results"][0]["xml"] or "")


AIRMET_CCA_TEXT = """\
WAUK31 EGRR 121200 CCA
YUDD AIRMET 1 VALID 151520/151800 YUSO-
YUDD SHANLON FIR ISOL TS OBS N OF S50 TOP ABV FL100 STNR WKN=
"""


def test_convert_bulletin_airmet_ahl_bbb_report_status(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """EV-029 T8.2: WA AHL CCA → bulletin_meta.report_status + convert kwarg."""
    seen: dict[str, object] = {}

    def fake_convert(tac: str, **kwargs):
        seen.update(kwargs)
        return (
            f'<iwxxm:AIRMET reportStatus="CORRECTION">{tac[:20]}</iwxxm:AIRMET>',
            None,
        )

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = _multipart_bulletin(
        client,
        manual_text=AIRMET_CCA_TEXT,
        product="AIRMET",
        lint="false",
    )
    assert response.status_code == 200
    payload = response.json()
    meta = payload["bulletin_meta"]
    assert meta["tt"] == "WA"
    assert meta["bbb"] == "CCA"
    assert meta["report_status"] == "CORRECTION"
    assert seen.get("product") == "AIRMET"
    assert seen.get("report_status") == "CORRECTION"
    assert payload["results"][0]["ok"] is True
    assert "iwxxm:AIRMET" in (payload["results"][0]["xml"] or "")


def test_convert_bulletin_ignores_empty_upload_files(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """UploadFile path: empty files skipped; non-empty joined (PR #704)."""

    def fake_convert(tac: str, **kwargs):
        return f"<iwxxm:METAR>{tac[:20]}</iwxxm:METAR>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert-bulletin",
        data={"product": "METAR", "profile": "annex3", "lint": "false"},
        files=[
            ("files", ("empty.txt", b"", "text/plain")),
            ("files", ("metar_bulletin.txt", FIXTURE_TEXT.encode("utf-8"), "text/plain")),
        ],
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["bulletin_meta"]["report_count"] == 2
    assert payload["results"][0]["tac_input"].startswith("METAR KJFK")
    assert payload["results"][1]["tac_input"].startswith("METAR KLGA")
