"""Unit tests for ValidationService branch behavior."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.schemas.validation import ValidationLayer
from src.services import validation as val


class _FakeAirportValidator:
    def __init__(self, known_codes=None):
        self.known_codes = known_codes or {"KJFK"}

    def count(self):
        return 1

    def validate_icao(self, icao):
        return icao in self.known_codes

    def get_airport(self, icao):
        if icao in self.known_codes:
            return SimpleNamespace(name="JFK", city="New York", country="US")
        return None


def _make_service(monkeypatch, known_codes=None):
    monkeypatch.setattr(val, "get_airport_validator", lambda: _FakeAirportValidator(known_codes))
    return val.ValidationService()


def test_validate_airport_icao_success_with_metadata(monkeypatch):
    service = _make_service(monkeypatch, {"KJFK"})
    monkeypatch.setattr(service, "_extract_icao_from_tac", lambda _tac: "KJFK")

    result = service.validate_airport_icao("METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013")

    assert result.passed is True
    assert result.layer == ValidationLayer.AIRPORT_ICAO
    assert result.metadata["icao"] == "KJFK"


def test_validate_airport_icao_missing_code(monkeypatch):
    service = _make_service(monkeypatch)
    monkeypatch.setattr(service, "_extract_icao_from_tac", lambda _tac: None)

    with pytest.raises(val.ValidationError, match="No ICAO code"):
        service.validate_airport_icao("METAR 010000Z")


def test_validate_airport_icao_invalid_format(monkeypatch):
    service = _make_service(monkeypatch)
    monkeypatch.setattr(service, "_extract_icao_from_tac", lambda _tac: "ABC")

    with pytest.raises(val.ValidationError, match="Invalid ICAO code format"):
        service.validate_airport_icao("METAR ABC 010000Z")


def test_validate_airport_icao_unknown_code(monkeypatch):
    service = _make_service(monkeypatch, {"KLAX"})
    monkeypatch.setattr(service, "_extract_icao_from_tac", lambda _tac: "KJFK")

    with pytest.raises(val.ValidationError, match="Unknown ICAO code"):
        service.validate_airport_icao("METAR KJFK 010000Z")


def test_validate_airport_icao_wraps_unexpected_exception(monkeypatch):
    service = _make_service(monkeypatch)
    monkeypatch.setattr(service, "_extract_icao_from_tac", lambda _tac: "KJFK")
    monkeypatch.setattr(service.airport_validator, "validate_icao", lambda _icao: (_ for _ in ()).throw(RuntimeError("db down")))

    with pytest.raises(val.ValidationError, match="ICAO validation error"):
        service.validate_airport_icao("METAR KJFK 010000Z")


def test_validate_tac_syntax_detects_keyword_timestamp_length_tabs(monkeypatch):
    service = _make_service(monkeypatch)

    result = service.validate_tac_syntax("NOPE\t")

    codes = {issue.code for issue in result.issues}
    assert "MISSING_KEYWORD" in codes
    assert "MISSING_TIMESTAMP" in codes
    assert "SHORT_MESSAGE" in codes
    assert "CONTAINS_TABS" in codes
    assert result.passed is False


def test_validate_tac_syntax_passes_for_valid_metar(monkeypatch):
    service = _make_service(monkeypatch)

    result = service.validate_tac_syntax("METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013")

    assert result.passed is True
    assert result.issues == []


def test_validate_all_layers_stops_when_icao_fails(monkeypatch):
    service = _make_service(monkeypatch)
    monkeypatch.setattr(service, "validate_airport_icao", lambda _tac: (_ for _ in ()).throw(val.ValidationError("boom")))

    aggregated = service.validate_all_layers("METAR KJFK 010000Z")

    assert aggregated.passed is False
    assert len(aggregated.results) == 1
    assert aggregated.results[0].layer == ValidationLayer.AIRPORT_ICAO
    assert aggregated.results[0].issues[0].code == "ICAO_VALIDATION_FAILED"


def test_extract_icao_from_tac_fallback(monkeypatch):
    monkeypatch.setattr(val, "extract_airport_code", lambda _tac: None)

    extracted = val.ValidationService._extract_icao_from_tac("SOMETHING KDEN EXTRA")

    assert extracted == "KDEN"


def test_get_validation_service_singleton(monkeypatch):
    val._validation_service = None
    monkeypatch.setattr(val, "get_airport_validator", lambda: _FakeAirportValidator({"KJFK"}))

    first = val.get_validation_service()
    second = val.get_validation_service()

    assert first is second
