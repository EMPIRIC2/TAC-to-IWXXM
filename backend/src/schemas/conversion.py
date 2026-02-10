"""Pydantic schemas for METAR conversion API responses."""
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class ConversionResult(BaseModel):
    """Individual conversion result."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "KJFK_231751Z.txt",
                "content": "<?xml version='1.0' encoding='utf-8'?><iwxxm:METAR ...>",
                "source": "file",
                "size_bytes": 1452,
            }
        }
    )

    name: str = Field(..., description="Output filename", examples=["manual_input.txt"])
    content: str = Field(
        ..., description="IWXXM XML document as UTF-8 text", min_length=1
    )
    source: Optional[str] = Field(
        None, description="Source of input", examples=["manual"]
    )
    size_bytes: Optional[int] = Field(None, description="XML output size in bytes", ge=0)


class ConversionResponse(BaseModel):
    """Response containing conversion results and errors."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [
                    {
                        "name": "manual_input.txt",
                        "content": "...",
                        "source": "manual",
                        "size_bytes": 1452,
                    }
                ],
                "errors": [],
                "total_processed": 1,
                "successful": 1,
                "failed": 0,
            }
        }
    )

    results: List[ConversionResult] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    total_processed: int = Field(..., ge=0)
    successful: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)


class ErrorDetail(BaseModel):
    """Detailed error response."""

    message: str
    errors: List[str] = Field(default_factory=list)
    total_errors: int = Field(..., ge=0)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    gifts_available: bool
