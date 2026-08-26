"""EV-037 TD-3a: api_deps patch surface contract."""

from __future__ import annotations

import inspect

import pytest

from src import api as api_module
from src import api_deps

# Symbols unit tests monkeypatch on ``src.api`` (grep inventory 2026-08-26).
PATCH_SURFACE = frozenset(
    {
        "ValidationService",
        "_call_iwxxm_validate",
        "classify_and_validate_upload_content",
        "convert_metar_tac_with_metadata",
        "get_icao_region",
        "get_translation_centre_info",
        "get_validation_orchestrator",
        "iwxxm_validate_fn",
        "msgspec_json_response",
        "read_upload_files_text",
        "read_uploaded_text",
        "statistics_service",
        "tac2iwxxm_split_bulletin",
        "webhook_service",
    }
)


def test_api_deps_exports_patch_surface() -> None:
    missing = sorted(name for name in PATCH_SURFACE if not hasattr(api_deps, name))
    assert missing == []


def test_api_reexports_match_api_deps() -> None:
    for name in PATCH_SURFACE:
        assert hasattr(api_module, name), f"api missing re-export: {name}"
        assert getattr(api_module, name) is getattr(api_deps, name), name


def test_api_module_patch_reaches_handler_globals(monkeypatch: pytest.MonkeyPatch) -> None:
    """Monkeypatch on api_module must update api globals used by route handlers."""

    sentinel = object()

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", sentinel)
    assert api_module.convert_metar_tac_with_metadata is sentinel

    # Handler globals resolve at call time in the api module namespace.
    frame = inspect.currentframe()
    assert frame is not None
    caller_globals = frame.f_globals
    assert caller_globals.get("convert_metar_tac_with_metadata") is not sentinel  # test module scope

    # Simulate handler lookup: api module __dict__
    assert api_module.__dict__["convert_metar_tac_with_metadata"] is sentinel


def test_iwxxm_validate_lazy_lookup_uses_api_reexport(monkeypatch: pytest.MonkeyPatch) -> None:
    from src import api_wire

    def fake_sdk(**_kwargs):
        return "patched"

    monkeypatch.setattr(api_module, "iwxxm_validate_fn", fake_sdk)
    assert api_wire._iwxxm_validate_fn() is fake_sdk
