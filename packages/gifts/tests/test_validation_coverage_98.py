"""Targeted validation coverage tests for 98% package threshold."""

from __future__ import annotations

import argparse
import builtins
import importlib
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "validation"))

import checkGMLReferences
import codeListsToSchematron
import iwxxmValidator


def _run_gml_check(tmpdir: str, version: str = "3.0", internet: bool = False) -> int:
    open(os.path.join(tmpdir, "ignoredURLs.txt"), "w").close()
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    try:
        return checkGMLReferences.check_GML_references(tmpdir, version, internet=internet)
    finally:
        os.chdir(original_cwd)


class TestCheckGMLReferencesCoverage:
    def test_urllib2_fallback_import(self) -> None:
        real_import = builtins.__import__
        fake_urllib2 = MagicMock()

        def import_hook(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "urllib.request":
                raise ImportError("urllib.request unavailable")
            if name == "urllib2":
                return fake_urllib2
            return real_import(name, globals, locals, fromlist, level)

        saved = sys.modules.pop("checkGMLReferences", None)
        with patch("builtins.__import__", import_hook):
            mod = importlib.import_module("checkGMLReferences")
            assert mod.urlRequest is fake_urllib2
        if saved is not None:
            sys.modules["checkGMLReferences"] = saved
        else:
            importlib.reload(checkGMLReferences)

    def test_internet_mode_bad_response_code(self) -> None:
        xml_content = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/common/test/ABC"/>
</root>"""

        class WeirdCode:
            def __lt__(self, other) -> bool:
                return True

            def __ge__(self, other) -> bool:
                return True

        mock_response = MagicMock()
        mock_response.getcode.return_value = WeirdCode()

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.xml"), "w") as fh:
                fh.write(xml_content)
            with patch("checkGMLReferences.urlRequest.urlopen", return_value=mock_response):
                result = _run_gml_check(tmpdir, internet=True)
        assert result == 1

    def test_concept_not_in_codelist_warning(self) -> None:
        xml_content = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/common/test/MISSING"/>
</root>"""
        rdf_path = os.path.join("schematrons", "3.0", "codes.wmo.int-common-test.rdf")
        rdf_content = """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/test/KNOWN"/>
    </skos:member>
</rdf:RDF>"""

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "schematrons", "3.0"), exist_ok=True)
            with open(os.path.join(tmpdir, rdf_path), "w") as fh:
                fh.write(rdf_content)
            with open(os.path.join(tmpdir, "test.xml"), "w") as fh:
                fh.write(xml_content)
            result = _run_gml_check(tmpdir)
        assert result == 0

    def test_invalid_codelist_reference_ioerror(self) -> None:
        xml_content = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/unknown/list/XYZ"/>
</root>"""

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.xml"), "w") as fh:
                fh.write(xml_content)
            result = _run_gml_check(tmpdir)
        assert result == 1

    def test_concept_mismatch_after_load(self) -> None:
        xml_content = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/common/test/WRONG"/>
</root>"""
        rdf_path = os.path.join("schematrons", "3.0", "codes.wmo.int-common-test.rdf")
        rdf_content = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Collection>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/test/foo/WRONG"/>
    </skos:member>
  </skos:Collection>
</rdf:RDF>"""

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "schematrons", "3.0"), exist_ok=True)
            with open(os.path.join(tmpdir, rdf_path), "w") as fh:
                fh.write(rdf_content)
            with open(os.path.join(tmpdir, "test.xml"), "w") as fh:
                fh.write(xml_content)
            result = _run_gml_check(tmpdir)
        assert result == 1

    def test_cached_rdf_mismatch_error(self) -> None:
        xml_content = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/common/test/a/A"/>
  <ref xlink:href="http://codes.wmo.int/common/test/b/A"/>
</root>"""
        rdf_path = os.path.join("schematrons", "3.0", "codes.wmo.int-common-test.rdf")
        rdf_content = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Collection>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/test/a/A"/>
    </skos:member>
  </skos:Collection>
</rdf:RDF>"""

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "schematrons", "3.0"), exist_ok=True)
            with open(os.path.join(tmpdir, rdf_path), "w") as fh:
                fh.write(rdf_content)
            with open(os.path.join(tmpdir, "test.xml"), "w") as fh:
                fh.write(xml_content)
            result = _run_gml_check(tmpdir)
        assert result == 1


class TestCodeListsToSchematronCoverage:
    def test_download_codelist_unicode_encode_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "café"

            real_open = open
            writes: list = []

            class TextWriter:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

                def write(self, data) -> None:
                    if isinstance(data, str):
                        raise UnicodeEncodeError("ascii", data, 0, 1, "bad")
                    writes.append(data)

            def open_hook(file, mode="r", *args, **kwargs):
                if "w" in mode:
                    return TextWriter()
                return real_open(file, mode, *args, **kwargs)

            with patch("codeListsToSchematron.requests.get", return_value=mock_response):
                with patch("builtins.open", side_effect=open_hook):
                    codeListsToSchematron.download_codelist("http://codes.wmo.int/common/nil", tmpdir)
            assert writes

    def test_fetch_local_copy_unicode_encode_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            html = "<html><body><table><a href='schema.xsd'>schema.xsd</a></table></body></html>"
            mock_page = MagicMock()
            mock_page.text = html
            mock_schema = MagicMock()
            mock_schema.status_code = 200
            mock_schema.text = "café"

            mock_file = MagicMock()
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=False)

            def write_side_effect(data) -> None:
                if isinstance(data, str):
                    raise UnicodeEncodeError("ascii", data, 0, 1, "bad")

            mock_file.write.side_effect = write_side_effect

            with patch("codeListsToSchematron.requests.get", side_effect=[mock_page, mock_schema]):
                with patch("builtins.open", return_value=mock_file):
                    codeListsToSchematron.fetchLocalCopy("http://schemas.wmo.int/iwxxm/3.0", "xsd", tmpdir)

    def test_symlink_skipped_when_destination_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_dir = os.path.join(tmpdir, "schemas", "3.0")
            schematron_dir = os.path.join(tmpdir, "schematrons", "3.0")
            os.makedirs(schema_dir)
            os.makedirs(schematron_dir)
            xsd_path = os.path.join(schema_dir, "test.xsd")
            with open(xsd_path, "w") as fh:
                fh.write(
                    """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:complexType name="WeatherType">
    <xs:annotation>
      <xs:appinfo>
        <xs:vocabulary>http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather</xs:vocabulary>
      </xs:appinfo>
    </xs:annotation>
  </xs:complexType>
</xs:schema>"""
                )
            with open(os.path.join(schema_dir, "iwxxm.xsd"), "w") as fh:
                fh.write('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>')
            open(os.path.join(schematron_dir, "iwxxm.sch"), "w").close()
            src_rdf = codeListsToSchematron.parseLocalCodeListFile("http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather")
            open(os.path.join(schematron_dir, src_rdf), "w").close()
            deslink = codeListsToSchematron.parseLocalCodeListFile("http://codes.wmo.int/306/4678")
            open(os.path.join(schematron_dir, deslink), "w").close()

            args = Mock()
            args.version = "3.0"

            with patch("codeListsToSchematron.os.getcwd", return_value=tmpdir):
                with patch("codeListsToSchematron.download_codelist"):
                    with patch("codeListsToSchematron.os.symlink") as mock_symlink:
                        codeListsToSchematron.run(args)
            mock_symlink.assert_not_called()

    def test_symlink_success_for_aerodrome_weather(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_dir = os.path.join(tmpdir, "schemas", "3.0")
            schematron_dir = os.path.join(tmpdir, "schematrons", "3.0")
            os.makedirs(schema_dir)
            os.makedirs(schematron_dir)
            xsd_path = os.path.join(schema_dir, "test.xsd")
            with open(xsd_path, "w") as fh:
                fh.write(
                    """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:complexType name="WeatherType">
    <xs:annotation>
      <xs:appinfo>
        <xs:vocabulary>http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather</xs:vocabulary>
      </xs:appinfo>
    </xs:annotation>
  </xs:complexType>
</xs:schema>"""
                )
            with open(os.path.join(schema_dir, "iwxxm.xsd"), "w") as fh:
                fh.write('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>')
            open(os.path.join(schematron_dir, "iwxxm.sch"), "w").close()
            src_rdf = codeListsToSchematron.parseLocalCodeListFile("http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather")
            open(os.path.join(schematron_dir, src_rdf), "w").close()

            args = Mock()
            args.version = "3.0"

            with patch("codeListsToSchematron.os.getcwd", return_value=tmpdir):
                with patch("codeListsToSchematron.download_codelist"):
                    with patch("codeListsToSchematron.os.symlink") as mock_symlink:
                        codeListsToSchematron.run(args)
            mock_symlink.assert_called_once()

    def test_symlink_failure_for_aerodrome_weather(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_dir = os.path.join(tmpdir, "schemas", "3.0")
            schematron_dir = os.path.join(tmpdir, "schematrons", "3.0")
            os.makedirs(schema_dir)
            os.makedirs(schematron_dir)
            xsd_path = os.path.join(schema_dir, "test.xsd")
            with open(xsd_path, "w") as fh:
                fh.write(
                    """<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:complexType name="WeatherType">
    <xs:annotation>
      <xs:appinfo>
        <xs:vocabulary>http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather</xs:vocabulary>
      </xs:appinfo>
    </xs:annotation>
  </xs:complexType>
</xs:schema>"""
                )
            with open(os.path.join(schema_dir, "iwxxm.xsd"), "w") as fh:
                fh.write('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>')
            open(os.path.join(schematron_dir, "iwxxm.sch"), "w").close()
            src_rdf = codeListsToSchematron.parseLocalCodeListFile("http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather")
            open(os.path.join(schematron_dir, src_rdf), "w").close()

            args = Mock()
            args.version = "3.0"

            with patch("codeListsToSchematron.os.getcwd", return_value=tmpdir):
                with patch("codeListsToSchematron.download_codelist"):
                    with patch("codeListsToSchematron.os.symlink", side_effect=OSError("symlink denied")):
                        codeListsToSchematron.run(args)

    def test_symlink_ms_windows(self) -> None:
        import ctypes

        mock_csl = MagicMock(return_value=1)
        mock_kernel = MagicMock()
        mock_kernel.kernel32.CreateSymbolicLinkW = mock_csl
        with patch.object(ctypes, "windll", mock_kernel, create=True):
            codeListsToSchematron.symlink_ms("/tmp/source", "/tmp/link")
        mock_csl.assert_called_once()

    def test_symlink_ms_windows_failure_raises(self) -> None:
        import ctypes

        mock_csl = MagicMock(return_value=0)
        mock_kernel = MagicMock()
        mock_kernel.kernel32.CreateSymbolicLinkW = mock_csl
        with patch.object(ctypes, "windll", mock_kernel, create=True):
            with patch.object(ctypes, "WinError", side_effect=ValueError("symlink failed"), create=True):
                with pytest.raises(ValueError):
                    codeListsToSchematron.symlink_ms("/tmp/source", "/tmp/link")


class TestIwxxmValidatorCoverage:
    def _setup_validator_tree(self, root: str) -> None:
        os.makedirs(os.path.join(root, "bin"), exist_ok=True)
        os.makedirs(os.path.join(root, "externalSchemas"), exist_ok=True)
        open(os.path.join(root, "bin", "crux-1.3-all.jar"), "w").close()

    def test_main_fetches_missing_schema_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._setup_validator_tree(tmpdir)
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                args = argparse.Namespace(
                    fetch=False,
                    version="3.0",
                    directory=tmpdir,
                    useInternet=False,
                    noGMLChecks=True,
                    keep=False,
                )
                with patch.object(codeListsToSchematron, "run") as mock_run:
                    with patch.object(iwxxmValidator, "validate_xml_files", return_value=0):
                        with pytest.raises(SystemExit) as exc_info:
                            iwxxmValidator.main(args)
                assert exc_info.value.code == 0
                mock_run.assert_called_once()
                assert getattr(args, "noGMLCheck", False) is False
            finally:
                os.chdir(original_cwd)

    def test_validate_xml_files_gml_check_failure_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._setup_validator_tree(tmpdir)
            schema_dir = os.path.join(tmpdir, "schemas", "3.0")
            schematron_dir = os.path.join(tmpdir, "schematrons", "3.0")
            os.makedirs(schema_dir)
            os.makedirs(schematron_dir)
            open(os.path.join(schema_dir, "iwxxm.xsd"), "w").close()
            open(os.path.join(schematron_dir, "iwxxm.sch"), "w").close()
            open(os.path.join(tmpdir, "catalog.template.xml"), "w").write("<catalog/>")

            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                args = argparse.Namespace(
                    version="3.0",
                    directory=tmpdir,
                    useInternet=False,
                    noGMLChecks=False,
                    keep=True,
                )
                with patch("iwxxmValidator.os.system", return_value=0):
                    with patch.object(checkGMLReferences, "check_GML_references", return_value=1):
                        result = iwxxmValidator.validate_xml_files(args)
                assert result == 1
            finally:
                os.chdir(original_cwd)

    def test_validate_xml_files_skips_gml_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._setup_validator_tree(tmpdir)
            schema_dir = os.path.join(tmpdir, "schemas", "3.0")
            schematron_dir = os.path.join(tmpdir, "schematrons", "3.0")
            os.makedirs(schema_dir)
            os.makedirs(schematron_dir)
            with open(os.path.join(schema_dir, "iwxxm.xsd"), "w") as fh:
                fh.write('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>')
            open(os.path.join(schematron_dir, "iwxxm.sch"), "w").close()
            open(os.path.join(tmpdir, "catalog.template.xml"), "w").write("<catalog/>")

            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                args = argparse.Namespace(
                    version="3.0",
                    directory=tmpdir,
                    useInternet=False,
                    noGMLChecks=True,
                    keep=True,
                )
                with patch("iwxxmValidator.os.system", return_value=0):
                    with patch.object(checkGMLReferences, "check_GML_references") as mock_gml:
                        result = iwxxmValidator.validate_xml_files(args)
                mock_gml.assert_not_called()
                assert result == 0
            finally:
                os.chdir(original_cwd)


class TestCheckGMLReferencesRemainingBranches:
    def test_ignored_external_url_is_skipped(self) -> None:
        xml_content = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/common/test/SKIP"/>
</root>"""

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.xml"), "w") as fh:
                fh.write(xml_content)
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                with open("ignoredURLs.txt", "w") as fh:
                    fh.write("http://codes.wmo.int/common/test\n")
                result = checkGMLReferences.check_GML_references(tmpdir, "3.0", internet=False)
            finally:
                os.chdir(original_cwd)
        assert result == 0

    def test_second_valid_ref_uses_cached_concepts(self) -> None:
        xml_content = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/common/test/ONE"/>
  <ref xlink:href="http://codes.wmo.int/common/test/TWO"/>
</root>"""
        rdf_path = os.path.join("schematrons", "3.0", "codes.wmo.int-common-test.rdf")
        rdf_content = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Collection>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/test/ONE"/>
    </skos:member>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/test/TWO"/>
    </skos:member>
  </skos:Collection>
</rdf:RDF>"""

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "schematrons", "3.0"), exist_ok=True)
            with open(os.path.join(tmpdir, rdf_path), "w") as fh:
                fh.write(rdf_content)
            with open(os.path.join(tmpdir, "test.xml"), "w") as fh:
                fh.write(xml_content)
            result = _run_gml_check(tmpdir)
        assert result == 0

    def test_cached_rdf_mismatch_on_second_document(self) -> None:
        valid_doc = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/common/test/a/KNOWN"/>
</root>"""
        invalid_doc = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/common/test/b/KNOWN"/>
</root>"""
        rdf_path = os.path.join("schematrons", "3.0", "codes.wmo.int-common-test.rdf")
        rdf_content = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Collection>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/test/a/KNOWN"/>
    </skos:member>
  </skos:Collection>
</rdf:RDF>"""

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "schematrons", "3.0"), exist_ok=True)
            with open(os.path.join(tmpdir, rdf_path), "w") as fh:
                fh.write(rdf_content)
            with open(os.path.join(tmpdir, "01-warm.xml"), "w") as fh:
                fh.write(valid_doc)
            with open(os.path.join(tmpdir, "02-bad.xml"), "w") as fh:
                fh.write(invalid_doc)
            result = _run_gml_check(tmpdir)
        assert result == 1

    def test_duplicate_unknown_codelist_only_warns_once(self) -> None:
        xml_content = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/unknown/list/A"/>
  <ref xlink:href="http://codes.wmo.int/unknown/list/B"/>
</root>"""

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.xml"), "w") as fh:
                fh.write(xml_content)
            result = _run_gml_check(tmpdir)
        assert result == 1

    def test_concept_key_collision_triggers_cache_miss_keyerror(self) -> None:
        xml_content = """<?xml version="1.0"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink">
  <ref xlink:href="http://codes.wmo.int/common/alpha/ITEM"/>
  <ref xlink:href="http://codes.wmo.int/common/beta/ITEM"/>
</root>"""
        alpha_rdf = os.path.join("schematrons", "3.0", "codes.wmo.int-common-alpha.rdf")
        beta_rdf = os.path.join("schematrons", "3.0", "codes.wmo.int-common-beta.rdf")
        alpha_content = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Collection>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/alpha/ITEM"/>
    </skos:member>
  </skos:Collection>
</rdf:RDF>"""
        beta_content = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Collection>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/beta/ITEM"/>
    </skos:member>
  </skos:Collection>
</rdf:RDF>"""

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "schematrons", "3.0"), exist_ok=True)
            with open(os.path.join(tmpdir, alpha_rdf), "w") as fh:
                fh.write(alpha_content)
            with open(os.path.join(tmpdir, beta_rdf), "w") as fh:
                fh.write(beta_content)
            with open(os.path.join(tmpdir, "test.xml"), "w") as fh:
                fh.write(xml_content)
            result = _run_gml_check(tmpdir)
        assert result == 0
