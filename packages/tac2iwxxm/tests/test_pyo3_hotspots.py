"""T4.4: PyO3 hotspot API contract (ADR-017).

Enabled when ``TAC2IWXXM_REQUIRE_RUST=1`` (CI maturin job / ``make test-tac2iwxxm-native``).
Hotspot implementations land in T4.5.
"""

from __future__ import annotations

import os

import pytest

from tac2iwxxm import rust_module
from tac2iwxxm.native import scan_metar_tokens

METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="

pytestmark = pytest.mark.skipif(
    os.environ.get("TAC2IWXXM_REQUIRE_RUST", "") != "1",
    reason="Set TAC2IWXXM_REQUIRE_RUST=1 after maturin develop (CI rust / T4.5 gate)",
)


def test_rust_module_exposes_scan_metar_tokens() -> None:
    mod = rust_module()
    assert mod is not None
    assert callable(getattr(mod, "scan_metar_tokens", None))


def test_scan_metar_tokens_returns_non_empty_for_metar() -> None:
    tokens = scan_metar_tokens(METAR)
    assert isinstance(tokens, list)
    assert tokens == [
        "METAR",
        "KJFK",
        "231751Z",
        "18012KT",
        "10SM",
        "FEW040",
        "15/07",
        "A3005",
    ]
    assert "=" not in "".join(tokens)
