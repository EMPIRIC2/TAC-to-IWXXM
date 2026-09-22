"""TC-EVYFC-004 — IWXXM pin ↔ Schematron bundle match (#1231 / D-YFC-05)."""

from __future__ import annotations

import importlib
from collections.abc import Callable
from pathlib import Path

import pytest
from iwxxm_validate.api import validate
from iwxxm_validate.pin_sch import (
    PinSchError,
    assert_pin_schematron_match,
    expected_iwxxm_namespace,
)
from iwxxm_validate.validate_iwxxm import validate_iwxxm

_PINS = ("2023-1", "2025-2", "3.0.0")


def _const_path(path: Path) -> Callable[[str], Path]:
    def _inner(_pin: str) -> Path:
        del _pin
        return path

    return _inner


@pytest.mark.parametrize("pin", _PINS)
def test_tc_evyfc_004_pin_sch_match_ok(pin: str) -> None:
    bundle = assert_pin_schematron_match(pin)
    assert bundle.pin == pin
    assert bundle.xsd.is_file()
    assert bundle.schematron.is_file()
    assert bundle.namespace_uri == expected_iwxxm_namespace(pin)
    assert bundle.schematron.parent.name == "rule"


def test_tc_evyfc_004_unknown_pin_raises() -> None:
    with pytest.raises(PinSchError, match="unsupported IWXXM pin"):
        assert_pin_schematron_match("2099-9")


def test_tc_evyfc_004_validate_reports_pin_sch_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(pin: str) -> None:
        del pin
        raise PinSchError("forced mismatch")

    monkeypatch.setattr("iwxxm_validate.api.assert_pin_schematron_match", _boom)
    report = validate("<root/>", iwxxm_version="2025-2")
    assert report.ok is False
    assert any(i.code == "PIN_SCH_MISMATCH" for i in report.issues)


def test_tc_evyfc_004_validate_iwxxm_reports_pin_sch_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _boom(pin: str) -> None:
        del pin
        raise PinSchError("forced mismatch")

    # Package __init__ re-exports ``validate_iwxxm`` and shadows the submodule path.
    mod = importlib.import_module("iwxxm_validate.validate_iwxxm")
    monkeypatch.setattr(mod, "assert_pin_schematron_match", _boom)
    report = validate_iwxxm("<root/>", iwxxm_version="2025-2")
    assert report.ok is False
    assert any(i.code == "PIN_SCH_MISMATCH" for i in report.issues)


def test_tc_evyfc_004_sch_namespace_mismatch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from iwxxm_validate import pin_sch

    fake_root = tmp_path / "2025-2"
    iwxxm = fake_root / "IWXXM"
    rule = iwxxm / "rule"
    rule.mkdir(parents=True)
    xsd = iwxxm / "iwxxm.xsd"
    sch = rule / "iwxxm.sch"
    xsd.write_text("<xs:schema/>", encoding="utf-8")
    sch.write_text(
        '<sch:schema><sch:ns prefix="iwxxm" uri="http://icao.int/iwxxm/2023-1"/></sch:schema>',
        encoding="utf-8",
    )
    monkeypatch.setattr(pin_sch, "version_dir", _const_path(fake_root))
    monkeypatch.setattr(pin_sch, "xsd_path", _const_path(xsd))
    monkeypatch.setattr(pin_sch, "schematron_path", _const_path(sch))
    with pytest.raises(PinSchError, match="must declare iwxxm namespace"):
        assert_pin_schematron_match("2025-2")


def test_tc_evyfc_004_missing_bundle_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    from iwxxm_validate import pin_sch

    def _missing(_pin: str) -> Path:
        raise FileNotFoundError("no such pin tree")

    monkeypatch.setattr(pin_sch, "version_dir", _missing)
    with pytest.raises(PinSchError, match="no such pin tree"):
        assert_pin_schematron_match("2025-2")


def test_tc_evyfc_004_path_outside_pin_tree(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from iwxxm_validate import pin_sch

    fake_root = tmp_path / "2025-2"
    fake_root.mkdir()
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    xsd = outside / "iwxxm.xsd"
    sch = outside / "iwxxm.sch"
    xsd.write_text("<xs:schema/>", encoding="utf-8")
    sch.write_text(
        '<sch:ns prefix="iwxxm" uri="http://icao.int/iwxxm/2025-2"/>',
        encoding="utf-8",
    )
    monkeypatch.setattr(pin_sch, "version_dir", _const_path(fake_root))
    monkeypatch.setattr(pin_sch, "xsd_path", _const_path(xsd))
    monkeypatch.setattr(pin_sch, "schematron_path", _const_path(sch))
    with pytest.raises(PinSchError, match="must live under"):
        assert_pin_schematron_match("2025-2")


def test_tc_evyfc_004_sch_unreadable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from iwxxm_validate import pin_sch

    fake_root = tmp_path / "2025-2"
    iwxxm = fake_root / "IWXXM"
    rule = iwxxm / "rule"
    rule.mkdir(parents=True)
    xsd = iwxxm / "iwxxm.xsd"
    sch = rule / "iwxxm.sch"
    xsd.write_text("<xs:schema/>", encoding="utf-8")
    sch.write_text("placeholder", encoding="utf-8")

    real_read = Path.read_text

    def _boom_read(self: Path, encoding: str | None = None, errors: str | None = None) -> str:
        if self == sch:
            raise OSError("cannot read")
        return real_read(self, encoding=encoding, errors=errors)

    monkeypatch.setattr(pin_sch, "version_dir", _const_path(fake_root))
    monkeypatch.setattr(pin_sch, "xsd_path", _const_path(xsd))
    monkeypatch.setattr(pin_sch, "schematron_path", _const_path(sch))
    monkeypatch.setattr(Path, "read_text", _boom_read)
    with pytest.raises(PinSchError, match="cannot read Schematron"):
        assert_pin_schematron_match("2025-2")


def test_tc_evyfc_004_single_quoted_namespace_ok(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from iwxxm_validate import pin_sch

    fake_root = tmp_path / "2025-2"
    iwxxm = fake_root / "IWXXM"
    rule = iwxxm / "rule"
    rule.mkdir(parents=True)
    xsd = iwxxm / "iwxxm.xsd"
    sch = rule / "iwxxm.sch"
    xsd.write_text("<xs:schema/>", encoding="utf-8")
    sch.write_text(
        "<sch:schema><sch:ns prefix='iwxxm' uri='http://icao.int/iwxxm/2025-2'/></sch:schema>",
        encoding="utf-8",
    )
    monkeypatch.setattr(pin_sch, "version_dir", _const_path(fake_root))
    monkeypatch.setattr(pin_sch, "xsd_path", _const_path(xsd))
    monkeypatch.setattr(pin_sch, "schematron_path", _const_path(sch))
    bundle = assert_pin_schematron_match("2025-2")
    assert bundle.namespace_uri == "http://icao.int/iwxxm/2025-2"
