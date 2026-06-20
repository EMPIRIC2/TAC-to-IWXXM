"""
Comprehensive tests for validation modules
"""
import pytest
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from lxml import etree

# Add validation to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'validation'))

import checkGMLReferences
import codeListsToSchematron
import iwxxmValidator


class TestCheckGMLReferences:
    """Test checkGMLReferences.py functionality"""

    def test_get_concepts_with_valid_rdf(self):
        """Test getConcepts with valid RDF file matching actual WMO format"""
        # Use actual WMO RDF structure with nested skos:member tags
        rdf_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Collection>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/test/ABC"/>
    </skos:member>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/test/DEF"/>
    </skos:member>
  </skos:Collection>
</rdf:RDF>'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.rdf', delete=False) as f:
            f.write(rdf_content)
            temp_file = f.name

        try:
            concepts = {}
            checkGMLReferences.getConcepts(temp_file, concepts)

            assert 'ABC' in concepts
            assert 'DEF' in concepts
            assert len(concepts) == 2
            assert concepts['ABC'] == ['http://codes.wmo.int/common/test/ABC']
            assert concepts['DEF'] == ['http://codes.wmo.int/common/test/DEF']
        finally:
            os.unlink(temp_file)

    def test_get_concepts_empty_file(self):
        """Test getConcepts with file without concepts"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="http://example.com"/>'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            concepts = {}
            checkGMLReferences.getConcepts(temp_file, concepts)
            assert len(concepts) == 0
        finally:
            os.unlink(temp_file)

    def test_read_ignored_urls(self):
        """Test readIgnoredURLs with valid file"""
        content = '''# Comment line
http://example.com/ignore1
http://example.com/ignore2

# Another comment
http://example.com/ignore3'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            urls = checkGMLReferences.readIgnoredURLs(temp_file)
            assert len(urls) == 3
            assert 'http://example.com/ignore1' in urls
            assert 'http://example.com/ignore2' in urls
            assert 'http://example.com/ignore3' in urls
        finally:
            os.unlink(temp_file)

    def test_read_ignored_urls_empty(self):
        """Test readIgnoredURLs with empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('# Only comments\n\n# More comments')
            temp_file = f.name

        try:
            urls = checkGMLReferences.readIgnoredURLs(temp_file)
            assert len(urls) == 0
        finally:
            os.unlink(temp_file)

    def test_check_gml_references_no_files(self):
        """Test check_GML_references with empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = checkGMLReferences.check_GML_references(tmpdir, '3.0', internet=False)
            assert result == 1  # Should return error for no files

    def test_check_gml_references_with_valid_xml(self):
        """Test check_GML_references with valid XML file"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <element gml:id="uuid.test-id-1"/>
  <reference xlink:href="#uuid.test-id-1"/>
</root>'''

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test.xml')
            with open(test_file, 'w') as f:
                f.write(xml_content)

            # Change to temp directory so ignoredURLs.txt check works
            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                result = checkGMLReferences.check_GML_references(tmpdir, '3.0', internet=False)
                # Should succeed as all references are valid
                assert result == 0
            finally:
                os.chdir(original_cwd)

    def test_check_gml_references_with_missing_id(self):
        """Test check_GML_references with missing gml:id"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <element gml:id="uuid.test-id-1"/>
  <reference xlink:href="#uuid.missing-id"/>
</root>'''

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test.xml')
            with open(test_file, 'w') as f:
                f.write(xml_content)

            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                result = checkGMLReferences.check_GML_references(tmpdir, '3.0', internet=False)
                # Should fail due to missing ID
                assert result == 1
            finally:
                os.chdir(original_cwd)


class TestCodeListsToSchematron:
    """Test codeListsToSchematron.py functionality"""

    def test_run_creates_directories(self):
        """Test run function creates necessary directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Create mock args
                args = Mock()
                args.version = '3.0'

                # Mock the fetchLocalCopy function
                with patch.object(codeListsToSchematron, 'fetchLocalCopy', return_value=None):
                    with patch.object(codeListsToSchematron, 'download_codelist', return_value=None):
                        # Mock os.listdir to return empty
                        with patch('os.listdir', return_value=[]):
                            codeListsToSchematron.run(args)

                # Check directories were created
                assert os.path.exists(os.path.join(tmpdir, 'schemas'))
                assert os.path.exists(os.path.join(tmpdir, 'schemas', '3.0'))
                assert os.path.exists(os.path.join(tmpdir, 'schematrons'))
                assert os.path.exists(os.path.join(tmpdir, 'schematrons', '3.0'))
            finally:
                os.chdir(original_cwd)

    def test_run_with_existing_directories(self):
        """Test run function with existing directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Pre-create directories
                os.makedirs(os.path.join(tmpdir, 'schemas', '3.0'))
                os.makedirs(os.path.join(tmpdir, 'schematrons', '3.0'))

                # Create mock schema and schematron files
                with open(os.path.join(tmpdir, 'schemas', '3.0', 'iwxxm.xsd'), 'w') as f:
                    f.write('<schema/>')
                with open(os.path.join(tmpdir, 'schematrons', '3.0', 'iwxxm.sch'), 'w') as f:
                    f.write('<schema/>')

                args = Mock()
                args.version = '3.0'

                with patch.object(codeListsToSchematron, 'fetchLocalCopy', return_value=None):
                    with patch.object(codeListsToSchematron, 'download_codelist', return_value=None):
                        with patch('os.listdir', return_value=[]):
                            codeListsToSchematron.run(args)

                # Should complete successfully
                assert os.path.exists(os.path.join(tmpdir, 'schemas', '3.0'))
            finally:
                os.chdir(original_cwd)


class TestIWXXMValidator:
    """Test iwxxmValidator.py functionality"""

    def test_validate_xml_files_creates_catalog(self):
        """Test validate_xml_files creates catalog file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()

            # Create necessary structure
            bin_dir = os.path.join(tmpdir, 'bin')
            os.makedirs(bin_dir)
            schemas_dir = os.path.join(tmpdir, 'schemas', '3.0')
            os.makedirs(schemas_dir)
            schematrons_dir = os.path.join(tmpdir, 'schematrons', '3.0')
            os.makedirs(schematrons_dir)

            # Create mock files
            with open(os.path.join(bin_dir, 'crux-1.3-all.jar'), 'w') as f:
                f.write('mock')
            with open(os.path.join(schematrons_dir, 'iwxxm.sch'), 'w') as f:
                f.write('<schema/>')

            # Create catalog template
            catalog_template = os.path.join(tmpdir, 'catalog.template.xml')
            with open(catalog_template, 'w') as f:
                f.write('''<?xml version="1.0"?>
<catalog>
  <installDir>${INSTALL_DIR}</installDir>
  <version>${IWXXM_VERSION}</version>
  <versionDir>${IWXXM_VERSION_DIR}</versionDir>
</catalog>''')

            # Create test directory with XML
            test_dir = os.path.join(tmpdir, 'test_xml')
            os.makedirs(test_dir)
            with open(os.path.join(test_dir, 'test.xml'), 'w') as f:
                f.write('<root/>')

            os.chdir(tmpdir)

            try:
                args = Mock()
                args.version = '3.0'
                args.directory = test_dir
                args.keep = False
                args.noGMLChecks = True

                # Mock os.system to return success
                with patch('os.system', return_value=0):
                    result = iwxxmValidator.validate_xml_files(args)

                # Should create catalog file
                catalog_file = os.path.join(tmpdir, 'catalog-3.0.xml')
                assert not os.path.exists(catalog_file)  # Should be deleted
                assert result == 0
            finally:
                os.chdir(original_cwd)

    def test_validate_xml_files_with_gml_checks(self):
        """Test validate_xml_files with GML checks enabled"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()

            # Setup
            bin_dir = os.path.join(tmpdir, 'bin')
            os.makedirs(bin_dir)
            schemas_dir = os.path.join(tmpdir, 'schemas', '3.0')
            os.makedirs(schemas_dir)
            schematrons_dir = os.path.join(tmpdir, 'schematrons', '3.0')
            os.makedirs(schematrons_dir)

            with open(os.path.join(bin_dir, 'crux-1.3-all.jar'), 'w') as f:
                f.write('mock')
            with open(os.path.join(schematrons_dir, 'iwxxm.sch'), 'w') as f:
                f.write('<schema/>')

            catalog_template = os.path.join(tmpdir, 'catalog.template.xml')
            with open(catalog_template, 'w') as f:
                f.write('<?xml version="1.0"?><catalog/>')

            test_dir = os.path.join(tmpdir, 'test_xml')
            os.makedirs(test_dir)

            os.chdir(tmpdir)

            try:
                args = Mock()
                args.version = '3.0'
                args.directory = test_dir
                args.keep = False
                args.noGMLChecks = False
                args.useInternet = False

                with patch('os.system', return_value=0):
                    with patch.object(checkGMLReferences, 'check_GML_references', return_value=0):
                        result = iwxxmValidator.validate_xml_files(args)

                assert result == 0
            finally:
                os.chdir(original_cwd)

    def test_main_with_fetch(self):
        """Test main function with fetch option"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()

            # Setup required directory structure
            bin_dir = os.path.join(tmpdir, 'bin')
            os.makedirs(bin_dir)
            external_dir = os.path.join(tmpdir, 'externalSchemas')
            os.makedirs(external_dir)
            schemas_dir = os.path.join(tmpdir, 'schemas', '3.0')
            os.makedirs(schemas_dir)
            schematrons_dir = os.path.join(tmpdir, 'schematrons', '3.0')
            os.makedirs(schematrons_dir)

            # Create required files
            with open(os.path.join(bin_dir, 'crux-1.3-all.jar'), 'w') as f:
                f.write('mock')
            with open(os.path.join(schemas_dir, 'iwxxm.xsd'), 'w') as f:
                f.write('<schema/>')
            with open(os.path.join(schematrons_dir, 'iwxxm.sch'), 'w') as f:
                f.write('<schema/>')

            # Create catalog template
            catalog_template = os.path.join(tmpdir, 'catalog.template.xml')
            with open(catalog_template, 'w') as f:
                f.write('''<?xml version="1.0"?>
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
  <rewriteSystem systemIdStartString="http://schemas.wmo.int/iwxxm" 
                  rewritePrefix="${INSTALL_DIR}/schemas/${IWXXM_VERSION}"/>
</catalog>''')

            os.chdir(tmpdir)

            try:
                args = Mock()
                args.version = '3.0'
                args.directory = tmpdir
                args.fetch = True
                args.keep = False
                args.noGMLChecks = True

                with patch.object(codeListsToSchematron, 'run', return_value=None):
                    with patch('os.system', return_value=0):
                        with pytest.raises(SystemExit) as exc_info:
                            iwxxmValidator.main(args)

                        assert exc_info.value.code == 0
            finally:
                os.chdir(original_cwd)

    def test_main_missing_jar_file(self):
        """Test main function with missing JAR file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                args = Mock()
                args.version = '3.0'

                with pytest.raises(SystemExit) as exc_info:
                    iwxxmValidator.main(args)

                assert exc_info.value.code == 1
            finally:
                os.chdir(original_cwd)


class TestCodeListsToSchematronXMLProcessing:
    """Test XML processing in codeListsToSchematron"""

    def test_xsd_file_parsing(self):
        """Test XSD file parsing for vocabularies"""
        xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:complexType name="TestType">
    <xs:annotation>
      <xs:appinfo>
        <xs:vocabulary>http://codes.wmo.int/test/vocab</xs:vocabulary>
      </xs:appinfo>
    </xs:annotation>
  </xs:complexType>
</xs:schema>'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as f:
            f.write(xsd_content)
            temp_file = f.name

        try:
            tree = etree.parse(temp_file)
            root = tree.getroot()

            ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
            complexTypes = root.findall('xs:complexType', ns)

            assert len(complexTypes) == 1
            assert complexTypes[0].attrib['name'] == 'TestType'
        finally:
            os.unlink(temp_file)


class TestGMLReferencesConcepts:
    """Test concept extraction from RDF"""

    def test_concepts_with_multiple_urls(self):
        """Test concept extraction with multiple URLs for same key"""
        rdf_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Collection>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/common/test/ABC"/>
    </skos:member>
    <skos:member>
      <skos:Concept rdf:about="http://codes.wmo.int/other/test/ABC"/>
    </skos:member>
  </skos:Collection>
</rdf:RDF>'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.rdf', delete=False) as f:
            f.write(rdf_content)
            temp_file = f.name

        try:
            concepts = {}
            checkGMLReferences.getConcepts(temp_file, concepts)

            # Same key 'ABC' should have two URLs
            assert 'ABC' in concepts
            assert len(concepts['ABC']) == 2
            assert 'http://codes.wmo.int/common/test/ABC' in concepts['ABC']
            assert 'http://codes.wmo.int/other/test/ABC' in concepts['ABC']
        finally:
            os.unlink(temp_file)


class TestIWXXMValidatorEdgeCases:
    """Test edge cases in IWXXM validator"""

    def test_validate_with_existing_catalog(self):
        """Test validation with existing catalog file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()

            # Setup
            bin_dir = os.path.join(tmpdir, 'bin')
            os.makedirs(bin_dir)
            schemas_dir = os.path.join(tmpdir, 'schemas', '3.0')
            os.makedirs(schemas_dir)
            schematrons_dir = os.path.join(tmpdir, 'schematrons', '3.0')
            os.makedirs(schematrons_dir)

            with open(os.path.join(bin_dir, 'crux-1.3-all.jar'), 'w') as f:
                f.write('mock')
            with open(os.path.join(schematrons_dir, 'iwxxm.sch'), 'w') as f:
                f.write('<schema/>')

            catalog_template = os.path.join(tmpdir, 'catalog.template.xml')
            with open(catalog_template, 'w') as f:
                f.write('<?xml version="1.0"?><catalog/>')

            # Pre-create catalog file
            catalog_file = os.path.join(tmpdir, 'catalog-3.0.xml')
            with open(catalog_file, 'w') as f:
                f.write('<?xml version="1.0"?><existing/>')

            test_dir = os.path.join(tmpdir, 'test_xml')
            os.makedirs(test_dir)

            os.chdir(tmpdir)

            try:
                args = Mock()
                args.version = '3.0'
                args.directory = test_dir
                args.keep = True
                args.noGMLChecks = True

                with patch('os.system', return_value=0):
                    result = iwxxmValidator.validate_xml_files(args)

                # Catalog should still exist (keep=True)
                assert os.path.exists(catalog_file)
                assert result == 0
            finally:
                os.chdir(original_cwd)

    def test_validate_with_validation_failure(self):
        """Test validation with failed validation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()

            # Setup
            bin_dir = os.path.join(tmpdir, 'bin')
            os.makedirs(bin_dir)
            schemas_dir = os.path.join(tmpdir, 'schemas', '3.0')
            os.makedirs(schemas_dir)
            schematrons_dir = os.path.join(tmpdir, 'schematrons', '3.0')
            os.makedirs(schematrons_dir)

            with open(os.path.join(bin_dir, 'crux-1.3-all.jar'), 'w') as f:
                f.write('mock')
            with open(os.path.join(schematrons_dir, 'iwxxm.sch'), 'w') as f:
                f.write('<schema/>')

            catalog_template = os.path.join(tmpdir, 'catalog.template.xml')
            with open(catalog_template, 'w') as f:
                f.write('<?xml version="1.0"?><catalog/>')

            test_dir = os.path.join(tmpdir, 'test_xml')
            os.makedirs(test_dir)

            os.chdir(tmpdir)

            try:
                args = Mock()
                args.version = '3.0'
                args.directory = test_dir
                args.keep = False
                args.noGMLChecks = True

                # Mock validation failure (return code 256)
                with patch('os.system', return_value=256):
                    result = iwxxmValidator.validate_xml_files(args)

                # Should normalize 256 to 1
                assert result == 1
            finally:
                os.chdir(original_cwd)
