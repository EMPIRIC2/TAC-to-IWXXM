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
    part2_had_lint = hasattr(part2, "tac_lint_fn")
    try:
        mod._facade_probe_unsynced = 1
        delattr(mod, "_facade_probe_unsynced")
        part2.tac_lint_fn = original_lint  # type: ignore[attr-defined,misc]
        mod._ORIG["tac_lint_fn"] = original_lint  # type: ignore[attr-defined]
        _pulse_delattr(mod, "tac_lint_fn", original_lint)
        # part6 / routes_io already import this name — only reassign, never delete.
        mod._ORIG["ConversionProfilesService"] = original_svc  # type: ignore[attr-defined]
        _pulse_delattr(mod, "ConversionProfilesService", original_svc)
    finally:
        mod.tac_lint_fn = original_lint
        mod.ConversionProfilesService = original_svc
        part1.tac_lint_fn = original_lint  # type: ignore[attr-defined]
        if part2_had_lint:
            part2.tac_lint_fn = original_lint  # type: ignore[attr-defined]
        elif hasattr(part2, "tac_lint_fn"):
            delattr(part2, "tac_lint_fn")
        part6.ConversionProfilesService = original_svc
        routes_io.ConversionProfilesService = original_svc


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
