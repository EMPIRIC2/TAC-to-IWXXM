"""
SQLAlchemy ORM models for the backend.

This module defines the database models for translation statistics and related data.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import json

from sqlalchemy import (
    Column, String, DateTime, Text, Integer, Boolean, JSON, Index,
    CheckConstraint, ForeignKey, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy import DateTime as SA_DateTime

Base = declarative_base()


class TranslationStatisticsModel(Base):
    """
    SQLAlchemy ORM model for translation_statistics table.
    
    Stores translations of meteorological observations from METAR TAC format
    to IWXXM XML format with metadata and validation results.
    """
    __tablename__ = "translation_statistics"
    
    # Primary identifier
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    translation_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), unique=True, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(SA_DateTime(timezone=True), nullable=False, server_default="NOW()")
    translation_timestamp: Mapped[datetime] = mapped_column(SA_DateTime(timezone=True), nullable=False)
    
    # Airport and region identification
    icao_airport_code: Mapped[str] = mapped_column(String(4), nullable=False)
    icao_region: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Input/Output
    tac_message: Mapped[str] = mapped_column(Text, nullable=False)
    iwxxm_version: Mapped[str] = mapped_column(String(10), nullable=False)
    iwxxm_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Translation result
    translation_status: Mapped[str] = mapped_column(String(20), nullable=False)
    validation_layers_passed: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    validation_errors: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Performance metrics
    translation_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # User context
    user_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Translation Centre metadata
    translation_centre_designator: Mapped[str] = mapped_column(String(50), nullable=False, server_default="NOAA-MDL")
    bulletin_reception_time: Mapped[Optional[datetime]] = mapped_column(SA_DateTime(timezone=True), nullable=True)
    bulletin_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("length(icao_airport_code) = 4", name="ck_airport_code_length"),
        CheckConstraint("icao_region IN ('AFI', 'APAC', 'ESAF', 'EUR', 'MID', 'NAM', 'NAT', 'SAM', 'WAFR')", name="ck_icao_region"),
        CheckConstraint("translation_status IN ('success', 'partial', 'failed', 'validation_error')", name="ck_translation_status"),
        CheckConstraint("translation_duration_ms >= 0", name="ck_duration_positive"),
        CheckConstraint("iwxxm_version IN ('2025-2', '2023-1')", name="ck_iwxxm_version"),
        # Indexes for common query patterns
        Index("idx_translation_stats_timestamp", "translation_timestamp"),
        Index("idx_translation_stats_airport", "icao_airport_code"),
        Index("idx_translation_stats_region", "icao_region"),
        Index("idx_translation_stats_version", "iwxxm_version"),
        Index("idx_translation_stats_status", "translation_status"),
        Index("idx_translation_stats_user", "user_id"),
        Index("idx_translation_stats_created", "created_at"),
        Index("idx_translation_stats_timestamp_region", "translation_timestamp", "icao_region"),
        Index("idx_translation_stats_timestamp_version", "translation_timestamp", "iwxxm_version"),
    )
    
    def __repr__(self) -> str:
        return f"<TranslationStatistics(id={self.translation_id}, airport={self.icao_airport_code}, status={self.translation_status})>"


class TranslationStatisticsSummaryModel(Base):
    """
    SQLAlchemy ORM model for translation_statistics_summary table.
    
    Stores pre-computed aggregations of translation statistics for faster queries.
    """
    __tablename__ = "translation_statistics_summary"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    
    # Time period
    period_start: Mapped[datetime] = mapped_column(SA_DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(SA_DateTime(timezone=True), nullable=False)
    interval_type: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Filters (NULL means "all")
    icao_region: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    iwxxm_version: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Aggregated metrics
    total_translations: Mapped[int] = mapped_column(Integer, nullable=False)
    successful_translations: Mapped[int] = mapped_column(Integer, nullable=False)
    failed_translations: Mapped[int] = mapped_column(Integer, nullable=False)
    partial_translations: Mapped[int] = mapped_column(Integer, nullable=False)
    success_rate: Mapped[float] = mapped_column(Integer, nullable=False)  # Stored as numeric
    average_duration_ms: Mapped[float] = mapped_column(Integer, nullable=False)  # Stored as numeric
    
    last_updated: Mapped[datetime] = mapped_column(SA_DateTime(timezone=True), nullable=False, server_default="NOW()")
    
    __table_args__ = (
        CheckConstraint("interval_type IN ('1h', '1d', '7d', '30d')", name="ck_interval_type"),
        CheckConstraint("icao_region IN ('AFI', 'APAC', 'ESAF', 'EUR', 'MID', 'NAM', 'NAT', 'SAM', 'WAFR')", name="ck_summary_region"),
        CheckConstraint("iwxxm_version IN ('2025-2', '2023-1')", name="ck_summary_version"),
        Index("idx_summary_period", "period_start", "period_end"),
    )
    
    def __repr__(self) -> str:
        return f"<TranslationStatisticsSummary(period={self.period_start} to {self.period_end}, total={self.total_translations})>"
