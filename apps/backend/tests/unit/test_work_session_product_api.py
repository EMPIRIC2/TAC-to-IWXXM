"""T5.1 — API contract: product required, list filter, one WIP across products."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.routers import work_sessions as ws_router
from src.schemas.work_session import (
    WorkSession,
    WorkSessionCreate,
    WorkSessionProduct,
    WorkSessionStatus,
    WorkSessionUpdate,
)
from src.services import work_session_service as svc_mod
from src.utilities.security import verify_supabase_token

USER_ID = uuid4()
NOW = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def _sample(
    *,
    product: WorkSessionProduct = WorkSessionProduct.METAR,
    status: WorkSessionStatus = WorkSessionStatus.DRAFT,
    session_id: UUID | None = None,
) -> WorkSession:
    return WorkSession(
        id=session_id or uuid4(),
        user_id=USER_ID,
        product=product,
        status=status,
        title="session",
        manual_tac="",
        created_at=NOW,
        updated_at=NOW,
    )


class _FakeService:
    def __init__(self) -> None:
        self.sessions: list[WorkSession] = [
            _sample(product=WorkSessionProduct.METAR),
            _sample(product=WorkSessionProduct.TAF),
            _sample(product=WorkSessionProduct.SPECI),
        ]
        self.last_list_kwargs: dict[str, Any] = {}

    def list_sessions(self, **kwargs: Any) -> tuple[list[WorkSession], int]:
        self.last_list_kwargs = kwargs
        products: Optional[list[WorkSessionProduct]] = kwargs.get("products")
        rows = self.sessions
        if products:
            allowed = {p.value for p in products}
            rows = [s for s in rows if s.product.value in allowed]
        return rows, len(rows)

    def get_session(self, session_id: UUID) -> WorkSession:
        for row in self.sessions:
            if row.id == session_id:
                return row
        raise HTTPException(status_code=404, detail="Work session not found")

    def create_session(self, user_id: str, payload: WorkSessionCreate) -> WorkSession:
        if payload.status == WorkSessionStatus.WIP and any(s.status == WorkSessionStatus.WIP for s in self.sessions):
            raise HTTPException(status_code=409, detail="Only one WIP session is allowed per user")
        row = _sample(product=payload.product, status=payload.status or WorkSessionStatus.DRAFT)
        self.sessions.append(row)
        return row

    def update_session(self, session_id: UUID, payload: WorkSessionUpdate) -> WorkSession:
        if payload.status == WorkSessionStatus.WIP and any(
            s.status == WorkSessionStatus.WIP and s.id != session_id for s in self.sessions
        ):
            raise HTTPException(status_code=409, detail="Only one WIP session is allowed per user")
        row = self.get_session(session_id)
        updates: dict[str, Any] = {}
        if payload.status is not None:
            updates["status"] = payload.status
        if payload.product is not None:
            updates["product"] = payload.product
        return row.model_copy(update=updates)

    def soft_delete(self, session_id: UUID) -> WorkSession:
        return self.get_session(session_id)

    def restore_session(self, session_id: UUID) -> WorkSession:
        return self.get_session(session_id)


@pytest.fixture
def client() -> TestClient:
    """Local mount of retired work-sessions router (production app no longer includes it)."""
    fake = _FakeService()

    async def override_verify_token() -> dict[str, str]:
        return {"sub": str(USER_ID), "aud": "test-project", "role": "user"}

    test_app = FastAPI()
    test_app.include_router(ws_router.router, prefix="/api/v1/work-sessions")
    test_app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_app.dependency_overrides[ws_router.work_session_service] = lambda: fake
    test_client = TestClient(test_app)
    test_client.fake_service = fake  # type: ignore[attr-defined]
    yield test_client
    test_app.dependency_overrides.clear()


def test_create_requires_product_field(client: TestClient) -> None:
    response = client.post(
        "/api/v1/work-sessions",
        headers={"Authorization": "Bearer test-token"},
        json={"manual_tac": "METAR KJFK"},
    )
    assert response.status_code == 422


def test_create_returns_product(client: TestClient) -> None:
    response = client.post(
        "/api/v1/work-sessions",
        headers={"Authorization": "Bearer test-token"},
        json={"product": "taf", "manual_tac": "TAF KJFK"},
    )
    assert response.status_code == 201, response.json()
    assert response.json()["product"] == "taf"


def test_list_accepts_comma_separated_product_filter(client: TestClient) -> None:
    response = client.get(
        "/api/v1/work-sessions?product=metar,speci",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["product"] for item in body["items"]} == {"metar", "speci"}
    fake: _FakeService = client.fake_service  # type: ignore[attr-defined]
    assert fake.last_list_kwargs.get("products") == [
        WorkSessionProduct.METAR,
        WorkSessionProduct.SPECI,
    ]


def test_second_wip_rejected_across_products(client: TestClient) -> None:
    fake: _FakeService = client.fake_service  # type: ignore[attr-defined]
    wip = _sample(product=WorkSessionProduct.METAR, status=WorkSessionStatus.WIP)
    draft = _sample(product=WorkSessionProduct.TAF, status=WorkSessionStatus.DRAFT)
    fake.sessions = [wip, draft]

    response = client.patch(
        f"/api/v1/work-sessions/{draft.id}",
        headers={"Authorization": "Bearer test-token"},
        json={"status": "wip"},
    )
    assert response.status_code == 409
    assert "WIP" in response.json()["detail"]


def test_handle_db_error_maps_unified_wip_constraint() -> None:
    with pytest.raises(HTTPException) as exc:
        svc_mod._handle_db_error(Exception("23505 duplicate tac_work_sessions_one_wip_per_user"))
    assert exc.value.status_code == 409


def test_service_targets_tac_work_sessions_table() -> None:
    assert svc_mod.TABLE == "tac_work_sessions"
