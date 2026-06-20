"""Unit tests for XSD validator branches and cache behavior."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from lxml import etree

from src.utilities.xsd_validator import XSDValidator, get_xsd_validator, validate_xml_schema


class _FakeSchema:
    def __init__(self, valid: bool = True, error_log=None, should_raise: bool = False):
        self._valid = valid
        self.error_log = error_log or []
        self._should_raise = should_raise

    def validate(self, _xml_doc):
        if self._should_raise:
            raise RuntimeError("schema validate boom")
        return self._valid


def test_validate_reports_xml_syntax_error():
    validator = XSDValidator()

    result = validator.validate("<root>", "2025-2")

    assert result.is_valid is False
    assert result.issues[0].code == "XML_SYNTAX_ERROR"


def test_validate_schema_import_warning_is_non_blocking(monkeypatch):
    validator = XSDValidator()

    def raise_parse(_version):
        raise etree.XMLSchemaParseError("substitutionGroup missing for 2025 schema")

    monkeypatch.setattr(validator, "_get_compiled_schema", raise_parse)

    result = validator.validate("<root/>", "2025-2")

    assert result.is_valid is True
    assert result.issues[0].code == "SCHEMA_IMPORT_WARNING"


def test_validate_schema_parse_error_blocks(monkeypatch):
    validator = XSDValidator()

    monkeypatch.setattr(
        validator,
        "_get_compiled_schema",
        lambda _version: (_ for _ in ()).throw(etree.XMLSchemaParseError("fatal parse")),
    )

    result = validator.validate("<root/>", "2023-1")

    assert result.is_valid is False
    assert result.issues[0].code == "SCHEMA_PARSE_ERROR"


def test_validate_schema_not_available_from_value_error(monkeypatch):
    validator = XSDValidator()
    monkeypatch.setattr(
        validator,
        "_get_compiled_schema",
        lambda _version: (_ for _ in ()).throw(ValueError("unsupported")),
    )

    result = validator.validate("<root/>", "9999-9")

    assert result.is_valid is False
    assert result.issues[0].code == "SCHEMA_NOT_AVAILABLE"


def test_validate_schema_not_available_from_missing_file(monkeypatch):
    validator = XSDValidator()
    monkeypatch.setattr(
        validator,
        "_get_compiled_schema",
        lambda _version: (_ for _ in ()).throw(FileNotFoundError("missing")),
    )

    result = validator.validate("<root/>", "2025-2")

    assert result.is_valid is False
    assert result.issues[0].code == "SCHEMA_NOT_AVAILABLE"


def test_validate_schema_none_is_skipped(monkeypatch):
    validator = XSDValidator()
    monkeypatch.setattr(validator, "_get_compiled_schema", lambda _version: None)

    result = validator.validate("<root/>", "2025-2")

    assert result.is_valid is True
    assert result.issues[0].code == "SCHEMA_SKIPPED"


def test_validate_schema_invalid_collects_error_log(monkeypatch):
    validator = XSDValidator()

    fake_error = SimpleNamespace(
        message="Element 'x': This element is not expected.",
        line=2,
        column=4,
        path="/root/x",
        type_name="SCHEMAV_ELEMENT_CONTENT",
    )
    schema = _FakeSchema(valid=False, error_log=[fake_error])
    monkeypatch.setattr(validator, "_get_compiled_schema", lambda _version: schema)

    result = validator.validate("<root><x/></root>", "2025-2")

    assert result.is_valid is False
    assert result.issues[0].code == "SCHEMAV_ELEMENT_CONTENT"


def test_validate_schema_unexpected_exception_is_wrapped(monkeypatch):
    validator = XSDValidator()
    schema = _FakeSchema(valid=True, should_raise=True)
    monkeypatch.setattr(validator, "_get_compiled_schema", lambda _version: schema)

    result = validator.validate("<root/>", "2025-2")

    assert result.is_valid is False
    assert result.issues[0].code == "RuntimeError"


def test_get_compiled_schema_uses_cache(monkeypatch):
    validator = XSDValidator()

    class _FakeRegistry:
        def get_xsd_path(self, _version):
            return Path("/tmp/fake.xsd")

    parse_calls = {"count": 0}

    monkeypatch.setattr(validator, "registry", _FakeRegistry())
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(etree, "parse", lambda _path: object())

    def fake_xml_schema(_doc):
        parse_calls["count"] += 1
        return object()

    monkeypatch.setattr(etree, "XMLSchema", fake_xml_schema)

    first = validator._get_compiled_schema("2025-2")
    second = validator._get_compiled_schema("2025-2")

    assert first is second
    assert parse_calls["count"] == 1


def test_get_compiled_schema_missing_file_raises(monkeypatch):
    validator = XSDValidator()

    class _FakeRegistry:
        def get_xsd_path(self, _version):
            return Path("/tmp/does-not-exist.xsd")

    monkeypatch.setattr(validator, "registry", _FakeRegistry())

    with pytest.raises(FileNotFoundError):
        validator._get_compiled_schema("2025-2")


def test_get_compiled_schema_known_2025_issue_caches_none(monkeypatch):
    validator = XSDValidator()

    class _FakeRegistry:
        def get_xsd_path(self, _version):
            return Path("/tmp/fake.xsd")

    monkeypatch.setattr(validator, "registry", _FakeRegistry())
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(etree, "parse", lambda _path: object())
    monkeypatch.setattr(
        etree,
        "XMLSchema",
        lambda _doc: (_ for _ in ()).throw(etree.XMLSchemaParseError("substitutionGroup unresolved for 2025 schema")),
    )

    with pytest.raises(etree.XMLSchemaParseError):
        validator._get_compiled_schema("2025-2")

    assert "2025-2" in validator._schema_cache
    assert validator._schema_cache["2025-2"] is None


def test_clear_cache_specific_and_all():
    validator = XSDValidator()
    validator._schema_cache = {"2025-2": object(), "2023-1": object()}

    validator.clear_cache("2025-2")
    assert "2025-2" not in validator._schema_cache
    assert "2023-1" in validator._schema_cache

    validator.clear_cache()
    assert validator._schema_cache == {}


def test_singleton_and_wrapper(monkeypatch):
    singleton_one = get_xsd_validator()
    singleton_two = get_xsd_validator()
    assert singleton_one is singleton_two

    validator = XSDValidator()
    monkeypatch.setattr("src.utilities.xsd_validator.get_xsd_validator", lambda: validator)
    monkeypatch.setattr(
        validator,
        "validate",
        lambda xml_content, version: SimpleNamespace(is_valid=True, issues=[], schema_version=version),
    )

    result = validate_xml_schema("<root/>", "2025-2")
    assert result.is_valid is True
    assert result.schema_version == "2025-2"
