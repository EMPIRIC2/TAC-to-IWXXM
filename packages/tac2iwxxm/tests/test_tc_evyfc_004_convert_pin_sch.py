"""TC-EVYFC-004 convert path — pin↔SCH fail-closed; soft-preview waived (#1231)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import ModuleType

import pytest
from iwxxm_validate.pin_sch import PinSchError
from tac2iwxxm.convert import convert

_TAC = "METAR KJFK 121255Z 18008KT 10SM FEW250 22/18 A2992="


def test_tc_evyfc_004_convert_pin_sch_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(pin: str) -> None:
        del pin
        raise PinSchError("forced convert mismatch")

    monkeypatch.setattr("iwxxm_validate.pin_sch.assert_pin_schematron_match", _boom)
    result = convert(_TAC, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is False
    assert any(i.code == "PIN_SCH_MISMATCH" for i in result.issues)


def test_tc_evyfc_004_convert_preview_waives_pin_sch(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(pin: str) -> None:
        del pin
        raise PinSchError("should not run in preview")

    monkeypatch.setattr("iwxxm_validate.pin_sch.assert_pin_schematron_match", _boom)
    result = convert(
        _TAC,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        preview=True,
    )
    assert not any(i.code == "PIN_SCH_MISMATCH" for i in result.issues)


def test_tc_evyfc_004_convert_import_error_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def _guarded(
        name: str,
        globals: Mapping[str, object] | None = None,
        locals: Mapping[str, object] | None = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> ModuleType:
        if name == "iwxxm_validate.pin_sch" or name.startswith("iwxxm_validate.pin_sch"):
            raise ImportError("simulated missing iwxxm_validate")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _guarded)
    result = convert(_TAC, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert not any(i.code == "PIN_SCH_MISMATCH" for i in result.issues)
