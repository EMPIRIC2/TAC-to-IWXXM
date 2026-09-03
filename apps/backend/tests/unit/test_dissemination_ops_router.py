"""Unit tests for EV-936 dissemination ops JWT routes (TC-F16-OPS-003..004)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.api import app
from src.routers import dissemination_ops as ops_router
from src.schemas.dissemination_ops import (
    AuditRecordOut,
    DisseminationPlanCreate,
    DisseminationPlanOut,
    DisseminationPlanUpdate,
    MappingConfigCreate,
    MappingConfigOut,
    MappingConfigUpdate,
)
from src.services import dissemination_ops_service as svc_mod
from src.utilities.security import verify_supabase_token

USER_ID = uuid4()
PLAN_ID = uuid4()
AUDIT_ID = uuid4()
MAPPING_ID = uuid4()
NOW = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)


def _sample_plan() -> DisseminationPlanOut:
    return DisseminationPlanOut(
        id=PLAN_ID,
        user_id=USER_ID,
        slug="default",
        validity_policy="valid-only",
        destination_refs=["amhs"],
        transforms=[],
        retry=None,
        created_at=NOW,
        updated_at=NOW,
    )


class _FakeOpsService:
    def __init__(self) -> None:
        self.plan = _sample_plan()
        self.audits: list[AuditRecordOut] = []
        self.mapping = MappingConfigOut(
            id=MAPPING_ID,
            user_id=USER_ID,
            name="sink-default",
            mode="sink",
            config={"iwxxm": "payload_xml"},
            created_at=NOW,
            updated_at=NOW,
        )

    def create_plan(self, payload: DisseminationPlanCreate) -> DisseminationPlanOut:
        svc_mod._reject_secrets(payload.model_dump())
        self.plan = self.plan.model_copy(
            update={
                "slug": payload.slug,
                "validity_policy": payload.validity_policy,
                "destination_refs": payload.destination_refs,
                "transforms": payload.transforms,
                "retry": payload.retry,
            }
        )
        return self.plan

    def get_plan(self, plan_id: UUID) -> DisseminationPlanOut:
        if plan_id != self.plan.id:
            raise HTTPException(status_code=404, detail="Plan not found")
        return self.plan

    def update_plan(self, plan_id: UUID, payload: DisseminationPlanUpdate) -> DisseminationPlanOut:
        data = payload.model_dump(exclude_unset=True)
        svc_mod._reject_secrets(data)
        self.plan = self.plan.model_copy(update=data)
        return self.plan

    def record_audit(self, **kwargs: Any) -> AuditRecordOut:
        row = AuditRecordOut(
            id=uuid4(),
            user_id=USER_ID,
            message_id=kwargs.get("message_id"),
            station=kwargs.get("station"),
            profile=kwargs.get("profile"),
            iwxxm_version=kwargs.get("iwxxm_version"),
            product=kwargs.get("product"),
            status=kwargs["status_value"],
            gateway=kwargs["gateway"],
            detail=kwargs.get("detail"),
            destinations=kwargs.get("destinations") or {},
            created_at=NOW,
        )
        self.audits.append(row)
        return row

    def list_audit(self, **_kwargs: Any) -> tuple[list[AuditRecordOut], int]:
        return self.audits, len(self.audits)

    def get_audit(self, audit_id: UUID) -> AuditRecordOut:
        for row in self.audits:
            if row.id == audit_id:
                return row
        raise HTTPException(status_code=404, detail="Audit record not found")

    def create_mapping(self, payload: MappingConfigCreate) -> MappingConfigOut:
        svc_mod._reject_secrets(payload.model_dump())
        self.mapping = self.mapping.model_copy(
            update={"name": payload.name, "mode": payload.mode, "config": payload.config}
        )
        return self.mapping

    def get_mapping(self, mapping_id: UUID) -> MappingConfigOut:
        if mapping_id != self.mapping.id:
            raise HTTPException(status_code=404, detail="Mapping not found")
        return self.mapping

    def update_mapping(self, mapping_id: UUID, payload: MappingConfigUpdate) -> MappingConfigOut:
        data = payload.model_dump(exclude_unset=True)
        svc_mod._reject_secrets(data)
        self.mapping = self.mapping.model_copy(update=data)
        return self.mapping


@pytest.fixture
def ops_client() -> TestClient:
    fake = _FakeOpsService()

    async def override_verify_token() -> dict[str, str]:
        return {"sub": str(USER_ID), "aud": "test-project", "role": "user"}

    def override_service() -> _FakeOpsService:
        return fake

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    app.dependency_overrides[ops_router.ops_service] = override_service
    client = TestClient(app)
    client.fake = fake  # type: ignore[attr-defined]
    yield client
    app.dependency_overrides.clear()


def test_gateways_health_requires_auth() -> None:
    client = TestClient(app)
    assert client.get("/api/v1/dissemination/gateways/health").status_code in {401, 403}


def test_gateways_health_ok(ops_client: TestClient) -> None:
    response = ops_client.get(
        "/api/v1/dissemination/gateways/health",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert len(items) >= 9
    amhs = next(i for i in items if i["gateway"] == "amhs")
    assert amhs["ok"] is False
    assert amhs["connectivity_ok"] is False


def test_upsert_plan_and_get(ops_client: TestClient) -> None:
    created = ops_client.put(
        "/api/v1/dissemination/plans/default",
        headers={"Authorization": "Bearer test-token"},
        json={
            "slug": "ignored",
            "validity_policy": "warn-ok",
            "destination_refs": ["amhs", "swim"],
        },
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["validity_policy"] == "warn-ok"
    assert body["destination_refs"] == ["amhs", "swim"]

    got = ops_client.get(
        f"/api/v1/dissemination/plans/{PLAN_ID}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert got.status_code == 200
    assert got.json()["slug"] == "default"

    patched = ops_client.patch(
        f"/api/v1/dissemination/plans/{PLAN_ID}",
        headers={"Authorization": "Bearer test-token"},
        json={"transforms": ["collect"]},
    )
    assert patched.status_code == 200
    assert patched.json()["transforms"] == ["collect"]


def test_ops_service_dependency_factory() -> None:
    service = ops_router.ops_service(user={"sub": str(USER_ID)})
    assert isinstance(service, svc_mod.DisseminationOpsService)
    assert service.user_id == USER_ID


def test_plan_rejects_secret_fields(ops_client: TestClient) -> None:
    response = ops_client.put(
        "/api/v1/dissemination/plans/bad",
        headers={"Authorization": "Bearer test-token"},
        json={
            "slug": "bad",
            "validity_policy": "valid-only",
            "destination_refs": [],
            "retry": {"password": "nope"},
        },
    )
    assert response.status_code == 422


def test_execute_dry_run_writes_audit(ops_client: TestClient) -> None:
    response = ops_client.post(
        f"/api/v1/dissemination/plans/{PLAN_ID}/execute",
        headers={"Authorization": "Bearer test-token"},
        json={
            "dry_run": True,
            "message_id": "msg-1",
            "station": "KJFK",
            "product": "metar",
        },
    )
    assert response.status_code == 200, response.text
    receipts = response.json()["receipts"]
    assert len(receipts) == 1
    assert receipts[0]["status"] == "SKIPPED"
    fake = ops_client.fake  # type: ignore[attr-defined]
    assert len(fake.audits) == 1
    assert fake.audits[0].station == "KJFK"
    assert "password" not in str(fake.audits[0].destinations)


def test_list_and_get_audit(ops_client: TestClient) -> None:
    ops_client.post(
        f"/api/v1/dissemination/plans/{PLAN_ID}/execute",
        headers={"Authorization": "Bearer test-token"},
        json={"dry_run": True},
    )
    listed = ops_client.get(
        "/api/v1/dissemination/audit",
        headers={"Authorization": "Bearer test-token"},
    )
    assert listed.status_code == 200
    items = listed.json()["items"]
    assert items
    audit_id = items[0]["id"]
    detail = ops_client.get(
        f"/api/v1/dissemination/audit/{audit_id}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert detail.status_code == 200
    assert detail.json()["gateway"] == "amhs"


def test_mapping_crud(ops_client: TestClient) -> None:
    created = ops_client.put(
        "/api/v1/dissemination/mappings/sink-default",
        headers={"Authorization": "Bearer test-token"},
        json={
            "name": "x",
            "mode": "sink",
            "config": {"iwxxm": "col_xml", "sourceId": "ext_id"},
        },
    )
    assert created.status_code == 200, created.text
    assert created.json()["config"]["iwxxm"] == "col_xml"

    got = ops_client.get(
        f"/api/v1/dissemination/mappings/{MAPPING_ID}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert got.status_code == 200

    patched = ops_client.patch(
        f"/api/v1/dissemination/mappings/{MAPPING_ID}",
        headers={"Authorization": "Bearer test-token"},
        json={"mode": "source"},
    )
    assert patched.status_code == 200
    assert patched.json()["mode"] == "source"


def test_mapping_rejects_uri(ops_client: TestClient) -> None:
    response = ops_client.put(
        "/api/v1/dissemination/mappings/evil",
        headers={"Authorization": "Bearer test-token"},
        json={"name": "evil", "mode": "sink", "config": {"uri": "postgres://x"}},
    )
    assert response.status_code == 422


def test_reject_secrets_helper() -> None:
    with pytest.raises(HTTPException) as exc:
        svc_mod._reject_secrets({"connection_string": "x"})
    assert exc.value.status_code == 422
