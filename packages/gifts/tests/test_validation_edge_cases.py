"""
Additional tests to push checkGMLReferences and codeListsToSchematron above 90% coverage
"""

import os
import sys
from unittest.mock import Mock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import validation.checkGMLReferences as checkGMLReferences
import validation.codeListsToSchematron as codeListsToSchematron


class TestCheckGMLReferencesEdgeCases:
    """Additional edge case tests for checkGMLReferences to reach 90%+"""

    def test_check_GML_references_no_external_refs(self, tmp_path):
        """Test when there are no external references in XML"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:gml="http://www.opengis.net/gml/3.2">
    <element gml:id="uuid.test123">Test</element>
    <ref xlink:href="#uuid.test123"/>
</root>"""

        xml_file = tmp_path / "test.xml"
        xml_file.write_text(xml_content)

        ignored_file = tmp_path / "ignoredURLs.txt"
        ignored_file.write_text("")

        with patch("validation.checkGMLReferences.os.getcwd", return_value=str(tmp_path)):
            result = checkGMLReferences.check_GML_references(str(tmp_path), "3.0", internet=False)

        # No external refs, should succeed
        assert result == 0


class TestCodeListsToSchematronEdgeCases:
    """Additional edge case tests for codeListsToSchematron to reach 90%+"""

    def test_run_directory_not_exist_error(self, tmp_path):
        """Test run() when schema/schematron directories don't exist after creation attempts"""
        mock_args = Mock()
        mock_args.version = "3.0"

        # Mock os.path.isdir to return False even after mkdir attempts
        with patch("validation.codeListsToSchematron.os.getcwd", return_value=str(tmp_path)):
            with patch("validation.codeListsToSchematron.os.path.exists", return_value=False):
                with patch("validation.codeListsToSchematron.os.mkdir"):
                    with patch("validation.codeListsToSchematron.os.path.isfile", return_value=False):
                        with patch("validation.codeListsToSchematron.os.path.isdir", return_value=False):
                            with pytest.raises(SystemExit) as exc_info:
                                codeListsToSchematron.run(mock_args)
                            assert exc_info.value.code == 1

    def test_run_python2_windows_symlink(self, tmp_path):
        """Test run() with Python 2 on Windows (symlink_ms)"""
        mock_args = Mock()
        mock_args.version = "3.0"

        schemas_dir = tmp_path / "schemas" / "3.0"
        schemas_dir.mkdir(parents=True)

        schematrons_dir = tmp_path / "schematrons" / "3.0"
        schematrons_dir.mkdir(parents=True)

        # Create XSD with AerodromePresentOrForecastWeather vocabulary
        xsd_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:complexType name="Test">
        <xs:annotation>
            <xs:appinfo>
                <xs:vocabulary>http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather</xs:vocabulary>
            </xs:appinfo>
        </xs:annotation>
    </xs:complexType>
</xs:schema>"""

        (schemas_dir / "test.xsd").write_text(xsd_content)
        (schemas_dir / "iwxxm.xsd").write_text('<?xml version="1.0"?>\n<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>')
        (schematrons_dir / "iwxxm.sch").write_text('<?xml version="1.0"?>\n<schema/>')

        # Create source RDF file
        src_rdf = schematrons_dir / "codes.wmo.int-49-2-AerodromePresentOrForecastWeather.rdf"
        src_rdf.write_text('<?xml version="1.0"?><rdf:RDF/>')

        # Mock Python 2 on Windows
        with patch("validation.codeListsToSchematron.sys.version_info", Mock(major=2)):
            with patch("validation.codeListsToSchematron.os.name", "nt"):
                with patch("validation.codeListsToSchematron.os.getcwd", return_value=str(tmp_path)):
                    with patch("validation.codeListsToSchematron.download_codelist"):
                        with patch("validation.codeListsToSchematron.symlink_ms") as mock_symlink:
                            # Assign the mock function to os.symlink
                            with patch("validation.codeListsToSchematron.os.symlink", mock_symlink):
                                codeListsToSchematron.run(mock_args)

    def test_symlink_creation_exception(self, tmp_path):
        """Test run() when symlink creation raises an exception"""
        mock_args = Mock()
        mock_args.version = "3.0"

        schemas_dir = tmp_path / "schemas" / "3.0"
        schemas_dir.mkdir(parents=True)

        schematrons_dir = tmp_path / "schematrons" / "3.0"
        schematrons_dir.mkdir(parents=True)

        # Create XSD with vocabulary
        xsd_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:complexType name="Test">
        <xs:annotation>
            <xs:appinfo>
                <xs:vocabulary>http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather</xs:vocabulary>
            </xs:appinfo>
        </xs:annotation>
    </xs:complexType>
</xs:schema>"""

        (schemas_dir / "test.xsd").write_text(xsd_content)
        (schemas_dir / "iwxxm.xsd").write_text('<?xml version="1.0"?>\n<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>')
        (schematrons_dir / "iwxxm.sch").write_text('<?xml version="1.0"?>\n<schema/>')

        # Create source RDF file
        src_rdf = schematrons_dir / "codes.wmo.int-49-2-AerodromePresentOrForecastWeather.rdf"
        src_rdf.write_text('<?xml version="1.0"?><rdf:RDF/>')

        with patch("validation.codeListsToSchematron.os.getcwd", return_value=str(tmp_path)):
            with patch("validation.codeListsToSchematron.download_codelist"):
                with patch("validation.codeListsToSchematron.os.symlink", side_effect=Exception("Symlink failed")):
                    # Should handle exception gracefully
                    codeListsToSchematron.run(mock_args)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
