import io
import pathlib
import sys
import zipfile

import pytest
from fastapi.testclient import TestClient

# Ensure src layout path precedence for imports
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api import app
from utilities.security import verify_supabase_token


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
        assert "gifts_available" in data
    
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
    
    def test_result_structure(self, client):
        """Test result object structure."""
        r = client.post("/api/v1/convert", data={"manual_text": SAMPLE_METAR})
        data = r.json()
        result = data["results"][0]
        assert "name" in result
        assert "content" in result
        assert "source" in result
        assert "size_bytes" in result


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


class TestErrorHandling:
    """Test error handling."""
    
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
