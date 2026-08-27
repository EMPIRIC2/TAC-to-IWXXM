"""Pydantic schemas for F5/F7 unified TAC work session API (ADR-020)."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class WorkSessionStatus(StrEnum):
    """Lifecycle status for a user's TAC work session."""

    DRAFT = "draft"
    WIP = "wip"
    FINISHED = "finished"
    FAILED = "failed"


class WorkSessionProduct(StrEnum):
    """Product ids stored on ``tac_work_sessions.product`` (lowercase)."""

    AIRMET = "airmet"
    METAR = "metar"
    SIGMET = "sigmet"
    SPECI = "speci"
    TAF = "taf"
    VAA = "vaa"
    TCA = "tca"
    SWXA = "swxa"


class PendingFilePayload(BaseModel):
    """Queued file content stored inline on the session row."""

    name: str = Field(min_length=1)
    content: str = ""


def _normalize_product_value(value: object) -> object:
    if isinstance(value, str):
        return value.strip().lower()
    return value


class WorkSessionPayload(BaseModel):
    """Shared optional fields for create/update payloads (product declared on subclasses)."""

    title: str | None = None
    manual_tac: str = ""
    pending_files: list[PendingFilePayload] = Field(default_factory=list)
    converted_results: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    issues: list[dict[str, Any]] = Field(default_factory=list)
    conversion_params: dict[str, Any] = Field(default_factory=dict)
    status: WorkSessionStatus | None = None
    kv_upload_key: str | None = None


class WorkSessionCreate(WorkSessionPayload):
    """Body for POST /api/v1/work-sessions."""

    product: WorkSessionProduct

    @field_validator("product", mode="before")
    @classmethod
    def _normalize_product(cls, value: object) -> object:
        return _normalize_product_value(value)


class WorkSessionUpdate(WorkSessionPayload):
    """Body for PATCH /api/v1/work-sessions/{id}."""

    product: WorkSessionProduct | None = None

    @field_validator("product", mode="before")
    @classmethod
    def _normalize_product(cls, value: object) -> object:
        return _normalize_product_value(value)


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
    kv_upload_key: str | None = None
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("product", mode="before")
    @classmethod
    def _normalize_product(cls, value: object) -> object:
        return _normalize_product_value(value)


class WorkSessionListResponse(BaseModel):
    """Paginated list of work sessions."""

    items: list[WorkSession]
    total: int
    page: int
    limit: int


class AdminWorkSession(WorkSession):
    """Deprecated admin list row (routes removed - schema retained for typing only)."""

    user_email: str | None = None
