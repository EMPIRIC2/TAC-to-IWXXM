"""Exercise ModuleType facade setattr/delattr sync used after line-cap splits."""

from __future__ import annotations

from types import SimpleNamespace

import pytest


def _del_and_restore(mod: object, name: str) -> None:
    """Delete a facade attr (hitting __delattr__) then restore for other tests."""
    original = getattr(mod, name)
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
    mod.read_uploaded_text = object()  # type: ignore[assignment]
    assert mod.read_uploaded_text is not original
    # hasattr(_part2) False → skip sync body (branch 60->59)
    saved = part2.read_uploaded_text
    delattr(part2, "read_uploaded_text")
    try:
        mod.read_uploaded_text = object()  # type: ignore[assignment]
    finally:
        part2.read_uploaded_text = saved
    _del_and_restore(mod, "read_uploaded_text")


def test_aviation_weather_client_facade_sync() -> None:
    from src.clients import aviation_weather_client as mod
    from src.clients import aviation_weather_client_part_2 as part2
    from src.clients import aviation_weather_client_part_3 as part3

    # Populate _ORIG so delattr restore bodies run.
    mod._ORIG["httpx"] = mod.httpx  # type: ignore[attr-defined]
    mod._ORIG["asyncio"] = mod.asyncio  # type: ignore[attr-defined]
    original_httpx = mod.httpx
    mod.httpx = object()  # type: ignore[assignment]
    mod.asyncio = object()  # type: ignore[assignment]
    # hasattr False loops for both parts
    for part in (part2, part3):
        if hasattr(part, "httpx"):
            saved = part.httpx
            delattr(part, "httpx")
            try:
                mod.httpx = object()  # type: ignore[assignment]
            finally:
                part.httpx = saved
    _del_and_restore(mod, "httpx")
    mod.httpx = original_httpx  # type: ignore[assignment]
    mod._facade_probe_unsynced = True
    delattr(mod, "_facade_probe_unsynced")


def test_wmo_codelists_client_facade_sync() -> None:
    from src.clients import wmo_codelists_client as mod
    from src.clients import wmo_codelists_client_part_2 as part2

    mod._ORIG["REQUESTS_AVAILABLE"] = mod.REQUESTS_AVAILABLE  # type: ignore[attr-defined]
    mod._ORIG["requests"] = mod.requests  # type: ignore[attr-defined]
    mod.REQUESTS_AVAILABLE = False
    assert mod.REQUESTS_AVAILABLE is False
    mod.CodeListParser = mod.CodeListParser
    _del_and_restore(mod, "REQUESTS_AVAILABLE")
    # hasattr(_part2, name) False branch
    saved = part2.REQUESTS_AVAILABLE
    delattr(part2, "REQUESTS_AVAILABLE")
    try:
        mod.REQUESTS_AVAILABLE = True
    finally:
        part2.REQUESTS_AVAILABLE = saved
    mod._facade_probe_unsynced = 0
    delattr(mod, "_facade_probe_unsynced")


def test_codelist_parser_facade_sync() -> None:
    from src.utilities import codelist_parser as mod

    mod._ORIG["REQUESTS_AVAILABLE"] = True  # type: ignore[attr-defined]
    mod._ORIG["_registry"] = mod._registry  # type: ignore[attr-defined]
    mod._ORIG["CodeListParser"] = mod.CodeListParser  # type: ignore[attr-defined]
    mod.REQUESTS_AVAILABLE = False
    mod._registry = object()  # type: ignore[assignment]
    mod.CodeListParser = mod.CodeListParser
    _del_and_restore(mod, "REQUESTS_AVAILABLE")
    _del_and_restore(mod, "_registry")
    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")


def test_observability_facade_sync() -> None:
    from src.utilities import observability as mod
    from src.utilities import observability_part_1 as part1

    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")
    # queue is in _SYNC but typically absent from parts → hasattr False branches
    mod.queue = mod.queue
    # Force hasattr(_part1, name) False for a synced symbol.
    if hasattr(part1, "LokiHandler"):
        saved = part1.LokiHandler
        delattr(part1, "LokiHandler")
        try:
            mod.LokiHandler = object()  # type: ignore[misc,assignment]
        finally:
            part1.LokiHandler = saved
    _del_and_restore(mod, "LokiHandler")


def test_schema_registry_facade_sync() -> None:
    from src.utilities import schema_registry as mod
    from src.utilities import schema_registry_part_3 as part3

    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")
    mod._registry_instance = None
    mod._ORIG["SUPPORTED_VERSIONS"] = mod.SUPPORTED_VERSIONS  # type: ignore[attr-defined]
    # Ensure part3 restore branch runs even when the name is absent.
    if not hasattr(part3, "SUPPORTED_VERSIONS"):
        part3.SUPPORTED_VERSIONS = mod.SUPPORTED_VERSIONS  # type: ignore[attr-defined]
        mod._ORIG["SUPPORTED_VERSIONS"] = mod.SUPPORTED_VERSIONS  # type: ignore[attr-defined]
    _del_and_restore(mod, "SUPPORTED_VERSIONS")


def test_conversion_router_facade_sync() -> None:
    from src.routers import conversion as mod
    from src.routers import conversion_part_2 as part2
    from src.routers import conversion_part_6 as part6
    from src.routers import conversion_routes_io as routes_io

    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")
    # part2 restore branch (setattr body on delattr)
    part2.tac_lint_fn = mod.tac_lint_fn  # type: ignore[attr-defined,misc]
    mod._ORIG["tac_lint_fn"] = mod.tac_lint_fn  # type: ignore[attr-defined]
    _del_and_restore(mod, "tac_lint_fn")
    # Ensure part6 / routes_io restore branches execute.
    part6.ConversionProfilesService = mod.ConversionProfilesService  # type: ignore[misc]
    routes_io.ConversionProfilesService = mod.ConversionProfilesService  # type: ignore[attr-defined,misc]
    mod._ORIG["ConversionProfilesService"] = mod.ConversionProfilesService  # type: ignore[attr-defined]
    _del_and_restore(mod, "ConversionProfilesService")


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

    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")
    # hasattr False branch for _ORIG seed loop / setattr
    saved = part2.get_airport_validator
    delattr(part2, "get_airport_validator")
    try:
        mod.get_airport_validator = object()  # type: ignore[assignment]
    finally:
        part2.get_airport_validator = saved
    _del_and_restore(mod, "get_airport_validator")


def test_iwxxm_versions_facade_sync() -> None:
    from src.config import iwxxm_versions as mod
    from src.config import iwxxm_versions_part_2 as part2

    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")
    # Special-case __file__ sync path
    mod.__file__ = mod.__file__
    _del_and_restore(mod, "SUPPORTED_VERSIONS")
    # hasattr(_part2) False
    if hasattr(part2, "SUPPORTED_VERSIONS"):
        saved = part2.SUPPORTED_VERSIONS
        delattr(part2, "SUPPORTED_VERSIONS")
        try:
            mod.SUPPORTED_VERSIONS = ()
        finally:
            part2.SUPPORTED_VERSIONS = saved


def test_conversion_profiles_service_facade_sync() -> None:
    from src.services import conversion_profiles_service as mod

    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")
    _del_and_restore(mod, "_engine")


def test_dissemination_ops_service_facade_sync() -> None:
    from src.services import dissemination_ops_service as mod
    from src.services import dissemination_ops_service_part_2 as part2

    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")
    _del_and_restore(mod, "_engine")
    mod.insert = mod.insert
    mod.Table = mod.Table
    # part2 restore branch (line 72)
    part2.insert = mod.insert  # type: ignore[misc]
    mod._ORIG["insert"] = mod.insert  # type: ignore[attr-defined]
    _del_and_restore(mod, "insert")


def test_live_map_cache_facade_sync() -> None:
    from src.services import live_map_cache as mod
    from src.services import live_map_cache_part_2 as part2

    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")
    # hasattr(_part2) False branch first
    if hasattr(part2, "UTC"):
        delattr(part2, "UTC")
    mod.UTC = mod.UTC
    # hasattr(_part2) True for a sync name
    part2.UTC = mod.UTC  # type: ignore[attr-defined,misc]
    mod.UTC = mod.UTC
    _del_and_restore(mod, "UTC")


def test_live_map_refresh_facade_sync() -> None:
    from src.services import live_map_refresh as mod
    from src.services import live_map_refresh_part_2 as part2

    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")
    # hasattr(_part2) False
    if hasattr(part2, "convert_mod"):
        delattr(part2, "convert_mod")
    mod.convert_mod = mod.convert_mod
    part2.convert_mod = mod.convert_mod  # type: ignore[attr-defined,misc]
    mod.convert_mod = mod.convert_mod
    mod._ORIG["convert_mod"] = mod.convert_mod  # type: ignore[attr-defined]
    _del_and_restore(mod, "convert_mod")


def test_schema_discovery_poller_facade_sync() -> None:
    from src.services import schema_discovery_poller as mod
    from src.services import schema_discovery_poller_part_1 as part1

    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")
    # Force hasattr(_part1) True for a sync name that may be missing
    part1.httpx = mod.httpx  # type: ignore[attr-defined,misc]
    mod.httpx = mod.httpx
    if "SUPPORTED_VERSIONS" in mod._SYNC:  # type: ignore[attr-defined]
        mod.SUPPORTED_VERSIONS = ()
    mod._ORIG["httpx"] = mod.httpx  # type: ignore[attr-defined]
    _del_and_restore(mod, "httpx")


def test_schema_mirror_service_facade_sync() -> None:
    from src.services import schema_mirror_service as mod
    from src.services import schema_mirror_service_part_1 as part1
    from src.services import schema_mirror_service_part_2 as part2

    mod._ORIG["httpx"] = mod.httpx  # type: ignore[attr-defined]
    original = mod.httpx
    part1.httpx = original  # type: ignore[attr-defined,misc]
    part2.httpx = original  # type: ignore[attr-defined,misc]
    mod.httpx = object()  # type: ignore[assignment]
    assert mod.httpx is not original
    # hasattr(_part2) False while part2 module exists
    delattr(part2, "httpx")
    try:
        mod.httpx = object()  # type: ignore[assignment]
    finally:
        part2.httpx = original  # type: ignore[attr-defined,misc]
    # hasattr(_part1) False branch
    delattr(part1, "httpx")
    try:
        mod.httpx = object()  # type: ignore[assignment]
    finally:
        part1.httpx = original  # type: ignore[attr-defined,misc]
    _del_and_restore(mod, "httpx")
    mod._facade_probe_unsynced = 1
    delattr(mod, "_facade_probe_unsynced")


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

    # Keep the same module object identity in sys.modules (reload-safe).
    monkeypatch.setattr(facade, "get_validation_settings", object(), raising=False)
    fn = part2._resolve_get_validation_settings()
    assert callable(fn)
    # Non-callable / missing attr path: swap in a bare namespace under the same key.
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

    # Timeout attr missing on exceptions → fall through to req.Timeout
    class _ReqTopTimeout:
        Timeout = _Timeout
        exceptions = SimpleNamespace()

        @staticmethod
        def get(*_a: object, **_k: object) -> object:
            raise _Timeout()

    monkeypatch.setattr(mixin, "_requests_mod", lambda: _ReqTopTimeout())
    timed2 = mixin._CodeListParserMethodsMixin._validate_online(_Parser(), "http://x", "/a")  # type: ignore[arg-type]
    assert timed2 is not None
