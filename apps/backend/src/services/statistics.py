"""
Translation Statistics Service.

Logs translation operations to PostgreSQL for ICAO OPMET compliance.
Implements indefinite retention policy (User Decision 1).
"""

import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Sequence, Union

from sqlalchemy import Integer, and_, func, select

from ..config.icao_opmet import get_icao_region, should_log_statistics
from ..models import TranslationStatisticsModel
from ..schemas.icao_opmet import TranslationStatus, ValidationLayer
from ..schemas.validation import ValidationLayer as RuntimeValidationLayer
from ..utilities.observability import record_translation_metric
from .database import get_db_session

logger = logging.getLogger(__name__)

_ICAO_FALLBACK_CODE = "ZZZZ"
_ICAO_PATTERN = re.compile(r"^[A-Z0-9]{4}$")


def _normalize_icao_code(icao_airport_code: Optional[str]) -> str:
    """Normalize ICAO airport code for persistence.

    Returns a guaranteed non-null 4-character placeholder when input is missing/invalid.
    """
    if isinstance(icao_airport_code, str):
        candidate = icao_airport_code.strip().upper()
        if _ICAO_PATTERN.match(candidate):
            return candidate
    return _ICAO_FALLBACK_CODE


class StatisticsService:
    """Service for logging and querying translation statistics."""

    @staticmethod
    async def log_translation(
        tac_message: str,
        iwxxm_version: str,
        icao_airport_code: Optional[str],
        translation_status: TranslationStatus,
        translation_duration_ms: float | int,
        iwxxm_output: Optional[str] = None,
        validation_layers_passed: Optional[Sequence[Union[ValidationLayer, RuntimeValidationLayer, str]]] = None,
        validation_errors: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        bulletin_reception_time: Optional[datetime] = None,
        bulletin_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Log a translation operation to the database.

        Args:
            tac_message: Original METAR TAC message
            iwxxm_version: Target IWXXM version (2025-2 or 2023-1)
            icao_airport_code: 4-letter ICAO airport identifier
            translation_status: Translation outcome status
            translation_duration_ms: Processing time in milliseconds
            iwxxm_output: Generated IWXXM XML (None if failed)
            validation_layers_passed: List of passed validation layers
            validation_errors: Detailed validation errors by layer
            user_id: Authenticated user ID (Supabase UUID)
            session_id: User session identifier
            bulletin_reception_time: Original bulletin reception time
            bulletin_id: WMO bulletin identifier

        Returns:
            Translation UUID if logged successfully, None otherwise
        """
        if not should_log_statistics():
            logger.debug("Statistics logging disabled")
            return None

        try:
            # Generate unique translation ID
            translation_id = uuid.uuid4()
            timestamp = datetime.utcnow()
            normalized_icao_code = _normalize_icao_code(icao_airport_code)
            if normalized_icao_code != (icao_airport_code or ""):
                logger.warning(
                    "Invalid airport code %r normalized to fallback %s",
                    icao_airport_code,
                    _ICAO_FALLBACK_CODE,
                )

            # Determine ICAO region
            try:
                icao_region = get_icao_region(normalized_icao_code)
            except ValueError as e:
                logger.warning(f"Invalid airport code {normalized_icao_code}: {e}, defaulting to NAM")
                icao_region = "NAM"

            # Convert validation layers to strings
            validation_layer_strings = [
                layer.value if isinstance(layer, (ValidationLayer, RuntimeValidationLayer)) else str(layer)
                for layer in (validation_layers_passed or [])
            ]

            # Create ORM model instance
            record = TranslationStatisticsModel(
                translation_id=translation_id,
                translation_timestamp=timestamp,
                icao_airport_code=normalized_icao_code,
                icao_region=icao_region,
                tac_message=tac_message,
                iwxxm_version=iwxxm_version,
                iwxxm_output=iwxxm_output,
                translation_status=translation_status.value
                if isinstance(translation_status, TranslationStatus)
                else translation_status,
                validation_layers_passed=validation_layer_strings if validation_layer_strings else None,
                validation_errors=validation_errors,
                translation_duration_ms=int(round(translation_duration_ms)),
                user_id=uuid.UUID(user_id) if user_id and isinstance(user_id, str) and len(user_id) == 36 else user_id,
                session_id=session_id,
                bulletin_reception_time=bulletin_reception_time,
                bulletin_id=bulletin_id,
            )

            # Insert into database
            try:
                async with get_db_session() as session:
                    session.add(record)
                    await session.commit()
            except Exception as commit_error:
                logger.error(f"Failed to commit translation statistics to database: {commit_error}")
                # Don't re-raise - allow translation to continue even if logging fails
                return None

            logger.info(
                f"Logged translation {translation_id} for {normalized_icao_code} ({icao_region}, {translation_status})"
            )
            translation_status_value = (
                translation_status.value
                if isinstance(translation_status, TranslationStatus)
                else str(translation_status)
            )
            record_translation_metric(
                status=translation_status_value,
                iwxxm_version=iwxxm_version,
                icao_region=icao_region,
                duration_ms=int(round(translation_duration_ms)),
            )
            return str(translation_id)

        except Exception as e:
            logger.error(f"Failed to log translation statistics: {e}", exc_info=True)
            return None

    @staticmethod
    async def get_statistics(
        start_date: datetime,
        end_date: datetime,
        icao_region: Optional[str] = None,
        iwxxm_version: Optional[str] = None,
        airport_code: Optional[str] = None,
        include_airport_breakdown: bool = False,
        include_error_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Query aggregated translation statistics.

        Args:
            start_date: Statistics period start
            end_date: Statistics period end
            icao_region: Optional ICAO region filter
            iwxxm_version: Optional IWXXM version filter
            airport_code: Optional airport code filter
            include_airport_breakdown: Include per-airport statistics
            include_error_details: Include detailed error analysis

        Returns:
            Dictionary with aggregated statistics
        """
        try:
            async with get_db_session() as session:
                # Build base query with filters
                filters = [
                    TranslationStatisticsModel.translation_timestamp >= start_date,
                    TranslationStatisticsModel.translation_timestamp < end_date,
                ]

                if icao_region:
                    filters.append(TranslationStatisticsModel.icao_region == icao_region)

                if iwxxm_version:
                    filters.append(TranslationStatisticsModel.iwxxm_version == iwxxm_version)

                if airport_code:
                    filters.append(TranslationStatisticsModel.icao_airport_code == airport_code)

                where_clause = and_(*filters)

                # Overall statistics query
                overall_query = select(
                    func.count(TranslationStatisticsModel.id).label("total"),
                    func.sum((TranslationStatisticsModel.translation_status == "success").cast(Integer)).label(
                        "successful"
                    ),
                    func.sum((TranslationStatisticsModel.translation_status == "failed").cast(Integer)).label("failed"),
                    func.sum((TranslationStatisticsModel.translation_status == "partial").cast(Integer)).label(
                        "partial"
                    ),
                    func.avg(TranslationStatisticsModel.translation_duration_ms).label("avg_duration"),
                    func.percentile_cont(0.5)
                    .within_group(TranslationStatisticsModel.translation_duration_ms)
                    .label("median_duration"),
                ).where(where_clause)

                result = await session.execute(overall_query)
                row = result.first()
                if row is None:
                    row_total = row_successful = row_failed = row_partial = 0
                    row_avg_duration = 0.0
                    row_median_duration = None
                else:
                    row_total = row.total or 0
                    row_successful = row.successful or 0
                    row_failed = row.failed or 0
                    row_partial = row.partial or 0
                    row_avg_duration = row.avg_duration or 0
                    row_median_duration = row.median_duration

                total = row_total
                successful = row_successful
                failed = row_failed
                partial = row_partial
                success_rate = (successful / total * 100) if total > 0 else 0.0

                # Region breakdown
                region_query = (
                    select(
                        TranslationStatisticsModel.icao_region,
                        func.count(TranslationStatisticsModel.id).label("count"),
                    )
                    .where(where_clause)
                    .group_by(TranslationStatisticsModel.icao_region)
                    .order_by(func.count(TranslationStatisticsModel.id).desc())
                )

                region_result = await session.execute(region_query)
                translations_by_region = {r.icao_region: r.count for r in region_result.all()}

                # Version breakdown
                version_query = (
                    select(
                        TranslationStatisticsModel.iwxxm_version,
                        func.count(TranslationStatisticsModel.id).label("count"),
                    )
                    .where(where_clause)
                    .group_by(TranslationStatisticsModel.iwxxm_version)
                    .order_by(func.count(TranslationStatisticsModel.id).desc())
                )

                version_result = await session.execute(version_query)
                translations_by_version = {v.iwxxm_version: v.count for v in version_result.all()}

                # Airport breakdown (if requested)
                translations_by_airport = None
                if include_airport_breakdown:
                    airport_query = (
                        select(
                            TranslationStatisticsModel.icao_airport_code,
                            func.count(TranslationStatisticsModel.id).label("count"),
                        )
                        .where(where_clause)
                        .group_by(TranslationStatisticsModel.icao_airport_code)
                        .order_by(func.count(TranslationStatisticsModel.id).desc())
                        .limit(50)
                    )

                    airport_result = await session.execute(airport_query)
                    translations_by_airport = {a.icao_airport_code: a.count for a in airport_result.all()}

                # Common validation errors (if requested)
                common_validation_errors = None
                if include_error_details and total > 0:
                    error_query = (
                        select(
                            TranslationStatisticsModel.translation_status,
                            func.count(TranslationStatisticsModel.id).label("count"),
                        )
                        .where(and_(where_clause, TranslationStatisticsModel.translation_status != "success"))
                        .group_by(TranslationStatisticsModel.translation_status)
                        .order_by(func.count(TranslationStatisticsModel.id).desc())
                        .limit(10)
                    )

                    error_result = await session.execute(error_query)
                    common_validation_errors = [
                        {"status": e.translation_status, "count": e.count} for e in error_result.all()
                    ]

                return {
                    "period_start": start_date,
                    "period_end": end_date,
                    "total_translations": total,
                    "successful_translations": successful,
                    "failed_translations": failed,
                    "partial_translations": partial,
                    "success_rate": round(success_rate, 2),
                    "average_duration_ms": round(float(row_avg_duration), 2),
                    "median_duration_ms": round(float(row_median_duration), 2)
                    if row_median_duration is not None
                    else None,
                    "translations_by_region": translations_by_region,
                    "translations_by_version": translations_by_version,
                    "translations_by_airport": translations_by_airport,
                    "validation_layer_success_rates": {},
                    "common_validation_errors": common_validation_errors,
                }

        except Exception as e:
            logger.error(f"Failed to query translation statistics: {e}", exc_info=True)
            # Return empty statistics on error
            return {
                "period_start": start_date,
                "period_end": end_date,
                "total_translations": 0,
                "successful_translations": 0,
                "failed_translations": 0,
                "partial_translations": 0,
                "success_rate": 0.0,
                "average_duration_ms": 0.0,
                "median_duration_ms": None,
                "translations_by_region": {},
                "translations_by_version": {},
                "translations_by_airport": None,
                "validation_layer_success_rates": {},
                "common_validation_errors": None,
            }

    @staticmethod
    async def get_statistics_by_region(
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get translation statistics grouped by ICAO region.

        Args:
            start_date: Statistics period start
            end_date: Statistics period end

        Returns:
            Dictionary mapping region codes to statistics
        """
        try:
            async with get_db_session() as session:
                query = (
                    select(
                        TranslationStatisticsModel.icao_region,
                        func.count(TranslationStatisticsModel.id).label("total"),
                        func.sum((TranslationStatisticsModel.translation_status == "success").cast(Integer)).label(
                            "successful"
                        ),
                        func.avg(TranslationStatisticsModel.translation_duration_ms).label("avg_duration"),
                    )
                    .where(
                        and_(
                            TranslationStatisticsModel.translation_timestamp >= start_date,
                            TranslationStatisticsModel.translation_timestamp < end_date,
                        )
                    )
                    .group_by(TranslationStatisticsModel.icao_region)
                    .order_by(func.count(TranslationStatisticsModel.id).desc())
                )

                result = await session.execute(query)
                rows = result.all()

                result_dict = {}
                for row in rows:
                    total = row.total
                    successful = row.successful
                    success_rate = (successful / total * 100) if total > 0 else 0.0

                    result_dict[row.icao_region] = {
                        "total_translations": total,
                        "successful_translations": successful,
                        "success_rate": round(success_rate, 2),
                        "average_duration_ms": round(float(row.avg_duration or 0), 2),
                    }

                return result_dict

        except Exception as e:
            logger.error(f"Failed to query region statistics: {e}", exc_info=True)
            return {}


# Singleton instance
statistics_service = StatisticsService()
