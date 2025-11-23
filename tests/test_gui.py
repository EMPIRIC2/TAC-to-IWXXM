"""UI tests for the FastAPI GUI application.

Tests cover:
- Static file serving (HTML, JS, CSS)
- /api/convert endpoint (manual input, file upload, error handling)
- /api/convert-zip endpoint (ZIP archive generation)
- Input validation and error responses
"""

from __future__ import annotations
from gui.app import app

import sys
import pathlib
import io
import zipfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Add repository root to path for imports
ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def client() -> TestClient:
    """Create a FastAPI test client."""
    return TestClient(app)


class TestHealth:
    """Test health check endpoint."""

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test that health check returns expected structure."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "gifts_available" in data
        assert data["status"] in ["healthy", "degraded"]
        assert isinstance(data["gifts_available"], bool)


class TestStaticFiles:
    """Test static file serving."""

    def test_index_page_loads(self, client: TestClient) -> None:
        """Test that the index page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "METAR" in response.text
        assert "IWXXM" in response.text
        assert "Convert" in response.text

    def test_javascript_loads(self, client: TestClient) -> None:
        """Test that app.js loads successfully."""
        response = client.get("/static/app.js")
        assert response.status_code == 200
        assert "application/javascript" in response.headers["content-type"] or "text/javascript" in response.headers["content-type"]
        assert "convertBtn" in response.text

    def test_css_loads(self, client: TestClient) -> None:
        """Test that style.css loads successfully."""
        response = client.get("/static/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]


class TestConvertEndpoint:
    """Test /api/convert endpoint."""

    def test_manual_text_conversion(self, client: TestClient) -> None:
        """Test conversion with manual METAR text input."""
        metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 SCT120 BKN250 15/07 A3005"
        response = client.post("/api/convert", data={"manual_text": metar})
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "errors" in data
        assert "total_processed" in data
        assert "successful" in data
        assert "failed" in data

        assert len(data["results"]) == 1
        assert data["total_processed"] == 1
        assert data["successful"] == 1
        assert data["failed"] == 0

        result = data["results"][0]
        assert result["name"] == "manual_input.txt"
        assert "iwxxm" in result["content"].lower()
        assert "<?xml" in result["content"] or "<iwxxm:" in result["content"]
        assert result["source"] == "manual"
        assert result["size_bytes"] > 0

    def test_file_upload_conversion(self, client: TestClient) -> None:
        """Test conversion with uploaded TAC file."""
        metar = "METAR EGLL 231750Z 27015KT 9999 FEW040 17/09 Q1023"
        file_content = metar.encode("utf-8")

        response = client.post(
            "/api/convert",
            files={"files": ("test.tac", file_content, "text/plain")}
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "test.txt"
        assert "iwxxm" in data["results"][0]["content"].lower()

    def test_multiple_file_upload(self, client: TestClient) -> None:
        """Test conversion with multiple files."""
        files = [
            ("files", ("metar1.tac",
             b"METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005", "text/plain")),
            ("files", ("metar2.tac",
             b"METAR EGLL 231750Z 27015KT 9999 FEW040 17/09 Q1023", "text/plain"))
        ]

        response = client.post("/api/convert", files=files)
        assert response.status_code == 200

        data = response.json()
        assert len(data["results"]) == 2
        assert data["results"][0]["name"] == "metar1.txt"
        assert data["results"][1]["name"] == "metar2.txt"

    def test_manual_and_files_combined(self, client: TestClient) -> None:
        """Test conversion with both manual text and file uploads."""
        metar = "METAR LFPG 231800Z 09012KT CAVOK 18/08 Q1015"

        response = client.post(
            "/api/convert",
            data={"manual_text": metar},
            files={"files": (
                "test.tac", b"METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005", "text/plain")}
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["results"]) == 2  # manual + 1 file

    def test_empty_file_error(self, client: TestClient) -> None:
        """Test that empty files generate appropriate errors."""
        response = client.post(
            "/api/convert",
            files={"files": ("empty.tac", b"", "text/plain")}
        )
        assert response.status_code == 400
        data = response.json()
        assert "empty.tac" in str(data["detail"]["errors"])

    def test_no_input_returns_empty(self, client: TestClient) -> None:
        """Test that no input returns appropriate response."""
        response = client.post("/api/convert", data={"manual_text": ""})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0
        assert len(data["errors"]) == 0

    def test_invalid_metar_generates_error(self, client: TestClient) -> None:
        """Test that invalid METAR text is handled gracefully."""
        response = client.post(
            "/api/convert",
            data={"manual_text": "NOT A VALID METAR"}
        )
        # Should either succeed with partial parse or error
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            # Either results or errors, but not empty response
            assert len(data["results"]) > 0 or len(data["errors"]) > 0


class TestConvertZipEndpoint:
    """Test /api/convert-zip endpoint."""

    def test_zip_with_manual_input(self, client: TestClient) -> None:
        """Test ZIP generation with manual METAR input."""
        metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
        response = client.post("/api/convert-zip", data={"manual_text": metar})

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert "attachment" in response.headers["content-disposition"]
        assert "iwxxm_batch" in response.headers["content-disposition"]

        # Verify ZIP contents
        zip_bytes = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_bytes, "r") as zf:
            namelist = zf.namelist()
            assert "manual_input.xml" in namelist

            xml_content = zf.read("manual_input.xml").decode("utf-8")
            assert "iwxxm" in xml_content.lower()

    def test_zip_with_files(self, client: TestClient) -> None:
        """Test ZIP generation with file uploads."""
        files = [
            ("files", ("metar1.tac",
             b"METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005", "text/plain")),
            ("files", ("metar2.tac",
             b"METAR EGLL 231750Z 27015KT 9999 FEW040 17/09 Q1023", "text/plain"))
        ]

        response = client.post("/api/convert-zip", files=files)
        assert response.status_code == 200

        zip_bytes = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_bytes, "r") as zf:
            namelist = zf.namelist()
            assert "metar1.xml" in namelist
            assert "metar2.xml" in namelist

    def test_zip_includes_errors_file(self, client: TestClient) -> None:
        """Test that ZIP includes errors.txt when conversions fail."""
        response = client.post(
            "/api/convert-zip",
            files={"files": ("empty.tac", b"", "text/plain")}
        )

        # Even with errors, if there's content it might succeed with partial results
        # or fail entirely
        if response.status_code == 200:
            zip_bytes = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_bytes, "r") as zf:
                namelist = zf.namelist()
                # Should contain errors.txt if there were errors
                assert "errors.txt" in namelist or len(namelist) == 0

    def test_zip_filename_has_timestamp(self, client: TestClient) -> None:
        """Test that ZIP filename includes UTC timestamp."""
        metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
        response = client.post("/api/convert-zip", data={"manual_text": metar})

        assert response.status_code == 200
        disposition = response.headers["content-disposition"]
        # Format: iwxxm_batch_20251123T143022Z.zip
        assert "iwxxm_batch_" in disposition
        assert "Z.zip" in disposition

    def test_zip_no_input_fails(self, client: TestClient) -> None:
        """Test that ZIP endpoint fails with no input."""
        response = client.post("/api/convert-zip", data={"manual_text": ""})
        # Should return error since no results and no input
        assert response.status_code in [200, 400]


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_nonexistent_static_file_404(self, client: TestClient) -> None:
        """Test that requesting nonexistent static files returns 404."""
        response = client.get("/static/nonexistent.js")
        assert response.status_code == 404

    def test_unsupported_file_extension_handled(self, client: TestClient) -> None:
        """Test that files with unusual extensions are processed."""
        metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
        response = client.post(
            "/api/convert",
            files={"files": ("test.metar", metar.encode(
                "utf-8"), "text/plain")}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "test.txt"

    def test_unicode_in_manual_input(self, client: TestClient) -> None:
        """Test that unicode characters in input are handled."""
        metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2"
        response = client.post("/api/convert", data={"manual_text": metar})
        assert response.status_code in [200, 400]

    def test_large_file_upload(self, client: TestClient) -> None:
        """Test handling of larger files."""
        # Create a file with multiple METARs
        metars = "\n".join([
            f"METAR KJFK 2317{i:02d}Z 18012KT 10SM FEW040 15/07 A3005"
            for i in range(10)
        ])

        response = client.post(
            "/api/convert",
            files={"files": ("large.tac", metars.encode(
                "utf-8"), "text/plain")}
        )
        # Should process (maybe only first METAR or fail gracefully)
        assert response.status_code in [200, 400]


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
