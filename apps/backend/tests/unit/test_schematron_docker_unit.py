"""Unit tests for SchematronValidatorDocker – 0% coverage target."""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from src.utilities.schematron_validator_docker import (
    SchematronValidationResult,
    SchematronValidatorDocker,
    validate_against_schematron,
)


class TestSchematronValidationResult:
    def test_default_fields(self):
        r = SchematronValidationResult(valid=True)
        assert r.status == "UNKNOWN"
        assert r.assertions_passed == 0
        assert r.assertions_failed == 0
        assert r.failed_constraints == []
        assert r.errors == []

    def test_to_dict(self):
        r = SchematronValidationResult(valid=True, status="PASS", assertions_passed=3)
        d = r.to_dict()
        assert d["valid"] is True
        assert d["status"] == "PASS"
        assert d["assertions_passed"] == 3

    def test_to_json_round_trips(self):
        r = SchematronValidationResult(valid=False, status="FAIL", errors=["oops"])
        data = json.loads(r.to_json())
        assert data["valid"] is False
        assert data["errors"] == ["oops"]


class TestSchematronValidatorDockerInit:
    def test_raises_when_schema_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            SchematronValidatorDocker(schema_path=str(tmp_path / "missing.sch"))

    def test_init_success(self, tmp_path):
        schema = tmp_path / "test.sch"
        schema.write_text("<schema/>")
        v = SchematronValidatorDocker(schema_path=str(schema), version="2023-1")
        assert v.version == "2023-1"
        assert v.schema_path == schema


class TestSchematronValidatorDockerValidate:
    def _make_validator(self, tmp_path):
        schema = tmp_path / "test.sch"
        schema.write_text("<schema/>")
        return SchematronValidatorDocker(schema_path=str(schema), version="2023-1")

    def test_validate_calls_subprocess(self, tmp_path):
        validator = self._make_validator(tmp_path)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "status": "PASS",
                "assertions_passed": 5,
                "assertions_failed": 0,
                "failed_constraints": [],
                "passed_constraints": [],
            }
        )
        mock_result.stderr = ""

        with patch("src.utilities.schematron_validator_docker.subprocess.run", return_value=mock_result):
            result = validator.validate("<xml/>")

        assert result.valid is True
        assert result.status == "PASS"
        assert result.assertions_passed == 5

    def test_validate_fail_result(self, tmp_path):
        validator = self._make_validator(tmp_path)
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = json.dumps(
            {
                "status": "FAIL",
                "assertions_passed": 0,
                "assertions_failed": 2,
                "failed_constraints": [{"id": "c1", "msg": "error"}],
                "passed_constraints": [],
            }
        )
        mock_result.stderr = "some warning"

        with patch("src.utilities.schematron_validator_docker.subprocess.run", return_value=mock_result):
            result = validator.validate("<xml/>")

        assert result.valid is False
        assert result.assertions_failed == 2

    def test_validate_docker_exception_returns_error_result(self, tmp_path):
        validator = self._make_validator(tmp_path)

        with patch(
            "src.utilities.schematron_validator_docker.subprocess.run",
            side_effect=Exception("Docker not running"),
        ):
            result = validator.validate("<xml/>")

        assert result.valid is False
        assert result.status == "ERROR"
        assert any("Docker not running" in e for e in result.errors)

    def test_validate_bad_json_output_returns_error(self, tmp_path):
        validator = self._make_validator(tmp_path)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "{{NOT JSON"
        mock_result.stderr = ""

        with patch("src.utilities.schematron_validator_docker.subprocess.run", return_value=mock_result):
            result = validator.validate("<xml/>")

        # Should gracefully handle JSON parse error
        assert result is not None
        assert isinstance(result, SchematronValidationResult)

    def test_run_docker_validation_builds_correct_cmd(self, tmp_path):
        validator = self._make_validator(tmp_path)
        xml_file = tmp_path / "test.xml"
        xml_file.write_text("<xml/>")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "status": "PASS",
                "assertions_passed": 0,
                "assertions_failed": 0,
                "failed_constraints": [],
                "passed_constraints": [],
            }
        )
        mock_result.stderr = ""

        with patch("src.utilities.schematron_validator_docker.subprocess.run", return_value=mock_result) as mock_run:
            validator._run_docker_validation(str(xml_file))

        cmd = mock_run.call_args[0][0]
        assert "docker" in cmd
        assert "run" in cmd
        assert "--rm" in cmd

    def test_run_docker_validation_timeout(self, tmp_path):
        validator = self._make_validator(tmp_path)
        xml_file = tmp_path / "test.xml"
        xml_file.write_text("<xml/>")

        with patch(
            "src.utilities.schematron_validator_docker.subprocess.run",
            side_effect=subprocess.TimeoutExpired("docker", 60),
        ):
            result = validator._run_docker_validation(str(xml_file))

        assert result.valid is False
        assert "timeout" in result.errors[0].lower()

    def test_run_docker_validation_error_string_normalized(self, tmp_path):
        validator = self._make_validator(tmp_path)
        xml_file = tmp_path / "test.xml"
        xml_file.write_text("<xml/>")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = json.dumps({"status": "ERROR", "error": "single error"})
        mock_result.stderr = ""

        with patch("src.utilities.schematron_validator_docker.subprocess.run", return_value=mock_result):
            result = validator._run_docker_validation(str(xml_file))

        assert result.errors == ["single error"]


class TestSchematronValidatorDockerHelpers:
    def test_check_docker_image_true_false(self, tmp_path):
        schema = tmp_path / "test.sch"
        schema.write_text("<schema/>")
        validator = SchematronValidatorDocker(schema_path=str(schema))

        ok = MagicMock(returncode=0)
        bad = MagicMock(returncode=1)

        with patch("src.utilities.schematron_validator_docker.subprocess.run", return_value=ok):
            assert validator.check_docker_image() is True
        with patch("src.utilities.schematron_validator_docker.subprocess.run", return_value=bad):
            assert validator.check_docker_image() is False

    def test_check_docker_image_exception_returns_false(self, tmp_path):
        schema = tmp_path / "test.sch"
        schema.write_text("<schema/>")
        validator = SchematronValidatorDocker(schema_path=str(schema))
        with patch("src.utilities.schematron_validator_docker.subprocess.run", side_effect=RuntimeError("x")):
            assert validator.check_docker_image() is False

    def test_validate_against_schematron_wrapper(self, tmp_path):
        schema = tmp_path / "test.sch"
        schema.write_text("<schema/>")
        with patch.object(
            SchematronValidatorDocker, "validate", return_value=SchematronValidationResult(valid=True, status="PASS")
        ):
            result = validate_against_schematron("<xml/>", str(schema))
        assert result.valid is True
