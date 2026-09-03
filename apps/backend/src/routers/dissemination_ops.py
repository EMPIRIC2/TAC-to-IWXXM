"""JWT routes for dissemination ops (EV-936 / #936) — plans, audit, mappings, health."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from dissemination.allowlist import parse_allowlist
from dissemination.f19_stubs import F19_SINK_TYPES, get_staging_sink
from dissemination.gateway import DisseminationGateway, DisseminationMessage
from dissemination.health import default_health_for_kind
from dissemination.models import DRAWER_SINK_TYPES
from dissemination.plan import DisseminationPlan, execute_plan
from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer

from ..schemas.dissemination_ops import (
    AuditListResponse,
    AuditRecordOut,
    DeliveryReceiptOut,
    DisseminationPlanCreate,
    DisseminationPlanOut,
    DisseminationPlanUpdate,
    GatewayHealthListResponse,
    GatewayHealthOut,
    MappingConfigCreate,
    MappingConfigOut,
    MappingConfigUpdate,
    PlanExecuteRequest,
    PlanExecuteResponse,
)
from ..services.dissemination_ops_service import DisseminationOpsService
from ..utilities.security import verify_supabase_token

router = APIRouter(prefix="/api/v1/dissemination", tags=["Dissemination Ops"])
_bearer = HTTPBearer(auto_error=True)


def ops_service(
    user: dict[str, Any] = Depends(verify_supabase_token),
) -> DisseminationOpsService:
    """Build owner-scoped ops service from JWT ``sub``."""
    return DisseminationOpsService(str(user.get("sub") or user.get("user_id")))


@router.put("/plans/{slug}", response_model=DisseminationPlanOut)
def upsert_plan_by_slug(
    slug: str,
    payload: DisseminationPlanCreate,
    service: DisseminationOpsService = Depends(ops_service),
) -> DisseminationPlanOut:
    """
    Create a plan under ``slug`` (unique per user).

    Path slug wins over body.slug when they differ.
    """
    body = payload.model_copy(update={"slug": slug})
    return service.create_plan(body)


@router.get("/plans/{plan_id}", response_model=DisseminationPlanOut)
def get_plan(
    plan_id: UUID,
    service: DisseminationOpsService = Depends(ops_service),
) -> DisseminationPlanOut:
    """Fetch one plan by id (owner-scoped)."""
    return service.get_plan(plan_id)


@router.patch("/plans/{plan_id}", response_model=DisseminationPlanOut)
def patch_plan(
    plan_id: UUID,
    payload: DisseminationPlanUpdate,
    service: DisseminationOpsService = Depends(ops_service),
) -> DisseminationPlanOut:
    """Update plan fields (no secrets)."""
    return service.update_plan(plan_id, payload)


@router.post("/plans/{plan_id}/execute", response_model=PlanExecuteResponse)
async def execute_plan_route(
    plan_id: UUID,
    body: PlanExecuteRequest,
    service: DisseminationOpsService = Depends(ops_service),
) -> PlanExecuteResponse:
    """
    Execute or dry-run a plan; persist redacted audit rows per receipt.

    Default ``dry_run=true`` so operators can exercise audit without egress.
    """
    stored = service.get_plan(plan_id)
    plan = DisseminationPlan(
        plan_id=str(stored.id),
        validity_policy=stored.validity_policy,
        destination_refs=list(stored.destination_refs),
        transforms=list(stored.transforms),
        dry_run=body.dry_run,
    )
    # Allowlist unused on dry_run when params empty
    allowlist = parse_allowlist("127.0.0.1")
    message = DisseminationMessage(
        gateway_kind=stored.destination_refs[0] if stored.destination_refs else "amhs",
        params={},
        allowlist=allowlist,
        iwxxm_xml=body.iwxxm_xml,
        tac_text=body.tac_text,
    )
    adapters = {kind: get_staging_sink(kind) for kind in F19_SINK_TYPES}
    gateway = DisseminationGateway(adapters=adapters)  # type: ignore[arg-type]

    receipts = await execute_plan(plan, message, gateway)
    out: list[DeliveryReceiptOut] = []
    for receipt in receipts:
        service.record_audit(
            status_value=receipt.status,
            gateway=receipt.gateway,
            detail=receipt.detail,
            message_id=body.message_id,
            station=body.station,
            profile=body.profile,
            iwxxm_version=body.iwxxm_version,
            product=body.product,
            destinations={receipt.gateway: receipt.status},
        )
        out.append(
            DeliveryReceiptOut(
                status=receipt.status,  # type: ignore[arg-type]
                gateway=receipt.gateway,
                detail=receipt.detail,
                attempt=receipt.attempt,
                completed_at=receipt.completed_at,
            )
        )
    return PlanExecuteResponse(plan_id=plan_id, receipts=out)


@router.get("/audit", response_model=AuditListResponse)
def list_audit(
    product: str | None = None,
    station: str | None = None,
    profile: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: DisseminationOpsService = Depends(ops_service),
) -> AuditListResponse:
    """List redacted delivery audit rows for the caller."""
    items, total = service.list_audit(
        product=product,
        station=station,
        profile=profile,
        status_filter=status_filter,
        page=page,
        limit=limit,
    )
    return AuditListResponse(items=items, total=total, page=page, limit=limit)


@router.get("/audit/{audit_id}", response_model=AuditRecordOut)
def get_audit(
    audit_id: UUID,
    service: DisseminationOpsService = Depends(ops_service),
) -> AuditRecordOut:
    """Fetch one audit row (owner-scoped)."""
    return service.get_audit(audit_id)


@router.put("/mappings/{name}", response_model=MappingConfigOut)
def upsert_mapping(
    name: str,
    payload: MappingConfigCreate,
    service: DisseminationOpsService = Depends(ops_service),
) -> MappingConfigOut:
    """Create MappingConfig by name (unique per user)."""
    body = payload.model_copy(update={"name": name})
    return service.create_mapping(body)


@router.get("/mappings/{mapping_id}", response_model=MappingConfigOut)
def get_mapping(
    mapping_id: UUID,
    service: DisseminationOpsService = Depends(ops_service),
) -> MappingConfigOut:
    """Fetch MappingConfig by id."""
    return service.get_mapping(mapping_id)


@router.patch("/mappings/{mapping_id}", response_model=MappingConfigOut)
def patch_mapping(
    mapping_id: UUID,
    payload: MappingConfigUpdate,
    service: DisseminationOpsService = Depends(ops_service),
) -> MappingConfigOut:
    """Update MappingConfig fields."""
    return service.update_mapping(mapping_id, payload)


@router.get("/gateways/health", response_model=GatewayHealthListResponse)
async def gateways_health(
    _user: dict[str, Any] = Depends(verify_supabase_token),
) -> GatewayHealthListResponse:
    """
    Connectivity-only health for known drawer gateway kinds.

    F19 kinds are staging-honest; others report no live probe until registered.
    """
    items = [
        GatewayHealthOut(
            ok=h.ok,
            gateway=h.gateway,
            connectivity_ok=h.connectivity_ok,
            detail=h.detail,
        )
        for kind in DRAWER_SINK_TYPES
        for h in [default_health_for_kind(kind)]
    ]
    return GatewayHealthListResponse(items=items)
