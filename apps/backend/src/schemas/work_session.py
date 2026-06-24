"""Pydantic schemas for F5 METAR work session API."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorkSessionStatus(str, Enum):
    """Lifecycle status for a user's METAR work session."""

    DRAFT = "draft"
    WIP = "wip"
    FINISHED = "finished"
    FAILED = "failed"


class PendingFilePayload(BaseModel):
    """Queued file content stored inline on the session row."""

    name: str = Field(min_length=1)
    content: str = ""


class WorkSessionPayload(BaseModel):
    """Shared optional fields for create/update payloads."""

    title: Optional[str] = None
    manual_tac: str = ""
    pending_files: list[PendingFilePayload] = Field(default_factory=list)
    converted_results: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    issues: list[dict[str, Any]] = Field(default_factory=list)
    conversion_params: dict[str, Any] = Field(default_factory=dict)
    status: Optional[WorkSessionStatus] = None
    kv_upload_key: Optional[str] = None


class WorkSessionCreate(WorkSessionPayload):
    """Body for POST /api/v1/work-sessions."""


class WorkSessionUpdate(WorkSessionPayload):
    """Body for PATCH /api/v1/work-sessions/{id}."""


class WorkSession(BaseModel):
    """Persisted work session returned by the API."""

    id: UUID
    user_id: UUID
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


class WorkSessionListResponse(BaseModel):
    """Paginated list of work sessions."""

    items: list[WorkSession]
    total: int
    page: int
    limit: int


class AdminWorkSession(WorkSession):
    """Admin list row with user email when available."""

    user_email: Optional[str] = None
