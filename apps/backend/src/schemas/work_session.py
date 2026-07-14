"""Pydantic schemas for F5/F7 unified TAC work session API (ADR-020)."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class WorkSessionStatus(str, Enum):
    """Lifecycle status for a user's TAC work session."""

    DRAFT = "draft"
    WIP = "wip"
    FINISHED = "finished"
    FAILED = "failed"


class WorkSessionProduct(str, Enum):
    """F6 product ids stored on ``tac_work_sessions.product`` (lowercase)."""

    AIRMET = "airmet"
    METAR = "metar"
    SIGMET = "sigmet"
    SPECI = "speci"
    TAF = "taf"
    VAA = "vaa"
    TCA = "tca"


class PendingFilePayload(BaseModel):
    """Queued file content stored inline on the session row."""

    name: str = Field(min_length=1)
    content: str = ""


class WorkSessionPayload(BaseModel):
    """Shared optional fields for create/update payloads."""

    title: Optional[str] = None
    product: Optional[WorkSessionProduct] = None
    manual_tac: str = ""
    pending_files: list[PendingFilePayload] = Field(default_factory=list)
    converted_results: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    issues: list[dict[str, Any]] = Field(default_factory=list)
    conversion_params: dict[str, Any] = Field(default_factory=dict)
    status: Optional[WorkSessionStatus] = None
    kv_upload_key: Optional[str] = None

    @field_validator("product", mode="before")
    @classmethod
    def _normalize_product(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class WorkSessionCreate(WorkSessionPayload):
    """Body for POST /api/v1/work-sessions."""

    product: WorkSessionProduct


class WorkSessionUpdate(WorkSessionPayload):
    """Body for PATCH /api/v1/work-sessions/{id}."""


class WorkSession(BaseModel):
    """Persisted work session returned by the API."""

    id: UUID
    user_id: UUID
    product: WorkSessionProduct
    status: WorkSessionStatus
    title: str
    manual_tac: str = ""
    pending_files: list[PendingFilePayload] = Field(default_factory=list)
    converted_results: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    issues: list[dict[str, Any]] = Field(default_factory=list)
    conversion_params: dict[str, Any] = Field(default_factory=dict)
    kv_upload_key: Optional[str] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @field_validator("product", mode="before")
    @classmethod
    def _normalize_product(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class WorkSessionListResponse(BaseModel):
    """Paginated list of work sessions."""

    items: list[WorkSession]
    total: int
    page: int
    limit: int


class AdminWorkSession(WorkSession):
    """Deprecated admin list row (routes removed — schema retained for typing only)."""

    user_email: Optional[str] = None
