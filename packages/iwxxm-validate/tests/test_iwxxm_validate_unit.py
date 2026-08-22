"""Unit coverage for iwxxm-validate internals (T2.2 / coverage gate)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import msgspec
import pytest
from lxml import etree

from iwxxm_validate import validate
from iwxxm_validate.codec import json_decoder, json_encoder
from iwxxm_validate.models import Issue, ValidationReport
from iwxxm_validate.paths import (
    ca_xsd_path,
    codelists_dir,
    repo_root,
    schematron_path,
    us_catalog_path,
    vendor_iwxxm_ca_root,
    vendor_iwxxm_us_root,
    version_dir,
    xsd_path,
)
from iwxxm_validate.schematron import clear_schematron_cache, validate_schematron
from iwxxm_validate.xsd import clear_xsd_cache, validate_xsd


def test_codec_roundtrip_validation_report() -> None:
    report = ValidationReport(
        ok=True,
        iwxxm_version="2023-1",
        profile="annex3",
        issues=[],
    )
    raw = json_encoder.encode(report)
    decoded = json_decoder.decode(raw)
    assert decoded.ok is True
    assert decoded.iwxxm_version == "2023-1"


def test_repo_root_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("IWXXM_VALIDATE_REPO_ROOT", str(tmp_path))
    assert repo_root() == tmp_path.resolve()


def test_repo_root_from_schemas_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    iwxxm = tmp_path / "vendor" / "schemas" / "iwxxm"
    iwxxm.mkdir(parents=True)
    monkeypatch.delenv("IWXXM_VALIDATE_REPO_ROOT", raising=False)
    monkeypatch.setenv("IWXXM_SCHEMAS_ROOT", str(iwxxm))
    assert repo_root() == tmp_path.resolve()


def test_version_dir_missing_raises() -> None:
    with pytest.raises(FileNotFoundError):
        version_dir("9999-9")


def test_xsd_and_schematron_paths_resolve_2023_1() -> None:
    assert xsd_path("2023-1").name == "iwxxm.xsd"
    assert schematron_path("2023-1").name == "iwxxm.sch"
    assert codelists_dir("2023-1").is_dir()
    assert us_catalog_path() is not None
    assert vendor_iwxxm_us_root().is_dir()


def test_ca_eccc_paths_resolve_when_vendored() -> None:
    """TC-EV064-003: iwxxm-ca pin paths resolve for ca_eccc profile."""
    assert vendor_iwxxm_ca_root().is_dir()
    assert ca_xsd_path() is not None
    assert xsd_path("3.0.0").name == "iwxxm.xsd"
    assert schematron_path("3.0.0").name == "iwxxm.sch"


def test_vendor_iwxxm_ca_root_repo_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """When packaged subset is absent, resolve CA schemas from monorepo vendor pin."""
    from iwxxm_validate.paths import vendor_iwxxm_ca_root

    monkeypatch.setattr("iwxxm_validate.paths.packaged_schemas_root", lambda: None)
    root = vendor_iwxxm_ca_root()
    assert root.name == "iwxxm-ca"
    assert root.is_dir()


def test_validate_iwxxm_catalog_roots_include_ca_pin() -> None:
    import importlib

    vi = importlib.import_module("iwxxm_validate.validate_iwxxm")
    roots = vi._catalog_roots("3.0.0", profile="ca_eccc")
    assert any("iwxxm-ca" in entry for entry in roots)


def test_validate_iwxxm_ca_eccc_accepts_3_0_0_rust_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import importlib

    vi = importlib.import_module("iwxxm_validate.validate_iwxxm")
    xsd = tmp_path / "iwxxm.xsd"
    sch = tmp_path / "iwxxm.sch"
    xsd.write_text("<schema/>", encoding="utf-8")
    sch.write_text("<schema/>", encoding="utf-8")
    monkeypatch.setattr(vi, "rust_available", lambda: True)
    monkeypatch.setattr(
        vi,
        "rust_module",
        lambda: type(
            "R",
            (),
            {"validate_document": staticmethod(lambda *a, **k: [])},
        )(),
    )
    monkeypatch.setattr(vi, "xsd_path", lambda _v: xsd)
    monkeypatch.setattr(vi, "schematron_path", lambda _v: sch)
    report = vi.validate_iwxxm("<root/>", iwxxm_version="3.0.0", profile="ca_eccc")
    assert report.ok is True
    assert report.profile == "ca_eccc"


def test_validate_invalid_profile() -> None:
    report = validate("<root/>", iwxxm_version="2023-1", profile="nope")
    assert report.ok is False
    assert report.issues[0].code == "INVALID_PROFILE"


def test_validate_invalid_levels() -> None:
    report = validate("<root/>", iwxxm_version="2023-1", levels=("nope",))
    assert report.ok is False
    assert report.issues[0].code == "INVALID_LEVELS"


def test_validate_us_catalog_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("iwxxm_validate.api.us_catalog_path", lambda: None)
    report = validate("<root/>", iwxxm_version="2023-1", profile="iwxxm_us")
    assert report.ok is False
    assert report.issues[0].code == "US_CATALOG_NOT_FOUND"


def test_validate_ca_schema_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("iwxxm_validate.api.ca_xsd_path", lambda **_: None)
    report = validate("<root/>", iwxxm_version="3.0.0", profile="ca_eccc")
    assert report.ok is False
    assert report.issues[0].code == "CA_SCHEMA_NOT_FOUND"


def test_validate_xsd_schema_not_available(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_xsd_cache()
    monkeypatch.setattr(
        "iwxxm_validate.xsd.xsd_path",
        lambda _v: (_ for _ in ()).throw(FileNotFoundError("missing")),
    )
    issues = validate_xsd("<root/>", "2023-1")
    assert issues[0].code == "SCHEMA_NOT_AVAILABLE"


def test_validate_xsd_schema_parse_error(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_xsd_cache()

    def boom(_version: str) -> etree.XMLSchema:
        raise etree.XMLSchemaParseError("fatal parse")

    monkeypatch.setattr("iwxxm_validate.xsd._compile_schema", boom)
    issues = validate_xsd("<root/>", "2023-1")
    assert issues[0].code == "SCHEMA_PARSE_ERROR"


def test_validate_xsd_import_warning_none_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_xsd_cache()
    monkeypatch.setattr("iwxxm_validate.xsd._compile_schema", lambda _v: None)
    issues = validate_xsd("<root/>", "2025-2")
    assert issues[0].code == "SCHEMA_IMPORT_WARNING"


def test_validate_xsd_success_with_fake_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_xsd_cache()

    class _Ok:
        error_log: list[object] = []

        def validate(self, _doc: object) -> bool:
            return True

    monkeypatch.setattr("iwxxm_validate.xsd._compile_schema", lambda _v: _Ok())
    assert validate_xsd("<root/>", "2023-1") == []


def test_validate_xsd_failure_with_error_log(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_xsd_cache()
    err = SimpleNamespace(message="bad element", line=1, column=2)

    class _Bad:
        error_log = [err]

        def validate(self, _doc: object) -> bool:
            return False

    monkeypatch.setattr("iwxxm_validate.xsd._compile_schema", lambda _v: _Bad())
    issues = validate_xsd("<root/>", "2023-1")
    assert issues[0].code == "XSD_VALIDATION_ERROR"
    assert issues[0].location == "line 1, column 2"


def test_validate_xsd_failure_empty_error_log(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_xsd_cache()

    class _Bad:
        error_log: list[object] = []

        def validate(self, _doc: object) -> bool:
            return False

    monkeypatch.setattr("iwxxm_validate.xsd._compile_schema", lambda _v: _Bad())
    issues = validate_xsd("<root/>", "2023-1")
    assert issues[0].code == "XSD_VALIDATION_ERROR"


def test_validate_xsd_validate_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_xsd_cache()

    class _Boom:
        error_log: list[object] = []

        def validate(self, _doc: object) -> bool:
            raise RuntimeError("boom")

    monkeypatch.setattr("iwxxm_validate.xsd._compile_schema", lambda _v: _Boom())
    issues = validate_xsd("<root/>", "2023-1")
    assert issues[0].code == "XSD_VALIDATE_ERROR"


def test_compile_schema_2025_substitution_returns_none(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    clear_xsd_cache()
    xsd_file = tmp_path / "iwxxm.xsd"
    xsd_file.write_text(
        '<?xml version="1.0"?><xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>',
        encoding="utf-8",
    )
    monkeypatch.setattr("iwxxm_validate.xsd.xsd_path", lambda _v: xsd_file)

    def raise_sub(_doc: object) -> etree.XMLSchema:
        raise etree.XMLSchemaParseError("substitutionGroup missing for 2025")

    monkeypatch.setattr(etree, "XMLSchema", raise_sub)
    from iwxxm_validate import xsd as xsd_mod

    assert xsd_mod._compile_schema("2025-2") is None


def test_schematron_malformed_xml() -> None:
    issues = validate_schematron("<root>", "2023-1")
    assert issues[0].code == "XML_SYNTAX_ERROR"


def test_schematron_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_schematron_cache()
    monkeypatch.setattr(
        "iwxxm_validate.schematron.schematron_path",
        lambda _v: (_ for _ in ()).throw(FileNotFoundError("missing sch")),
    )
    issues = validate_schematron("<root/>", "2023-1")
    assert issues[0].code == "SCHEMATRON_NOT_FOUND"


def test_schematron_compile_xslt2_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_schematron_cache()

    def boom(_version: str) -> object:
        raise RuntimeError("xslt2 not supported")

    monkeypatch.setattr("iwxxm_validate.schematron._compile_schematron", boom)
    issues = validate_schematron("<root/>", "2023-1")
    assert issues[0].code == "SCHEMATRON_SKIPPED"


def test_schematron_compile_other_error(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_schematron_cache()

    def boom(_version: str) -> object:
        raise RuntimeError("other failure")

    monkeypatch.setattr("iwxxm_validate.schematron._compile_schematron", boom)
    issues = validate_schematron("<root/>", "2023-1")
    assert issues[0].code == "SCHEMATRON_COMPILE_ERROR"


def test_schematron_validate_success(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_schematron_cache()

    class _Ok:
        def validate(self, _doc: object) -> bool:
            return True

    monkeypatch.setattr("iwxxm_validate.schematron._compile_schematron", lambda _v: _Ok())
    assert validate_schematron("<root/>", "2023-1") == []


def test_schematron_validate_fail_with_svrl(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_schematron_cache()
    svrl = etree.fromstring(
        b"""<svrl:schematron-output xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
        <svrl:failed-assert id="R1" location="/root">
          <svrl:text>bad</svrl:text>
        </svrl:failed-assert>
        </svrl:schematron-output>"""
    )

    class _Bad:
        validation_report = svrl

        def validate(self, _doc: object) -> bool:
            return False

    monkeypatch.setattr("iwxxm_validate.schematron._compile_schematron", lambda _v: _Bad())
    issues = validate_schematron("<root/>", "2023-1")
    assert issues[0].code == "R1"
    assert issues[0].message == "bad"


def test_schematron_validate_fail_no_report(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_schematron_cache()

    class _Bad:
        validation_report = None

        def validate(self, _doc: object) -> bool:
            return False

    monkeypatch.setattr("iwxxm_validate.schematron._compile_schematron", lambda _v: _Bad())
    issues = validate_schematron("<root/>", "2023-1")
    assert issues[0].code == "SCHEMATRON_ASSERT"


def test_schematron_validate_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_schematron_cache()

    class _Boom:
        def validate(self, _doc: object) -> bool:
            raise RuntimeError("sch boom")

    monkeypatch.setattr("iwxxm_validate.schematron._compile_schematron", lambda _v: _Boom())
    issues = validate_schematron("<root/>", "2023-1")
    assert issues[0].code == "SCHEMATRON_VALIDATE_ERROR"


def test_schematron_docker_env_still_skips_xslt2(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_schematron_cache()
    monkeypatch.setenv("IWXXM_VALIDATE_SCHEMATRON_DOCKER", "1")
    issues = validate_schematron("<root/>", "2023-1")
    assert any(i.code == "SCHEMATRON_SKIPPED" for i in issues)


def test_uses_xslt2_false_on_read_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from iwxxm_validate import schematron as sch

    missing = tmp_path / "missing.sch"
    assert sch._uses_xslt2(missing) is False


def test_compile_schematron_non_xslt2(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    clear_schematron_cache()
    sch_file = tmp_path / "iwxxm.sch"
    sch_file.write_text(
        """<?xml version="1.0"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt">
  <sch:pattern id="p"><sch:rule context="*">
    <sch:assert test="true()">ok</sch:assert>
  </sch:rule></sch:pattern>
</sch:schema>
""",
        encoding="utf-8",
    )
    rule_dir = tmp_path / "rule"
    rule_dir.mkdir()
    (rule_dir / "codes.wmo.int-common-nil.rdf").write_text("<rdf/>", encoding="utf-8")

    monkeypatch.setattr("iwxxm_validate.schematron.schematron_path", lambda _v: sch_file)
    monkeypatch.setattr("iwxxm_validate.schematron.codelists_dir", lambda _v: rule_dir)

    from iwxxm_validate import schematron as sch

    compiled = sch._compile_schematron("test-xslt1")
    assert compiled is not None
    # second call hits cache / working dir reuse
    assert sch._compile_schematron("test-xslt1") is compiled
    clear_schematron_cache()


def test_issue_encode_via_msgspec() -> None:
    issue = Issue(severity="error", code="X", message="m", layer="xsd")
    payload = msgspec.json.encode(issue)
    assert b"X" in payload


def test_repo_root_schemas_root_non_iwxxm_layout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("IWXXM_VALIDATE_REPO_ROOT", raising=False)
    monkeypatch.setenv("IWXXM_SCHEMAS_ROOT", str(tmp_path / "custom"))
    assert repo_root() == (tmp_path / "custom").resolve()


def test_xsd_path_missing_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from iwxxm_validate import paths as paths_mod

    paths_mod.version_dir.cache_clear()
    monkeypatch.setattr(paths_mod, "version_dir", lambda _v: tmp_path)
    with pytest.raises(FileNotFoundError):
        xsd_path("2023-1")


def test_schematron_path_missing_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from iwxxm_validate import paths as paths_mod

    monkeypatch.setattr(paths_mod, "version_dir", lambda _v: tmp_path)
    with pytest.raises(FileNotFoundError):
        schematron_path("2023-1")


def test_codelists_dir_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from iwxxm_validate import paths as paths_mod

    monkeypatch.setattr(paths_mod, "version_dir", lambda _v: tmp_path)
    with pytest.raises(FileNotFoundError):
        codelists_dir("2023-1")


def test_us_catalog_path_none(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from iwxxm_validate import paths as paths_mod

    monkeypatch.setattr(paths_mod, "vendor_iwxxm_us_root", lambda: tmp_path)
    assert us_catalog_path() is None


def test_validate_xsd_generic_compile_error(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_xsd_cache()

    def boom(_version: str) -> etree.XMLSchema:
        raise ValueError("unsupported")

    monkeypatch.setattr("iwxxm_validate.xsd._compile_schema", boom)
    issues = validate_xsd("<root/>", "2023-1")
    assert issues[0].code == "SCHEMA_NOT_AVAILABLE"


def test_working_dir_cache_reuse(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from iwxxm_validate import schematron as sch

    clear_schematron_cache()
    rule_dir = tmp_path / "rule"
    rule_dir.mkdir()
    (rule_dir / "a.rdf").write_text("<rdf/>", encoding="utf-8")
    monkeypatch.setattr(sch, "codelists_dir", lambda _v: rule_dir)
    first = sch._setup_working_directory("cache-me")
    second = sch._setup_working_directory("cache-me")
    assert first == second
    clear_schematron_cache()


def test_api_skips_schematron_after_xml_syntax() -> None:
    report = validate(
        "<iwxxm:METAR>",
        iwxxm_version="2023-1",
        profile="annex3",
        levels=("xsd", "schematron"),
    )
    assert report.ok is False
    assert any(i.code == "XML_SYNTAX_ERROR" for i in report.issues)
    assert not any(i.layer == "schematron" and i.code != "XML_SYNTAX_ERROR" for i in report.issues)
