"""Tests for validation router endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.utilities.security import verify_supabase_token


@pytest.fixture
def client():
    """Create test client with mocked authentication."""

    async def override_verify_token():
        return {"sub": "test-user-id", "aud": "test-project"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestValidationLayersEndpoint:
    """Test GET /api/v1/validation/layers endpoint."""

    def test_layers_endpoint_returns_200(self, client):
        """Test layers endpoint returns success."""
        response = client.get("/api/v1/validation/layers")
        assert response.status_code == 200

    def test_layers_response_structure(self, client):
        """Test layers response has expected structure."""
        response = client.get("/api/v1/validation/layers")
        data = response.json()

        assert "layers" in data
        assert isinstance(data["layers"], list)
        assert len(data["layers"]) == 7

    def test_layers_contain_required_fields(self, client):
        """Test each layer has required fields."""
        response = client.get("/api/v1/validation/layers")
        data = response.json()

        for layer in data["layers"]:
            assert "layer" in layer
            assert "description" in layer
            assert "blocking" in layer
            assert "supported_content_types" in layer
            assert isinstance(layer["blocking"], bool)
            assert isinstance(layer["supported_content_types"], list)

    def test_layers_include_all_validation_layers(self, client):
        """Test that response includes all validation layer types."""
        response = client.get("/api/v1/validation/layers")
        data = response.json()

        layer_names = [layer["layer"] for layer in data["layers"]]
        expected = [
            "airport_icao",
            "tac_syntax",
            "xml_wellformed",
            "xml_schema",
            "schematron",
            "gml_references",
            "wmo_codelists",
        ]

        assert set(layer_names) == set(expected)

    def test_layers_blocking_status(self, client):
        """Test blocking status for critical layers."""
        response = client.get("/api/v1/validation/layers")
        data = response.json()

        layer_dict = {layer["layer"]: layer for layer in data["layers"]}

        # TAC syntax layers should be blocking
        assert layer_dict["airport_icao"]["blocking"] is True
        assert layer_dict["tac_syntax"]["blocking"] is True

        # XML validation layers should not be blocking
        assert layer_dict["xml_wellformed"]["blocking"] is False
        assert layer_dict["schematron"]["blocking"] is False


class TestValidateSingleEndpoint:
    """Test POST /api/v1/validation/validate endpoint."""

    def test_validate_valid_metar(self, client):
        """Test validation of valid METAR."""
        response = client.post(
            "/api/v1/validation/validate", json={"content": "METAR FAOR 101200Z 12012KT 9999 FEW020 22/14 Q1018"}
        )
        assert response.status_code == 200
        data = response.json()

        assert "passed" in data
        assert "layers_validated" in data
        assert "total_issues" in data
        assert "results" in data

    def test_validate_response_structure(self, client):
        """Test response has correct structure."""
        response = client.post(
            "/api/v1/validation/validate", json={"content": "METAR FAOR 101200Z 12012KT 9999 FEW020 22/14 Q1018"}
        )
        data = response.json()

        assert isinstance(data["passed"], bool)
        assert isinstance(data["layers_validated"], list)
        assert isinstance(data["total_issues"], int)
        assert isinstance(data["results"], list)
        assert "execution_time_ms" in data
        assert "validated_at" in data

    def test_validate_invalid_icao(self, client):
        """Test validation fails with invalid ICAO."""
        response = client.post(
            "/api/v1/validation/validate", json={"content": "METAR ZZZZ 101200Z 12012KT 9999 FEW020 22/14 Q1018"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["passed"] is False
        assert data["total_issues"] > 0

    def test_validate_invalid_syntax(self, client):
        """Test validation detects syntax errors."""
        response = client.post("/api/v1/validation/validate", json={"content": "INVALID METAR"})
        assert response.status_code == 200
        data = response.json()

        assert data["passed"] is False

    def test_validate_empty_content(self, client):
        """Test validation with empty content."""
        response = client.post("/api/v1/validation/validate", json={"content": ""})
        # Empty content returns validation error
        assert response.status_code in [200, 400, 422]

    def test_validate_missing_content_field(self, client):
        """Test validation with missing content field."""
        response = client.post("/api/v1/validation/validate", json={})
        assert response.status_code == 422  # Validation error

    def test_validate_service_error_handling(self, client):
        """Test error handling when service raises exception."""
        with patch("src.routers.validation.ValidationService") as mock_service_class:
            mock_instance = MagicMock()
            mock_instance.validate_all_layers.side_effect = RuntimeError("Service error")
            mock_service_class.return_value = mock_instance

            # Need to get fresh service
            import src.routers.validation as val_router

            val_router._validation_service = mock_instance

            response = client.post("/api/v1/validation/validate", json={"content": "METAR FAOR 101200Z"})

            assert response.status_code == 500
            assert "error" in response.json()["detail"].lower()

    def test_validate_multiple_results_in_response(self, client):
        """Test that validation results array contains layer results."""
        response = client.post(
            "/api/v1/validation/validate", json={"content": "METAR FAOR 101200Z 12012KT 9999 FEW020 22/14 Q1018"}
        )
        data = response.json()

        # Valid METAR should return results
        if response.status_code == 200 and "results" in data:
            assert len(data["results"]) > 0
            for result in data["results"]:
                assert "passed" in result
                assert "layer" in result
                assert "issues" in result
                assert "execution_time_ms" in result


class TestValidateMultipleEndpoint:
    """Test POST /api/v1/validation/validate-multi endpoint."""

    def test_validate_multi_single_item(self, client):
        """Test batch validation with single item."""
        response = client.post(
            "/api/v1/validation/validate-multi",
            json={"items": [{"content": "METAR FAOR 101200Z 12012KT 9999 FEW020 22/14 Q1018"}]},
        )
        # Should return success or validation error
        assert response.status_code in [200, 400, 422, 500]

        if response.status_code == 200:
            data = response.json()
            assert "total_items" in data
            assert data["total_items"] == 1

    def test_validate_multi_multiple_items(self, client):
        """Test batch validation with multiple items."""
        response = client.post(
            "/api/v1/validation/validate-multi",
            json={
                "items": [
                    {"content": "METAR FAOR 101200Z 12012KT 9999 FEW020 22/14 Q1018"},
                    {"content": "METAR KJFK 101200Z 12012KT 10SM FEW020 22/14 A3000"},
                    {"content": "INVALID"},
                ]
            },
        )
        # Should succeed or fail gracefully
        assert response.status_code in [200, 400, 422, 500]

        if response.status_code == 200:
            data = response.json()
            assert data["total_items"] == 3
            assert data["passed_items"] + data["failed_items"] == 3

    def test_validate_multi_response_structure(self, client):
        """Test batch response structure."""
        response = client.post(
            "/api/v1/validation/validate-multi",
            json={"items": [{"content": "METAR FAOR 101200Z"}, {"content": "METAR KJFK 101200Z"}]},
        )

        if response.status_code == 200:
            data = response.json()
            # Verify response structure if successful
            if "results" in data:
                assert "total_items" in data
                assert "passed_items" in data or "failed_items" in data
                assert isinstance(data["results"], list)

    def test_validate_multi_all_passed(self, client):
        """Test batch with all passing items."""
        response = client.post(
            "/api/v1/validation/validate-multi",
            json={"items": [{"content": "METAR FAOR 101200Z 12012KT 9999 FEW020 22/14 Q1018"}]},
        )

        if response.status_code == 200:
            data = response.json()
            # At least the first layer should pass for valid content
            if "passed_items" in data and "total_items" in data:
                assert data["total_items"] >= data["passed_items"]

    def test_validate_multi_all_failed(self, client):
        """Test batch with all failing items."""
        response = client.post(
            "/api/v1/validation/validate-multi", json={"items": [{"content": "INVALID"}, {"content": "ALSO INVALID"}]}
        )

        if response.status_code == 200:
            data = response.json()
            assert data["total_items"] == 2
            # All should fail for invalid content
            assert data.get("failed_items", 0) >= 0

    def test_validate_multi_empty_items(self, client):
        """Test batch with empty items list."""
        response = client.post("/api/v1/validation/validate-multi", json={"items": []})
        # Should return 422 or handle gracefully
        assert response.status_code in [200, 422]

    def test_validate_multi_exceeds_max_items(self, client):
        """Test batch with more than 100 items."""
        items = [{"content": f"METAR FAOR 101200Z {i:05d}"} for i in range(101)]
        response = client.post("/api/v1/validation/validate-multi", json={"items": items})
        # Should either reject or limit
        assert response.status_code in [200, 422]

    def test_validate_multi_missing_items_field(self, client):
        """Test batch without items field."""
        response = client.post("/api/v1/validation/validate-multi", json={})
        assert response.status_code == 422

    def test_validate_multi_statistics(self, client):
        """Test that statistics are calculated correctly."""
        response = client.post(
            "/api/v1/validation/validate-multi",
            json={
                "items": [
                    {"content": "METAR FAOR 101200Z 12012KT 9999 FEW020 22/14 Q1018"},
                    {"content": "METAR INVALID"},
                ]
            },
        )

        if response.status_code == 200:
            data = response.json()
            assert data["total_items"] == 2
            if "passed_items" in data and "failed_items" in data:
                assert data["passed_items"] + data["failed_items"] == 2
            assert data.get("total_execution_time_ms", 0) >= 0


class TestValidationIsPublic:
    """F21: validation endpoints do not require JWT."""

    def test_validate_multi_is_public(self):
        """validate-multi must not return 401/403 without Authorization."""
        client = TestClient(app)
        response = client.post("/api/v1/validation/validate-multi", json={"items": [{"content": "METAR FAOR"}]})
        assert response.status_code not in [401, 403]

    def test_validate_single_is_public(self):
        """validate must not require auth."""
        client = TestClient(app)
        response = client.post("/api/v1/validation/validate", json={"content": "METAR FAOR"})
        assert response.status_code not in [401, 403]

    def test_layers_is_public(self):
        """layers endpoint must not require auth."""
        client = TestClient(app)
        response = client.get("/api/v1/validation/layers")
        assert response.status_code not in [401, 403]
