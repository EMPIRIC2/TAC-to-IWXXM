"""
Tests for Schema Status API Endpoint

Tests the new /api/v1/schema-status endpoint for RC version information.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client for API testing."""
    from src.api import app
    return TestClient(app)


class TestSchemaStatusEndpoint:
    """Test /api/v1/schema-status endpoint."""
    
    def test_schema_status_endpoint_exists(self, client):
        """Test the schema-status endpoint is accessible."""
        response = client.get("/api/v1/schema-status")
        assert response.status_code == 200
    
    def test_schema_status_returns_channels(self, client):
        """Test response contains stable, rc, and all version lists."""
        response = client.get("/api/v1/schema-status")
        data = response.json()
        
        assert "stable" in data
        assert "rc" in data
        assert "all" in data
        assert "default" in data
        assert "metadata" in data
    
    def test_schema_status_stable_versions(self, client):
        """Test stable versions list is populated."""
        response = client.get("/api/v1/schema-status")
        data = response.json()
        
        stable = data["stable"]
        assert isinstance(stable, list)
        assert len(stable) >= 2  # At least 2025-2 and 2023-1
        assert "2025-2" in stable
        assert "2023-1" in stable
    
    def test_schema_status_default_version(self, client):
        """Test default version is specified."""
        response = client.get("/api/v1/schema-status")
        data = response.json()
        
        assert data["default"] == "2025-2"
    
    def test_schema_status_metadata_structure(self, client):
        """Test metadata contains required fields for each version."""
        response = client.get("/api/v1/schema-status")
        data = response.json()
        
        metadata = data["metadata"]
        assert "2025-2" in metadata
        
        version_meta = metadata["2025-2"]
        assert "name" in version_meta
        assert "channel" in version_meta
        assert "status" in version_meta
        assert "discovered" in version_meta
        assert "source_url" in version_meta
        assert "mirrored" in version_meta
    
    def test_schema_status_channel_classification(self, client):
        """Test versions are correctly classified by channel."""
        response = client.get("/api/v1/schema-status")
        data = response.json()
        
        # Check stable versions have stable channel
        metadata = data["metadata"]
        for version in data["stable"]:
            assert metadata[version]["channel"] == "stable"
    
    def test_schema_status_rc_metadata_fields(self, client):
        """Test RC versions have promoted_to_stable field."""
        response = client.get("/api/v1/schema-status")
        data = response.json()
        
        # If any RC versions exist, check their metadata
        rc_versions = data["rc"]
        metadata = data["metadata"]
        
        for rc_version in rc_versions:
            if rc_version in metadata:
                # RC versions should have this field
                assert "promoted_to_stable" in metadata[rc_version]


@pytest.mark.unit
class TestVersionsEndpointBackwardCompatibility:
    """Test that existing /api/v1/versions endpoint still works."""
    
    def test_versions_endpoint_unchanged(self, client):
        """Test original versions endpoint is unaffected."""
        response = client.get("/api/v1/versions")
        assert response.status_code == 200
        
        data = response.json()
        assert "default_version" in data
        assert "supported_versions" in data
        assert "deprecated_versions" in data
        assert "notes" in data
    
    def test_versions_response_structure(self, client):
        """Test versions endpoint response structure unchanged."""
        response = client.get("/api/v1/versions")
        data = response.json()
        
        assert data["default_version"] == "2025-2"
        assert isinstance(data["supported_versions"], list)
        assert isinstance(data["deprecated_versions"], list)
        
        # Check version object structure
        if data["supported_versions"]:
            version_obj = data["supported_versions"][0]
            assert "version" in version_obj
            assert "name" in version_obj
            assert "status" in version_obj
            assert "release_date" in version_obj
            assert "wmo_amendment" in version_obj


@pytest.mark.integration
class TestSchemaStatusIntegration:
    """Integration tests for schema status endpoint."""
    
    def test_schema_status_and_versions_consistent(self, client):
        """Test schema-status and versions endpoints are consistent."""
        status_response = client.get("/api/v1/schema-status")
        versions_response = client.get("/api/v1/versions")
        
        status_data = status_response.json()
        versions_data = versions_response.json()
        
        # Both should agree on default version
        assert status_data["default"] == versions_data["default_version"]
        
        # Stable versions from schema-status should be in supported_versions
        stable_from_status = set(status_data["stable"])
        supported_versions = {v["version"] for v in versions_data["supported_versions"]}
        
        assert stable_from_status.issubset(supported_versions)
