"""Unit tests for codelist parser branches and online validation paths."""

from __future__ import annotations

import builtins
import importlib
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from lxml import etree

from src.utilities import codelist_parser as cp
from src.utilities.codelist_parser import (
    CodeListParser,
    CodeListRegistry,
    get_codelist_parser,
    validate_xml_codelists,
)


def _settings():
    return SimpleNamespace(
        wmo_online_validation=False,
        wmo_validation_timeout=1,
        wmo_registry_cache_ttl=3600,
        wmo_registry_url="https://codes.wmo.int",
    )


def test_load_codelists_missing_directory_marks_loaded(tmp_path):
    parser = CodeListParser(tmp_path / "missing", settings=_settings())

    parser.load_codelists()

    assert parser._loaded is True
    assert parser.list_codelists() == []


def test_load_codelists_already_loaded_short_circuits(tmp_path, monkeypatch):
    parser = CodeListParser(tmp_path, settings=_settings())
    parser._loaded = True
    called = []

    monkeypatch.setattr(parser, "_parse_rdf_file", lambda _path: called.append(True))
    parser.load_codelists()

    assert called == []


def test_init_uses_default_settings_when_validation_config_missing(monkeypatch, tmp_path):
    original_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.endswith("config.validation"):
            raise ImportError("missing validation config")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import)

    parser = CodeListParser(tmp_path)

    assert parser.settings.wmo_online_validation is False
    assert parser.settings.wmo_validation_timeout == 5


def test_reload_without_requests_disables_online_validation(monkeypatch):
    original_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "requests":
            raise ImportError("requests unavailable")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import)
    reloaded = importlib.reload(cp)

    try:
        assert reloaded.REQUESTS_AVAILABLE is False
    finally:
        monkeypatch.setattr(builtins, "__import__", original_import)
        importlib.reload(cp)


def test_parse_rdf_file_extracts_codes(tmp_path):
    rdf_file = tmp_path / "codes.wmo.int-49-2-Weather.rdf"
    rdf_file.write_text(
        """
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:skos="http://www.w3.org/2004/02/skos/core#">
          <skos:Concept rdf:about="http://codes.wmo.int/49-2/Weather/RA">
            <skos:prefLabel>Rain</skos:prefLabel>
          </skos:Concept>
        </rdf:RDF>
        """,
        encoding="utf-8",
    )

    parser = CodeListParser(tmp_path, settings=_settings())
    parser._parse_rdf_file(rdf_file)

    weather_codes = parser.get_codes("Weather")
    assert "RA" in weather_codes
    assert "Rain" in weather_codes


def test_parse_rdf_file_with_no_concepts_does_not_cache_entry(tmp_path):
    rdf_file = tmp_path / "empty.rdf"
    rdf_file.write_text(
        "<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' />",
        encoding="utf-8",
    )

    parser = CodeListParser(tmp_path, settings=_settings())
    parser._parse_rdf_file(rdf_file)

    assert parser.list_codelists() == []


def test_load_codelists_logs_parse_failures_and_continues(tmp_path):
    bad_rdf = tmp_path / "broken.rdf"
    bad_rdf.write_text("<rdf:RDF>", encoding="utf-8")
    parser = CodeListParser(tmp_path, settings=_settings())

    parser.load_codelists()

    assert parser._loaded is True
    assert parser.list_codelists() == []


def test_extract_codelist_references_only_wmo_urls():
    parser = CodeListParser(Path("."), settings=_settings())
    xml = etree.fromstring(
        b"""
        <root xmlns:xlink="http://www.w3.org/1999/xlink">
          <a xlink:href="http://codes.wmo.int/49-2/Weather/RA"/>
          <b xlink:href="#internal"/>
        </root>
        """
    )

    refs = parser._extract_codelist_references(xml)

    assert len(refs) == 1
    assert refs[0][1] == "RA"


def test_extract_codelist_references_ignores_unparseable_url(caplog):
    parser = CodeListParser(Path("."), settings=_settings())

    class _BadHref:
        def __contains__(self, value):
            return value == "codes.wmo.int"

        def rstrip(self, _chars=None):
            raise ValueError("bad href")

    class _Elem:
        def get(self, _name):
            return _BadHref()

    class _RootTree:
        def getpath(self, _elem):
            return "/root/a"

    class _Tree:
        def xpath(self, *_args, **_kwargs):
            return [_Elem()]

        def getroottree(self):
            return _RootTree()

    refs = parser._extract_codelist_references(_Tree())

    assert refs == []
    assert "Failed to parse codelist URL" in caplog.text


def test_validate_xml_codelists_xml_syntax_error():
    parser = CodeListParser(Path("."), settings=_settings())

    result = parser.validate_xml_codelists("<root>")

    assert result.is_valid is False
    assert result.issues[0].code == "XML_SYNTAX_ERROR"


def test_validate_xml_codelists_codelist_not_found_warning(monkeypatch):
    parser = CodeListParser(Path("."), settings=_settings())
    parser._loaded = True

    monkeypatch.setattr(
        parser,
        "_extract_codelist_references",
        lambda _tree: [("http://codes.wmo.int/49-2/Weather/RA", "RA", "/root/a")],
    )

    result = parser.validate_xml_codelists("<root/>")

    assert result.is_valid is True
    assert result.issues[0].code == "CODELIST_NOT_FOUND"


def test_validate_xml_codelists_invalid_value_error(monkeypatch):
    parser = CodeListParser(Path("."), settings=_settings())
    parser._loaded = True
    parser._cache = {"RA": {"GOOD"}}

    monkeypatch.setattr(
        parser,
        "_extract_codelist_references",
        lambda _tree: [("http://codes.wmo.int/49-2/Weather/RA", "RA", "/root/a")],
    )

    result = parser.validate_xml_codelists("<root/>")

    assert result.is_valid is False
    assert result.invalid_references == 1
    assert result.issues[0].code == "INVALID_CODELIST_VALUE"


def test_validate_xml_codelists_uses_second_to_last_url_segment(monkeypatch):
    parser = CodeListParser(Path("."), settings=_settings())
    parser._loaded = True
    parser._cache = {"Weather": {"RA"}}

    monkeypatch.setattr(
        parser,
        "_extract_codelist_references",
        lambda _tree: [("http://codes.wmo.int/49-2/RA/Weather", "Weather", "/root/a")],
    )

    result = parser.validate_xml_codelists("<root/>")

    assert result.is_valid is True
    assert result.invalid_references == 0
    assert result.issues == []


def test_validate_online_requests_unavailable(monkeypatch):
    parser = CodeListParser(Path("."), settings=_settings())
    monkeypatch.setattr(cp, "REQUESTS_AVAILABLE", False)

    issue = parser._validate_online("http://codes.wmo.int/49-2/Weather/RA", "/root/a")

    assert issue.code == "ONLINE_VALIDATION_UNAVAILABLE"


def test_validate_online_cache_hit(monkeypatch):
    settings = SimpleNamespace(
        wmo_online_validation=True,
        wmo_validation_timeout=1,
        wmo_registry_cache_ttl=3600,
        wmo_registry_url="https://codes.wmo.int",
    )
    parser = CodeListParser(Path("."), settings=settings)
    cached = cp.ValidationIssue(
        layer=cp.ValidationLayer.WMO_CODELISTS,
        level=cp.ValidationSeverity.INFO,
        message="cached",
        code="CODELIST_VALID_ONLINE",
    )
    parser._online_cache["http://codes.wmo.int/49-2/Weather/RA"] = (
        cached,
        datetime.utcnow() - timedelta(seconds=10),
    )

    issue = parser._validate_online("http://codes.wmo.int/49-2/Weather/RA", "/root/new")

    assert issue.code == "CODELIST_VALID_ONLINE"
    assert issue.location == "/root/new"


def test_validate_online_http_status_paths(monkeypatch):
    settings = SimpleNamespace(
        wmo_online_validation=True,
        wmo_validation_timeout=1,
        wmo_registry_cache_ttl=1,
        wmo_registry_url="https://codes.wmo.int",
    )
    parser = CodeListParser(Path("."), settings=settings)
    monkeypatch.setattr(cp, "REQUESTS_AVAILABLE", True)

    class _Resp:
        def __init__(self, status_code, content=b""):
            self.status_code = status_code
            self.content = content

    class _Requests:
        class Timeout(Exception):
            pass

        @staticmethod
        def get(url, timeout, headers):
            if url.endswith("/200"):
                return _Resp(
                    200,
                    b"<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:reg='http://purl.org/linked-data/registry#'><reg:status rdf:resource='http://codes.wmo.int/common/reg-status/valid'/></rdf:RDF>",
                )
            if url.endswith("/404"):
                return _Resp(404)
            return _Resp(500)

    monkeypatch.setattr(cp, "requests", _Requests)

    ok = parser._validate_online("http://codes.wmo.int/200", "/a")
    missing = parser._validate_online("http://codes.wmo.int/404", "/b")
    err = parser._validate_online("http://codes.wmo.int/500", "/c")

    assert ok.code == "CODELIST_VALID_ONLINE"
    assert missing.code == "CODELIST_NOT_FOUND"
    assert err.code == "CODELIST_ONLINE_ERROR"


def test_validate_online_cache_expiry_and_status_variants(monkeypatch):
    settings = SimpleNamespace(
        wmo_online_validation=True,
        wmo_validation_timeout=1,
        wmo_registry_cache_ttl=1,
        wmo_registry_url="https://codes.wmo.int",
    )
    parser = CodeListParser(Path("."), settings=settings)
    monkeypatch.setattr(cp, "REQUESTS_AVAILABLE", True)

    stale_issue = cp.ValidationIssue(
        layer=cp.ValidationLayer.WMO_CODELISTS,
        level=cp.ValidationSeverity.INFO,
        message="stale",
        code="STALE",
    )
    parser._online_cache["http://codes.wmo.int/deprecated"] = (
        stale_issue,
        datetime.utcnow() - timedelta(seconds=10),
    )

    class _Resp:
        def __init__(self, content):
            self.status_code = 200
            self.content = content

    class _Requests:
        class Timeout(Exception):
            pass

        @staticmethod
        def get(url, timeout, headers):
            if url.endswith("deprecated"):
                return _Resp(
                    b"<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:reg='http://purl.org/linked-data/registry#'><reg:status rdf:resource='http://codes.wmo.int/common/reg-status/deprecated'/></rdf:RDF>"
                )
            return _Resp(b"<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'></rdf:RDF>")

    monkeypatch.setattr(cp, "requests", _Requests)

    deprecated = parser._validate_online("http://codes.wmo.int/deprecated", "/deprecated")
    unknown = parser._validate_online("http://codes.wmo.int/unknown", "/unknown")

    assert deprecated.code == "CODELIST_DEPRECATED"
    assert unknown.code == "CODELIST_STATUS_UNKNOWN"


def test_validate_online_timeout_returns_warning(monkeypatch):
    settings = SimpleNamespace(
        wmo_online_validation=True,
        wmo_validation_timeout=1,
        wmo_registry_cache_ttl=1,
        wmo_registry_url="https://codes.wmo.int",
    )
    parser = CodeListParser(Path("."), settings=settings)
    monkeypatch.setattr(cp, "REQUESTS_AVAILABLE", True)

    class _Requests:
        class Timeout(Exception):
            pass

        @staticmethod
        def get(_url, timeout, headers):
            raise _Requests.Timeout("timeout")

    monkeypatch.setattr(cp, "requests", _Requests)

    issue = parser._validate_online("http://codes.wmo.int/49-2/Weather/RA", "/root/a")
    assert issue.code == "CODELIST_TIMEOUT"


def test_validate_online_exception_returns_warning(monkeypatch):
    settings = SimpleNamespace(
        wmo_online_validation=True,
        wmo_validation_timeout=1,
        wmo_registry_cache_ttl=1,
        wmo_registry_url="https://codes.wmo.int",
    )
    parser = CodeListParser(Path("."), settings=settings)
    monkeypatch.setattr(cp, "REQUESTS_AVAILABLE", True)

    class _Requests:
        class Timeout(Exception):
            pass

        @staticmethod
        def get(_url, timeout, headers):
            raise RuntimeError("network down")

    monkeypatch.setattr(cp, "requests", _Requests)

    issue = parser._validate_online("http://codes.wmo.int/49-2/Weather/RA", "/root/a")
    assert issue.code == "CODELIST_ONLINE_FAILED"


def test_parse_rdf_status_variants():
    parser = CodeListParser(Path("."), settings=_settings())

    valid = parser._parse_rdf_status(
        b"<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:reg='http://purl.org/linked-data/registry#'><reg:status rdf:resource='http://codes.wmo.int/common/reg-status/valid'/></rdf:RDF>"
    )
    concept_only = parser._parse_rdf_status(
        b"<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:skos='http://www.w3.org/2004/02/skos/core#'><skos:Concept/></rdf:RDF>"
    )
    unknown = parser._parse_rdf_status(b"<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'></rdf:RDF>")

    assert valid == "valid"
    assert concept_only == "valid"
    assert unknown == "unknown"


def test_parse_rdf_status_superseded_and_deprecated():
    parser = CodeListParser(Path("."), settings=_settings())

    superseded = parser._parse_rdf_status(
        b"<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:reg='http://purl.org/linked-data/registry#'><reg:status rdf:resource='http://codes.wmo.int/common/reg-status/superseded'/></rdf:RDF>"
    )
    deprecated = parser._parse_rdf_status(
        b"<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:reg='http://purl.org/linked-data/registry#'><reg:status rdf:resource='http://codes.wmo.int/common/reg-status/deprecated'/></rdf:RDF>"
    )

    assert superseded == "superseded"
    assert deprecated == "deprecated"


def test_validate_xml_codelists_online_validation_path(monkeypatch):
    parser = CodeListParser(
        Path("."),
        settings=SimpleNamespace(
            wmo_online_validation=True,
            wmo_validation_timeout=1,
            wmo_registry_cache_ttl=3600,
            wmo_registry_url="https://codes.wmo.int",
        ),
    )
    parser._loaded = True
    parser._cache = {}
    monkeypatch.setattr(cp, "REQUESTS_AVAILABLE", True)

    monkeypatch.setattr(
        parser,
        "_extract_codelist_references",
        lambda _tree: [("http://codes.wmo.int/49-2/Weather/RA", "Weather", "/root/a")],
    )
    monkeypatch.setattr(
        parser,
        "_validate_online",
        lambda _href, xpath: cp.ValidationIssue(
            layer=cp.ValidationLayer.WMO_CODELISTS,
            level=cp.ValidationSeverity.INFO,
            message="validated online",
            location=xpath,
            code="CODELIST_VALID_ONLINE",
        ),
    )

    result = parser.validate_xml_codelists("<root/>")
    assert result.is_valid is True
    assert result.issues[0].code == "CODELIST_VALID_ONLINE"


def test_validate_xml_codelists_outer_exception_returns_error(monkeypatch):
    parser = CodeListParser(Path("."), settings=_settings())
    parser._loaded = True

    def _raise(_tree):
        raise RuntimeError("boom")

    monkeypatch.setattr(parser, "_extract_codelist_references", _raise)

    result = parser.validate_xml_codelists("<root/>")
    assert result.is_valid is False
    assert result.issues[0].code == "RuntimeError"


def test_registry_and_wrapper(tmp_path):
    registry = CodeListRegistry()
    monkey_parser = CodeListParser(tmp_path, settings=_settings())
    monkey_parser._loaded = True
    monkey_parser._cache = {"Weather": {"RA"}}
    registry._parsers["2025-2"] = monkey_parser
    parser = registry.get_parser("2025-2", tmp_path)
    same = registry.get_parser("2025-2", tmp_path)
    assert parser is same

    assert registry.validate_code("2025-2", "Weather", "RA", tmp_path) is True


def test_registry_creates_new_parser_instance(monkeypatch, tmp_path):
    registry = CodeListRegistry()
    parser_class = CodeListParser

    monkeypatch.setattr(cp, "CodeListParser", lambda codelists_dir: parser_class(codelists_dir, settings=_settings()))

    parser = registry.get_parser("2023-1", tmp_path)

    assert isinstance(parser, parser_class)
    assert registry.get_parser("2023-1", tmp_path) is parser


def test_global_getter_and_validate_wrapper(monkeypatch, tmp_path):
    parser = CodeListParser(tmp_path, settings=_settings())
    parser._loaded = True
    monkeypatch.setattr(cp, "_registry", SimpleNamespace(get_parser=lambda version, codelists_dir: parser))
    monkeypatch.setattr(
        parser, "validate_xml_codelists", lambda xml_content: cp.CodelistValidationResult(is_valid=True, issues=[])
    )

    got = get_codelist_parser("2025-2", tmp_path)
    result = validate_xml_codelists("<root/>", "2025-2", tmp_path)

    assert got is parser
    assert result.is_valid is True


def test_load_codelists_logs_warning_when_rdf_parse_fails(tmp_path, monkeypatch, caplog):
    import logging

    rdf_path = tmp_path / "broken.rdf"
    rdf_path.write_text("<not-valid", encoding="utf-8")
    parser = CodeListParser(tmp_path, settings=_settings())

    def _boom(_path):
        raise ValueError("parse failed")

    monkeypatch.setattr(parser, "_parse_rdf_file", _boom)
    with caplog.at_level(logging.WARNING, logger="src.utilities.codelist_parser"):
        parser.load_codelists()

    assert parser._loaded is True
    assert "Failed to parse broken.rdf" in caplog.text


def test_validate_online_returns_warning_when_requests_missing(monkeypatch, tmp_path):
    parser = CodeListParser(tmp_path, settings=_settings())
    parser.settings.wmo_online_validation = True
    monkeypatch.setattr(cp, "REQUESTS_AVAILABLE", False)
    monkeypatch.setattr(cp, "requests", None)

    issue = parser._validate_online("https://codes.wmo.int/test", "/root")
    assert issue.code == "ONLINE_VALIDATION_UNAVAILABLE"


def test_parse_rdf_status_returns_unknown_on_failure(monkeypatch):
    parser = CodeListParser(Path("/tmp"), settings=_settings())
    monkeypatch.setattr(
        "src.utilities.codelist_parser.etree.fromstring",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("bad rdf")),
    )
    assert parser._parse_rdf_status(b"<rdf/>") == "unknown"
