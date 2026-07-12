"""Unit tests for schemas."""

import pathlib
import sys

import pytest

# Ensure src layout path precedence
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from schemas.conversion import (
    ConversionResponse,
    ConversionResult,
    ErrorDetail,
    HealthResponse,
)


def test_conversion_result_valid():
    """Test ConversionResult schema with valid data."""
    result = ConversionResult(
        name="test.xml",
        content="<xml>test</xml>",
        source="file",
        size_bytes=100,
    )
    assert result.name == "test.xml"
    assert result.content == "<xml>test</xml>"
    assert result.source == "file"
    assert result.size_bytes == 100


def test_conversion_result_minimal():
    """Test ConversionResult with minimal required fields."""
    result = ConversionResult(
        name="test.xml",
        content="<xml>test</xml>",
    )
    assert result.name == "test.xml"
    assert result.content == "<xml>test</xml>"
    assert result.source is None
    assert result.size_bytes is None


def test_conversion_result_validation():
    """Test ConversionResult validation."""
    with pytest.raises(ValueError):
        ConversionResult(
            name="test.xml",
            content="",  # Empty content should fail min_length=1
        )


def test_conversion_response_valid():
    """Test ConversionResponse schema."""
    response = ConversionResponse(
        results=[
            ConversionResult(name="file1.xml", content="<xml/>"),
            ConversionResult(name="file2.xml", content="<xml/>"),
        ],
        errors=["Error 1"],
        total_processed=3,
        successful=2,
        failed=1,
    )
    assert len(response.results) == 2
    assert len(response.errors) == 1
    assert response.total_processed == 3
    assert response.successful == 2
    assert response.failed == 1


def test_conversion_response_defaults():
    """Test ConversionResponse with default values."""
    response = ConversionResponse(
        total_processed=0,
        successful=0,
        failed=0,
    )
    assert response.results == []
    assert response.errors == []
    assert response.total_processed == 0


def test_conversion_response_validation():
    """Test ConversionResponse field validation."""
    with pytest.raises(ValueError):
        ConversionResponse(
            total_processed=-1,  # Should be >= 0
            successful=0,
            failed=0,
        )


def test_error_detail_valid():
    """Test ErrorDetail schema."""
    error = ErrorDetail(
        message="Conversion failed",
        errors=["Error 1", "Error 2"],
        total_errors=2,
    )
    assert error.message == "Conversion failed"
    assert len(error.errors) == 2
    assert error.total_errors == 2


def test_error_detail_defaults():
    """Test ErrorDetail with defaults."""
    error = ErrorDetail(
        message="Failed",
        total_errors=0,
    )
    assert error.message == "Failed"
    assert error.errors == []
    assert error.total_errors == 0


def test_health_response_valid():
    """Test HealthResponse schema."""
    health = HealthResponse(
        status="healthy",
        version="0.1.0",
        tac2iwxxm_available=True,
    )
    assert health.status == "healthy"
    assert health.version == "0.1.0"
    assert health.tac2iwxxm_available is True


def test_health_response_degraded():
    """Test HealthResponse with degraded status."""
    health = HealthResponse(
        status="degraded",
        version="0.1.0",
        tac2iwxxm_available=False,
    )
    assert health.status == "degraded"
    assert health.tac2iwxxm_available is False


def test_schema_json_serialization():
    """Test that schemas can be serialized to JSON."""
    result = ConversionResult(name="test.xml", content="<xml/>")
    json_data = result.model_dump_json()
    assert isinstance(json_data, str)
    assert "test.xml" in json_data
    assert "<xml/>" in json_data


def test_schema_dict_conversion():
    """Test schema conversion to dict."""
    result = ConversionResult(
        name="test.xml",
        content="<xml/>",
        size_bytes=42,
    )
    data_dict = result.model_dump()
    assert data_dict["name"] == "test.xml"
    assert data_dict["content"] == "<xml/>"
    assert data_dict["size_bytes"] == 42
