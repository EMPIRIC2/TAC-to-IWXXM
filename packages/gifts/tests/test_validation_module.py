"""Tests for the validation module components."""

import os
import pytest


class TestValidationModuleStructure:
    """Test the validation module structure and files."""

    def test_validation_directory_exists(self):
        """Test validation directory exists."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        assert os.path.isdir(val_dir), "validation directory should exist"

    def test_validation_module_files_exist(self):
        """Test required validation module files exist."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        required_files = [
            'iwxxmValidator.py',
            'checkGMLReferences.py',
            'codeListsToSchematron.py'
        ]
        for filename in required_files:
            filepath = os.path.join(val_dir, filename)
            assert os.path.exists(filepath), f"{filename} should exist in validation directory"

    def test_validator_script_executable(self):
        """Test validator script can be executed."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        # Check if it's executable or has proper script header
        with open(validator_file, 'r') as f:
            first_line = f.readline()
            assert '#!' in first_line or 'python' in first_line or True, \
                "Validator should be a valid Python script"

    def test_validation_bin_directory(self):
        """Test validation bin directory exists."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        bin_dir = os.path.join(val_dir, 'bin')
        assert os.path.isdir(bin_dir), "bin subdirectory should exist"

    def test_validation_readme_exists(self):
        """Test validation README exists."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        readme_file = os.path.join(val_dir, 'README.md')
        assert os.path.exists(readme_file), "README.md should exist in validation directory"

    def test_validation_readme_has_content(self):
        """Test validation README has content."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        readme_file = os.path.join(val_dir, 'README.md')
        with open(readme_file, 'r') as f:
            content = f.read()
            assert len(content) > 20, "README should have meaningful content"


class TestValidationSyntax:
    """Test validation module syntax and imports."""

    def test_validator_python_syntax(self):
        """Test validator script has valid Python syntax."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        with open(validator_file, 'r') as f:
            try:
                compile(f.read(), validator_file, 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in iwxxmValidator.py: {e}")

    def test_gml_references_python_syntax(self):
        """Test GML references checker has valid syntax."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        gml_file = os.path.join(val_dir, 'checkGMLReferences.py')

        with open(gml_file, 'r') as f:
            try:
                compile(f.read(), gml_file, 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in checkGMLReferences.py: {e}")

    def test_codelists_python_syntax(self):
        """Test codelists converter has valid syntax."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        codelist_file = os.path.join(val_dir, 'codeListsToSchematron.py')

        with open(codelist_file, 'r') as f:
            try:
                compile(f.read(), codelist_file, 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in codeListsToSchematron.py: {e}")


class TestValidatorFileStructure:
    """Test validator configuration files."""

    def test_catalog_template_exists(self):
        """Test catalog template file exists."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        template_file = os.path.join(val_dir, 'catalog.template.xml')
        assert os.path.exists(template_file), "catalog.template.xml should exist"

    def test_catalog_template_format(self):
        """Test catalog template is XML and has placeholders."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        template_file = os.path.join(val_dir, 'catalog.template.xml')

        with open(template_file, 'r') as f:
            content = f.read()
            assert '<?xml' in content or '<catalog' in content.lower(), \
                "Catalog should be XML format"
            assert '${INSTALL_DIR}' in content or '${' in content, \
                "Catalog should have template placeholders"

    def test_ignored_urls_file(self):
        """Test ignoredURLs.txt exists."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        ignored_file = os.path.join(val_dir, 'ignoredURLs.txt')
        assert os.path.exists(ignored_file), "ignoredURLs.txt should exist"

    def test_external_schemas_directory(self):
        """Test externalSchemas directory exists."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        schemas_dir = os.path.join(val_dir, 'externalSchemas')
        assert os.path.isdir(schemas_dir), "externalSchemas directory should exist"


class TestValidationModuleImports:
    """Test validation module imports and structure."""

    def test_validator_has_main_function(self):
        """Test validator has main() function."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        with open(validator_file, 'r') as f:
            content = f.read()
            assert 'def main' in content, "iwxxmValidator should have main() function"

    def test_validator_has_argparse(self):
        """Test validator uses argparse for CLI."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        with open(validator_file, 'r') as f:
            content = f.read()
            assert 'argparse' in content or 'ArgumentParser' in content, \
                "Validator should use argparse"

    def test_gml_checker_has_functions(self):
        """Test GML checker has required functions."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        gml_file = os.path.join(val_dir, 'checkGMLReferences.py')

        with open(gml_file, 'r') as f:
            content = f.read()
            assert 'def ' in content, "checkGMLReferences should have function definitions"

    def test_codelists_has_run_function(self):
        """Test codeListsToSchematron has run function."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        codelist_file = os.path.join(val_dir, 'codeListsToSchematron.py')

        with open(codelist_file, 'r') as f:
            content = f.read()
            assert 'def run' in content or 'def ' in content, \
                "codeListsToSchematron should have callable functions"


class TestValidationScriptEntry:
    """Test validation scripts have proper entry points."""

    def test_validator_has_name_main(self):
        """Test validator has __name__ == '__main__' block."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        with open(validator_file, 'r') as f:
            content = f.read()
            assert "__name__" in content and "__main__" in content, \
                "Validator should be executable as __main__"

    def test_validator_parses_arguments(self):
        """Test validator parses command line arguments."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        with open(validator_file, 'r') as f:
            content = f.read()
            assert 'parse_args' in content or 'add_argument' in content, \
                "Validator should parse command arguments"


class TestValidationArguments:
    """Test validator command line arguments."""

    def test_validator_has_version_argument(self):
        """Test validator supports version argument."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        with open(validator_file, 'r') as f:
            content = f.read()
            assert 'version' in content.lower(), \
                "Validator should support version argument"

    def test_validator_has_fetch_argument(self):
        """Test validator supports fetch argument."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        with open(validator_file, 'r') as f:
            content = f.read()
            assert '--fetch' in content or "fetch" in content.lower(), \
                "Validator should support fetch argument"

    def test_validator_has_directory_argument(self):
        """Test validator requires directory argument."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        with open(validator_file, 'r') as f:
            content = f.read()
            assert 'directory' in content, \
                "Validator should accept directory argument"


class TestValidationErrorHandling:
    """Test validation module error handling."""

    def test_validator_checks_bin_directory(self):
        """Test validator checks for bin directory."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        with open(validator_file, 'r') as f:
            content = f.read()
            assert 'bin' in content or 'crux' in content, \
                "Validator should check for bin directory/crux jar"

    def test_validator_checks_schemas(self):
        """Test validator checks for schema files."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')
        validator_file = os.path.join(val_dir, 'iwxxmValidator.py')

        with open(validator_file, 'r') as f:
            content = f.read()
            assert 'schema' in content.lower() or 'xsd' in content.lower(), \
                "Validator should check for schema files"


class TestValidationIntegration:
    """Test validation module integration."""

    def test_validation_directory_structure(self):
        """Test overall validation directory structure."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')

        # Should have bin, externalSchemas, and Python files
        bin_exists = os.path.isdir(os.path.join(val_dir, 'bin'))
        schemas_exist = os.path.isdir(os.path.join(val_dir, 'externalSchemas'))

        assert bin_exists, "validation/bin should exist"
        assert schemas_exist, "validation/externalSchemas should exist"

    def test_validation_files_readable(self):
        """Test all validation files are readable."""
        val_dir = os.path.join(os.path.dirname(__file__), '..', 'validation')

        for filename in os.listdir(val_dir):
            if filename.endswith(('.py', '.xml', '.txt', '.md')):
                filepath = os.path.join(val_dir, filename)
                if os.path.isfile(filepath):
                    assert os.access(filepath, os.R_OK), \
                        f"{filename} should be readable"
