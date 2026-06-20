"""Data schemas and models for the API."""
from .airport import Airport, AirportCoordinates, AirportValidator, get_airport_validator
from .conversion import ConversionResponse, ConversionResult, ErrorDetail, HealthResponse

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
    AggregatedValidationResult,
    TaskStatus,
    ValidationIssue,
    ValidationLayer,
    ValidationLevel,
    ValidationRequest,
    ValidationResult,
    ValidationTask,
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
