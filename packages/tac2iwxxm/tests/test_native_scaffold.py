"""T4.3: PyO3 / maturin scaffold smoke (ADR-017)."""

from __future__ import annotations

import os

import pytest

from tac2iwxxm import rust_available, rust_module


def test_rust_available_is_bool() -> None:
    assert isinstance(rust_available(), bool)


def test_rust_module_none_or_extension() -> None:
    from importlib.metadata import version

    mod = rust_module()
    if rust_available():
        assert mod is not None
        assert mod.ping() == "pong"
        assert mod.extension_version() == version("tac2iwxxm")
    else:
        assert mod is None


@pytest.mark.skipif(
    os.environ.get("TAC2IWXXM_REQUIRE_RUST", "") != "1",
    reason="Set TAC2IWXXM_REQUIRE_RUST=1 after maturin develop (CI rust job)",
)
def test_rust_extension_required_in_ci() -> None:
    assert rust_available() is True
    mod = rust_module()
    assert mod is not None
    assert mod.ping() == "pong"
