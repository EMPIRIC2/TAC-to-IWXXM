"""Coverage test for api.py top-level fallback imports.

This test executes api.py in a controlled stub environment where relative
imports fail, forcing the fallback absolute import block.
"""

from __future__ import annotations

import os
import runpy
import types


class _FakeHTTPException(Exception):
    def __init__(self, status_code=None, detail=None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class _FakeFastAPI:
    def __init__(self, *args, **kwargs):
        self.openapi_schema = None
        self.title = kwargs.get("title", "")
        self.version = kwargs.get("version", "")
        self.description = kwargs.get("description", "")
        self.routes = []
        self.openapi_tags = kwargs.get("openapi_tags", [])

    def add_middleware(self, *_args, **_kwargs):
        return None

    def middleware(self, *_args, **_kwargs):
        def _decorator(func):
            return func

        return _decorator

    def include_router(self, *_args, **_kwargs):
        return None

    def get(self, *_args, **_kwargs):
        def _decorator(func):
            return func

        return _decorator

    def post(self, *_args, **_kwargs):
        def _decorator(func):
            return func

        return _decorator


def _fake_dep(default=None, **_kwargs):
    return default


def _stub_module(name: str, **attrs):
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    return mod


def test_api_module_top_level_fallback_imports(monkeypatch):
    # Stub fastapi surface used during module import.
    fake_fastapi = _stub_module(
        "fastapi",
        Depends=_fake_dep,
        FastAPI=_FakeFastAPI,
        File=lambda *args, **kwargs: None,
        Form=lambda default=None, **_kwargs: default,
        HTTPException=_FakeHTTPException,
        Request=object,
        Response=object,
        UploadFile=object,
    )
    fake_fastapi_middleware = _stub_module("fastapi.middleware")
    fake_fastapi_cors = _stub_module("fastapi.middleware.cors", CORSMiddleware=object)
    fake_fastapi_responses = _stub_module(
        "fastapi.responses",
        Response=object,
        StreamingResponse=object,
    )

    # Stub fallback absolute import modules used by api.py.
    def extract_airport_code(_text):
        return "KJFK"

    def verify_supabase_token():
        return {"sub": "stub"}

    fake_config_icao = _stub_module(
        "config.icao_opmet",
        get_icao_region=lambda _icao: "EUR",
        get_translation_centre_info=lambda: {
            "translationCentreDesignator": "STUB",
            "translationCentreName": "Stub Centre",
            "icaoLocationIndicator": "ZZZZ",
        },
    )

    fake_validation_layer = types.SimpleNamespace(
        AIRPORT_ICAO="airport_icao",
        TAC_SYNTAX="tac_syntax",
        XML_WELLFORMED="xml_wellformed",
        XML_SCHEMA="xml_schema",
        SCHEMATRON="schematron",
        GML_REFERENCES="gml_references",
        WMO_CODELISTS="wmo_codelists",
    )

    class _StubModel:
        def __init__(self, *args, **kwargs):
            self.__dict__.update(kwargs)

        def model_dump(self):
            return self.__dict__

    fake_schemas_conversion = _stub_module(
        "schemas.conversion",
        ConversionIssue=_StubModel,
        ConversionIssueSeverity=types.SimpleNamespace(ERROR="error", WARNING="warning", INFO="info"),
        ConversionRequest=_StubModel,
        ConversionResponse=_StubModel,
        ConversionResult=_StubModel,
        ErrorDetail=_StubModel,
        FailedSpan=_StubModel,
        HealthResponse=_StubModel,
    )
    fake_schemas_icao = _stub_module(
        "schemas.icao_opmet",
        TranslationStatus=types.SimpleNamespace(SUCCESS="success", FAILED="failed"),
    )
    fake_schemas_validation = _stub_module(
        "schemas.validation",
        ValidateRequest=_StubModel,
        ValidateResponse=_StubModel,
        ValidationLayer=fake_validation_layer,
        BulletinMetaModel=_StubModel,
        BulletinReportResultModel=_StubModel,
        ConvertBulletinResponse=_StubModel,
        DecodeResidualModel=_StubModel,
        DecodeSegmentModel=_StubModel,
        DecodeTacResponse=_StubModel,
        LintTacResponse=_StubModel,
        LintIssueModel=_StubModel,
        LintFixModel=_StubModel,
        LintIssueCatalogEntryModel=_StubModel,
        LintIssueCatalogResponse=_StubModel,
    )

    fake_statistics_service = types.SimpleNamespace()
    fake_webhook_service = types.SimpleNamespace()

    fake_services_database = _stub_module("services.database", database_lifespan=lambda app: app)
    fake_services_statistics = _stub_module("services.statistics", statistics_service=fake_statistics_service)
    fake_services_validation = _stub_module(
        "services.validation",
        ValidationError=RuntimeError,
        ValidationService=type("ValidationService", (), {}),
    )
    fake_services_orchestrator = _stub_module(
        "services.validation_orchestrator", get_validation_orchestrator=lambda: None
    )
    fake_services_webhooks = _stub_module("services.webhooks", webhook_service=fake_webhook_service)

    fake_util_conversion = _stub_module(
        "utilities.conversion",
        ConversionError=RuntimeError,
        convert_metar_tac_with_metadata=lambda *args, **kwargs: ("<xml/>", None),
    )
    fake_util_iwxxm_pass_through = _stub_module(
        "utilities.iwxxm_pass_through",
        NOT_XML_CODE="NOT_XML",
        lint_iwxxm_pass_through=lambda _text: types.SimpleNamespace(ok=True, product="IWXXM", issues=[]),
    )
    fake_util_iwxxm_readable_decode = _stub_module(
        "utilities.iwxxm_readable_decode",
        decode_for_validate=lambda **_kwargs: types.SimpleNamespace(segments=[], summary=""),
    )
    fake_util_metar_normalizer = _stub_module(
        "utilities.metar_normalizer",
        normalize_recent_weather_tokens=lambda tac: (tac, []),
    )
    fake_util_observability = _stub_module(
        "utilities.observability",
        install_fastapi_observability=lambda **_kwargs: None,
        record_profile_wire_metrics=lambda *_args, **_kwargs: None,
        set_request_log_level=lambda *_args, **_kwargs: "INFO",
        setup_logging=lambda *_args, **_kwargs: None,
    )
    fake_util_profile_wire = _stub_module(
        "utilities.profile_wire",
        WireProfileSelection=type("WireProfileSelection", (), {}),
        resolve_route_profiles=lambda **_kwargs: types.SimpleNamespace(
            emit_key="annex3",
            semantic_canonical="icao_2025",
            deprecated_alias_used=False,
            exchange_profile=None,
        ),
    )
    fake_util_sentry = _stub_module(
        "utilities.sentry_init",
        init_sentry=lambda **_kwargs: None,
    )
    fake_util_abuse = _stub_module(
        "utilities.abuse_controls",
        install_abuse_controls=lambda *_a, **_k: None,
        get_limiter=lambda: None,
        dissemination_limit=lambda *_a, **_k: lambda f: f,
        public_limit=lambda *_a, **_k: lambda f: f,
    )
    fake_util_security = _stub_module("utilities.security", verify_supabase_token=verify_supabase_token)
    fake_util_tac = _stub_module("utilities.tac_parser", extract_airport_code=extract_airport_code)
    fake_util_extension_wire = _stub_module(
        "utilities.extension_wire",
        IWXXM_CA_TOKEN="IWXXM_CA",
        parse_extension_tokens=lambda values: list(values or []),
        validate_extension_tokens=lambda tokens: tokens,
        ca_eccc_validate_product=lambda emit_key, extensions, product: product,
    )
    fake_util_ca_exchange_wire = _stub_module(
        "utilities.ca_exchange_wire",
        apply_ca_eccc_collect_output=lambda xml, **_kwargs: xml,
        ca_eccc_output_spec_for_request=lambda **_kwargs: None,
    )

    fake_router_module = _stub_module("router_mod", router=object())
    fake_mass_ingest_router = _stub_module(
        "router_mod",
        router=object(),
        ingest_collect=lambda **_kwargs: None,
    )
    fake_health_router = _stub_module(
        "router_mod",
        router=object(),
        health=lambda: types.SimpleNamespace(status="healthy", version="0.1.0", tac2iwxxm_available=True),
    )
    fake_conversion_meta_router = _stub_module(
        "router_mod",
        router=object(),
        get_supported_versions=lambda: {
            "default_version": "2025-2",
            "supported_versions": [],
            "deprecated_versions": [],
        },
        get_schema_status=lambda: {
            "stable": [],
            "rc": [],
            "all": [],
            "default": "2025-2",
            "metadata": {},
            "profile_pins": {},
        },
    )
    fake_tac_quality_router = _stub_module(
        "router_mod",
        router=object(),
        lint_issue_catalog=lambda **_kwargs: types.SimpleNamespace(),
        lint_tac=lambda **_kwargs: types.SimpleNamespace(),
        decode_tac_endpoint=lambda **_kwargs: types.SimpleNamespace(),
    )
    fake_conversion_router = _stub_module(
        "router_mod",
        router=object(),
        convert_bulletin=lambda **_kwargs: None,
        convert=lambda **_kwargs: None,
        convert_zip=lambda **_kwargs: None,
    )
    fake_comprehensive_validation_router = _stub_module(
        "router_mod",
        router=object(),
        validate_comprehensive=lambda **_kwargs: None,
    )
    fake_routers = _stub_module(
        "routers",
        comprehensive_validation=fake_comprehensive_validation_router,
        conversion=fake_conversion_router,
        conversion_meta=fake_conversion_meta_router,
        conversion_profiles=fake_router_module,
        dissemination=fake_router_module,
        dissemination_ops=fake_router_module,
        evaluation=fake_router_module,
        health=fake_health_router,
        icao_opmet=fake_router_module,
        mass_ingest=fake_mass_ingest_router,
        quality_metrics=fake_router_module,
        tac_quality=fake_tac_quality_router,
        validation=fake_router_module,
        work_sessions=fake_router_module,
    )

    stubs = {
        "fastapi": fake_fastapi,
        "fastapi.middleware": fake_fastapi_middleware,
        "fastapi.middleware.cors": fake_fastapi_cors,
        "fastapi.responses": fake_fastapi_responses,
        "config": _stub_module("config"),
        "config.icao_opmet": fake_config_icao,
        "msgspec_http": _stub_module(
            "msgspec_http",
            msgspec_json_response=lambda obj, **_kwargs: obj,
        ),
        "api_wire": _stub_module(
            "api_wire",
            is_dev_cors_relaxation_enabled=lambda: False,
            add_origin_if_missing=lambda origins, origin: origins,
            add_loopback_origin_variants=lambda origins: origins,
            get_cors_origins=lambda: ["http://localhost:5173"],
            get_cors_allowed_headers=lambda: ["*"],
            _is_named_upload=lambda _f: False,
            parse_files=lambda files: files,
            normalize_api_product=lambda product, default=None: product or default,
            _coerce_form_list=lambda value: value,
            _coerce_form_str=lambda value: value,
            _resolve_request_extensions=lambda *_a, **_k: None,
            _package_issue_payload=lambda *_a, **_k: {},
            _package_stages_payload=lambda *_a, **_k: {},
            _resolve_request_profiles=lambda **_kwargs: types.SimpleNamespace(
                emit_key="annex3",
                semantic_canonical="icao_2025",
                deprecated_alias_used=False,
                exchange_profile=None,
            ),
            _is_multiline_template_product=lambda _p: False,
            split_manual_entries=lambda text: [text],
            manual_entries_with_offsets=lambda text: [(text, 0)],
            read_uploaded_text=lambda *_a, **_k: ("", None),
            read_upload_files_text=lambda *_a, **_k: ("", None),
            is_xml_input=lambda _t: False,
            classify_and_validate_upload_content=lambda *_a, **_k: None,
            normalize_code=lambda c: c,
            parse_optional_bulletin_id=lambda _v: None,
            parse_optional_issuing_center=lambda _v: None,
            normalize_validation_level=lambda v: v,
            _product_uses_metar_tac_layers=lambda _p: True,
            parse_optional_files=lambda files: files,
            bulletin_split_http_error=lambda *_a, **_k: None,
            MAX_BULLETIN_REPORTS=100,
            _call_iwxxm_validate=lambda *_a, **_k: None,
        ),
        "api_deps": _stub_module(
            "api_deps",
            ValidationService=type("ValidationService", (), {}),
            _call_iwxxm_validate=lambda *_a, **_k: None,
            classify_and_validate_upload_content=lambda *_a, **_k: None,
            convert_metar_tac_with_metadata=lambda *a, **k: ("<xml/>", None),
            get_icao_region=lambda _icao: "EUR",
            get_translation_centre_info=lambda: {},
            get_validation_orchestrator=lambda: None,
            iwxxm_validate_fn=lambda *a, **k: None,
            msgspec_json_response=lambda obj, **_kwargs: obj,
            read_upload_files_text=lambda *_a, **_k: ("", None),
            read_uploaded_text=lambda *_a, **_k: ("", None),
            statistics_service=fake_statistics_service,
            tac2iwxxm_split_bulletin=lambda *a, **k: None,
            webhook_service=fake_webhook_service,
        ),
        "routers": fake_routers,
        "schemas": _stub_module("schemas"),
        "schemas.conversion": fake_schemas_conversion,
        "schemas.icao_opmet": fake_schemas_icao,
        "schemas.validation": fake_schemas_validation,
        "services": _stub_module("services"),
        "services.database": fake_services_database,
        "services.statistics": fake_services_statistics,
        "services.validation": fake_services_validation,
        "services.validation_orchestrator": fake_services_orchestrator,
        "services.webhooks": fake_services_webhooks,
        "utilities": _stub_module("utilities"),
        "utilities.abuse_controls": fake_util_abuse,
        "utilities.conversion": fake_util_conversion,
        "utilities.iwxxm_pass_through": fake_util_iwxxm_pass_through,
        "utilities.iwxxm_readable_decode": fake_util_iwxxm_readable_decode,
        "utilities.metar_normalizer": fake_util_metar_normalizer,
        "utilities.observability": fake_util_observability,
        "utilities.profile_wire": fake_util_profile_wire,
        "utilities.sentry_init": fake_util_sentry,
        "utilities.security": fake_util_security,
        "utilities.tac_parser": fake_util_tac,
        "utilities.extension_wire": fake_util_extension_wire,
        "utilities.ca_exchange_wire": fake_util_ca_exchange_wire,
        "iwxxm_validate": _stub_module(
            "iwxxm_validate",
            validate=lambda *a, **k: None,
            validate_iwxxm=lambda *a, **k: None,
        ),
        "iwxxm_validate.models": _stub_module(
            "iwxxm_validate.models",
            ValidationReport=_StubModel,
        ),
        "tac2iwxxm": _stub_module(
            "tac2iwxxm",
            BulletinSplitError=Exception,
            decode_tac=lambda *a, **k: None,
            iwxxm_filename=lambda *a, **k: "stub.xml",
            parse_ahl=lambda *a, **k: None,
            split_bulletin=lambda *a, **k: None,
        ),
        "tac_validate": _stub_module("tac_validate", lint=lambda *a, **k: None),
        "tac_validate.issue_registry": _stub_module(
            "tac_validate.issue_registry",
            catalog_entries=lambda **_kwargs: (),
            ISSUES=(),
        ),
    }

    for name, module in stubs.items():
        monkeypatch.setitem(__import__("sys").modules, name, module)

    # Execute module with a non-package run name so relative imports fail,
    # forcing api.py into its fallback import block.
    api_path = os.path.join(os.path.dirname(__file__), "..", "..", "src", "api.py")
    result = runpy.run_path(
        api_path,
        run_name="api_fallback_cov",
    )

    assert "app" in result
    assert result["extract_airport_code"] is extract_airport_code
    assert "verify_supabase_token" not in result  # F21: JWT import removed from api.py
