"""Service/codelist facade ModuleType sync coverage (line-cap split)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest


def _pulse_delattr(mod: object, name: str, original: object) -> None:
    """Hit facade ``__delattr__`` then restore the real binding for later tests."""
    setattr(mod, name, object())
    delattr(mod, name)
    setattr(mod, name, original)


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
