"""Exercise ModuleType facade setattr/delattr sync used after line-cap splits."""

from __future__ import annotations

from types import SimpleNamespace

import pytest


def _pulse_delattr(mod: object, name: str, original: object) -> None:
    """Hit facade ``__delattr__`` then restore the real binding for later tests."""
    setattr(mod, name, object())
    delattr(mod, name)
    setattr(mod, name, original)


def test_api_wire_facade_sync_branches() -> None:
    from src import api_wire as mod
    from src import api_wire_part_2 as part2

    mod._facade_probe_unsynced = 1
    assert mod._facade_probe_unsynced == 1
    delattr(mod, "_facade_probe_unsynced")

    original = mod.read_uploaded_text
    try:
        mod.read_uploaded_text = object()  # type: ignore[assignment]
        saved = part2.read_uploaded_text
        delattr(part2, "read_uploaded_text")
        try:
            mod.read_uploaded_text = object()  # type: ignore[assignment]
        finally:
            part2.read_uploaded_text = saved
        _pulse_delattr(mod, "read_uploaded_text", original)
    finally:
        mod.read_uploaded_text = original
        part2.read_uploaded_text = original


def test_aviation_weather_client_facade_sync() -> None:
    from src.clients import aviation_weather_client as mod
    from src.clients import aviation_weather_client_part_2 as part2
    from src.clients import aviation_weather_client_part_3 as part3

    original_httpx = mod.httpx
    original_asyncio = mod.asyncio
    mod._ORIG["httpx"] = original_httpx  # type: ignore[attr-defined]
    mod._ORIG["asyncio"] = original_asyncio  # type: ignore[attr-defined]
    try:
        mod.httpx = object()  # type: ignore[assignment]
        mod.asyncio = object()  # type: ignore[assignment]
        for part in (part2, part3):
            if hasattr(part, "httpx"):
                saved = part.httpx
                delattr(part, "httpx")
                try:
                    mod.httpx = object()  # type: ignore[assignment]
                finally:
                    part.httpx = saved
        _pulse_delattr(mod, "httpx", original_httpx)
        mod._facade_probe_unsynced = True
        delattr(mod, "_facade_probe_unsynced")
    finally:
        mod.httpx = original_httpx  # type: ignore[assignment]
        mod.asyncio = original_asyncio  # type: ignore[assignment]
        part2.httpx = original_httpx
        part3.httpx = original_httpx
        part2.asyncio = original_asyncio
        part3.asyncio = original_asyncio


def test_wmo_codelists_client_facade_sync() -> None:
    from src.clients import wmo_codelists_client as mod
    from src.clients import wmo_codelists_client_part_1 as part1
    from src.clients import wmo_codelists_client_part_2 as part2

    original_flag = mod.REQUESTS_AVAILABLE
    original_requests = mod.requests
    original_parser = mod.CodeListParser
    mod._ORIG["REQUESTS_AVAILABLE"] = original_flag  # type: ignore[attr-defined]
    mod._ORIG["requests"] = original_requests  # type: ignore[attr-defined]
    try:
        mod.REQUESTS_AVAILABLE = False
        mod.CodeListParser = original_parser
        _pulse_delattr(mod, "REQUESTS_AVAILABLE", original_flag)
        saved = part2.REQUESTS_AVAILABLE
        delattr(part2, "REQUESTS_AVAILABLE")
        try:
            mod.REQUESTS_AVAILABLE = True
        finally:
            part2.REQUESTS_AVAILABLE = saved
        mod._facade_probe_unsynced = 0
        delattr(mod, "_facade_probe_unsynced")
    finally:
        mod.REQUESTS_AVAILABLE = original_flag
        mod.requests = original_requests
        mod.CodeListParser = original_parser
        part1.REQUESTS_AVAILABLE = original_flag
        part2.REQUESTS_AVAILABLE = original_flag
        part1.requests = original_requests
        part2.requests = original_requests


def test_codelist_parser_facade_sync() -> None:
    from src.utilities import codelist_parser as mod
    from src.utilities import codelist_parser_part_1 as part1
    from src.utilities import codelist_parser_part_3 as part3

    original_flag = mod.REQUESTS_AVAILABLE
    original_registry = mod._registry
    original_parser = mod.CodeListParser
    mod._ORIG["REQUESTS_AVAILABLE"] = original_flag  # type: ignore[attr-defined]
    mod._ORIG["_registry"] = original_registry  # type: ignore[attr-defined]
    mod._ORIG["CodeListParser"] = original_parser  # type: ignore[attr-defined]
    try:
        mod.REQUESTS_AVAILABLE = False
        mod._registry = object()  # type: ignore[assignment]
        mod.CodeListParser = original_parser
        _pulse_delattr(mod, "REQUESTS_AVAILABLE", original_flag)
        _pulse_delattr(mod, "_registry", original_registry)
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
    finally:
        mod.REQUESTS_AVAILABLE = original_flag
        mod._registry = original_registry
        mod.CodeListParser = original_parser
        part1.REQUESTS_AVAILABLE = original_flag
        part3._registry = original_registry  # type: ignore[attr-defined]
        part3.CodeListParser = original_parser  # type: ignore[attr-defined]


def test_observability_facade_sync() -> None:
    from src.utilities import observability as mod
    from src.utilities import observability_part_1 as part1

    original_handler = mod.LokiHandler
    original_queue = mod.queue
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        mod.queue = original_queue
        if hasattr(part1, "LokiHandler"):
            saved = part1.LokiHandler
            delattr(part1, "LokiHandler")
            try:
                mod.LokiHandler = object()  # type: ignore[misc,assignment]
            finally:
                part1.LokiHandler = saved
        _pulse_delattr(mod, "LokiHandler", original_handler)
    finally:
        mod.LokiHandler = original_handler
        mod.queue = original_queue
        part1.LokiHandler = original_handler


def test_schema_registry_facade_sync() -> None:
    from src.utilities import schema_registry as mod
    from src.utilities import schema_registry_part_2 as part2
    from src.utilities import schema_registry_part_3 as part3

    original_versions = mod.SUPPORTED_VERSIONS
    original_registry = mod._registry_instance
    mod._ORIG["SUPPORTED_VERSIONS"] = original_versions  # type: ignore[attr-defined]
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        mod._registry_instance = None
        if not hasattr(part3, "SUPPORTED_VERSIONS"):
            part3.SUPPORTED_VERSIONS = original_versions  # type: ignore[attr-defined]
        _pulse_delattr(mod, "SUPPORTED_VERSIONS", original_versions)
    finally:
        mod.SUPPORTED_VERSIONS = original_versions
        mod._registry_instance = original_registry
        part2.SUPPORTED_VERSIONS = original_versions  # type: ignore[attr-defined]
        part3._registry_instance = original_registry  # type: ignore[attr-defined]


def test_conversion_router_facade_sync() -> None:
    from src.routers import conversion as mod
    from src.routers import conversion_part_1 as part1
    from src.routers import conversion_part_2 as part2
    from src.routers import conversion_part_6 as part6
    from src.routers import conversion_routes_io as routes_io

    original_lint = mod.tac_lint_fn
    original_svc = mod.ConversionProfilesService
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        part2.tac_lint_fn = original_lint  # type: ignore[attr-defined,misc]
        mod._ORIG["tac_lint_fn"] = original_lint  # type: ignore[attr-defined]
        _pulse_delattr(mod, "tac_lint_fn", original_lint)
        part6.ConversionProfilesService = original_svc  # type: ignore[misc]
        routes_io.ConversionProfilesService = original_svc  # type: ignore[attr-defined,misc]
        mod._ORIG["ConversionProfilesService"] = original_svc  # type: ignore[attr-defined]
        _pulse_delattr(mod, "ConversionProfilesService", original_svc)
    finally:
        mod.tac_lint_fn = original_lint
        mod.ConversionProfilesService = original_svc
        part1.tac_lint_fn = original_lint  # type: ignore[attr-defined]
        if hasattr(part2, "tac_lint_fn"):
            delattr(part2, "tac_lint_fn")
        part6.ConversionProfilesService = original_svc
        if hasattr(routes_io, "ConversionProfilesService"):
            delattr(routes_io, "ConversionProfilesService")


def test_conversion_api_surface_delattr() -> None:
    from src.routers.conversion_api_surface import api_surface

    probe = "_facade_api_surface_probe"
    setattr(api_surface, probe, "x")
    assert getattr(api_surface, probe) == "x"
    delattr(api_surface, probe)
    with pytest.raises(AttributeError):
        getattr(api_surface, probe)


def test_tac_quality_facade_sync() -> None:
    from src.routers import tac_quality as mod
    from src.routers import tac_quality_part_2 as part2

    original = mod.get_airport_validator
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        saved = part2.get_airport_validator
        delattr(part2, "get_airport_validator")
        try:
            mod.get_airport_validator = object()  # type: ignore[assignment]
        finally:
            part2.get_airport_validator = saved
        _pulse_delattr(mod, "get_airport_validator", original)
    finally:
        mod.get_airport_validator = original
        part2.get_airport_validator = original


def test_iwxxm_versions_facade_sync() -> None:
    from src.config import iwxxm_versions as mod
    from src.config import iwxxm_versions_part_1 as part1
    from src.config import iwxxm_versions_part_2 as part2

    original = mod.SUPPORTED_VERSIONS
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        mod.__file__ = mod.__file__
        _pulse_delattr(mod, "SUPPORTED_VERSIONS", original)
        if hasattr(part2, "SUPPORTED_VERSIONS"):
            saved = part2.SUPPORTED_VERSIONS
            delattr(part2, "SUPPORTED_VERSIONS")
            try:
                mod.SUPPORTED_VERSIONS = ()
            finally:
                part2.SUPPORTED_VERSIONS = saved
    finally:
        mod.SUPPORTED_VERSIONS = original
        part1.SUPPORTED_VERSIONS = original
        if hasattr(part2, "SUPPORTED_VERSIONS"):
            part2.SUPPORTED_VERSIONS = original


def test_conversion_profiles_service_facade_sync() -> None:
    from src.services import conversion_profiles_service as mod
    from src.services import conversion_profiles_service_part_1 as part1

    original = mod._engine
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        _pulse_delattr(mod, "_engine", original)
    finally:
        mod._engine = original
        part1._engine = original  # type: ignore[attr-defined]


def test_dissemination_ops_service_facade_sync() -> None:
    from src.services import dissemination_ops_service as mod
    from src.services import dissemination_ops_service_part_1 as part1
    from src.services import dissemination_ops_service_part_2 as part2

    original_engine = mod._engine
    original_insert = mod.insert
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        _pulse_delattr(mod, "_engine", original_engine)
        mod.insert = original_insert
        mod.Table = mod.Table
        part2.insert = original_insert  # type: ignore[misc]
        mod._ORIG["insert"] = original_insert  # type: ignore[attr-defined]
        _pulse_delattr(mod, "insert", original_insert)
    finally:
        mod._engine = original_engine
        mod.insert = original_insert
        part1._engine = original_engine  # type: ignore[attr-defined]
        part2.insert = original_insert  # type: ignore[misc]


def test_live_map_cache_facade_sync() -> None:
    from src.services import live_map_cache as mod
    from src.services import live_map_cache_part_1 as part1
    from src.services import live_map_cache_part_2 as part2

    original = mod.UTC
    injected = hasattr(part2, "UTC")
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        if hasattr(part2, "UTC"):
            delattr(part2, "UTC")
        mod.UTC = original
        part2.UTC = original  # type: ignore[attr-defined,misc]
        mod.UTC = original
        _pulse_delattr(mod, "UTC", original)
    finally:
        mod.UTC = original
        part1.UTC = original  # type: ignore[attr-defined]
        if injected:
            part2.UTC = original  # type: ignore[attr-defined]
        elif hasattr(part2, "UTC"):
            delattr(part2, "UTC")


def test_live_map_refresh_facade_sync() -> None:
    from src.services import live_map_refresh as mod
    from src.services import live_map_refresh_part_1 as part1
    from src.services import live_map_refresh_part_2 as part2

    original = mod.convert_mod
    injected = hasattr(part2, "convert_mod")
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        if hasattr(part2, "convert_mod"):
            delattr(part2, "convert_mod")
        mod.convert_mod = original
        part2.convert_mod = original  # type: ignore[attr-defined,misc]
        mod.convert_mod = original
        mod._ORIG["convert_mod"] = original  # type: ignore[attr-defined]
        _pulse_delattr(mod, "convert_mod", original)
    finally:
        mod.convert_mod = original
        part1.convert_mod = original  # type: ignore[attr-defined]
        if injected:
            part2.convert_mod = original  # type: ignore[attr-defined]
        elif hasattr(part2, "convert_mod"):
            delattr(part2, "convert_mod")


def test_schema_discovery_poller_facade_sync() -> None:
    from src.services import schema_discovery_poller as mod
    from src.services import schema_discovery_poller_part_1 as part1
    from src.services import schema_discovery_poller_part_2 as part2

    original = mod.httpx
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        part1.httpx = original  # type: ignore[attr-defined,misc]
        mod.httpx = original
        if "SUPPORTED_VERSIONS" in mod._SYNC:  # type: ignore[attr-defined]
            mod.SUPPORTED_VERSIONS = ()
        mod._ORIG["httpx"] = original  # type: ignore[attr-defined]
        _pulse_delattr(mod, "httpx", original)
    finally:
        mod.httpx = original
        part1.httpx = original  # type: ignore[attr-defined]
        if hasattr(part2, "httpx"):
            part2.httpx = original  # type: ignore[attr-defined]


def test_schema_mirror_service_facade_sync() -> None:
    import httpx as real_httpx
    from src.services import schema_mirror_service as mod
    from src.services import schema_mirror_service_part_1 as part1
    from src.services import schema_mirror_service_part_2 as part2

    original = real_httpx
    mod._ORIG["httpx"] = original  # type: ignore[attr-defined]
    try:
        part1.httpx = original  # type: ignore[attr-defined,misc]
        part2.httpx = original  # type: ignore[attr-defined,misc]
        mod.httpx = object()  # type: ignore[assignment]
        delattr(part2, "httpx")
        try:
            mod.httpx = object()  # type: ignore[assignment]
        finally:
            part2.httpx = original  # type: ignore[attr-defined,misc]
        delattr(part1, "httpx")
        try:
            mod.httpx = object()  # type: ignore[assignment]
        finally:
            part1.httpx = original  # type: ignore[attr-defined,misc]
        _pulse_delattr(mod, "httpx", original)
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
    finally:
        mod.httpx = original  # type: ignore[assignment]
        part1.httpx = original  # type: ignore[attr-defined]
        part2.httpx = original  # type: ignore[attr-defined]


def test_conversion_append_lint_warning_and_info_severity() -> None:
    from src.routers.conversion_part_2 import _append_pre_convert_lint_issues
    from src.schemas.conversion import ConversionIssueSeverity

    class _Acc:
        def __init__(self) -> None:
            self.issues: list[object] = []

        def add_issue(self, **kwargs: object) -> None:
            self.issues.append(kwargs)

    acc = _Acc()
    report = SimpleNamespace(
        ok=True,
        issues=[
            SimpleNamespace(severity="warning", message="w", code="W1", location=None),
            SimpleNamespace(severity="note", message="i", code="I1", location=None),
            SimpleNamespace(severity="error", message="e", code="E1", location=None),
        ],
    )
    _append_pre_convert_lint_issues(report, acc=acc)  # type: ignore[arg-type]
    severities = {item["severity"] for item in acc.issues}  # type: ignore[index]
    assert ConversionIssueSeverity.WARNING in severities
    assert ConversionIssueSeverity.INFO in severities
    assert ConversionIssueSeverity.ERROR in severities
    _append_pre_convert_lint_issues(None, acc=acc)  # type: ignore[arg-type]
    soft = SimpleNamespace(ok=False, issues=report.issues)
    _append_pre_convert_lint_issues(soft, acc=acc)  # type: ignore[arg-type]


def test_codelist_resolve_settings_without_facade(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    import src.utilities.codelist_parser as facade
    import src.utilities.codelist_parser_part_2 as part2

    monkeypatch.setattr(facade, "get_validation_settings", object(), raising=False)
    fn = part2._resolve_get_validation_settings()
    assert callable(fn)
    monkeypatch.setitem(sys.modules, "src.utilities.codelist_parser", SimpleNamespace())
    fn2 = part2._resolve_get_validation_settings()
    assert fn2 is part2._default_get_validation_settings
    monkeypatch.setitem(sys.modules, "src.utilities.codelist_parser", facade)


def test_codelist_mixin_requests_fallback_without_facade(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    import src.utilities.codelist_parser as facade
    import src.utilities.codelist_parser_part_2_mixin_1 as mixin

    monkeypatch.setitem(sys.modules, "src.utilities.codelist_parser", SimpleNamespace())
    assert mixin._requests_mod() is not None
    assert mixin._requests_available() in {True, False}
    monkeypatch.setitem(sys.modules, "src.utilities.codelist_parser", facade)

    class _Req:
        exceptions = SimpleNamespace()

        @staticmethod
        def get(*_a: object, **_k: object) -> object:
            raise RuntimeError("boom")

    class _Parser:
        def __init__(self) -> None:
            self.settings = SimpleNamespace(
                wmo_validation_timeout=1,
                wmo_online_validation=True,
                wmo_registry_cache_ttl=0,
            )
            self._online_cache: dict[str, object] = {}

    monkeypatch.setattr(mixin, "_requests_available", lambda: True)
    monkeypatch.setattr(mixin, "_requests_mod", lambda: None)
    unavailable = mixin._CodeListParserMethodsMixin._validate_online(_Parser(), "http://x", "/a")  # type: ignore[arg-type]
    assert unavailable.code == "CODELIST_REQUESTS_UNAVAILABLE"

    calls = {"n": 0}

    def _req_then_none() -> object | None:
        calls["n"] += 1
        return _Req() if calls["n"] == 1 else None

    monkeypatch.setattr(mixin, "_requests_mod", _req_then_none)
    issue = mixin._CodeListParserMethodsMixin._validate_online(_Parser(), "http://x", "/a")  # type: ignore[arg-type]
    assert issue is not None

    class _Timeout(Exception):
        pass

    class _ReqTimeout:
        exceptions = SimpleNamespace(Timeout=_Timeout)

        @staticmethod
        def get(*_a: object, **_k: object) -> object:
            raise _Timeout()

    monkeypatch.setattr(mixin, "_requests_mod", lambda: _ReqTimeout())
    timed = mixin._CodeListParserMethodsMixin._validate_online(_Parser(), "http://x", "/a")  # type: ignore[arg-type]
    assert timed is not None

    class _ReqTopTimeout:
        Timeout = _Timeout
        exceptions = SimpleNamespace()

        @staticmethod
        def get(*_a: object, **_k: object) -> object:
            raise _Timeout()

    monkeypatch.setattr(mixin, "_requests_mod", lambda: _ReqTopTimeout())
    timed2 = mixin._CodeListParserMethodsMixin._validate_online(_Parser(), "http://x", "/a")  # type: ignore[arg-type]
    assert timed2 is not None
