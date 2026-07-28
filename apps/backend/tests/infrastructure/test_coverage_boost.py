"""Targeted tests to boost coverage to 95%."""

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.utilities.conversion import ConversionError
from src.utilities.security import verify_supabase_token


@pytest.fixture
def client():
    """Create test client with mocked authentication."""

    async def override_verify_token():
        return {"sub": "test-user-id", "aud": "test-project"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


class TestAPIConversionErrorPaths:
    """Test API exception paths to increase coverage."""

    def test_convert_manual_text_conversion_error(self, client):
        """Test manual text conversion error path (line 88-89)."""
        with patch("src.api.convert_metar_tac_with_metadata", side_effect=ConversionError("Test error")):
            response = client.post("/api/v1/convert", data={"manual_text": "METAR KJFK 231751Z"})
            # Should fail since all conversions failed
            assert response.status_code == 400
            assert "All conversions failed" in response.json()["detail"]["message"]

    def test_convert_file_conversion_error_path(self, client):
        """Test file ConversionError handling (line 108)."""
        test_file = io.BytesIO(b"METAR KJFK 231751Z")

        with patch("src.api.convert_metar_tac_with_metadata", side_effect=ConversionError("Parse error")):
            response = client.post("/api/v1/convert", files={"files": ("test.txt", test_file, "text/plain")})
            assert response.status_code == 400

    def test_convert_file_generic_exception_path(self, client):
        """Test file generic Exception handling (line 110-111)."""
        test_file = io.BytesIO(b"METAR KJFK 231751Z")

        with patch("src.api.convert_metar_tac_with_metadata", side_effect=RuntimeError("Unexpected error")):
            response = client.post("/api/v1/convert", files={"files": ("test.txt", test_file, "text/plain")})
            assert response.status_code == 400
            data = response.json()
            assert "unexpected error" in str(data["detail"]["errors"]).lower()

    def test_zip_manual_conversion_error(self, client):
        """Test zip manual text ConversionError (line 150-151)."""
        with patch("src.api.convert_metar_tac_with_metadata", side_effect=ConversionError("Zip error")):
            response = client.post("/api/v1/convert-zip", data={"manual_text": "METAR KJFK 231751Z"})
            # ZIP endpoint always returns 200 with ZIP file containing errors
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/zip"

    def test_zip_empty_file_error(self, client):
        """Test zip empty file handling (line 157-158)."""
        empty_file = io.BytesIO(b"   ")  # Only whitespace

        response = client.post("/api/v1/convert-zip", files={"files": ("empty.txt", empty_file, "text/plain")})
        # ZIP endpoint always returns 200 with ZIP file
        # Empty files are skipped, resulting in empty ZIP with no errors.txt
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"

    def test_zip_file_conversion_error(self, client):
        """Test zip file ConversionError handling (line 162)."""
        test_file = io.BytesIO(b"METAR KJFK 231751Z")

        with patch("src.api.convert_metar_tac_with_metadata", side_effect=ConversionError("Conversion failed")):
            response = client.post("/api/v1/convert-zip", files={"files": ("test.txt", test_file, "text/plain")})
            # ZIP endpoint always returns 200 with errors in ZIP
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/zip"

    def test_zip_file_generic_exception(self, client):
        """Test zip file generic Exception handling (line 164-165)."""
        test_file = io.BytesIO(b"METAR KJFK 231751Z")

        with patch("src.api.convert_metar_tac_with_metadata", side_effect=RuntimeError("Unexpected")):
            response = client.post("/api/v1/convert-zip", files={"files": ("test.txt", test_file, "text/plain")})
            # ZIP endpoint always returns 200 with errors in ZIP
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/zip"

    def test_zip_no_valid_conversions(self, client):
        """Test zip with no valid conversions (line 168)."""
        with patch("src.api.convert_metar_tac_with_metadata", side_effect=ConversionError("All fail")):
            response = client.post("/api/v1/convert-zip", data={"manual_text": "INVALID"})
            # ZIP endpoint always returns 200 with errors.txt in ZIP
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/zip"

    def test_zip_response_headers(self, client):
        """Test zip StreamingResponse headers (line 180)."""
        with patch("src.api.convert_metar_tac_with_metadata", return_value=("<iwxxm>test</iwxxm>", None)):
            response = client.post("/api/v1/convert-zip", data={"manual_text": "METAR KJFK 231751Z"})
            assert response.status_code == 200
            # Check Content-Disposition header includes timestamp
            content_disp = response.headers.get("content-disposition", "")
            assert "iwxxm_batch_" in content_disp
            assert ".zip" in content_disp


class TestIWXXMValidationFunctions:
    """Test IWXXM validation utility functions."""

    def test_extract_iwxxm_namespace_invalid(self):
        """Test namespace validation with invalid namespace."""
        from schemas.iwxxm_validation import extract_iwxxm_namespace_version

        with pytest.raises(ValueError) as exc_info:
            extract_iwxxm_namespace_version("http://invalid.com/namespace")
        assert "Invalid IWXXM namespace" in str(exc_info.value)

    def test_extract_iwxxm_namespace_unsupported_version(self):
        """Test namespace validation with unsupported version."""
        from schemas.iwxxm_validation import extract_iwxxm_namespace_version

        with pytest.raises(ValueError) as exc_info:
            extract_iwxxm_namespace_version("http://icao.int/iwxxm/9999.9")
        assert "Unsupported IWXXM version" in str(exc_info.value)

    def test_extract_iwxxm_namespace_valid(self):
        """Test namespace validation with valid namespace."""
        from schemas.iwxxm_validation import extract_iwxxm_namespace_version

        result = extract_iwxxm_namespace_version("http://icao.int/iwxxm/2023-1")
        assert result == "2023-1"


class TestConversionUtilityEdgeCases:
    """Test remaining conversion utility edge cases."""

    def test_conversion_module_exports_convert(self):
        """Cutover: conversion module exposes tac2iwxxm-backed entrypoints."""
        from src.utilities import conversion

        assert hasattr(conversion, "convert_metar_tac")
        assert hasattr(conversion, "convert_metar_tac_with_metadata")
        assert not hasattr(conversion, "_load_aerodrome_db")
        assert not hasattr(conversion, "_lookup_aerodrome")
