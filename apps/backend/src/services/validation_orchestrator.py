"""Facade for ``validation_orchestrator.py`` (line-cap split)."""

from src.services.validation_orchestrator_part_1 import (
    ComprehensiveValidationResult,
    ValidationOutcome,
    logger,
)
from src.services.validation_orchestrator_part_2 import (
    ValidationOrchestrator,
    _orchestrator_instance,
)
from src.services.validation_orchestrator_part_3 import (
    get_validation_orchestrator,
)

__all__ = [
    "ComprehensiveValidationResult",
    "ValidationOrchestrator",
    "ValidationOutcome",
    "_orchestrator_instance",
    "get_validation_orchestrator",
    "logger",
]
