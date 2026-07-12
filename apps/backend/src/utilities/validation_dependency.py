"""Validation dependencies for FastAPI request preprocessing."""

from typing import List, Optional

from fastapi import HTTPException

try:
    # Try relative imports first (when run as module in Docker)
    from ..schemas.validation import AggregatedValidationResult, ValidationLayer
    from ..services.validation import ValidationService
except ImportError:  # pragma: no cover - flat layout fallback
    from schemas.validation import AggregatedValidationResult, ValidationLayer
    from services.validation import ValidationService


# Singleton validation service for reuse
_validation_service: Optional[ValidationService] = None


def get_validation_service() -> ValidationService:
    """Get or create validation service singleton."""
    global _validation_service
    if _validation_service is None:
        _validation_service = ValidationService()
    return _validation_service


async def validate_metar_input(
    content: str,
    layers: Optional[List[ValidationLayer]] = None,
    iwxxm_version: Optional[str] = None,
) -> AggregatedValidationResult:
    """Validate METAR TAC input with validation layers.

    Can be used as a dependency or called directly for preprocessing.

    Args:
        content: METAR TAC content to validate
        layers: Optional specific layers to validate (None = all)
        iwxxm_version: Optional IWXXM version context

    Returns:
        AggregatedValidationResult with validation details

    Raises:
        HTTPException: If validation service fails
    """
    if not content or not content.strip():
        raise HTTPException(status_code=400, detail="METAR content cannot be empty")

    service = get_validation_service()

    try:
        result = service.validate(
            content=content.strip(),
            content_type="tac",
            layers=layers,
            iwxxm_version=iwxxm_version,
        )
        return result
    except ValueError as e:  # pragma: no cover - exercised via API routes
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Validation service error: {str(e)}")


async def validate_iwxxm_input(
    content: str,
    layers: Optional[List[ValidationLayer]] = None,
    iwxxm_version: Optional[str] = None,
) -> AggregatedValidationResult:
    """Validate IWXXM XML input with validation layers.

    Can be used as a dependency or called directly for preprocessing.

    Args:
        content: IWXXM XML content to validate
        layers: Optional specific layers to validate (None = all)
        iwxxm_version: Optional IWXXM version context

    Returns:
        AggregatedValidationResult with validation details

    Raises:
        HTTPException: If validation service fails
    """
    if not content or not content.strip():
        raise HTTPException(status_code=400, detail="IWXXM content cannot be empty")

    service = get_validation_service()

    try:
        result = service.validate(
            content=content.strip(),
            content_type="xml",
            layers=layers,
            iwxxm_version=iwxxm_version,
        )
        return result
    except ValueError as e:  # pragma: no cover - exercised via API routes
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Validation service error: {str(e)}")


__all__ = [
    "get_validation_service",
    "validate_metar_input",
    "validate_iwxxm_input",
]
