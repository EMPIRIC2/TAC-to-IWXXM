"""
Final tests to push validation coverage to 95%
Focus on uncovered lines: checkGMLReferences 89-146, codeListsToSchematron 86-169, iwxxmValidator 27-34
"""
import pytest
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / 'validation'))

import checkGMLReferences
import codeListsToSchematron
import iwxxmValidator


class TestValidationTo95Percent:
    """Targeted tests to reach 95% coverage"""

    def test_checkGMLReferences_success_message(self):
        """Test successful URL resolution message"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2">
  <element gml:id="uuid.test-1"/>
</root>'''

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test.xml')
            with open(test_file, 'w') as f:
                f.write(xml_content)

            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # This should print "SUCCESS: All URL successfully resolved."
                result = checkGMLReferences.check_GML_references(tmpdir, '3.0', internet=False)
                assert result == 0
            finally:
                os.chdir(original_cwd)

    def test_iwxxmValidator_main_success_message(self):
        """Test main function success message"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()

            bin_dir = os.path.join(tmpdir, 'bin')
            os.makedirs(bin_dir)
            external_dir = os.path.join(tmpdir, 'externalSchemas')
            os.makedirs(external_dir)
            schemas_dir = os.path.join(tmpdir, 'schemas', '3.0')
            os.makedirs(schemas_dir)
            schematrons_dir = os.path.join(tmpdir, 'schematrons', '3.0')
            os.makedirs(schematrons_dir)

            with open(os.path.join(bin_dir, 'crux-1.3-all.jar'), 'w') as f:
                f.write('mock')
            with open(os.path.join(schemas_dir, 'iwxxm.xsd'), 'w') as f:
                f.write('<schema/>')
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
                args.fetch = False
                args.keep = False
                args.noGMLChecks = True

                # Mock successful validation
                with patch('os.system', return_value=0):
                    with pytest.raises(SystemExit) as exc_info:
                        iwxxmValidator.main(args)

                    # Should print "Validation SUCCESSFUL"
                    assert exc_info.value.code == 0
            finally:
                os.chdir(original_cwd)

    def test_iwxxmValidator_main_failure_message(self):
        """Test main function failure message"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()

            bin_dir = os.path.join(tmpdir, 'bin')
            os.makedirs(bin_dir)
            external_dir = os.path.join(tmpdir, 'externalSchemas')
            os.makedirs(external_dir)
            schemas_dir = os.path.join(tmpdir, 'schemas', '3.0')
            os.makedirs(schemas_dir)
            schematrons_dir = os.path.join(tmpdir, 'schematrons', '3.0')
            os.makedirs(schematrons_dir)

            with open(os.path.join(bin_dir, 'crux-1.3-all.jar'), 'w') as f:
                f.write('mock')
            with open(os.path.join(schemas_dir, 'iwxxm.xsd'), 'w') as f:
                f.write('<schema/>')
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
                args.fetch = False
                args.keep = False
                args.noGMLChecks = True

                # Mock failed validation
                with patch('os.system', return_value=256):
                    with pytest.raises(SystemExit) as exc_info:
                        iwxxmValidator.main(args)

                    # Should print "Validation FAILED"
                    assert exc_info.value.code == 1
            finally:
                os.chdir(original_cwd)

    def test_codeListsToSchematron_run_detailed(self):
        """Test run function creates directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                args = Mock()
                args.version = '3.0'

                # Mock all external calls
                with patch('codeListsToSchematron.fetchLocalCopy', return_value=None):
                    with patch('codeListsToSchematron.download_codelist', return_value=None):
                        with patch('os.listdir', return_value=[]):
                            codeListsToSchematron.run(args)

                # Should create directories
                assert os.path.exists(os.path.join(tmpdir, 'schemas', '3.0'))
                assert os.path.exists(os.path.join(tmpdir, 'schematrons', '3.0'))
            finally:
                os.chdir(original_cwd)
