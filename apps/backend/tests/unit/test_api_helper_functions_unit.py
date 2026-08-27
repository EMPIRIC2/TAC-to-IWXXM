"""Unit tests for helper functions in src.api."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from src import api as api_module
from starlette.responses import Response


@pytest.mark.parametrize("value", ["true", "1", "yes", "on", "TRUE"])
def test_is_dev_cors_relaxation_enabled_truthy(monkeypatch, value):
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", value)
    assert api_module.is_dev_cors_relaxation_enabled() is True


def test_get_cors_origins_from_env_with_relaxation_and_loopback(monkeypatch):
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)

    origins = api_module.get_cors_origins()

    assert "http://localhost:18000" in origins
    assert "http://127.0.0.1:18000" in origins
    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:5173" in origins


def test_get_cors_origins_deprecated_env_fallback(monkeypatch):
    monkeypatch.setenv("METAR_CONFIG_ENV", "missing-profile")
    monkeypatch.setenv("METAR_CORS_ORIGINS", "https://example.test")

    with pytest.warns(DeprecationWarning, match="METAR_CORS_ORIGINS"):
        origins = api_module.get_cors_origins()

    assert "https://example.test" in origins


def test_get_cors_origins_defaults(monkeypatch):
    monkeypatch.delenv("ENABLE_DEV_CORS_RELAXATION", raising=False)
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")

    origins = api_module.get_cors_origins()

    assert "http://localhost:18000" in origins
    assert "http://127.0.0.1:18000" in origins


def test_get_cors_allowed_headers_relaxed_and_default(monkeypatch):
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")
    assert api_module.get_cors_allowed_headers() == ["*"]

    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "false")
    assert api_module.get_cors_allowed_headers() == ["Authorization", "Content-Type"]


def test_split_manual_entries_and_normalizers():
    entries = api_module.split_manual_entries("\nMETAR KJFK\n\nSPECI KLAX\n")
    assert entries == ["METAR KJFK", "SPECI KLAX"]

    with_offsets = api_module.manual_entries_with_offsets("\nMETAR KJFK\n\nSPECI KLAX\n")
    assert [e for e, _ in with_offsets] == entries
    assert with_offsets[0][1] == 1  # leading newline
    assert with_offsets[1][1] == len("\nMETAR KJFK\n\n")

    vaa = "VA ADVISORY\nDTG: 20240923/0130Z\nVAAC: TOKYO\n"
    assert api_module.split_manual_entries(vaa, product="VAA") == [vaa.strip()]
    vaa_off = api_module.manual_entries_with_offsets("\n" + vaa, product="VAA")
    assert len(vaa_off) == 1
    assert vaa_off[0][0] == vaa.strip()
    assert vaa_off[0][1] == 1

    tca = "TC ADVISORY\nDTG: 20040925/1900Z\n"
    assert api_module.split_manual_entries(tca, product="TCA") == [tca.strip()]

    sigmet = (
        "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
        "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=\n"
    )
    assert api_module.split_manual_entries(sigmet, product="SIGMET") == [sigmet.strip()]
    sig_off = api_module.manual_entries_with_offsets(sigmet, product="SIGMET")
    assert len(sig_off) == 1
    assert "SHANLON" in sig_off[0][0]

    assert api_module.normalize_code(" kjfk ", 4) == "KJFK"
    assert api_module.normalize_code("", 4) is None
    assert api_module.normalize_validation_level("icao-opmet") == "icao_opmet"
    assert api_module.normalize_validation_level("unknown") == "basic"


def test_is_xml_input_by_filename_or_payload():
    assert api_module.is_xml_input("report.xml", "METAR TEST") is True
    assert api_module.is_xml_input("report.txt", "   <iwxxm:METAR/>") is True
    assert api_module.is_xml_input("report.txt", "METAR KJFK") is False


def test_classify_and_validate_upload_content_non_xml_returns_none():
    result = api_module.classify_and_validate_upload_content(
        filename="report.txt",
        content="METAR KJFK 010000Z 00000KT CAVOK",
        iwxxm_version="2025-2",
        endpoint_path="/api/v1/convert",
        validation_orchestrator=None,
    )
    assert result is None


def test_classify_and_validate_upload_content_validation_unavailable():
    result = api_module.classify_and_validate_upload_content(
        filename="report.xml",
        content="<iwxxm:METAR/>",
        iwxxm_version="2025-2",
        endpoint_path="/api/v1/convert",
        validation_orchestrator=None,
    )
    assert result["code"] == "XML_VALIDATION_UNAVAILABLE"


def test_classify_and_validate_upload_content_not_wellformed():
    orchestrator = SimpleNamespace(
        validate_wellformed=lambda _xml: SimpleNamespace(
            passed=False,
            issues=[SimpleNamespace(message="bad xml")],
        )
    )

    result = api_module.classify_and_validate_upload_content(
        filename="report.xml",
        content="<iwxxm:METAR>",
        iwxxm_version="2025-2",
        endpoint_path="/api/v1/convert",
        validation_orchestrator=orchestrator,
    )
    assert result["code"] == "XML_NOT_WELLFORMED"


def test_classify_and_validate_upload_content_schema_error():
    orchestrator = SimpleNamespace(
        validate_wellformed=lambda _xml: SimpleNamespace(passed=True, issues=[]),
        validate_xml_schema=lambda _xml, _version: SimpleNamespace(
            is_valid=False,
            issues=[SimpleNamespace(level="ERROR", message="schema fail")],
        ),
    )

    result = api_module.classify_and_validate_upload_content(
        filename="report.xml",
        content="<iwxxm:METAR/>",
        iwxxm_version="2025-2",
        endpoint_path="/api/v1/convert",
        validation_orchestrator=orchestrator,
    )
    assert result["code"] == "XML_SCHEMA_VALIDATION_FAILED"


def test_classify_and_validate_upload_content_valid_xml_but_tac_only():
    orchestrator = SimpleNamespace(
        validate_wellformed=lambda _xml: SimpleNamespace(passed=True, issues=[]),
        validate_xml_schema=lambda _xml, _version: SimpleNamespace(is_valid=True, issues=[]),
    )

    result = api_module.classify_and_validate_upload_content(
        filename="report.xml",
        content="<iwxxm:METAR/>",
        iwxxm_version="2025-2",
        endpoint_path="/api/v1/convert",
        validation_orchestrator=orchestrator,
    )
    assert result["code"] == "XML_INPUT_NOT_CONVERTIBLE"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", False),
        (None, False),
        (123, False),
        (SimpleNamespace(filename=""), False),
        (SimpleNamespace(filename="valid.txt"), True),
    ],
)
def test_is_named_upload(value, expected):
    assert api_module._is_named_upload(value) is expected


@pytest.mark.asyncio
async def test_parse_files_wraps_form_parse_error():
    class _BadRequest:
        async def form(self):
            raise RuntimeError("bad multipart payload")

    with pytest.raises(api_module.HTTPException) as exc:
        await api_module.parse_files(_BadRequest())

    assert exc.value.status_code == 400
    assert exc.value.detail["issues"][0]["code"] == "INVALID_MULTIPART_PAYLOAD"


@pytest.mark.asyncio
async def test_parse_files_filters_non_file_and_empty_filename_entries():
    class _Upload:
        def __init__(self, filename: str):
            self.filename = filename

    class _Form:
        def multi_items(self):
            return [
                ("other", _Upload("ignored.txt")),
                ("files", ""),
                ("files", _Upload("")),
                ("files", _Upload("valid.txt")),
            ]

    class _Req:
        async def form(self):
            return _Form()

    files = await api_module.parse_files(_Req())
    assert len(files) == 1
    assert files[0].filename == "valid.txt"


def test_custom_openapi_has_no_bearer_auth_and_caches():
    original = api_module.app.openapi_schema
    try:
        api_module.app.openapi_schema = None
        schema = api_module.custom_openapi()
        schemes = schema.get("components", {}).get("securitySchemes")
        assert not schemes

        # Cached branch should return same object without regenerating.
        cached = api_module.custom_openapi()
        assert cached is schema
    finally:
        api_module.app.openapi_schema = original


@pytest.mark.asyncio
async def test_add_translation_centre_headers_sets_known_headers(monkeypatch):
    monkeypatch.setattr(
        api_module,
        "get_translation_centre_info",
        lambda: {
            "translationCentreDesignator": "NOAA-MDL",
            "translationCentreName": "NOAA Test Centre",
            "icaoLocationIndicator": "KWBC",
        },
    )

    async def _next(_request):
        return Response("ok")

    response = await api_module.add_translation_centre_headers(object(), _next)
    assert response.headers["X-Translation-Centre"] == "NOAA-MDL"
    assert response.headers["X-Translation-Centre-Name"] == "NOAA Test Centre"
    assert response.headers["X-ICAO-Location-Indicator"] == "KWBC"


@pytest.mark.asyncio
async def test_add_translation_centre_headers_tolerates_config_exception(monkeypatch):
    monkeypatch.setattr(
        api_module, "get_translation_centre_info", lambda: (_ for _ in ()).throw(RuntimeError("no config"))
    )

    async def _next(_request):
        return Response("ok")

    response = await api_module.add_translation_centre_headers(object(), _next)
    assert response.status_code == 200
