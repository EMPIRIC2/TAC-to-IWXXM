"""Unit tests for GML reference validator branches."""

from __future__ import annotations

import pytest

from src.utilities.gml_validator import (
    GMLReferenceValidator,
    get_gml_validator,
    validate_gml_references,
)


def test_external_reference_helpers():
    validator = GMLReferenceValidator()

    assert validator._is_external_reference("codes.wmo.int-49-2-AerodromeState.rdf#OPEN")
    assert not validator._is_external_reference("#uuid.1")

    rdf_file, element_id = validator._extract_rdf_file_and_element(
        "codes.wmo.int-49-2-AerodromeState.rdf#CodeAerodromeState_OPEN"
    )
    assert rdf_file == "codes.wmo.int-49-2-AerodromeState.rdf"
    assert element_id == "CodeAerodromeState_OPEN"


def test_load_rdf_elements_without_codelist_dir_returns_empty_set():
    validator = GMLReferenceValidator(codelists_dir=None)

    elements = validator._load_rdf_elements("codes.wmo.int-49-2-AerodromeState.rdf")

    assert elements == set()


def test_validate_invalid_xml_reports_xml_syntax_error():
    validator = GMLReferenceValidator()

    result = validator.validate("<root>", version="2025-2")

    assert result.is_valid is False
    assert result.issues[0].code == "XML_SYNTAX_ERROR"


def test_validate_duplicate_ids_and_broken_internal_reference():
    validator = GMLReferenceValidator()

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        validator,
        "_extract_gml_ids",
        lambda _tree: {"same-id": ["/a", "/b"]},
    )

    xml = """
    <iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
                 xmlns:gml="http://www.opengis.net/gml/3.2.1"
                 xmlns:xlink="http://www.w3.org/1999/xlink">
      <gml:Point gml:id="same-id"><gml:pos>10 20</gml:pos></gml:Point>
      <gml:Point gml:id="same-id"><gml:pos>30 40</gml:pos></gml:Point>
      <iwxxm:surfaceWind xlink:href="#missing-id"/>
    </iwxxm:METAR>
    """

    result = validator.validate(xml, version="2025-2")

    assert result.is_valid is False
    codes = {issue.code for issue in result.issues}
    assert "DUPLICATE_GML_ID" in codes
    assert "BROKEN_INTERNAL_REFERENCE" in codes
    monkeypatch.undo()


def test_validate_external_reference_error_and_warning_paths(monkeypatch):
    validator = GMLReferenceValidator()

    xml = """
    <iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
                 xmlns:gml="http://www.opengis.net/gml/3.2.1"
                 xmlns:xlink="http://www.w3.org/1999/xlink">
      <gml:Point gml:id="known-id"><gml:pos>10 20</gml:pos></gml:Point>
    </iwxxm:METAR>
    """

    refs = [
        (
            "codes.wmo.int-49-2-AerodromeState.rdf#CodeAerodromeState_CLOSED",
            "CodeAerodromeState_CLOSED",
            "/iwxxm:METAR[1]/iwxxm:surfaceWind[1]",
        ),
        (
            "codes.wmo.int-49-2-AerodromeState.rdf#CodeAerodromeState_OPEN",
            "CodeAerodromeState_OPEN",
            "/iwxxm:METAR[1]/iwxxm:weather[1]",
        ),
    ]

    monkeypatch.setattr(validator, "_extract_href_references", lambda _tree: refs)

    calls = {"count": 0}

    def fake_load(_filename):
        calls["count"] += 1
        if calls["count"] == 1:
            return set()
        return {"CodeAerodromeState_OPEN"}

    monkeypatch.setattr(validator, "_load_rdf_elements", fake_load)

    result = validator.validate(xml, version="2025-2")

    codes = [issue.code for issue in result.issues]
    assert "UNRESOLVABLE_EXTERNAL_REFERENCE" in codes
    assert result.broken_references == 1


def test_validate_unexpected_exception_is_wrapped(monkeypatch):
    validator = GMLReferenceValidator()

    monkeypatch.setattr(validator, "_extract_gml_ids", lambda _tree: (_ for _ in ()).throw(RuntimeError("boom")))

    xml = "<root xmlns:gml='http://www.opengis.net/gml/3.2.1'/>"
    result = validator.validate(xml, version="2025-2")

    assert result.is_valid is False
    assert result.issues[0].code == "RuntimeError"


def test_validate_geometry_no_geometry_returns_valid():
    validator = GMLReferenceValidator()

    xml = "<root xmlns:gml='http://www.opengis.net/gml/3.2.1'/>"
    result = validator.validate_geometry(xml)

    assert result.is_valid is True
    assert result.issues == []


def test_validate_geometry_missing_crs_and_coordinates_issues():
    validator = GMLReferenceValidator()

    xml = """
    <root xmlns:gml="http://www.opengis.net/gml/3.2.1">
      <gml:Point />
      <gml:LineString srsName="EPSG:4326" />
    </root>
    """

    result = validator.validate_geometry(xml)

    codes = [issue.code for issue in result.issues]
    assert "MISSING_CRS" in codes
    assert "MISSING_COORDINATES" in codes
    assert result.is_valid is False


def test_get_gml_validator_singleton_and_set_dir(tmp_path):
    first = get_gml_validator()
    second = get_gml_validator(codelists_dir=tmp_path)

    assert first is second
    assert first.codelists_dir == tmp_path


def test_validate_gml_references_wrapper(monkeypatch):
    validator = GMLReferenceValidator()
    monkeypatch.setattr("src.utilities.gml_validator.get_gml_validator", lambda codelists_dir=None: validator)

    result = validate_gml_references("<root/>", version="2025-2")

    assert result.is_valid is True


def test_load_rdf_elements_parses_and_caches(tmp_path):
    rdf_file = tmp_path / "codes.wmo.int-49-2-AerodromeState.rdf"
    rdf_file.write_text(
        """
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
          <rdf:Description rdf:about="http://codes.wmo.int/49-2/AerodromeState#CodeAerodromeState_OPEN"/>
        </rdf:RDF>
        """,
        encoding="utf-8",
    )

    validator = GMLReferenceValidator(codelists_dir=tmp_path)
    first = validator._load_rdf_elements(rdf_file.name)
    second = validator._load_rdf_elements(rdf_file.name)
    assert "CodeAerodromeState_OPEN" in first
    assert first == second


def test_load_rdf_elements_missing_file_returns_empty(tmp_path):
    validator = GMLReferenceValidator(codelists_dir=tmp_path)
    assert validator._load_rdf_elements("missing.rdf") == set()


def test_validate_external_reference_broken_element_is_error(monkeypatch):
    validator = GMLReferenceValidator()
    xml = """
    <iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
                 xmlns:gml="http://www.opengis.net/gml/3.2.1"
                 xmlns:xlink="http://www.w3.org/1999/xlink">
      <gml:Point gml:id="known-id"><gml:pos>10 20</gml:pos></gml:Point>
    </iwxxm:METAR>
    """
    monkeypatch.setattr(
        validator,
        "_extract_href_references",
        lambda _tree: [
            (
                "codes.wmo.int-49-2-AerodromeState.rdf#MISSING",
                "MISSING",
                "/iwxxm:METAR[1]/iwxxm:surfaceWind[1]",
            )
        ],
    )
    monkeypatch.setattr(validator, "_load_rdf_elements", lambda _filename: {"OTHER"})

    result = validator.validate(xml, version="2025-2")
    assert result.is_valid is False
    assert any(issue.code == "BROKEN_EXTERNAL_REFERENCE" for issue in result.issues)


def test_validate_geometry_invalid_xml_reports_syntax_error():
    validator = GMLReferenceValidator()
    result = validator.validate_geometry("<root>")
    assert result.is_valid is False
    assert result.issues[0].code == "XML_SYNTAX_ERROR"


def test_load_rdf_elements_parses_about_without_fragment(tmp_path):
    rdf_file = tmp_path / "codes.wmo.int-49-2-AerodromeState.rdf"
    rdf_file.write_text(
        """
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
          <rdf:Description rdf:about="http://codes.wmo.int/49-2/AerodromeState/CodeAerodromeState_OPEN"/>
        </rdf:RDF>
        """,
        encoding="utf-8",
    )

    validator = GMLReferenceValidator(codelists_dir=tmp_path)
    elements = validator._load_rdf_elements(rdf_file.name)
    assert "http://codes.wmo.int/49-2/AerodromeState/CodeAerodromeState_OPEN" in elements


def test_load_rdf_elements_returns_empty_on_parse_failure(tmp_path, monkeypatch):
    rdf_file = tmp_path / "broken.rdf"
    rdf_file.write_text("<broken", encoding="utf-8")

    validator = GMLReferenceValidator(codelists_dir=tmp_path)
    monkeypatch.setattr(
        "src.utilities.gml_validator.etree.parse",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("parse fail")),
    )
    assert validator._load_rdf_elements("broken.rdf") == set()


def test_extract_rdf_file_and_element_without_fragment():
    validator = GMLReferenceValidator()
    rdf_file, element_id = validator._extract_rdf_file_and_element("codes.wmo.int-49-2-AerodromeState.rdf")
    assert rdf_file == "codes.wmo.int-49-2-AerodromeState.rdf"
    assert element_id == ""


def test_load_rdf_elements_skips_description_without_about(tmp_path):
    """Cover false branch of ``if about:`` when rdf:Description has no about."""
    rdf_file = tmp_path / "codes.wmo.int-common-nil.rdf"
    rdf_file.write_text(
        """
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
          <rdf:Description/>
          <rdf:Description rdf:about="http://codes.wmo.int/common/nil#missing"/>
        </rdf:RDF>
        """,
        encoding="utf-8",
    )

    validator = GMLReferenceValidator(codelists_dir=tmp_path)
    elements = validator._load_rdf_elements(rdf_file.name)
    assert "missing" in elements


def test_extract_gml_ids_registers_and_duplicates():
    """
    Cover ``_extract_gml_ids`` body.

    XPath uses GML 3.2.1 namespace; attribute get uses GML 3.2 — both must be present.
    """
    from lxml import etree

    xml = """
    <root xmlns:gml="http://www.opengis.net/gml/3.2.1"
          xmlns:gml32="http://www.opengis.net/gml/3.2">
      <a gml:id="xpath-a" gml32:id="shared"/>
      <b gml:id="xpath-b" gml32:id="shared"/>
      <c gml:id="xpath-c" gml32:id="unique"/>
    </root>
    """
    tree = etree.fromstring(xml.encode("utf-8"))
    validator = GMLReferenceValidator()
    registry = validator._extract_gml_ids(tree)

    assert "shared" in registry
    assert len(registry["shared"]) == 2
    assert registry["unique"] == ["/root/c"]


def test_extract_href_references_skips_non_internal_hrefs():
    """Cover false branch when xlink:href does not start with '#'."""
    from lxml import etree

    xml = """
    <root xmlns:xlink="http://www.w3.org/1999/xlink">
      <ext xlink:href="codes.wmo.int-49-2-AerodromeState.rdf#OPEN"/>
      <internal xlink:href="#target-id"/>
    </root>
    """
    tree = etree.fromstring(xml.encode("utf-8"))
    validator = GMLReferenceValidator()
    refs = validator._extract_href_references(tree)

    assert len(refs) == 1
    assert refs[0][0] == "#target-id"
    assert refs[0][1] == "target-id"


def test_validate_autoload_codelists_exception_is_swallowed(monkeypatch):
    """Cover lines 251-252 when schema registry lookup fails."""
    validator = GMLReferenceValidator(codelists_dir=None)

    def _boom():
        raise RuntimeError("registry unavailable")

    # validate() does `from .schema_registry import get_schema_registry`
    monkeypatch.setattr(
        "src.utilities.schema_registry.get_schema_registry",
        _boom,
    )

    result = validator.validate("<root/>", version="2025-2")
    assert result.is_valid is True


def test_validate_skips_autoload_when_codelists_already_set(tmp_path):
    """Cover false branch of ``if version and not self.codelists_dir``."""
    validator = GMLReferenceValidator(codelists_dir=tmp_path)
    result = validator.validate("<root/>", version="2025-2")
    assert result.is_valid is True
    assert validator.codelists_dir == tmp_path


def test_validate_reports_broken_internal_via_real_id_extract():
    """Exercise duplicate-id and broken-internal paths without monkeypatching extractors."""
    xml = """
    <root xmlns:gml="http://www.opengis.net/gml/3.2.1"
          xmlns:gml32="http://www.opengis.net/gml/3.2"
          xmlns:xlink="http://www.w3.org/1999/xlink">
      <a gml:id="xa" gml32:id="dup"/>
      <b gml:id="xb" gml32:id="dup"/>
      <ref xlink:href="#missing"/>
    </root>
    """
    validator = GMLReferenceValidator()
    result = validator.validate(xml)

    codes = {issue.code for issue in result.issues}
    assert "DUPLICATE_GML_ID" in codes
    assert "BROKEN_INTERNAL_REFERENCE" in codes


def test_validate_geometry_passes_with_crs_and_coordinates():
    """Cover geometry success path (coordinates present + is_valid debug)."""
    xml = """
    <root xmlns:gml="http://www.opengis.net/gml/3.2.1">
      <gml:Point srsName="EPSG:4326">
        <gml:pos>10 20</gml:pos>
      </gml:Point>
    </root>
    """
    validator = GMLReferenceValidator()
    result = validator.validate_geometry(xml)

    assert result.is_valid is True
    assert result.issues == []
    assert result.total_ids == 1
