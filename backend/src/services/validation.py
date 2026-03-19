"""Main validation service with layered validation logic."""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

from ..schemas.airport import get_airport_validator
from ..schemas.validation import (
    AggregatedValidationResult,
    ValidationLayer,
    ValidationLevel,
    ValidationResult,
)
from ..utilities.tac_parser import extract_airport_code

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails critically."""
    pass


class ValidationService:
    """Service for layered validation of METAR/TAC and IWXXM XML."""

    def __init__(self):
        """Initialize validation service."""
        self.airport_validator = get_airport_validator()
        logger.info(f"ValidationService initialized with {self.airport_validator.count()} airports")

    def validate_airport_icao(self, tac_text: str) -> ValidationResult:
        """
        Layer 1: Validate ICAO airport code (BLOCKING).

        Extracts ICAO from TAC text and validates against airport database.

        Args:
            tac_text: METAR/SPECI TAC format text

        Returns:
            ValidationResult with pass/fail status

        Raises:
            ValidationError: If ICAO code is invalid (blocking validation)
        """
        start_time = time.time()
        result = ValidationResult(
            passed=True,
            layer=ValidationLayer.AIRPORT_ICAO,
        )

        try:
            # Extract ICAO code from TAC
            icao = self._extract_icao_from_tac(tac_text)

            if not icao:
                result.add_issue(
                    level=ValidationLevel.CRITICAL,
                    message="No ICAO code found in TAC text",
                    code="MISSING_ICAO",
                    suggestion="Ensure TAC text starts with METAR/SPECI followed by 4-letter ICAO code",
                )
                raise ValidationError("No ICAO code found in TAC text")

            # Validate ICAO format
            if not re.match(r"^[A-Z0-9]{4}$", icao):
                result.add_issue(
                    level=ValidationLevel.CRITICAL,
                    message=f"Invalid ICAO code format: {icao}",
                    code="INVALID_ICAO_FORMAT",
                    suggestion="ICAO codes must be exactly 4 alphanumeric characters",
                )
                raise ValidationError(f"Invalid ICAO code format: {icao}")

            # Check if ICAO exists in database
            if not self.airport_validator.validate_icao(icao):
                result.add_issue(
                    level=ValidationLevel.ERROR,
                    message=f"Unknown ICAO code: {icao}",
                    code="UNKNOWN_ICAO",
                    suggestion=f"ICAO code '{icao}' not found in airport database",
                )
                raise ValidationError(f"Unknown ICAO code: {icao}")

            # Success - add info about airport
            airport = self.airport_validator.get_airport(icao)
            if airport:
                result.metadata = {
                    "icao": icao,
                    "airport_name": airport.name,
                    "city": airport.city,
                    "country": airport.country,
                }

        except ValidationError:
            raise  # Re-raise for blocking behavior
        except Exception as e:
            logger.error(f"Error validating ICAO: {e}", exc_info=True)
            result.add_issue(
                level=ValidationLevel.ERROR,
                message=f"Validation error: {str(e)}",
                code="VALIDATION_ERROR",
            )
            raise ValidationError(f"ICAO validation error: {e}")
        finally:
            result.execution_time_ms = (time.time() - start_time) * 1000

        return result

    def validate_tac_syntax(self, tac_text: str) -> ValidationResult:
        """
        Layer 2: Validate TAC syntax (pre-conversion).

        Performs basic TAC format validation before attempting conversion.

        Args:
            tac_text: METAR/SPECI TAC format text

        Returns:
            ValidationResult with syntax issues
        """
        start_time = time.time()
        result = ValidationResult(
            passed=True,
            layer=ValidationLayer.TAC_SYNTAX,
        )

        try:
            # Check for METAR/SPECI keyword
            if not re.search(r'\b(METAR|SPECI)\b', tac_text.upper()):
                result.add_issue(
                    level=ValidationLevel.ERROR,
                    message="Missing METAR/SPECI keyword",
                    code="MISSING_KEYWORD",
                    suggestion="TAC text must start with METAR or SPECI",
                )

            # Check for timestamp (DDHHMM followed by Z)
            if not re.search(r'\b\d{6}Z\b', tac_text):
                result.add_issue(
                    level=ValidationLevel.WARNING,
                    message="No valid timestamp found (DDHHMM format + Z)",
                    code="MISSING_TIMESTAMP",
                )

            # Check minimum length
            if len(tac_text.strip()) < 20:
                result.add_issue(
                    level=ValidationLevel.WARNING,
                    message=f"TAC text seems too short ({len(tac_text)} characters)",
                    code="SHORT_MESSAGE",
                    suggestion="Valid METAR usually has at least 20 characters",
                )

            # Check for common formatting issues
            if '\t' in tac_text:
                result.add_issue(
                    level=ValidationLevel.INFO,
                    message="TAC contains tab characters (may cause parsing issues)",
                    code="CONTAINS_TABS",
                    suggestion="Replace tabs with spaces",
                )

        except Exception as e:
            logger.error(f"Error validating TAC syntax: {e}", exc_info=True)
            result.add_issue(
                level=ValidationLevel.ERROR,
                message=f"Syntax validation error: {str(e)}",
                code="VALIDATION_ERROR",
            )
        finally:
            result.execution_time_ms = (time.time() - start_time) * 1000

        return result

    def validate_all_layers(self, tac_text: str) -> AggregatedValidationResult:
        """
        Validate all applicable layers for TAC text.

        This performs synchronous validation of layers 1-2.
        For async XML validation (layers 3-6), use validate_xml_async.

        Args:
            tac_text: METAR/SPECI TAC format text

        Returns:
            AggregatedValidationResult with all layer results
        """
        results = []

        # Layer 1: ICAO validation (may raise)
        try:
            icao_result = self.validate_airport_icao(tac_text)
            results.append(icao_result)
        except ValidationError as e:
            # Create failed result for aggregation
            icao_result = ValidationResult(
                passed=False,
                layer=ValidationLayer.AIRPORT_ICAO,
            )
            icao_result.add_issue(
                level=ValidationLevel.CRITICAL,
                message=str(e),
                code="ICAO_VALIDATION_FAILED",
            )
            results.append(icao_result)
            # Stop here if ICAO validation fails
            return AggregatedValidationResult.from_results(results)

        # Layer 2: TAC syntax validation
        try:
            syntax_result = self.validate_tac_syntax(tac_text)
            results.append(syntax_result)
        except Exception as e:
            logger.error(f"TAC syntax validation failed: {e}", exc_info=True)

        return AggregatedValidationResult.from_results(results)

    @staticmethod
    def _extract_icao_from_tac(tac_text: str) -> Optional[str]:
        """Extract ICAO code from METAR/SPECI TAC text."""
        icao = extract_airport_code(tac_text)
        if icao:
            return icao

        # If no METAR/SPECI keyword, try first 4-character code
        match = re.search(r'\b([A-Z][A-Z0-9]{3})\b', tac_text.upper())
        if match:
            return match.group(1)

        return None


# Global validation service instance
_validation_service: Optional[ValidationService] = None


def get_validation_service() -> ValidationService:
    """Get or create the global ValidationService instance."""
    global _validation_service
    if _validation_service is None:
        _validation_service = ValidationService()
    return _validation_service
