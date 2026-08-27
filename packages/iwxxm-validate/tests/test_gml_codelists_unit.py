"""Unit tests for GML reference and offline codelist validation (EV-037 TD-1)."""

from __future__ import annotations

from pathlib import Path

import pytest
from iwxxm_validate.codelists import validate_codelist_references
from iwxxm_validate.gml import validate_gml_references

_GML_NS = "http://www.opengis.net/gml/3.2"
_XLINK_NS = "http://www.w3.org/1999/xlink"


def _minimal_gml_doc(*, body: str) -> str:
    return f'<root xmlns:gml="{_GML_NS}" xmlns:xlink="{_XLINK_NS}">{body}</root>'


def test_gml_malformed_xml_returns_syntax_error() -> None:
    issues = validate_gml_references("<not-closed")
    assert len(issues) == 1
    assert issues[0].code == "XML_SYNTAX_ERROR"
    assert issues[0].layer == "gml"


def test_gml_valid_internal_reference() -> None:
    xml = _minimal_gml_doc(body=('<gml:Point gml:id="target"/><gml:Point xlink:href="#target"/>'))
    assert validate_gml_references(xml) == []


def test_gml_duplicate_id_and_broken_internal_reference() -> None:
    xml = _minimal_gml_doc(body=('<gml:Point gml:id="a"/><gml:Point gml:id="a"/><gml:Point xlink:href="#missing"/>'))
    codes = {i.code for i in validate_gml_references(xml)}
    assert "DUPLICATE_GML_ID" in codes
    assert "BROKEN_INTERNAL_REFERENCE" in codes


def test_gml_external_rdf_reference(tmp_path: Path) -> None:
    rdf = tmp_path / "codes.wmo.int-example.rdf"
    rdf.write_text(
        """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="http://example.test#KNOWN"/>
</rdf:RDF>
""",
        encoding="utf-8",
    )
    ok_xml = _minimal_gml_doc(body='<gml:Point xlink:href="codes.wmo.int-example.rdf#KNOWN"/>')
    bad_xml = _minimal_gml_doc(body='<gml:Point xlink:href="codes.wmo.int-example.rdf#MISSING"/>')
    missing_xml = _minimal_gml_doc(body='<gml:Point xlink:href="codes.wmo.int-missing.rdf#KNOWN"/>')
    no_hash_xml = _minimal_gml_doc(body='<gml:Point xlink:href="http://example.test/external"/>')

    assert validate_gml_references(ok_xml, codelists_dir=tmp_path) == []
    bad_issues = validate_gml_references(bad_xml, codelists_dir=tmp_path)
    assert any(i.code == "BROKEN_EXTERNAL_REFERENCE" for i in bad_issues)
    warn_issues = validate_gml_references(missing_xml, codelists_dir=tmp_path)
    assert any(i.code == "UNRESOLVABLE_EXTERNAL_REFERENCE" for i in warn_issues)
    assert validate_gml_references(no_hash_xml, codelists_dir=tmp_path) == []


def test_gml_unparseable_rdf_file(tmp_path: Path) -> None:
    bad_rdf = tmp_path / "codes.wmo.int-bad.rdf"
    bad_rdf.write_text("not xml", encoding="utf-8")
    xml = _minimal_gml_doc(body='<gml:Point xlink:href="codes.wmo.int-bad.rdf#ID"/>')
    issues = validate_gml_references(xml, codelists_dir=tmp_path)
    assert any(i.code == "UNRESOLVABLE_EXTERNAL_REFERENCE" for i in issues)


def _write_skos_rdf(path: Path, *, codelist_suffix: str, code: str) -> None:
    path.write_text(
        f"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Concept rdf:about="http://codes.wmo.int/49-2/{codelist_suffix}/{code}">
    <skos:prefLabel>{code}</skos:prefLabel>
  </skos:Concept>
</rdf:RDF>
""",
        encoding="utf-8",
    )


def test_codelists_malformed_xml_returns_syntax_error() -> None:
    issues = validate_codelist_references("<bad", codelists_dir=Path("."))
    assert len(issues) == 1
    assert issues[0].code == "XML_SYNTAX_ERROR"


def test_codelists_missing_directory() -> None:
    assert validate_codelist_references(_minimal_gml_doc(body=""), codelists_dir=Path("/no/such/dir")) == []


def test_codelists_offline_validation(tmp_path: Path) -> None:
    _write_skos_rdf(tmp_path / "codes.wmo.int-49-2-CloudAmount.rdf", codelist_suffix="CloudAmount", code="FEW")

    ok_xml = _minimal_gml_doc(body='<gml:Point xlink:href="http://codes.wmo.int/49-2/CloudAmount/FEW"/>')
    missing_list_xml = _minimal_gml_doc(body='<gml:Point xlink:href="http://codes.wmo.int/49-2/UnknownList/FEW"/>')
    bad_code_xml = _minimal_gml_doc(body='<gml:Point xlink:href="http://codes.wmo.int/49-2/CloudAmount/BAD"/>')
    non_wmo_xml = _minimal_gml_doc(body='<gml:Point xlink:href="http://example.test/FEW"/>')
    short_url_xml = _minimal_gml_doc(body='<gml:Point xlink:href="http://codes.wmo.int/UnknownShort"/>')

    assert validate_codelist_references(ok_xml, codelists_dir=tmp_path) == []
    missing = validate_codelist_references(missing_list_xml, codelists_dir=tmp_path)
    assert any(i.code == "CODELIST_NOT_FOUND" for i in missing)
    invalid = validate_codelist_references(bad_code_xml, codelists_dir=tmp_path)
    assert any(i.code == "INVALID_CODELIST_VALUE" for i in invalid)
    assert validate_codelist_references(non_wmo_xml, codelists_dir=tmp_path) == []
    short = validate_codelist_references(short_url_xml, codelists_dir=tmp_path)
    assert any(i.code == "CODELIST_NOT_FOUND" for i in short)


def test_codelists_skips_unparseable_rdf(tmp_path: Path) -> None:
    (tmp_path / "codes.wmo.int-49-2-Broken.rdf").write_text("<<bad", encoding="utf-8")
    xml = _minimal_gml_doc(body='<gml:Point xlink:href="http://codes.wmo.int/49-2/Broken/X"/>')
    issues = validate_codelist_references(xml, codelists_dir=tmp_path)
    assert any(i.code == "CODELIST_NOT_FOUND" for i in issues)


def test_validate_iwxxm_gml_and_codelist_levels() -> None:
    from iwxxm_validate import validate_iwxxm

    xml = _minimal_gml_doc(body=('<gml:Point gml:id="a"/><gml:Point xlink:href="#a"/>'))
    report = validate_iwxxm(xml, iwxxm_version="2023-1", levels=("gml", "codelists"))
    assert report.ok is True


def test_validate_iwxxm_codelist_dir_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib

    vi = importlib.import_module("iwxxm_validate.validate_iwxxm")
    monkeypatch.setattr(vi, "codelists_dir", lambda _v: (_ for _ in ()).throw(FileNotFoundError("missing")))
    report = vi.validate_iwxxm("<root/>", iwxxm_version="2023-1", levels=("codelists",))
    assert any(i.code == "CODELIST_DIR_NOT_FOUND" for i in report.issues)


def test_wellformed_valid_xml() -> None:
    from iwxxm_validate.wellformed import run_wellformed_lxml

    assert run_wellformed_lxml("<root/>") == []


def test_wellformed_malformed_xml() -> None:
    from iwxxm_validate.wellformed import run_wellformed_lxml

    issues = run_wellformed_lxml("<not-closed")
    assert len(issues) == 1
    assert issues[0].code == "XML_SYNTAX_ERROR"
    assert issues[0].layer == "wellformed"
