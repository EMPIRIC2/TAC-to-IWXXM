"""Pin ↔ Schematron missing / mismatch failure paths (EV-stage coverage expansion).

[Corpus: tests] — pure unit tests with tmp paths; no vendor schema edits.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from iwxxm_validate.pin_sch import (
    PinSchError,
    assert_pin_schematron_match,
    clear_pin_sch_cache,
    expected_iwxxm_namespace,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_pin_sch_cache()


def _const_path(path: Path) -> Callable[[str], Path]:
    def _inner(_pin: str) -> Path:
        del _pin
        return path

    return _inner


def test_unsupported_pin_raises_pin_sch_error() -> None:
    with pytest.raises(PinSchError, match="unsupported IWXXM pin"):
        expected_iwxxm_namespace("2099-9")
    with pytest.raises(PinSchError, match="unsupported IWXXM pin"):
        assert_pin_schematron_match("2099-9")


def test_missing_pin_tree_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    from iwxxm_validate import pin_sch

    def _missing(_pin: str) -> Path:
        raise FileNotFoundError("pin tree missing")

    monkeypatch.setattr(pin_sch, "version_dir", _missing)
    with pytest.raises(PinSchError, match="pin tree missing"):
        assert_pin_schematron_match("2025-2")


def test_schematron_outside_pin_tree_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
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


def test_schematron_namespace_mismatch_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
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


def test_schematron_unreadable_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from iwxxm_validate import pin_sch

    fake_root = tmp_path / "3.0.0"
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
            raise OSError("permission denied")
        return real_read(self, encoding=encoding, errors=errors)

    monkeypatch.setattr(pin_sch, "version_dir", _const_path(fake_root))
    monkeypatch.setattr(pin_sch, "xsd_path", _const_path(xsd))
    monkeypatch.setattr(pin_sch, "schematron_path", _const_path(sch))
    monkeypatch.setattr(Path, "read_text", _boom_read)
    with pytest.raises(PinSchError, match="cannot read Schematron"):
        assert_pin_schematron_match("3.0.0")
