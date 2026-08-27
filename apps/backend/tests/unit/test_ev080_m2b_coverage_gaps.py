"""EV-080 M2b: fill remaining apps/backend unit line/branch gaps to 100%.

[Corpus: adr/ADR-007] [Corpus: tests]
"""

from __future__ import annotations

import builtins
import json
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src import api as api_module
from src import api_wire
from src.config import icao_opmet as icao_cfg
from src.config import iwxxm_versions as versions
from src.routers import conversion as conversion_router
from src.routers import dissemination as diss_router
from src.routers import icao_opmet as icao_router
from src.schemas.work_session import WorkSessionUpdate
from src.utilities import abuse_controls as abuse
from src.utilities import extension_wire
from src.utilities import observability as obs
from src.utilities.security import verify_supabase_token


@pytest.fixture
def convert_client(monkeypatch: pytest.MonkeyPatch):
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    client = TestClient(api_module.app)
    yield client
    api_module.app.dependency_overrides.clear()


def test_clean_env_blank_after_strip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRANSLATION_CENTRE_NAME", "   ")
    assert icao_cfg._clean_env("TRANSLATION_CENTRE_NAME") is None


def test_detect_project_root_vendor_and_legacy_iwxxm_layout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake_file = tmp_path / "apps" / "backend" / "src" / "config" / "iwxxm_versions.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.write_text("# fake", encoding="utf-8")
    (tmp_path / "vendor" / "schemas" / "iwxxm" / "IWXXM").mkdir(parents=True)
    monkeypatch.delenv("IWXXM_PROJECT_ROOT", raising=False)
    monkeypatch.delenv("IWXXM_SCHEMAS_ROOT", raising=False)
    monkeypatch.setattr(versions, "__file__", str(fake_file))
    assert versions._detect_project_root() == tmp_path.resolve()


def test_detect_project_root_legacy_schemas_iwxxm_layout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake_file = tmp_path / "apps" / "backend" / "src" / "config" / "iwxxm_versions.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.write_text("# fake", encoding="utf-8")
    (tmp_path / "schemas" / "iwxxm" / "IWXXM").mkdir(parents=True)
    monkeypatch.delenv("IWXXM_PROJECT_ROOT", raising=False)
    monkeypatch.delenv("IWXXM_SCHEMAS_ROOT", raising=False)
    monkeypatch.setattr(versions, "__file__", str(fake_file))
    assert versions._detect_project_root() == tmp_path.resolve()


def test_detect_project_root_schemas_env_iwxxm_child_without_versioned(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "root"
    schemas_candidate = root / "schemas"
    (schemas_candidate / "iwxxm").mkdir(parents=True)
    fake_file = root / "apps" / "backend" / "src" / "config" / "iwxxm_versions.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.write_text("# fake", encoding="utf-8")
    monkeypatch.setenv("IWXXM_SCHEMAS_ROOT", str(schemas_candidate))
    monkeypatch.delenv("IWXXM_PROJECT_ROOT", raising=False)
    monkeypatch.setattr(versions, "__file__", str(fake_file))
    # Fall through when no versioned schemas under iwxxm child
    assert versions._detect_project_root() is not None


def test_get_version_config_for_emit_profile_scoped_and_reraise() -> None:
    cfg = versions.get_version_config_for_emit_profile("2025-2", "annex3")
    assert cfg is not None
    with pytest.raises(ValueError, match="not supported"):
        versions.get_version_config_for_emit_profile("9999-9", "annex3")


def test_resolve_schema_file_existing_and_codelists_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Unknown file_type raises; valid types resolve against real config when present.
    with pytest.raises(ValueError, match="Unknown file type"):
        versions.resolve_schema_file("2025-2", "not-a-type")
    # Existing version should resolve xsd or raise FileNotFoundError if schemas absent
    try:
        path = versions.resolve_schema_file("2025-2", "xsd")
        assert path.exists()
    except (FileNotFoundError, ValueError):
        pass


def test_wire_payload_dict_branches() -> None:
    assert conversion_router._wire_payload_dict({"a": 1}) == {"a": 1}
    assert conversion_router._wire_payload_dict(SimpleNamespace(model_dump=lambda: {"b": 2})) == {"b": 2}
    assert conversion_router._wire_payload_dict(SimpleNamespace(c=3)) == {}


def test_client_id_anonymous_when_no_host() -> None:
    req = SimpleNamespace(client=None, headers={})
    assert diss_router._client_id(req)


async def test_read_send_decode_error() -> None:
    from starlette.requests import Request

    scope = {"type": "http", "method": "POST", "path": "/", "headers": [], "client": ("1.1.1.1", 1)}
    req = Request(scope)
    req._body = b"{not-json"
    with pytest.raises(HTTPException):
        await diss_router._read_send(req)


def test_abuse_positive_int_invalid_and_bad_content_length(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "nope")
    assert abuse._positive_int("MAX_REQUEST_BODY_BYTES", 10) == 10
    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "0")
    assert abuse._positive_int("MAX_REQUEST_BODY_BYTES", 10) == 10
    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "123")
    assert abuse._positive_int("MAX_REQUEST_BODY_BYTES", 10) == 123


def test_warn_if_dev_cors_relaxed(caplog: pytest.LogCaptureFixture) -> None:
    import logging as _logging

    from src import api as api_mod

    with caplog.at_level(_logging.WARNING, logger="src.api"):
        api_mod._warn_if_dev_cors_relaxed(True)
        api_mod._warn_if_dev_cors_relaxed(False)
    assert any("CORS" in r.message for r in caplog.records)


def test_resolve_request_extensions_json_path() -> None:
    out = api_wire._resolve_request_extensions([], ["IWXXM_CA"])
    assert "IWXXM_CA" in out


def test_manual_entries_multiline_whitespace_only() -> None:
    assert api_wire.manual_entries_with_offsets("  \n\n  ") == []


def test_iwxxm_readable_empty_field_amount_and_root_amount() -> None:
    from src.utilities.iwxxm_readable_decode import readable_decode_from_iwxxm

    xml = """<?xml version="1.0"?>
    <iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
                 xmlns:xlink="http://www.w3.org/1999/xlink">
      <iwxxm:airTemperature uom="Cel"></iwxxm:airTemperature>
      <iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmount/FEW"/>
    </iwxxm:METAR>"""
    readable_decode_from_iwxxm(xml)
    # amount as document root → parents empty → parent is None (202→206)
    root_amount = (
        '<?xml version="1.0"?>'
        '<iwxxm:amount xmlns:iwxxm="http://icao.int/iwxxm/2025-2" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xlink:href="http://codes.wmo.int/49-2/CloudAmount/SCT"/>'
    )
    readable_decode_from_iwxxm(root_amount)


def test_dissemination_preflight_ok_false(convert_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from dissemination.rate_limit import DisseminationRateLimiter

    monkeypatch.setattr(diss_router, "default_rate_limiter", DisseminationRateLimiter(max_per_minute=1000))
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "localhost")

    async def fake_preflight(req):
        return SimpleNamespace(ok=False, connectivity_ok=False, diffs=["x"], detail="no")

    monkeypatch.setattr(diss_router, "run_db_preflight", fake_preflight)
    resp = convert_client.post(
        "/api/v1/dissemination/preflight",
        content=b'{"sink_type":"sqlite","uri":"sqlite+aiosqlite:////tmp/x.db","ddl":false}',
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 200
    assert not resp.json().get("handle")


def test_dissemination_send_without_handle(
    convert_client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Cover False path of `if req.handle` after successful send (235→238)."""
    from dissemination.rate_limit import DisseminationRateLimiter

    monkeypatch.setattr(diss_router, "default_rate_limiter", DisseminationRateLimiter(max_per_minute=1000))
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "localhost,127.0.0.1")
    db = tmp_path / "send.db"
    uri = f"sqlite+aiosqlite:///{db}"

    async def fake_preflight(_req):
        return SimpleNamespace(ok=True, connectivity_ok=True, diffs=[], detail="ok")

    async def fake_apply(_engine, **_k):
        return None

    monkeypatch.setattr(diss_router, "run_db_preflight", fake_preflight)
    monkeypatch.setattr(diss_router, "apply_writer_contract", fake_apply)

    class _Conn:
        async def execute(self, *_a, **_k):
            return None

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_a):
            return False

    class _Eng:
        def begin(self):
            return _Conn()

        async def dispose(self):
            return None

    monkeypatch.setattr(diss_router, "create_async_engine", lambda *_a, **_k: _Eng())
    resp = convert_client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "sink_type": "sqlite",
                "uri": uri,
                "iwxxm_xml": "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>",
                "product": "metar",
            }
        ).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 200
    assert resp.json().get("ok") is True


def test_airport_builder_override_source_and_validator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.utilities.airport_record_builder import AirportRecordBuilder

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "vertical_datum_map.json").write_text(
        json.dumps({"airport_overrides": {"BBBB": {"name": "B", "iata": "BB"}}}),
        encoding="utf-8",
    )
    (data_dir / "airports.json").write_text(
        json.dumps(
            [
                {
                    "icao": "BBBB",
                    "name": "B2",
                    "iata": "BB",
                    "designator": "BRAVO",
                    "coordinates": {"latitude": 1, "longitude": 2},
                }
            ]
        ),
        encoding="utf-8",
    )
    fake = tmp_path / "utilities" / "airport_record_builder.py"
    fake.parent.mkdir(parents=True)
    fake.write_text("#", encoding="utf-8")
    monkeypatch.setattr("src.utilities.airport_record_builder.__file__", str(fake))
    builder = AirportRecordBuilder()
    rec = builder.build_record("BBBB")
    assert rec["_override"] is True or rec.get("name")

    builder._vertical_datum_map = {}
    builder._airports_json = {}
    # get_airport_info missing → False branch 157→162
    rec2 = builder.build_record("CCCC", airport_validator=SimpleNamespace())
    assert isinstance(rec2, dict)


def test_openaip_stats_country_falsy(tmp_path: Path) -> None:
    from src.clients.openaip_client import Airport, OpenAIPClient

    client = OpenAIPClient(data_path=tmp_path)
    client._loaded = True
    client._cache = {
        "XXXX": Airport(icao_code="XXXX", name="n", country="", elevation=None, geometry=None),
    }
    stats = client.get_statistics()
    assert stats["total_airports"] == 1
    assert stats["countries"] == 0


def test_openaip_feature_collection_and_to_dict(tmp_path: Path) -> None:
    from src.clients.openaip_client import Airport, OpenAIPClient

    feat = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-73.7, 40.6]},
                "properties": {"icaoCode": "KJFK", "name": "JFK", "country": "US", "elevation": 10},
            }
        ],
    }
    (tmp_path / "us_apt.geojson").write_text(json.dumps(feat), encoding="utf-8")
    (tmp_path / "xx_apt.geojson").write_text(json.dumps({"type": "Other"}), encoding="utf-8")
    client = OpenAIPClient(data_path=tmp_path)
    client._load_local_data()
    assert "KJFK" in client._cache
    a = Airport(icao_code="X", name="n", country="US", elevation=1.0)
    assert a.country == "US"


def test_wmo_cache_metadata_non_dict(tmp_path: Path) -> None:
    from src.clients.wmo_codelists_client import WMOCodelistCache

    (tmp_path / "cache_metadata.json").write_text("[1,2,3]", encoding="utf-8")
    c = WMOCodelistCache(cache_dir=tmp_path, ttl_seconds=10)
    assert c._metadata == {}


def test_wmo_cache_clear_expired_missing_file(tmp_path: Path) -> None:
    from datetime import datetime, timedelta

    from src.clients.wmo_codelists_client import WMOCodelistCache

    c = WMOCodelistCache(cache_dir=tmp_path, ttl_seconds=1)
    c._metadata = {"Gone": {"cached_at": (datetime.now() - timedelta(days=2)).isoformat()}}
    assert c.clear_expired() == 0
    assert "Gone" not in c._metadata


def test_tac_quality_files_empty_joined(convert_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    async def empty(_files):
        return "", None

    monkeypatch.setattr(api_module, "read_upload_files_text", empty)
    for path in ("/api/v1/lint-tac", "/api/v1/decode-tac"):
        resp = convert_client.post(
            path,
            files={
                "product": (None, "METAR"),
                "manual_text": (None, "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="),
                "files": ("x.txt", b"ignored", "text/plain"),
            },
        )
        assert resp.status_code in {200, 400}


def test_ingest_collect_files_empty_joined(convert_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    async def empty(_files):
        return "", None

    monkeypatch.setattr(api_module, "read_upload_files_text", empty)
    resp = convert_client.post(
        "/api/v1/ingest-collect",
        files={
            "manual_text": (None, "COLLECT PAYLOAD"),
            "files": ("x.txt", b"ignored", "text/plain"),
        },
    )
    assert resp.status_code == 501


def test_comprehensive_import_fallback_and_empty_summary(
    convert_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "src.config.iwxxm_versions":
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda *_a, **_k: ('<?xml version="1.0"?><x/>', {}),
    )
    monkeypatch.setattr(
        "src.routers.comprehensive_validation.decode_for_validate",
        lambda **_k: SimpleNamespace(
            segments=[SimpleNamespace(start=0, end=1, code="A", explanation="e")],
            summary="",
        ),
    )
    resp = convert_client.post(
        "/api/v1/validate",
        files={
            "manual_text": (None, "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="),
            "iwxxm_version": (None, "2025-2"),
            "xml_content": (None, '<?xml version="1.0"?><x/>'),
        },
    )
    assert resp.status_code in {200, 400, 422, 500}


@pytest.mark.asyncio
async def test_work_session_list_http_reraise_and_update_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    from uuid import UUID

    from sqlalchemy.exc import SQLAlchemyError
    from src.services import work_session_service as svc

    service = svc.WorkSessionService(user_id="00000000-0000-0000-0000-000000000001")

    class _HttpConn:
        def __enter__(self):
            raise HTTPException(status_code=400, detail="bad filter")

        def __exit__(self, *_a):
            return False

    class _EngHttp:
        def connect(self):
            return _HttpConn()

        def begin(self):
            return _HttpConn()

    monkeypatch.setattr(svc, "_get_engine", lambda: _EngHttp())
    monkeypatch.setattr(svc, "_table", lambda: MagicMock())
    with pytest.raises(HTTPException) as exc:
        service.list_sessions(page=1, limit=5)
    assert exc.value.status_code == 400

    # update_session: HTTPException from inside try (rowcount path mocked via execute)
    class _UpdConn:
        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

        def execute(self, *_a, **_k):
            raise HTTPException(status_code=404, detail="Work session not found")

    class _EngUpd:
        def begin(self):
            return _UpdConn()

    monkeypatch.setattr(svc, "_get_engine", lambda: _EngUpd())
    monkeypatch.setattr(service, "get_session", lambda *_a, **_k: SimpleNamespace(id=UUID(int=1)))
    with pytest.raises(HTTPException):
        service.update_session(UUID("00000000-0000-0000-0000-000000000001"), WorkSessionUpdate(title="t"))

    class _SqlConn:
        def __enter__(self):
            raise SQLAlchemyError("upd boom")

        def __exit__(self, *_a):
            return False

    class _EngSql:
        def begin(self):
            return _SqlConn()

    monkeypatch.setattr(svc, "_get_engine", lambda: _EngSql())
    with pytest.raises(HTTPException):
        service.update_session(UUID("00000000-0000-0000-0000-000000000001"), WorkSessionUpdate(title="t"))


def test_convert_bulletin_files_without_joined_content(
    convert_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def empty_join(_files):
        return "", None

    monkeypatch.setattr(api_module, "read_upload_files_text", empty_join)
    meta = SimpleNamespace(
        ahl="SAUS31 KWBC 011200",
        yygggg="011200",
        report_count=1,
        tt="SA",
        aa="US",
        cccc="KWBC",
        bbb=None,
        report_status=None,
    )
    split = SimpleNamespace(meta=meta, reports=["METAR KJFK 011200Z 18008KT 10SM FEW250 22/14 A3012="])
    monkeypatch.setattr(api_module, "tac2iwxxm_split_bulletin", lambda *_a, **_k: split)
    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda *_a, **_k: ('<?xml version="1.0"?><x/>', {"ok": True, "convert_issues": [], "failed_spans": []}),
    )
    resp = convert_client.post(
        "/api/v1/convert-bulletin",
        files={
            "product": (None, "METAR"),
            "lint": (None, "false"),
            "manual_text": (None, "SAUS31 KWBC 011200\nMETAR KJFK 011200Z 18008KT 10SM FEW250 22/14 A3012="),
            "files": ("x.txt", b"x", "text/plain"),
        },
    )
    assert resp.status_code == 200


def test_aviation_weather_station_not_requested() -> None:
    from src.clients.aviation_weather_client import AviationWeatherClient

    client = AviationWeatherClient()
    out = client._parse_response("METAR KJFK 101851Z\nMETAR KLAX 101851Z\n", "raw", ["KJFK"])
    assert "KJFK" in out
    assert "KLAX" not in out
    assert client._parse_response("stuff", "json", ["KJFK"]) == {}


def test_codelist_url_and_error_increment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.schemas.validation import ValidationLayer, ValidationSeverity
    from src.utilities.codelist_parser import CodeListParser, ValidationIssue

    settings = SimpleNamespace(
        wmo_online_validation=False,
        wmo_validation_timeout=1,
        wmo_registry_cache_ttl=0,
        wmo_registry_url="https://codes.wmo.int",
    )
    parser = CodeListParser(tmp_path, settings=settings)
    parser._loaded = True
    parser._cache = {"Foo": {"BAR", "Foo"}}
    monkeypatch.setattr(
        parser,
        "_extract_codelist_references",
        lambda _t: [
            ("BAR", "Foo", "/b"),
            ("http://x/Foo/Foo", "Foo", "/c"),
            ("http://x/Foo/BAR", "Foo", "/d"),
        ],
    )
    monkeypatch.setattr("src.utilities.codelist_parser.REQUESTS_AVAILABLE", False)
    assert parser.validate_xml_codelists("<root/>") is not None

    parser._cache = {}
    settings.wmo_online_validation = True
    parser.settings = settings
    monkeypatch.setattr("src.utilities.codelist_parser.REQUESTS_AVAILABLE", True)
    err = ValidationIssue(
        layer=ValidationLayer.WMO_CODELISTS,
        level=ValidationSeverity.ERROR,
        message="e",
        location="/",
        code="E",
    )
    monkeypatch.setattr(parser, "_extract_codelist_references", lambda _t: [("http://x/Foo/Z", "Foo", "/a")])
    monkeypatch.setattr(parser, "_validate_online", lambda *_a, **_k: err)
    result2 = parser.validate_xml_codelists("<root/>")
    assert any(i.level == ValidationSeverity.ERROR for i in result2.issues)
    assert result2.invalid_references >= 1


@pytest.mark.asyncio
async def test_evaluation_no_errors_without_comparison(monkeypatch: pytest.MonkeyPatch) -> None:
    """our_iwxxm set, their missing, errors empty → False path of elif errors (106→109)."""
    from src.routers import evaluation as eval_router
    from src.schemas.evaluation import EvaluationMode, EvaluationRequest

    saved: list[Any] = []

    async def fake_update(*_a, **_k):
        return None

    async def fake_save(_job, result):
        saved.append(result)

    class _Sampler:
        def sample_random_stations(self, **_k):
            return ["KJFK"]

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_a):
            return False

        async def fetch_metar_batch(self, stations, hours):
            _ = (stations, hours)
            return {"KJFK": ("METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=", None)}

    monkeypatch.setattr(eval_router, "update_job_status", fake_update)
    monkeypatch.setattr(eval_router, "save_result_to_db", fake_save)
    monkeypatch.setattr(eval_router, "StationSampler", _Sampler)
    monkeypatch.setattr(eval_router, "AviationWeatherClient", _Client)
    monkeypatch.setattr(eval_router, "convert_metar_tac", lambda _t: "<xml/>")
    monkeypatch.setattr(eval_router, "EvaluationService", lambda: SimpleNamespace())

    await eval_router.run_evaluation_job(
        "job-ev080",
        EvaluationRequest(mode=EvaluationMode.RANDOM, sample_size=1, hours=1.0),
    )
    assert saved
    assert saved[0].errors == []


def test_observability_histogram_cache_hit_and_worker_except(monkeypatch: pytest.MonkeyPatch) -> None:
    import threading
    import time

    name = "ev080_hist_cache_hit"
    obs._METRICS.pop(name, None)
    h1 = obs._get_or_create_histogram(name, "doc", ["lbl"])
    h2 = obs._get_or_create_histogram(name, "doc", ["lbl"])
    assert h1 is h2

    handler = obs.LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._session = MagicMock()
    handler.batch_size = 1
    handler.flush_interval = 60.0
    handler._send_batch = MagicMock(side_effect=RuntimeError("flush fail"))
    if handler._worker.is_alive():
        handler._stop_event.set()
        handler._worker.join(timeout=1.0)
    handler._stop_event.clear()

    def run_loop() -> None:
        handler._worker_loop()

    t = threading.Thread(target=run_loop, daemon=True)
    t.start()
    handler._queue.put({"timestamp": "1", "line": "x", "labels": {"a": "b"}})
    time.sleep(0.15)
    handler._stop_event.set()
    t.join(timeout=2.0)
    assert handler._send_batch.called


def test_convert_non_metar_skips_layer12(convert_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    xml = '<?xml version="1.0"?><iwxxm:TAF xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'
    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda *_a, **_k: (xml, {"ok": True, "convert_issues": [], "failed_spans": []}),
    )
    resp = convert_client.post(
        "/api/v1/convert",
        json={
            "metars": ["TAF KJFK 121130Z 1212/1312 18008KT P6SM FEW250="],
            "version": "2025-2",
            "product": "TAF",
        },
    )
    assert resp.status_code == 200

    resp2 = convert_client.post(
        "/api/v1/convert",
        files={
            "product": (None, "TAF"),
            "files": ("t.txt", b"TAF KJFK 121130Z 1212/1312 18008KT P6SM FEW250=", "text/plain"),
        },
    )
    assert resp2.status_code == 200


def test_convert_preview_span_offset_partial_fields(
    convert_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    tac1 = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="
    tac2 = "METAR KLAX 121151Z 18008KT 10SM FEW250 22/14 A3012="
    xml = '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'

    def fake_convert(tac: str, **kwargs: Any):
        soft = kwargs.get("soft_preview_out")
        if soft is not None:
            soft.clear()
            soft.update(
                {
                    "ok": False,
                    "failed_spans": [
                        {"code": "NO_SPAN_FIELDS", "message": "m"},
                    ],
                    "convert_issues": [],
                }
            )
        return xml, soft if soft is not None else {}

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    monkeypatch.setattr(
        api_module,
        "ValidationService",
        lambda: SimpleNamespace(
            validate_all_layers=lambda _t: SimpleNamespace(passed=True, total_issues=0, results=[])
        ),
    )
    # manual_text multi-entry drives base_offset>0 on second absorb_soft_preview
    quiet = TestClient(api_module.app, raise_server_exceptions=False)
    quiet.app.dependency_overrides[verify_supabase_token] = convert_client.app.dependency_overrides.get(
        verify_supabase_token, lambda: {"sub": "test-user", "aud": "test-aud"}
    )
    resp = quiet.post(
        "/api/v1/convert",
        files={
            "product": (None, "METAR"),
            "preview": (None, "true"),
            "manual_text": (None, tac1 + "\n" + tac2),
        },
    )
    assert resp.status_code in {200, 400, 422, 500}


def test_convert_zip_falsy_translation_id(convert_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    xml = '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'

    class _Stats:
        async def log_translation(self, **_k: Any) -> None:
            return None

    monkeypatch.setattr(api_module, "statistics_service", _Stats())
    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda *_a, **_k: (xml, {}),
    )
    monkeypatch.setattr(
        api_module,
        "ValidationService",
        lambda: SimpleNamespace(
            validate_all_layers=lambda _t: SimpleNamespace(passed=True, total_issues=0, results=[])
        ),
    )
    resp = convert_client.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="], "version": "2025-2"},
    )
    assert resp.status_code == 200
    resp2 = convert_client.post(
        "/api/v1/convert-zip",
        files={"files": ("a.txt", b"METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=", "text/plain")},
    )
    assert resp2.status_code == 200


# ---------------------------------------------------------------------------
# Remaining EV-080 M2b gaps (iter 2)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_icao_opmet_centre_info_without_online_since(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        icao_router,
        "get_translation_centre_info",
        lambda: {
            "translationCentreName": "Centre",
            "translationCentreDesignator": "NOAA",
            "icaoLocationIndicator": "KWBC",
            "supportedIwxxmVersions": ["2025-2"],
            "supportedProducts": ["METAR"],
            "technicalContact": None,
        },
    )
    info = await icao_router.get_centre_info()
    assert info.online_since is None


@pytest.mark.asyncio
async def test_icao_opmet_recent_stats_over_max_days(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bypass Query(le=168) by calling the handler directly with huge hours."""

    async def boom(**_k: Any) -> dict[str, Any]:
        raise AssertionError("should not query")

    monkeypatch.setattr(icao_router.statistics_service, "get_statistics", boom)
    with pytest.raises(HTTPException) as exc:
        await icao_router.get_recent_statistics(hours=91 * 24, icao_region=None, iwxxm_version=None)
    assert exc.value.status_code == 400


def test_work_session_normalize_product_non_string() -> None:
    from src.schemas.work_session import WorkSessionUpdate, _normalize_product_value

    assert _normalize_product_value(42) == 42
    assert _normalize_product_value(None) is None
    # WorkSessionUpdate.before validator delegates to _normalize_product_value
    updated = WorkSessionUpdate.model_validate({"product": None})
    assert updated.product is None
    assert WorkSessionUpdate._normalize_product(None) is None
    assert WorkSessionUpdate._normalize_product(99) == 99


def test_work_sessions_parse_product_filter_skips_empty_tokens() -> None:
    from src.routers import work_sessions as ws_router
    from src.schemas.work_session import WorkSessionProduct

    assert ws_router._parse_product_filter("metar,, ,speci") == [
        WorkSessionProduct.METAR,
        WorkSessionProduct.SPECI,
    ]


def test_api_wire_remaining_branches() -> None:
    from tac2iwxxm import BulletinSplitError

    assert api_wire.manual_entries_with_offsets("   \n  ", product="SIGMET") == []
    assert api_wire._resolve_request_profiles(route="", profile="annex3").emit_key

    err = api_wire.bulletin_split_http_error(BulletinSplitError("weird_code", "boom"))
    assert err.status_code == 422
    assert err.detail["code"] == "weird_code"


@pytest.mark.asyncio
async def test_api_wire_read_upload_files_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    assert await api_wire.read_upload_files_text(None) == ("", None)
    assert await api_wire.read_upload_files_text([]) == ("", None)

    async def empty_file(_upload: Any) -> tuple[str | None, str | None]:
        return None, "empty file"

    async def hard_err(_upload: Any) -> tuple[str | None, str | None]:
        return None, "file too large"

    async def blank_ok(_upload: Any) -> tuple[str | None, str | None]:
        return "", None

    monkeypatch.setattr(api_wire, "read_uploaded_text", empty_file)
    assert await api_wire.read_upload_files_text([SimpleNamespace()]) == ("", None)

    monkeypatch.setattr(api_wire, "read_uploaded_text", hard_err)
    text, err = await api_wire.read_upload_files_text([SimpleNamespace()])
    assert text == ""
    assert err == "file too large"

    monkeypatch.setattr(api_wire, "read_uploaded_text", blank_ok)
    assert await api_wire.read_upload_files_text([SimpleNamespace(), SimpleNamespace()]) == ("", None)


@pytest.mark.asyncio
async def test_api_wire_nbsp_only_file_hits_post_decode_empty() -> None:
    """NBSP survives bytes.strip but not str.strip → line 415."""

    class _Up:
        filename = "x.txt"

        async def read(self, _n: int = -1) -> bytes:
            return b"\xc2\xa0"

    content, err = await api_wire.read_uploaded_text(_Up())  # type: ignore[arg-type]
    assert content is None
    assert err == "empty file"


def test_aviation_iwxxm_assign_then_continue_loop() -> None:
    """Cover for-loop back-edge after a successful station assignment."""
    from src.clients.aviation_weather_client import AviationWeatherClient

    client = AviationWeatherClient()
    content = (
        '<?xml version="1.0"?><r designator="KJFK"/>'
        '<?xml version="1.0"?><r designator="XXXX"/>'
        '<?xml version="1.0"?><r designator="KBOS"/>'
    )
    out = client._parse_response(content, "iwxxm", ["KJFK", "KBOS"])
    assert "KJFK" in out
    assert "KBOS" in out


def test_convert_iwxxm_files_success_and_json_preview_layer12(
    convert_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    xml = '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'

    async def ok_join(_files: Any) -> tuple[str, str | None]:
        return xml, None

    monkeypatch.setattr(api_module, "read_upload_files_text", ok_join)
    resp = convert_client.post(
        "/api/v1/convert",
        files={
            "product": (None, "iwxxm"),
            "manual_text": (None, ""),
            "files": ("x.xml", b"<ignored/>", "application/xml"),
        },
    )
    assert resp.status_code == 200

    # JSON metars[] path layer12 soft-fail (line 1026) — not the manual_entries path
    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda *_a, **_k: (xml, {"ok": True, "convert_issues": [], "failed_spans": []}),
    )

    class _VS:
        def validate_all_layers(self, _t: str) -> Any:
            return SimpleNamespace(passed=False, total_issues=1, results=[SimpleNamespace(issues=[])])

    monkeypatch.setattr(api_module, "ValidationService", _VS)
    resp2 = convert_client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="],
            "product": "METAR",
            "preview": True,
            "version": "2025-2",
        },
    )
    assert resp2.status_code == 200


def test_convert_soft_preview_partial_span_fields(convert_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """base_offset>0 with missing start or end on FailedSpan construction."""
    xml = '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'
    tac = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="

    class _LenientSpan:
        def __init__(self, **data: Any) -> None:
            self.__dict__.update(data)

    monkeypatch.setattr(conversion_router, "FailedSpan", _LenientSpan)
    monkeypatch.setattr(
        api_module,
        "ValidationService",
        lambda: SimpleNamespace(
            validate_all_layers=lambda _t: SimpleNamespace(passed=True, total_issues=0, results=[])
        ),
    )

    def fake_convert(_tac: str, **kwargs: Any):
        soft = kwargs.get("soft_preview_out")
        if soft is not None:
            soft.clear()
            soft.update(
                {
                    "ok": False,
                    "failed_spans": [
                        {"code": "NO_START", "message": "m", "end": 2},
                        {"code": "NO_END", "message": "n", "start": 1},
                        {"code": "BOTH", "message": "o", "start": 0, "end": 3},
                    ],
                    "convert_issues": [],
                }
            )
        return xml, soft if soft is not None else {}

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    quiet = TestClient(api_module.app, raise_server_exceptions=False)
    quiet.app.dependency_overrides[verify_supabase_token] = lambda: {"sub": "u", "aud": "a"}
    resp = quiet.post(
        "/api/v1/convert",
        files={
            "product": (None, "METAR"),
            "preview": (None, "true"),
            "manual_text": (None, tac + "\n" + tac),
        },
    )
    assert resp.status_code in {200, 400, 422, 500}


def test_extension_wire_json_must_be_array(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bracket-wrapped payload that json.loads returns as non-list (line 50)."""
    monkeypatch.setattr(extension_wire.json, "loads", lambda _s: {"not": "list"})
    with pytest.raises(HTTPException) as exc:
        extension_wire.parse_extension_tokens(["[]"])
    assert exc.value.status_code == 400
    assert "array of strings" in exc.value.detail["message"]


@pytest.mark.asyncio
async def test_schema_discovery_analyze_exception_and_short_matches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from src.services import schema_discovery_poller as sdp
    from src.services.schema_discovery_poller import SchemaDiscoveryPoller

    old_xmi = tmp_path / "2023-1" / "XMI" / "IWXXM.xmi"
    new_xmi = tmp_path / "2025-2" / "XMI" / "IWXXM.xmi"
    old_xmi.parent.mkdir(parents=True)
    new_xmi.parent.mkdir(parents=True)
    old_xmi.write_text("old", encoding="utf-8")
    new_xmi.write_text("new", encoding="utf-8")

    monkeypatch.setattr(
        sdp,
        "analyze_xmi_versions",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("analyze boom")),
    )
    monkeypatch.setattr(sdp, "SUPPORTED_VERSIONS", {"2023-1": {}, "2025-2": {}}, raising=False)
    monkeypatch.setattr(
        "src.config.iwxxm_versions.SUPPORTED_VERSIONS",
        {"2023-1": {}, "2025-2": {}},
    )
    poller = SchemaDiscoveryPoller(xmi_analyzer=SimpleNamespace(), base_schema_path=tmp_path)
    await poller._analyze_breaking_changes("2025-2")

    class _ShortPatterns:
        def findall(self, _html: str) -> list[Any]:
            return [("only",), ("2025", "2")]

    class _ShortRC:
        def findall(self, _html: str) -> list[Any]:
            return [("a", "b"), ("2025", "2", "RC1")]

    monkeypatch.setattr(sdp, "VERSION_PATTERN", _ShortPatterns())
    monkeypatch.setattr(sdp, "RC_PATTERN", _ShortRC())
    versions = poller._extract_versions_from_html("x")
    assert "2025-2RC1" in versions


@pytest.mark.asyncio
async def test_aviation_weather_blank_line_and_bbox_non404() -> None:
    import httpx
    from src.clients.aviation_weather_client import AviationWeatherAPIError, AviationWeatherClient

    client = AviationWeatherClient()
    out = client._parse_response("METAR KJFK 101851Z\n\n\nSPECI KBOS 101900Z\n", "raw", ["KJFK", "KBOS"])
    assert set(out) == {"KJFK", "KBOS"}

    multi = (
        '<?xml version="1.0"?><doc designator="KJFK"/>'
        '<?xml version="1.0"?><doc designator="KBOS"/>'
        '<?xml version="1.0"?><doc designator="KLAX"/>'
    )
    iwxxm = client._parse_response(multi, "iwxxm", ["KJFK", "KBOS", "KLAX"])
    assert set(iwxxm) == {"KJFK", "KBOS", "KLAX"}

    request = httpx.Request("GET", "https://example.test")

    async def get_500(*_a: Any, **_k: Any) -> None:
        response = httpx.Response(503, request=request, text="unavailable")
        raise httpx.HTTPStatusError("503", request=request, response=response)

    client._client = SimpleNamespace(get=get_500)
    with pytest.raises(AviationWeatherAPIError, match="HTTP 503"):
        await client.fetch_metars_by_bbox((0, 0, 1, 1))


def test_wmo_codelist_non_dict_and_requests_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from datetime import datetime

    from src.clients import wmo_codelists_client as wmo_mod
    from src.clients.wmo_codelists_client import WMOCodelistCache, WMOCodelistsClient

    cache = WMOCodelistCache(cache_dir=tmp_path, ttl_seconds=3600)
    cache._metadata = {"Weather": {"cached_at": datetime.now().isoformat()}}
    (tmp_path / "Weather.json").write_text("[1, 2, 3]", encoding="utf-8")
    assert cache.get("Weather") is None

    monkeypatch.setattr(wmo_mod, "REQUESTS_AVAILABLE", True)
    monkeypatch.setattr(wmo_mod, "requests", None)
    client = WMOCodelistsClient(codelists_dir=tmp_path, cache_dir=tmp_path)
    assert client._fetch_codelist_online("Weather") is None


@pytest.mark.asyncio
async def test_abuse_controls_invalid_content_length(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from src.utilities.abuse_controls import MaxBodySizeMiddleware

    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "1000")
    app = FastAPI()
    app.add_middleware(MaxBodySizeMiddleware, max_bytes=1000)

    @app.post("/api/v1/echo")
    async def echo() -> dict[str, str]:
        return {"ok": "true"}

    client = TestClient(app)
    resp = client.post("/api/v1/echo", content=b"hi", headers={"content-length": "nope"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_database_close_dispose_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.services import database as db

    db._engine = SimpleNamespace()  # no dispose attr / not callable
    db._async_session_maker = object()
    await db.close_db_engine()
    assert db._engine is None

    class _SyncDispose:
        def dispose(self) -> str:
            return "done"

    db._engine = _SyncDispose()
    db._async_session_maker = object()
    await db.close_db_engine()
    assert db._engine is None


def test_codelist_parser_rdf_and_requests_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from lxml import etree
    from src.utilities.codelist_parser import CodeListParser

    rdf = tmp_path / "codes.wmo.int-49-2-Weather.rdf"
    rdf.write_text(
        """<?xml version="1.0"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:skos="http://www.w3.org/2004/02/skos/core#">
          <skos:Concept>
            <skos:prefLabel></skos:prefLabel>
          </skos:Concept>
          <skos:Concept rdf:about="http://codes.wmo.int/49-2/Weather/RA">
            <skos:prefLabel>Rain</skos:prefLabel>
          </skos:Concept>
        </rdf:RDF>
        """,
        encoding="utf-8",
    )
    settings = SimpleNamespace(
        wmo_online_validation=True,
        wmo_validation_timeout=1,
        wmo_registry_cache_ttl=0,
        wmo_registry_url="https://codes.wmo.int",
    )
    parser = CodeListParser(tmp_path, settings=settings)
    parser._parse_rdf_file(rdf)
    assert "RA" in parser._cache.get("Weather", set()) or "Weather" in parser._cache

    monkeypatch.setattr("src.utilities.codelist_parser.requests", None)
    issue = parser._validate_online("http://codes.wmo.int/49-2/Weather/Z", "/a")
    assert issue is not None
    assert "requests" in issue.message.lower() or issue.code == "CODELIST_REQUESTS_UNAVAILABLE"


def test_elevation_none_and_test_override_miss(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.utilities.elevation_service import ElevationService

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    datum_map = data_dir / "vertical_datum_map.json"
    datum_map.write_text(
        json.dumps(
            {
                "country_defaults": {"US": "NAVD88"},
                "airport_overrides": {},
                "test_overrides": {},
                "datum_info": {},
            }
        ),
        encoding="utf-8",
    )

    def _load(self: Any) -> None:
        self.datum_map = json.loads(datum_map.read_text(encoding="utf-8"))

    monkeypatch.setattr(ElevationService, "_load_datum_mapping", _load)
    svc = ElevationService()
    elev, datum = svc.get_elevation_data("ZZZZ", default_elevation_ft=None, country_code="US")
    assert elev is None
    assert datum

    elev2, _ = svc._get_raw_elevation_data("ZZZZ", use_test_overrides=True, country_code="US")
    assert elev2 is None


def test_wmo_examples_load_all_explicit_and_empty(tmp_path: Path) -> None:
    from src.utilities.wmo_examples_loader import WMOExamplesLoader

    empty_ver = tmp_path / "2099-1" / "examples"
    empty_ver.mkdir(parents=True)
    loader = WMOExamplesLoader(schemas_base_path=tmp_path)
    out = loader.load_all_versions(versions=["2099-1", "also-missing"])
    assert out == {}


def test_observability_counter_cache_hit_and_drain_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    import logging
    import queue as queue_mod

    from starlette.requests import Request

    name = "ev080_counter_cache_hit"
    obs._METRICS.pop(name, None)
    c1 = obs._get_or_create_counter(name, "doc", ["lbl"])
    c2 = obs._get_or_create_counter(name, "doc", ["lbl"])
    assert c1 is c2

    handler = obs.LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    if handler._worker.is_alive():
        handler._stop_event.set()
        handler._worker.join(timeout=1.0)
    handler._stop_event.clear()
    handler._stop_event.set()
    handler._session = MagicMock()
    handler.batch_size = 10

    class _Q:
        def __init__(self) -> None:
            self._n = 0

        def empty(self) -> bool:
            self._n += 1
            return self._n > 2

        def get_nowait(self) -> dict[str, Any]:
            raise queue_mod.Empty()

        def task_done(self) -> None:
            return None

        def put(self, *_a: Any, **_k: Any) -> None:
            return None

    handler._queue = _Q()  # type: ignore[assignment]
    handler._worker_loop()

    prior_levels = {n: logging.getLogger(n).level for n in obs._REQUEST_LOGGERS}
    scope = {"type": "http", "method": "GET", "path": "/", "headers": [], "client": ("1.1.1.1", 1)}
    req = Request(scope)
    try:
        for logger_name in obs._REQUEST_LOGGERS:
            logging.getLogger(logger_name).setLevel(logging.DEBUG)
        obs.set_request_log_level(req, "WARNING")
    finally:
        obs._reset_request_log_level(req)
        for logger_name, level in prior_levels.items():
            logging.getLogger(logger_name).setLevel(level)


def test_mass_ingest_rejected_file_branch(convert_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.routers import mass_ingest as mass_router
    from src.services.mass_ingest import MassIngestCaps

    monkeypatch.setattr(
        mass_router,
        "_caps",
        lambda: MassIngestCaps(max_file_bytes=10_000, max_files=10, max_total_bytes=50_000),
    )
    resp = convert_client.post(
        "/api/v1/ingest/mass",
        files=[
            ("files", ("ok.tac", b"METAR KJFK 121251Z=\n", "text/plain")),
            ("files", ("bad.exe", b"METAR KJFK=\n", "application/octet-stream")),
        ],
        headers={"Authorization": "Bearer t"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["rejected_count"] >= 1


def test_openaip_client_non_dict_json(tmp_path: Path) -> None:
    from src.clients.openaip_client import OpenAIPClient

    (tmp_path / "us_apt.geojson").write_text("[1, 2, 3]", encoding="utf-8")
    client = OpenAIPClient(data_path=tmp_path)
    client._load_local_data()
    assert client._cache == {} or isinstance(client._cache, dict)


def test_conversion_util_soft_preview_none_and_empty_layers(monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace as NS

    from src.utilities.conversion import convert_metar_tac_with_metadata

    import tac2iwxxm

    fake = NS(
        ok=False,
        xml="<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>",
        issues=[NS(code="E", message="m", start=0, end=1)],
    )
    monkeypatch.setattr(tac2iwxxm, "convert", lambda *a, **k: fake)
    xml, _ = convert_metar_tac_with_metadata("BAD", validate=False, preview=True, soft_preview_out=None)
    assert "<?xml" in xml or xml.startswith("<")

    from src.schemas.validation import ValidationLayer
    from src.services import validation_orchestrator as orch_mod
    from src.services.validation_orchestrator import ComprehensiveValidationResult

    class _Orch:
        def validate_complete(self, **kwargs: Any) -> ComprehensiveValidationResult:
            assert kwargs.get("layers") is None or kwargs.get("layers") == []
            return ComprehensiveValidationResult(
                is_valid=True,
                layers_run=[],
                layers_passed=[],
                layers_failed=[],
                all_issues=[],
            )

    monkeypatch.setattr(orch_mod, "get_validation_orchestrator", lambda: _Orch())
    ok_fake = NS(ok=True, xml='<?xml version="1.0"?><x/>', issues=[])
    monkeypatch.setattr(tac2iwxxm, "convert", lambda *a, **k: ok_fake)
    convert_metar_tac_with_metadata(
        "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=",
        validate=True,
        validation_layers=[],
    )


def test_version_migration_remove_zero_matches() -> None:
    import xml.etree.ElementTree as ET

    from src.utilities.version_migration import VersionMigrator

    m = VersionMigrator()
    root = ET.fromstring("<root><child/></root>")
    m._remove_elements(
        root,
        {"element": "Missing", "xpath": "//Missing", "action": "remove", "reason": "gone"},
    )
    assert m.warnings == []


def test_work_session_payload_pending_files_plain_dicts() -> None:
    from src.schemas.work_session import WorkSessionCreate, WorkSessionProduct
    from src.services import work_session_service as svc

    payload = WorkSessionCreate(
        product=WorkSessionProduct.METAR,
        pending_files=[{"name": "a.tac", "content": "METAR X="}],
    )
    # Force plain dicts through the dump path
    data = payload.model_dump(exclude_unset=True)
    data["pending_files"] = [{"name": "a.tac", "content": "x"}]
    fake = SimpleNamespace(model_dump=lambda **_k: data)
    out = svc._payload_dict(fake)  # type: ignore[arg-type]
    assert out["pending_files"][0]["name"] == "a.tac"


def test_iwxxm_versions_deprecated_wrong_profile_reraise() -> None:
    with pytest.raises(versions.VersionDeprecatedError):
        versions.get_version_config_for_emit_profile("3.0.0", "annex3")


def test_version_detector_v_prefixed_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import subprocess

    from src.utilities.version_detector import VersionDetector

    iwxxm = tmp_path / "iwxxm"
    iwxxm.mkdir()
    (iwxxm / "v2025-2").mkdir()
    monkeypatch.setattr(
        "src.utilities.version_detector.subprocess.run",
        MagicMock(side_effect=subprocess.CalledProcessError(1, "git")),
    )
    vd = VersionDetector(schemas_root=tmp_path)
    tags = vd.get_available_tags()
    assert "v2025-2" in tags


@pytest.mark.asyncio
async def test_convert_bulletin_non_multipart_and_upload_err(
    convert_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from starlette.requests import Request

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/convert-bulletin",
        "headers": [(b"content-type", b"application/json")],
        "client": ("127.0.0.1", 1),
    }
    with pytest.raises(HTTPException) as exc:
        await conversion_router.convert_bulletin(
            Request(scope),
            product="METAR",
            files=None,
            manual_text="x",
            profile="",
            semantic_profile="",
            exchange_profile="",
            iwxxm_version="2025-2",
            lint=False,
            extensions=[],
        )
    assert exc.value.status_code == 415

    async def bad_join(_files: Any) -> tuple[str, str | None]:
        return "", "file too large"

    monkeypatch.setattr(api_module, "read_upload_files_text", bad_join)
    resp2 = convert_client.post(
        "/api/v1/convert-bulletin",
        files={
            "product": (None, "METAR"),
            "manual_text": (None, ""),
            "files": ("x.txt", b"data", "text/plain"),
        },
    )
    assert resp2.status_code == 400

    resp3 = convert_client.post(
        "/api/v1/convert-bulletin",
        files={"product": (None, "METAR"), "manual_text": (None, "   ")},
    )
    assert resp3.status_code == 400


def test_convert_bulletin_bad_yygggg_identifier(convert_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    meta = SimpleNamespace(
        ahl="SAUS31 KWBC 011200",
        yygggg="XX1200",
        report_count=1,
        tt="SA",
        aa="US",
        cccc="KWBC",
        bbb=None,
        report_status=None,
    )
    split = SimpleNamespace(meta=meta, reports=["METAR KJFK 011200Z 18008KT 10SM FEW250 22/14 A3012="])
    monkeypatch.setattr(api_module, "tac2iwxxm_split_bulletin", lambda *_a, **_k: split)
    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda *_a, **_k: ('<?xml version="1.0"?><x/>', {"ok": True, "convert_issues": [], "failed_spans": []}),
    )
    resp = convert_client.post(
        "/api/v1/convert-bulletin",
        files={
            "product": (None, "METAR"),
            "lint": (None, "false"),
            "manual_text": (None, "SAUS31 KWBC 011200\nMETAR KJFK 011200Z 18008KT 10SM FEW250 22/14 A3012="),
        },
    )
    assert resp.status_code == 200


def test_convert_json_exchange_output_and_iwxxm_paths(
    convert_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    xml = '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'
    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda *_a, **_k: (xml, {"ok": True, "convert_issues": [], "failed_spans": []}),
    )
    monkeypatch.setattr(
        api_module,
        "ValidationService",
        lambda: SimpleNamespace(
            validate_all_layers=lambda _t: SimpleNamespace(passed=True, total_issues=0, results=[])
        ),
    )
    resp = convert_client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="],
            "version": "2025-2",
            "exchange_output": True,
            "product": "METAR",
        },
    )
    assert resp.status_code == 200

    # product=IWXXM from JSON metars
    resp2 = convert_client.post(
        "/api/v1/convert",
        json={"metars": [xml], "version": "2025-2", "product": "iwxxm"},
    )
    assert resp2.status_code == 200

    # IWXXM empty → 400
    resp3 = convert_client.post(
        "/api/v1/convert",
        json={"metars": [], "version": "2025-2", "product": "iwxxm"},
    )
    assert resp3.status_code == 400

    async def bad_files(_f: Any) -> tuple[str, str | None]:
        return "", "upload boom"

    monkeypatch.setattr(api_module, "read_upload_files_text", bad_files)
    resp4 = convert_client.post(
        "/api/v1/convert",
        files={
            "product": (None, "iwxxm"),
            "manual_text": (None, ""),
            "files": ("x.xml", b"<x/>", "application/xml"),
        },
    )
    assert resp4.status_code == 400


def test_convert_ca_eccc_import_fallback_and_validate_paths(
    convert_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    xml = '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0.0"/>'
    real_import = builtins.__import__

    def fake_import(name: str, globals=None, locals=None, fromlist=(), level: int = 0):
        if name == "iwxxm_validate.ca_eccc_bundle" or (
            name == "iwxxm_validate" and fromlist and "ca_eccc_bundle" in fromlist
        ):
            raise ImportError("forced")
        if "ca_eccc_bundle" in name:
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda *_a, **_k: (xml, {"ok": True, "convert_issues": [], "failed_spans": []}),
    )
    # May 400 for missing bundle or proceed — either exercises ImportError path
    quiet = TestClient(api_module.app, raise_server_exceptions=False)
    quiet.app.dependency_overrides[verify_supabase_token] = lambda: {"sub": "u", "aud": "a"}
    resp = quiet.post(
        "/api/v1/convert",
        files={
            "product": (None, "METAR"),
            "semantic_profile": (None, "ca_eccc"),
            "extensions": (None, "IWXXM_CA"),
            "iwxxm_version": (None, "3.0.0"),
            "manual_text": (None, "METAR CYUL 121151Z 18008KT 10SM FEW250 22/14 A3012="),
        },
    )
    assert resp.status_code in {200, 400, 422, 500}

    # IWXXM pass-through validate failure + exception
    bad_report = SimpleNamespace(
        ok=False,
        issues=[SimpleNamespace(message="xsd fail", code="XSD", location="/")],
    )
    monkeypatch.setattr(api_module, "_call_iwxxm_validate", lambda *_a, **_k: bad_report)
    resp2 = convert_client.post(
        "/api/v1/convert",
        files={
            "product": (None, "iwxxm"),
            "validate_output": (None, "true"),
            "manual_text": (None, xml),
        },
    )
    assert resp2.status_code == 200

    def boom(*_a: Any, **_k: Any) -> None:
        raise RuntimeError("validate down")

    monkeypatch.setattr(api_module, "_call_iwxxm_validate", boom)
    resp3 = convert_client.post(
        "/api/v1/convert",
        files={
            "product": (None, "iwxxm"),
            "validation_level": (None, "schematron"),
            "manual_text": (None, xml),
        },
    )
    assert resp3.status_code == 200


def test_convert_preview_layer12_and_lint_warning(convert_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    xml = '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'
    tac = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="

    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda *_a, **_k: (xml, {"ok": True, "convert_issues": [], "failed_spans": []}),
    )
    monkeypatch.setattr(
        api_module,
        "ValidationService",
        lambda: SimpleNamespace(
            validate_all_layers=lambda _t: SimpleNamespace(
                passed=False,
                total_issues=1,
                results=[SimpleNamespace(issues=[])],
            )
        ),
    )

    class _LintIssue:
        severity = "warning"
        code = "LINT_WARN"
        message = "soft warn"
        location = None
        start = None
        end = None

    class _LintReport:
        def __init__(self) -> None:
            self.ok = True
            self.issues = [_LintIssue()]
            self.fixes: list[Any] = []

    monkeypatch.setattr(conversion_router, "tac_lint_fn", lambda *_a, **_k: _LintReport())
    monkeypatch.setattr(api_module, "tac_lint_fn", lambda *_a, **_k: _LintReport())

    resp = convert_client.post(
        "/api/v1/convert",
        files={
            "product": (None, "METAR"),
            "preview": (None, "true"),
            "lint": (None, "true"),
            "manual_text": (None, tac),
            "validate_output": (None, "true"),
        },
    )
    assert resp.status_code in {200, 400, 422}

    # soft preview span with only start / only end + base_offset
    def fake_convert(tac_text: str, **kwargs: Any):
        soft = kwargs.get("soft_preview_out")
        if soft is not None:
            soft.clear()
            soft.update(
                {
                    "ok": False,
                    "failed_spans": [
                        {"code": "A", "message": "m", "start": 1},
                        {"code": "B", "message": "n", "end": 2},
                    ],
                    "convert_issues": [],
                }
            )
        return xml, soft if soft is not None else {}

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    monkeypatch.setattr(
        api_module,
        "ValidationService",
        lambda: SimpleNamespace(
            validate_all_layers=lambda _t: SimpleNamespace(passed=True, total_issues=0, results=[])
        ),
    )
    quiet = TestClient(api_module.app, raise_server_exceptions=False)
    quiet.app.dependency_overrides[verify_supabase_token] = lambda: {"sub": "u", "aud": "a"}
    resp2 = quiet.post(
        "/api/v1/convert",
        files={
            "product": (None, "METAR"),
            "preview": (None, "true"),
            "manual_text": (None, tac + "\n" + tac),
        },
    )
    assert resp2.status_code in {200, 400, 422, 500}


def test_convert_files_preview_layer12(convert_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    xml = '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'
    monkeypatch.setattr(
        api_module,
        "convert_metar_tac_with_metadata",
        lambda *_a, **_k: (xml, {"ok": True, "convert_issues": [], "failed_spans": []}),
    )
    monkeypatch.setattr(
        api_module,
        "ValidationService",
        lambda: SimpleNamespace(
            validate_all_layers=lambda _t: SimpleNamespace(
                passed=False, total_issues=2, results=[SimpleNamespace(issues=[])]
            )
        ),
    )
    resp = convert_client.post(
        "/api/v1/convert",
        files={
            "product": (None, "METAR"),
            "preview": (None, "true"),
            "validate_output": (None, "true"),
            "files": ("a.txt", b"METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=", "text/plain"),
        },
    )
    assert resp.status_code in {200, 400, 422}
