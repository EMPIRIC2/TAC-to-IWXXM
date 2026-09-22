"""TC-EVBRIDGE-008/009 API — transforms on send, not convert-only; decoding seed."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from dissemination.handles import default_handle_store
from dissemination.rate_limit import DisseminationRateLimiter
from fastapi.testclient import TestClient
from src import api as api_module
from src.routers import dissemination as diss_router
from src.utilities.abuse_controls import get_limiter
from src.utilities.security import verify_optional_supabase_token, verify_supabase_token
from tac2iwxxm.library_assets import get_first_party_library_asset

_TAC = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="
_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" gml:id="m1">'
    "<iwxxm:observation/></iwxxm:METAR>"
)


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    async def override_verify_token():
        return {"sub": str(uuid4()), "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    api_module.app.dependency_overrides[verify_optional_supabase_token] = override_verify_token
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "")
    lim = DisseminationRateLimiter(max_per_minute=1000)
    monkeypatch.setattr(diss_router, "default_rate_limiter", lim)
    default_handle_store.clear()
    get_limiter().reset()
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()
    default_handle_store.clear()
    get_limiter().reset()


def _sqlite_uri(tmp_path: Path) -> str:
    return f"sqlite+aiosqlite:///{tmp_path / 'dissem.db'}"


def test_tc_evbridge_008_convert_only_skips_dissemination_transforms(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _TAC),
            "product": (None, "METAR"),
            "conversion_library_id": (None, "LIB.CONVERSION.ICAO_2025"),
            "dissemination_library_id": (None, "LIB.DISSEMINATION.ICAO_2025"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:400]
    content = response.json()["results"][0]["content"]
    assert "MeteorologicalBulletin" not in content
    assert "dissemination-checksum" not in content


def test_tc_evbridge_008_convert_bulletin_applies_dissemination_library(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, "LIB.CONVERSION.ICAO_2025"),
            "dissemination_library_id": (None, "LIB.DISSEMINATION.ICAO_2025"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    xml = response.json()["results"][0]["xml"]
    assert xml is not None
    assert "MeteorologicalBulletin" in xml
    assert "dissemination-checksum" in xml


def test_tc_evbridge_008_convert_bulletin_unknown_conversion_library(
    client: TestClient,
) -> None:
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, "LIB.CONVERSION.NOT_REAL"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400
    assert "Unknown conversion library" in response.text


def test_tc_evbridge_008_convert_bulletin_unknown_dissemination_library(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, "LIB.CONVERSION.ICAO_2025"),
            "dissemination_library_id": (None, "LIB.CONVERSION.ICAO_2025"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400
    assert "Dissemination library" in response.text


def test_tc_evbridge_008_convert_bulletin_transform_value_error(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    def boom(*_a, **_k):
        raise ValueError("bad transform")

    monkeypatch.setattr(
        "dissemination.transforms.apply_dissemination_transforms",
        boom,
    )
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, "LIB.CONVERSION.ICAO_2025"),
            "dissemination_library_id": (None, "LIB.DISSEMINATION.ICAO_2025"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400
    assert "bad transform" in response.text


def test_tc_evbridge_008_convert_json_library_ids(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [_TAC],
            "version": "2025-2",
            "conversion_library_id": "LIB.CONVERSION.ICAO_2025",
            "tac_validation_library_id": "LIB.TAC_VALIDATION.ICAO_2025",
            "iwxxm_validation_library_id": "LIB.IWXXM_VALIDATION.ICAO_2025",
            "dissemination_library_id": "LIB.DISSEMINATION.ICAO_2025",
            "decoding_library_id": "LIB.DECODING.ICAO_2025",
            "validation_level": "basic",
        },
    )
    assert response.status_code == 200, response.text[:400]


def test_tc_evbridge_008_convert_custom_library_engine(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    custom = MagicMock()
    custom.engine_profile_id = "ICAO_2025"
    custom.kind = "conversion"
    fake_svc = MagicMock()
    fake_svc.get_library_asset.return_value = custom
    monkeypatch.setattr(
        "src.routers.conversion.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _TAC),
            "product": (None, "METAR"),
            "conversion_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200, response.text[:400]
    fake_svc.get_library_asset.assert_called()


def test_tc_evbridge_008_convert_custom_library_lookup_exception(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    fake_svc = MagicMock()
    fake_svc.get_library_asset.side_effect = RuntimeError("db down")
    monkeypatch.setattr(
        "src.routers.conversion.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _TAC),
            "product": (None, "METAR"),
            "conversion_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 400
    assert "Unknown conversion library" in response.text


def test_tc_evbridge_008_convert_unknown_library_without_auth(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unauthenticated convert: custom engine callback returns None (profiles_service absent)."""
    api_module.app.dependency_overrides.pop(verify_optional_supabase_token, None)

    async def no_auth():
        return None

    api_module.app.dependency_overrides[verify_optional_supabase_token] = no_auth

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _TAC),
            "product": (None, "METAR"),
            "conversion_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400
    assert "Unknown conversion library" in response.text


def test_tc_evbridge_008_send_applies_dissemination_library(
    client: TestClient,
    tmp_path: Path,
) -> None:
    uri = _sqlite_uri(tmp_path)
    pre = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "sqlite", "uri": uri, "ddl": True}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert pre.status_code == 200, pre.text
    handle = pre.json()["handle"]
    send = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "handle": handle,
                "iwxxm_xml": _XML,
                "product": "metar",
                "dissemination_library_id": "LIB.DISSEMINATION.ICAO_2025",
                "params": {"bulletin_identifier": "A_SEND.xml"},
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert send.status_code == 200, send.text
    assert send.json()["ok"] is True


def test_tc_evbridge_008_send_unknown_dissemination_library(
    client: TestClient,
    tmp_path: Path,
) -> None:
    uri = _sqlite_uri(tmp_path)
    pre = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "sqlite", "uri": uri, "ddl": True}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    handle = pre.json()["handle"]
    send = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "handle": handle,
                "iwxxm_xml": _XML,
                "product": "metar",
                "dissemination_library_id": "LIB.CONVERSION.ICAO_2025",
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert send.status_code == 400
    assert "Dissemination library" in send.text


def test_tc_evbridge_008_send_transform_value_error(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uri = _sqlite_uri(tmp_path)
    pre = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "sqlite", "uri": uri, "ddl": True}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    handle = pre.json()["handle"]

    def boom(*_a, **_k):
        raise ValueError("send transform boom")

    monkeypatch.setattr(
        "dissemination.transforms.apply_dissemination_transforms",
        boom,
    )
    send = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "handle": handle,
                "iwxxm_xml": _XML,
                "product": "metar",
                "dissemination_library_id": "LIB.DISSEMINATION.ICAO_2025",
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert send.status_code == 400
    assert "send transform boom" in send.text


def test_tc_evbridge_009_decoding_library_seeded_from_decode_tac() -> None:
    asset = get_first_party_library_asset("LIB.DECODING.ICAO_2025")
    assert asset is not None
    assert asset.kind == "decoding"
    assert asset.body.get("seed") == "decode_tac"
    entries = asset.body.get("entries") or []
    assert len(entries) >= 10
    tokens = {row["token"] for row in entries}
    assert "TS" in tokens
    assert all(row.get("source") == "decode_tac" for row in entries)


def test_tc_evbridge_008_convert_rejects_wrong_kind_custom(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Custom library with non-conversion kind is rejected."""

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    custom = MagicMock()
    custom.engine_profile_id = "ICAO_2025"
    custom.kind = "decoding"
    fake_svc = MagicMock()
    fake_svc.get_library_asset.return_value = custom
    monkeypatch.setattr(
        "src.routers.conversion.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )
    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _TAC),
            "product": (None, "METAR"),
            "conversion_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 400
    assert "Conversion library" in response.text


def test_tc_evbridge_008_convert_bulletin_custom_conversion(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """convert-bulletin resolves custom Conversion libraries when authenticated."""

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    custom = MagicMock()
    custom.engine_profile_id = "ICAO_2025"
    custom.kind = "conversion"
    fake_svc = MagicMock()
    fake_svc.get_library_asset.return_value = custom
    monkeypatch.setattr(
        "src.routers.conversion.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200, response.text[:400]
    fake_svc.get_library_asset.assert_called()


def test_tc_evbridge_008_send_custom_dissemination_library(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authenticated send applies custom Dissemination library transforms."""
    custom = MagicMock()
    custom.kind = "dissemination"
    custom.body = {"transforms": [{"type": "checksum", "params": {}}]}
    fake_svc = MagicMock()
    fake_svc.get_library_asset.return_value = custom
    monkeypatch.setattr(
        "src.routers.dissemination.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )
    uri = _sqlite_uri(tmp_path)
    pre = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "sqlite", "uri": uri, "ddl": True}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    handle = pre.json()["handle"]
    send = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "handle": handle,
                "iwxxm_xml": _XML,
                "product": "metar",
                "dissemination_library_id": str(uuid4()),
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert send.status_code == 200, send.text
    fake_svc.get_library_asset.assert_called()
    assert send.json()["ok"] is True


def test_tc_evbridge_008_convert_custom_library_value_error(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ValueError from get_library_asset is re-raised as HTTP 400."""

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    fake_svc = MagicMock()
    fake_svc.get_library_asset.side_effect = ValueError("conversion_library_id must reference a Conversion library")
    monkeypatch.setattr(
        "src.routers.conversion.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )
    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _TAC),
            "product": (None, "METAR"),
            "conversion_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 400
    assert "Conversion library" in response.text


def test_tc_evbridge_008_convert_bulletin_custom_without_auth(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unauthenticated convert-bulletin: custom engine callback returns None."""
    api_module.app.dependency_overrides.pop(verify_optional_supabase_token, None)

    async def no_auth():
        return None

    api_module.app.dependency_overrides[verify_optional_supabase_token] = no_auth

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400
    assert "Unknown conversion library" in response.text


def test_tc_evbridge_008_convert_bulletin_custom_value_error(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """convert-bulletin re-raises ValueError from custom Conversion lookup."""

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    fake_svc = MagicMock()
    fake_svc.get_library_asset.side_effect = ValueError("conversion_library_id must reference a Conversion library")
    monkeypatch.setattr(
        "src.routers.conversion.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 400
    assert "Conversion library" in response.text


def test_tc_evbridge_008_convert_bulletin_rejects_wrong_kind(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """convert-bulletin rejects custom assets that are not Conversion kind."""

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    custom = MagicMock()
    custom.engine_profile_id = "ICAO_2025"
    custom.kind = "decoding"
    fake_svc = MagicMock()
    fake_svc.get_library_asset.return_value = custom
    monkeypatch.setattr(
        "src.routers.conversion.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 400
    assert "Conversion library" in response.text


def test_tc_evbridge_008_convert_bulletin_custom_dissemination(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """convert-bulletin applies custom Dissemination library transforms."""

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    conversion = MagicMock()
    conversion.engine_profile_id = "ICAO_2025"
    conversion.kind = "conversion"
    dissem = MagicMock()
    dissem.kind = "dissemination"
    dissem.body = {"transforms": [{"type": "checksum", "params": {}}]}
    fake_svc = MagicMock()

    def _get(asset_id: str, **_k):
        if asset_id.startswith("conv"):
            return conversion
        return dissem

    fake_svc.get_library_asset.side_effect = _get
    monkeypatch.setattr(
        "src.routers.conversion.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    conv_id = f"conv-{uuid4()}"
    dissem_id = str(uuid4())
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, conv_id),
            "dissemination_library_id": (None, dissem_id),
            "lint": (None, "false"),
        },
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200, response.text[:500]
    xml = response.json()["results"][0]["xml"]
    assert xml is not None
    assert "dissemination-checksum" in xml


def test_tc_evbridge_008_convert_bulletin_dissem_wrong_kind(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """convert-bulletin rejects Dissemination library of wrong kind."""

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    conversion = MagicMock()
    conversion.engine_profile_id = "ICAO_2025"
    conversion.kind = "conversion"
    wrong = MagicMock()
    wrong.kind = "conversion"
    wrong.body = {}
    fake_svc = MagicMock()

    def _get(asset_id: str, **_k):
        if asset_id.startswith("conv"):
            return conversion
        return wrong

    fake_svc.get_library_asset.side_effect = _get
    monkeypatch.setattr(
        "src.routers.conversion.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, f"conv-{uuid4()}"),
            "dissemination_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 400
    assert "Dissemination library" in response.text


def test_tc_evbridge_008_convert_bulletin_dissem_lookup_paths(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """convert-bulletin Dissemination lookup: ValueError re-raise and soft Exception."""

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    conversion = MagicMock()
    conversion.engine_profile_id = "ICAO_2025"
    conversion.kind = "conversion"
    fake_svc = MagicMock()
    call_state = {"n": 0}

    def _get(asset_id: str, **_k):
        if asset_id.startswith("conv"):
            return conversion
        call_state["n"] += 1
        if call_state["n"] == 1:
            raise ValueError("dissemination_library_id must reference a Dissemination library")
        raise RuntimeError("db down")

    fake_svc.get_library_asset.side_effect = _get
    monkeypatch.setattr(
        "src.routers.conversion.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    files = {
        "manual_text": (None, bulletin),
        "product": (None, "METAR"),
        "conversion_library_id": (None, f"conv-{uuid4()}"),
        "dissemination_library_id": (None, str(uuid4())),
        "lint": (None, "false"),
    }
    r1 = client.post(
        "/api/v1/convert-bulletin",
        files=files,
        headers={"Authorization": "Bearer test-token"},
    )
    assert r1.status_code == 400
    assert "Dissemination library" in r1.text

    files["dissemination_library_id"] = (None, str(uuid4()))
    r2 = client.post(
        "/api/v1/convert-bulletin",
        files=files,
        headers={"Authorization": "Bearer test-token"},
    )
    assert r2.status_code == 400
    assert "Unknown dissemination library" in r2.text


def test_tc_evbridge_008_convert_bulletin_dissem_without_auth(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unauthenticated convert-bulletin: custom Dissemination callback returns None."""
    api_module.app.dependency_overrides.pop(verify_optional_supabase_token, None)

    async def no_auth():
        return None

    api_module.app.dependency_overrides[verify_optional_supabase_token] = no_auth

    def fake_convert(tac: str, **kwargs):
        return _XML, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    bulletin = f"SAUS31 KZNY 121200\n{_TAC}"
    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, bulletin),
            "product": (None, "METAR"),
            "conversion_library_id": (None, "LIB.CONVERSION.ICAO_2025"),
            "dissemination_library_id": (None, str(uuid4())),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400
    assert "Unknown dissemination library" in response.text


def test_tc_evbridge_008_send_custom_dissem_without_auth(
    client: TestClient,
    tmp_path: Path,
) -> None:
    """Unauthenticated send: custom Dissemination callback returns None."""
    api_module.app.dependency_overrides.pop(verify_optional_supabase_token, None)

    async def no_auth():
        return None

    api_module.app.dependency_overrides[verify_optional_supabase_token] = no_auth
    uri = _sqlite_uri(tmp_path)
    pre = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "sqlite", "uri": uri, "ddl": True}),
        headers={"Content-Type": "application/json"},
    )
    assert pre.status_code == 200, pre.text
    handle = pre.json()["handle"]
    send = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "handle": handle,
                "iwxxm_xml": _XML,
                "product": "metar",
                "dissemination_library_id": str(uuid4()),
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    assert send.status_code == 400
    assert "Unknown dissemination library" in send.text


def test_tc_evbridge_008_send_custom_dissem_lookup_paths(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Send Dissemination lookup: ValueError, soft Exception, and wrong kind."""
    uri = _sqlite_uri(tmp_path)
    pre = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "sqlite", "uri": uri, "ddl": True}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    handle = pre.json()["handle"]

    fake_svc = MagicMock()
    fake_svc.get_library_asset.side_effect = ValueError(
        "dissemination_library_id must reference a Dissemination library"
    )
    monkeypatch.setattr(
        "src.routers.dissemination.ConversionProfilesService",
        lambda *_a, **_k: fake_svc,
    )
    r1 = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "handle": handle,
                "iwxxm_xml": _XML,
                "product": "metar",
                "dissemination_library_id": str(uuid4()),
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert r1.status_code == 400
    assert "Dissemination library" in r1.text

    fake_svc.get_library_asset.side_effect = RuntimeError("db down")
    r2 = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "handle": handle,
                "iwxxm_xml": _XML,
                "product": "metar",
                "dissemination_library_id": str(uuid4()),
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert r2.status_code == 400
    assert "Unknown dissemination library" in r2.text

    wrong = MagicMock()
    wrong.kind = "conversion"
    wrong.body = {}
    fake_svc.get_library_asset.side_effect = None
    fake_svc.get_library_asset.return_value = wrong
    r3 = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "handle": handle,
                "iwxxm_xml": _XML,
                "product": "metar",
                "dissemination_library_id": str(uuid4()),
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert r3.status_code == 400
    assert "Dissemination library" in r3.text
