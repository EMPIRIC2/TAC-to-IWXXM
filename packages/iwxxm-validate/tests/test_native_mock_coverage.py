"""Native loader coverage — success (real/fake) + ImportError branches (EV-047)."""

from __future__ import annotations

import builtins
import types
from typing import Any

import pytest

import iwxxm_validate
from iwxxm_validate import native


def _install_fake_rust(monkeypatch: pytest.MonkeyPatch, *, clearer: Any = "callable") -> types.SimpleNamespace:
    calls: list[str] = []

    def _clear() -> None:
        calls.append("clear")

    fake = types.SimpleNamespace(
        clear_schema_caches=_clear if clearer == "callable" else "not-callable",
        calls=calls,
    )
    monkeypatch.setattr(iwxxm_validate, "_rust", fake, raising=False)
    return fake


def _force_rust_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make ``from iwxxm_validate import _rust`` raise ImportError."""
    real_import = builtins.__import__

    def _import(name: str, globals: Any = None, locals: Any = None, fromlist: Any = (), level: int = 0) -> Any:
        mod = real_import(name, globals, locals, fromlist, level)
        if name == "iwxxm_validate" and fromlist and "_rust" in fromlist:
            raise ImportError("forced missing iwxxm_validate._rust")
        return mod

    monkeypatch.setattr(builtins, "__import__", _import)


def test_rust_available_and_module_when_extension_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _install_fake_rust(monkeypatch)
    assert native.rust_available() is True
    assert native.rust_module() is fake


def test_rust_import_error_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    _force_rust_import_error(monkeypatch)
    assert native.rust_available() is False
    assert native.rust_module() is None


def test_clear_schema_caches_invokes_native_clearer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _install_fake_rust(monkeypatch)
    native.clear_schema_caches()
    assert fake.calls == ["clear"]


def test_clear_schema_caches_noop_without_extension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(native, "rust_module", lambda: None)
    native.clear_schema_caches()  # no-op


def test_clear_schema_caches_skips_non_callable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_rust(monkeypatch, clearer="not-callable")
    native.clear_schema_caches()  # attribute present but not callable
