"""Unit tests for Schematron validator branches and cache behavior."""

from __future__ import annotations

import builtins
from pathlib import Path
from types import SimpleNamespace

import pytest
from lxml import etree, isoschematron

from src.utilities.schematron_validator import (
    SchematronValidator,
    get_schematron_validator,
    validate_schematron,
)


class _FakeSchematron:
    def __init__(self, valid=True, report=None):
        self._valid = valid
        self.validation_report = report

    def validate(self, _xml_doc):
        return self._valid


def test_setup_working_directory_missing_dir_raises(monkeypatch):
    validator = SchematronValidator()
    validator.registry = SimpleNamespace(get_codelists_dir=lambda _version: Path("/missing"))

    with monkeypatch.context() as m:
        m.setattr(Path, "exists", lambda self: False)
        try:
            validator._setup_working_directory("2025-2")
            assert False
        except FileNotFoundError:
            assert True


def test_setup_working_directory_no_rdf_files_raises(tmp_path):
    validator = SchematronValidator()
    validator.registry = SimpleNamespace(get_codelists_dir=lambda _version: tmp_path)

    try:
        validator._setup_working_directory("2025-2")
        assert False
    except FileNotFoundError:
        assert True


def test_get_compiled_schematron_returns_none_for_2025_xslt2(monkeypatch, tmp_path):
    validator = SchematronValidator()

    sch_path = tmp_path / "iwxxm.sch"
    sch_path.write_text('<schema queryBinding="xslt2"></schema>', encoding="utf-8")
    validator.registry = SimpleNamespace(get_schematron_path=lambda _version: sch_path)

    result = validator._get_compiled_schematron("2025-2")
    assert result is None


def test_get_compiled_schematron_uses_cache(monkeypatch):
    validator = SchematronValidator()
    fake = _FakeSchematron(valid=True, report=None)
    validator._schematron_cache["2023-1"] = fake

    result = validator._get_compiled_schematron("2023-1")
    assert result is fake


def test_parse_svrl_report_extracts_failed_and_successful_reports():
    validator = SchematronValidator()
    report = etree.fromstring(
        b"""
        <svrl:schematron-output xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
          <svrl:failed-assert id="RULE1" test="x" location="/root/a">
            <svrl:text>failed msg</svrl:text>
          </svrl:failed-assert>
          <svrl:successful-report id="RULE2" test="y" location="/root/b">
            <svrl:text>warn msg</svrl:text>
          </svrl:successful-report>
        </svrl:schematron-output>
        """
    )

    issues = validator._parse_svrl_report(_FakeSchematron(report=report), "2025-2")

    codes = {issue.code for issue in issues}
    assert "RULE1" in codes
    assert "RULE2" in codes


def test_validate_invalid_xml_reports_syntax_error():
    validator = SchematronValidator()

    result = validator.validate("<root>", "2025-2")

    assert result.is_valid is False
    assert result.issues[0].code == "XML_SYNTAX_ERROR"


def test_validate_skipped_schematron_returns_non_blocking_warning(monkeypatch):
    validator = SchematronValidator()
    monkeypatch.setattr(validator, "_get_compiled_schematron", lambda _version: None)

    result = validator.validate("<root/>", "2025-2")

    assert result.is_valid is True
    assert result.issues[0].code == "SCHEMATRON_SKIPPED"


def test_validate_not_found_returns_error(monkeypatch):
    validator = SchematronValidator()
    monkeypatch.setattr(
        validator,
        "_get_compiled_schematron",
        lambda _version: (_ for _ in ()).throw(FileNotFoundError("missing")),
    )

    result = validator.validate("<root/>", "2025-2")

    assert result.is_valid is False
    assert result.issues[0].code == "SCHEMATRON_NOT_FOUND"


def test_validate_collects_svrl_issues(monkeypatch):
    validator = SchematronValidator()
    report = etree.fromstring(
        b"""
        <svrl:schematron-output xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
          <svrl:failed-assert id="RULE1" location="/root/a">
            <svrl:text>failed msg</svrl:text>
          </svrl:failed-assert>
        </svrl:schematron-output>
        """
    )

    monkeypatch.setattr(
        validator,
        "_get_compiled_schematron",
        lambda _version: _FakeSchematron(valid=False, report=report),
    )

    result = validator.validate("<root/>", "2025-2")

    assert result.is_valid is False
    assert result.rules_evaluated == 1
    assert result.issues[0].code == "RULE1"


def test_validate_unexpected_exception_wrapped(monkeypatch):
    validator = SchematronValidator()
    monkeypatch.setattr(
        validator,
        "_parse_svrl_report",
        lambda _schematron, _version: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    monkeypatch.setattr(
        validator,
        "_get_compiled_schematron",
        lambda _version: _FakeSchematron(valid=True, report=etree.Element("x")),
    )

    result = validator.validate("<root/>", "2025-2")

    assert result.is_valid is False
    assert result.issues[0].code == "RuntimeError"


def test_clear_cache_removes_working_dirs(tmp_path):
    validator = SchematronValidator()
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / "a.rdf").write_text("x", encoding="utf-8")

    validator._schematron_cache["2025-2"] = _FakeSchematron()
    validator._working_dirs["2025-2"] = work_dir

    validator.clear_cache("2025-2")

    assert "2025-2" not in validator._schematron_cache
    assert "2025-2" not in validator._working_dirs


def test_singleton_and_wrapper(monkeypatch):
    one = get_schematron_validator()
    two = get_schematron_validator()
    assert one is two

    validator = SchematronValidator()
    monkeypatch.setattr("src.utilities.schematron_validator.get_schematron_validator", lambda: validator)
    monkeypatch.setattr(
        validator,
        "validate",
        lambda xml_content, version: SimpleNamespace(is_valid=True, issues=[], schema_version=version),
    )

    result = validate_schematron("<root/>", "2025-2")
    assert result.is_valid is True
    assert result.schema_version == "2025-2"


def test_setup_working_directory_reuses_cached_path(tmp_path):
    validator = SchematronValidator()
    validator._working_dirs["2025-2"] = tmp_path
    assert validator._setup_working_directory("2025-2") == tmp_path


def test_setup_working_directory_copies_rdf_files(tmp_path):
    validator = SchematronValidator()
    codelists = tmp_path / "rule"
    codelists.mkdir()
    for name in [
        "codes.wmo.int-common-nil.rdf",
        "codes.wmo.int-49-2-AerodromeRecentWeather.rdf",
        "codes.wmo.int-49-2-CloudAmountReportedAtAerodrome.rdf",
    ]:
        (codelists / name).write_text("<rdf:RDF/>", encoding="utf-8")

    validator.registry = SimpleNamespace(get_codelists_dir=lambda _version: codelists)
    work_dir = validator._setup_working_directory("2023-1")
    assert (work_dir / "codes.wmo.int-common-nil.rdf").exists()

    validator.clear_cache("2023-1")


def test_parse_svrl_report_handles_none_report():
    validator = SchematronValidator()
    issues = validator._parse_svrl_report(_FakeSchematron(report=None), "2025-2")
    assert issues == []


def test_get_compiled_schematron_missing_file_raises(tmp_path):
    validator = SchematronValidator()
    validator.registry = SimpleNamespace(get_schematron_path=lambda _version: tmp_path / "missing.sch")
    with pytest.raises(FileNotFoundError):
        validator._get_compiled_schematron("2023-1")


def test_clear_cache_all_clears_everything(tmp_path):
    validator = SchematronValidator()
    work_dir = tmp_path / "work_all"
    work_dir.mkdir()
    validator._schematron_cache["2023-1"] = _FakeSchematron()
    validator._working_dirs["2023-1"] = work_dir

    validator.clear_cache()
    assert validator._schematron_cache == {}
    assert validator._working_dirs == {}


def test_setup_working_directory_warns_when_required_rdf_missing(tmp_path):
    validator = SchematronValidator()
    codelists = tmp_path / "rule"
    codelists.mkdir()
    # Intentionally omit required RDF names to trigger warning path.
    (codelists / "codes.wmo.int-49-2-Other.rdf").write_text("<rdf:RDF/>", encoding="utf-8")

    validator.registry = SimpleNamespace(get_codelists_dir=lambda _version: codelists)
    work_dir = validator._setup_working_directory("2023-1")
    assert work_dir.exists()

    validator.clear_cache("2023-1")


def test_get_compiled_schematron_read_check_exception_continues(monkeypatch, tmp_path):
    validator = SchematronValidator()
    sch_path = tmp_path / "iwxxm.sch"
    sch_path.write_text("<schema></schema>", encoding="utf-8")
    validator.registry = SimpleNamespace(get_schematron_path=lambda _version: sch_path)

    real_open = builtins.open

    def _fake_open(path, mode="r", *args, **kwargs):
        if str(path).endswith("iwxxm.sch") and "r" in mode and "b" not in mode:
            raise OSError("read check failed")
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", _fake_open)
    monkeypatch.setattr(validator, "_setup_working_directory", lambda _version: tmp_path)
    monkeypatch.setattr(etree, "parse", lambda *_args, **_kwargs: etree.ElementTree(etree.Element("schema")))
    monkeypatch.setattr(
        isoschematron,
        "Schematron",
        lambda *_args, **_kwargs: _FakeSchematron(valid=True, report=etree.Element("svrl")),
    )

    compiled = validator._get_compiled_schematron("2023-1")
    assert compiled is not None


def test_get_compiled_schematron_xslt2_exception_returns_none(monkeypatch, tmp_path):
    validator = SchematronValidator()
    sch_path = tmp_path / "iwxxm.sch"
    sch_path.write_text("<schema></schema>", encoding="utf-8")
    validator.registry = SimpleNamespace(get_schematron_path=lambda _version: sch_path)

    monkeypatch.setattr(validator, "_setup_working_directory", lambda _version: tmp_path)
    monkeypatch.setattr(etree, "parse", lambda *_args, **_kwargs: etree.ElementTree(etree.Element("schema")))

    def _boom(*_args, **_kwargs):
        raise RuntimeError("XSLT2 processor missing")

    monkeypatch.setattr(isoschematron, "Schematron", _boom)

    compiled = validator._get_compiled_schematron("2025-2")
    assert compiled is None


def test_clear_cache_version_without_working_dir(tmp_path):
    validator = SchematronValidator()
    validator._schematron_cache["2025-2"] = _FakeSchematron()
    # Do not create matching _working_dirs entry to hit non-working-dir branch.
    validator.clear_cache("2025-2")
    assert "2025-2" not in validator._schematron_cache


def test_setup_working_directory_uses_iwxxm_nil_for_2025_2(tmp_path):
    validator = SchematronValidator()
    codelists = tmp_path / "rule"
    codelists.mkdir()
    required = [
        "codes.wmo.int-iwxxm-nil.rdf",
        "codes.wmo.int-49-2-AerodromeRecentWeather.rdf",
        "codes.wmo.int-49-2-CloudAmountReportedAtAerodrome.rdf",
    ]
    for name in required:
        (codelists / name).write_text("<rdf:RDF/>", encoding="utf-8")

    validator.registry = SimpleNamespace(get_codelists_dir=lambda _version: codelists)
    work_dir = validator._setup_working_directory("2025-2")
    assert work_dir.exists()
    assert (work_dir / "codes.wmo.int-iwxxm-nil.rdf").exists()


def test_get_compiled_schematron_query_binding_read_failure_continues(monkeypatch, tmp_path):
    validator = SchematronValidator()
    sch_path = tmp_path / "iwxxm.sch"
    sch_path.write_text('<schema queryBinding="xslt1"></schema>', encoding="utf-8")
    validator.registry = SimpleNamespace(get_schematron_path=lambda _version: sch_path)

    real_open = builtins.open

    def _fake_open(path, mode="r", *args, **kwargs):
        if str(path).endswith("iwxxm.sch") and "r" in mode and "b" not in mode:
            raise OSError("cannot read sch")
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", _fake_open)
    monkeypatch.setattr(validator, "_setup_working_directory", lambda _version: tmp_path)
    monkeypatch.setattr(etree, "parse", lambda *_args, **_kwargs: etree.ElementTree(etree.Element("schema")))
    monkeypatch.setattr(
        isoschematron,
        "Schematron",
        lambda *_args, **_kwargs: _FakeSchematron(valid=True, report=etree.Element("svrl")),
    )

    compiled = validator._get_compiled_schematron("2023-1")
    assert compiled is not None


def test_get_compiled_schematron_xml_syntax_error_raises(tmp_path):
    validator = SchematronValidator()
    sch_path = tmp_path / "iwxxm.sch"
    sch_path.write_text("<schema><unclosed>", encoding="utf-8")
    codelists = tmp_path / "codelists"
    codelists.mkdir()
    for name in [
        "codes.wmo.int-common-nil.rdf",
        "codes.wmo.int-49-2-AerodromeRecentWeather.rdf",
        "codes.wmo.int-49-2-CloudAmountReportedAtAerodrome.rdf",
    ]:
        (codelists / name).write_text("<rdf:RDF/>", encoding="utf-8")

    validator.registry = SimpleNamespace(
        get_schematron_path=lambda _version: sch_path,
        get_codelists_dir=lambda _version: codelists,
    )

    with pytest.raises(etree.XMLSyntaxError):
        validator._get_compiled_schematron("2023-1")
