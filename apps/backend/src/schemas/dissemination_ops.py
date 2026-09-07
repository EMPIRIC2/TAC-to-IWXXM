"""Pydantic schemas for dissemination ops JWT routes (EV-936)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

ValidityPolicy = Literal["valid-only", "warn-ok"]
MappingMode = Literal["source", "sink"]
AuditStatus = Literal["DELIVERED", "FAILED", "SKIPPED"]


class DisseminationPlanCreate(BaseModel):
    """Body to create a DisseminationPlan (no secrets)."""

    slug: str = Field(min_length=1, max_length=128)
    validity_policy: ValidityPolicy = "valid-only"
    destination_refs: list[str] = Field(default_factory=list)
    transforms: list[str] = Field(default_factory=list)
    retry: dict[str, Any] | None = None


class DisseminationPlanUpdate(BaseModel):
    """Partial update for a DisseminationPlan."""

    validity_policy: ValidityPolicy | None = None
    destination_refs: list[str] | None = None
    transforms: list[str] | None = None
    retry: dict[str, Any] | None = None


class DisseminationPlanOut(BaseModel):
    """Persisted plan row."""

    id: UUID
    user_id: UUID
    slug: str
    validity_policy: str
    destination_refs: list[str]
    transforms: list[str]
    retry: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class PlanExecuteRequest(BaseModel):
    """Execute or dry-run a plan for a sample message."""

    dry_run: bool = True
    message_id: str | None = None
    station: str | None = None
    profile: str | None = None
    iwxxm_version: str | None = None
    product: str | None = None
    iwxxm_xml: str | None = None
    tac_text: str | None = None


class DeliveryReceiptOut(BaseModel):
    """Redacted delivery receipt (API)."""

    status: AuditStatus
    gateway: str
    detail: str | None = None
    attempt: int = 1
    completed_at: datetime | None = None


class PlanExecuteResponse(BaseModel):
    """Execute outcome with receipts."""

    plan_id: UUID
    receipts: list[DeliveryReceiptOut]


class AuditRecordOut(BaseModel):
    """Persisted audit row — never includes BYOC secrets or URIs."""

    id: UUID
    user_id: UUID
    message_id: str | None = None
    station: str | None = None
    profile: str | None = None
    iwxxm_version: str | None = None
    product: str | None = None
    status: str
    gateway: str
    detail: str | None = None
    destinations: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AuditListResponse(BaseModel):
    """Paginated audit list."""

    items: list[AuditRecordOut]
    total: int
    page: int
    limit: int


class MappingConfigCreate(BaseModel):
    """Create a field mapping — no connection secrets."""

    name: str = Field(min_length=1, max_length=128)
    mode: MappingMode
    config: dict[str, Any] = Field(default_factory=dict)


class MappingConfigUpdate(BaseModel):
    """Partial MappingConfig update."""

    mode: MappingMode | None = None
    config: dict[str, Any] | None = None


class MappingConfigOut(BaseModel):
    """Persisted MappingConfig row."""

    id: UUID
    user_id: UUID
    name: str
    mode: str
    config: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class GatewayHealthOut(BaseModel):
    """Operator-safe gateway health row."""

    ok: bool
    gateway: str
    connectivity_ok: bool
    detail: str | None = None


class GatewayHealthListResponse(BaseModel):
    """Health for registered gateway kinds."""

    items: list[GatewayHealthOut]
