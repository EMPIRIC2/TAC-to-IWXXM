"""T3.1: PyO3 / maturin scaffold smoke (E10-36; ADR-017 pattern)."""

from __future__ import annotations

import os

import pytest

from iwxxm_validate import rust_available, rust_module


def test_rust_available_is_bool() -> None:
    assert isinstance(rust_available(), bool)


def test_rust_module_none_or_extension() -> None:
    from importlib.metadata import version

    mod = rust_module()
    if rust_available():
        assert mod is not None
        assert mod.ping() == "pong"
        assert mod.extension_version() == version("iwxxm-validate")
    else:
        assert mod is None


@pytest.mark.skipif(
    os.environ.get("IWXXM_VALIDATE_REQUIRE_RUST", "") != "1",
    reason="Set IWXXM_VALIDATE_REQUIRE_RUST=1 after maturin develop (CI rust job)",
)
def test_rust_extension_required_in_ci() -> None:
    assert rust_available() is True
    mod = rust_module()
    assert mod is not None
    assert mod.ping() == "pong"
