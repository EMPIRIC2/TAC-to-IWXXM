import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.utilities.security import verify_supabase_token

SAMPLE_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
SAMPLE_METAR_2 = "METAR KLAX 231753Z 25008KT 10SM FEW020 18/12 A2992"
SAMPLE_METAR_3 = "METAR KORD 231756Z 16008KT 10SM SCT035 14/05 A3012"


@pytest.fixture
def client():
    """Create test client with mocked authentication."""

    # Mock the verify_supabase_token dependency
    async def override_verify_token():
        return {"sub": "test-user-id", "aud": "test-project"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_status_succeeds(self, client):
        """Test health check returns 200."""
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_response_structure(self, client):
        """Test health response has required fields."""
        r = client.get("/health")
        data = r.json()
        assert "status" in data
        assert "version" in data
        assert "tac2iwxxm_available" in data

    def test_health_status_values(self, client):
        """Test health status is valid value."""
        r = client.get("/health")
        data = r.json()
        assert data["status"] in {"healthy", "degraded"}


class TestConversionEndpoint:
    """Test /api/v1/convert endpoint."""

    def test_manual_text_conversion(self, client):
        """Test conversion of manual text."""
        r = client.post("/api/v1/convert", data={"manual_text": SAMPLE_METAR})
        assert r.status_code == 200
        data = r.json()
        assert len(data["results"]) > 0
        assert "<iwxxm:METAR" in data["results"][0]["content"]

    def test_multiple_manual_lines_conversion(self, client):
        """Test conversion of multiple manual TAC strings in one request."""
        manual_text = "\n".join([SAMPLE_METAR, SAMPLE_METAR_2])
        r = client.post("/api/v1/convert", data={"manual_text": manual_text})
        assert r.status_code == 200
        data = r.json()
        assert data["total_processed"] == 2
        assert data["successful"] == 2
        assert len(data["results"]) == 2

    def test_multiple_files_conversion(self, client):
        """Test conversion of multiple files."""
        files = [
            ("files", ("m1.tac", SAMPLE_METAR, "text/plain")),
            ("files", ("m2.tac", SAMPLE_METAR_2, "text/plain")),
        ]
        r = client.post("/api/v1/convert", files=files)
        assert r.status_code == 200
        data = r.json()
        assert len(data["results"]) == 2
        assert data["total_processed"] == 2

    def test_manual_and_files_combined_conversion(self, client):
        """Test combined manual text and file uploads in a single conversion request."""
        files = [
            ("files", ("m1.tac", SAMPLE_METAR_3, "text/plain")),
        ]
        r = client.post(
            "/api/v1/convert",
            data={"manual_text": SAMPLE_METAR},
            files=files,
        )
        assert r.status_code == 200
        payload = r.json()
        assert payload["total_processed"] == 2
        assert payload["successful"] == 2
        assert len(payload["results"]) == 2

    def test_xml_file_input_returns_validation_error(self, client):
        """XML uploads should be validated and rejected by conversion endpoint."""
        files = [
            ("files", ("sample.xml", "<root><valid /></root>", "application/xml")),
        ]
        r = client.post("/api/v1/convert", files=files)
        assert r.status_code == 400

        detail = r.json().get("detail", {})
        assert "errors" in detail
        assert any("xml" in err.lower() for err in detail["errors"])

    def test_invalid_utf8_file_rejected(self, client):
        """Reject files that are not UTF-8 encoded."""
        files = [
            ("files", ("bad.tac", b"\xff\xfe\xfa", "text/plain")),
        ]
        r = client.post("/api/v1/convert", files=files)
        assert r.status_code == 400

        detail = r.json().get("detail", {})
        assert "errors" in detail
        assert any("utf-8" in err.lower() for err in detail["errors"])

    def test_result_structure(self, client):
        """Test result object structure."""
        r = client.post("/api/v1/convert", data={"manual_text": SAMPLE_METAR})
        data = r.json()
        result = data["results"][0]
        assert "name" in result
        assert "content" in result
        assert "source" in result
        assert "size_bytes" in result

    def test_success_response_includes_issues_array(self, client):
        """Test successful response includes issues key for contract consistency."""
        r = client.post("/api/v1/convert", data={"manual_text": SAMPLE_METAR})
        assert r.status_code == 200
        data = r.json()
        assert "issues" in data
        assert isinstance(data["issues"], list)

    def test_partial_success_includes_structured_issues(self, client):
        """Test mixed valid/invalid input returns 200 with structured issues."""
        files = [
            ("files", ("valid.tac", SAMPLE_METAR, "text/plain")),
            ("files", ("invalid.tac", "NILl", "text/plain")),
        ]
        r = client.post("/api/v1/convert", files=files)
        assert r.status_code == 200

        data = r.json()
        assert data["successful"] == 1
        assert data["failed"] == 1
        assert "issues" in data
        assert len(data["issues"]) >= 1

        first_issue = data["issues"][0]
        assert "source" in first_issue
        assert "message" in first_issue
        assert "severity" in first_issue

    def test_all_failed_response_contains_structured_detail_issues(self, client):
        """Test all-failed conversion response includes structured detail/issues payload."""
        files = [
            ("files", ("invalid_only.tac", "NILl", "text/plain")),
        ]
        r = client.post("/api/v1/convert", files=files)
        assert r.status_code == 400

        detail = r.json().get("detail", {})
        assert "message" in detail
        assert "errors" in detail
        assert "issues" in detail
        assert "total_errors" in detail
        assert isinstance(detail["issues"], list)
        assert len(detail["issues"]) >= 1
        assert detail["issues"][0]["severity"] in {"error", "warning", "info"}


class TestConversionZipEndpoint:
    """Test /api/v1/convert-zip endpoint."""

    def test_zip_conversion(self, client):
        """Test ZIP conversion endpoint."""
        files = [
            ("files", ("m1.tac", SAMPLE_METAR, "text/plain")),
            ("files", ("m2.tac", SAMPLE_METAR_2, "text/plain")),
        ]
        r = client.post("/api/v1/convert-zip", files=files)
        assert r.status_code == 200
        assert "application/zip" in r.headers.get("content-type", "")

        zbytes = io.BytesIO(r.content)
        with zipfile.ZipFile(zbytes) as zf:
            xml_files = [n for n in zf.namelist() if n.endswith(".xml")]
            assert len(xml_files) >= 2

    def test_zip_manual_input(self, client):
        """Test ZIP with manual input."""
        r = client.post("/api/v1/convert-zip", data={"manual_text": SAMPLE_METAR})
        assert r.status_code == 200

        zbytes = io.BytesIO(r.content)
        with zipfile.ZipFile(zbytes) as zf:
            names = zf.namelist()
            assert "manual_input.xml" in names

    def test_zip_xml_input_writes_errors_file(self, client):
        """ZIP conversion should report XML uploads in errors.txt."""
        files = [
            ("files", ("sample.xml", "<root><valid /></root>", "application/xml")),
        ]
        r = client.post("/api/v1/convert-zip", files=files)
        assert r.status_code == 200

        zbytes = io.BytesIO(r.content)
        with zipfile.ZipFile(zbytes) as zf:
            names = zf.namelist()
            assert "errors.txt" in names
            errors_txt = zf.read("errors.txt").decode("utf-8")
            assert "TAC only" in errors_txt

    def test_zip_invalid_utf8_writes_errors_file(self, client):
        """ZIP conversion should report invalid UTF-8 uploads in errors.txt."""
        files = [
            ("files", ("bad.tac", b"\xff\xfe\xfa", "text/plain")),
        ]
        r = client.post("/api/v1/convert-zip", files=files)
        assert r.status_code == 200

        zbytes = io.BytesIO(r.content)
        with zipfile.ZipFile(zbytes) as zf:
            names = zf.namelist()
            assert "errors.txt" in names
            errors_txt = zf.read("errors.txt").decode("utf-8")
            assert "UTF-8" in errors_txt


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_json_body_returns_structured_issues(self, client):
        """Test malformed JSON request returns structured issue payload."""
        r = client.post(
            "/api/v1/convert",
            content="{invalid-json",
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 422

        detail = r.json().get("detail", {})
        assert detail.get("message") == "Invalid JSON in request body"
        assert isinstance(detail.get("issues"), list)
        assert len(detail["issues"]) == 1
        assert detail["issues"][0]["source"] == "request"
        assert detail["issues"][0]["severity"] == "error"

    def test_invalid_json_schema_returns_structured_issues(self, client):
        """Test invalid JSON schema request returns structured issue payload."""
        r = client.post(
            "/api/v1/convert",
            json={"version": "2025-2"},  # missing required metars
        )
        assert r.status_code == 400

        detail = r.json().get("detail", {})
        assert detail.get("message") == "No conversion input provided"
        assert isinstance(detail.get("issues"), list)
        assert len(detail["issues"]) == 1
        assert detail["issues"][0]["source"] == "request"
        assert detail["issues"][0]["severity"] == "error"

    def test_empty_files_error(self, client):
        """Test empty file error handling."""
        files = [
            ("files", ("empty.tac", "", "text/plain")),
        ]
        r = client.post("/api/v1/convert", files=files)
        assert r.status_code == 400

    def test_response_counts(self, client):
        """Test that response counts are consistent."""
        r = client.post("/api/v1/convert", data={"manual_text": SAMPLE_METAR})
        data = r.json()
        assert data["total_processed"] == data["successful"] + data["failed"]
