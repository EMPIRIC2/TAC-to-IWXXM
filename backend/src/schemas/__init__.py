"""Data schemas and models for the API."""
from .conversion import ConversionResult, ConversionResponse, ErrorDetail, HealthResponse
from .airport import Airport, AirportCoordinates, AirportValidator, get_airport_validator

__all__ = [
    "ConversionResult",
    "ConversionResponse",
    "ErrorDetail",
    "HealthResponse",
    "Airport",
    "AirportCoordinates",
    "AirportValidator",
    "get_airport_validator",
]
from .validation import (
    ValidationLevel,
    ValidationLayer,
    ValidationIssue,
    ValidationResult,
    AggregatedValidationResult,
    TaskStatus,
    ValidationTask,
    ValidationRequest,
)

__all__ = [
    "ConversionResult",
    "ConversionResponse",
    "ErrorDetail",
    "HealthResponse",
    "Airport",
    "AirportCoordinates",
    "AirportValidator",
    "get_airport_validator",
    "ValidationLevel",
    "ValidationLayer",
    "ValidationIssue",
    "ValidationResult",
    "AggregatedValidationResult",
    "TaskStatus",
    "ValidationTask",
    "ValidationRequest",
]
