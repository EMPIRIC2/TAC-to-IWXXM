"""T5.5 / TC-F7-005 — non-METAR Draft resume + My METARs product filter semantics."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.api import app
from src.routers import work_sessions as ws_router
from src.schemas.work_session import (
    WorkSession,
    WorkSessionCreate,
    WorkSessionProduct,
    WorkSessionStatus,
    WorkSessionUpdate,
)
from src.utilities.security import verify_supabase_token

USER_ID = uuid4()
NOW = datetime(2026, 7, 14, 15, 0, tzinfo=timezone.utc)


def _row(
    *,
    product: WorkSessionProduct,
    status: WorkSessionStatus = WorkSessionStatus.DRAFT,
    session_id: UUID | None = None,
    manual_tac: str = "",
) -> WorkSession:
    return WorkSession(
        id=session_id or uuid4(),
        user_id=USER_ID,
        product=product,
        status=status,
        title=f"{product.value} draft",
        manual_tac=manual_tac,
        created_at=NOW,
        updated_at=NOW,
    )


class _Store:
    def __init__(self) -> None:
        self.rows: dict[UUID, WorkSession] = {}

    def list_sessions(self, **kwargs: Any) -> tuple[list[WorkSession], int]:
        products: Optional[list[WorkSessionProduct]] = kwargs.get("products")
        items = list(self.rows.values())
        if products:
            allowed = {p.value for p in products}
            items = [r for r in items if r.product.value in allowed]
        return items, len(items)

    def get_session(self, session_id: UUID) -> WorkSession:
        row = self.rows.get(session_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Work session not found")
        return row

    def create_session(self, user_id: str, payload: WorkSessionCreate) -> WorkSession:
        row = _row(
            product=payload.product,
            status=payload.status or WorkSessionStatus.DRAFT,
            manual_tac=payload.manual_tac,
        )
        self.rows[row.id] = row
        return row

    def update_session(self, session_id: UUID, payload: WorkSessionUpdate) -> WorkSession:
        row = self.get_session(session_id)
        updates: dict[str, Any] = {}
        if payload.manual_tac:
            updates["manual_tac"] = payload.manual_tac
        if payload.product is not None:
            updates["product"] = payload.product
        if payload.status is not None:
            updates["status"] = payload.status
        row = row.model_copy(update=updates)
        self.rows[session_id] = row
        return row

    def soft_delete(self, session_id: UUID) -> WorkSession:
        return self.get_session(session_id)

    def restore_session(self, session_id: UUID) -> WorkSession:
        return self.get_session(session_id)


@pytest.fixture
def client() -> TestClient:
    store = _Store()

    async def _auth() -> dict[str, str]:
        return {"sub": str(USER_ID)}

    app.dependency_overrides[verify_supabase_token] = _auth
    app.dependency_overrides[ws_router.work_session_service] = lambda: store
    test_client = TestClient(app)
    test_client.store = store  # type: ignore[attr-defined]
    yield test_client
    app.dependency_overrides.clear()


def test_tc_f7_005_non_metar_draft_survives_get(client: TestClient) -> None:
    headers = {"Authorization": "Bearer t"}
    created = client.post(
        "/api/v1/work-sessions",
        headers=headers,
        json={
            "product": "taf",
            "manual_tac": "TAF KJFK 141200Z 1412/1512 18010KT",
            "status": "draft",
            "conversion_params": {"product": "TAF", "profile": "annex3"},
        },
    )
    assert created.status_code == 201, created.json()
    session_id = created.json()["id"]
    assert created.json()["product"] == "taf"

    resumed = client.get(f"/api/v1/work-sessions/{session_id}", headers=headers)
    assert resumed.status_code == 200
    body = resumed.json()
    assert body["product"] == "taf"
    assert "TAF KJFK" in body["manual_tac"]


def test_tc_f7_005_my_metars_filter_excludes_taf(client: TestClient) -> None:
    store: _Store = client.store  # type: ignore[attr-defined]
    metar = _row(product=WorkSessionProduct.METAR, manual_tac="METAR KJFK")
    speci = _row(product=WorkSessionProduct.SPECI, manual_tac="SPECI KJFK")
    taf = _row(product=WorkSessionProduct.TAF, manual_tac="TAF KJFK")
    store.rows = {metar.id: metar, speci.id: speci, taf.id: taf}

    response = client.get(
        "/api/v1/work-sessions?product=metar,speci",
        headers={"Authorization": "Bearer t"},
    )
    assert response.status_code == 200
    products = {item["product"] for item in response.json()["items"]}
    assert products == {"metar", "speci"}
    assert response.json()["total"] == 2


def test_tc_f7_005_workbench_history_lists_all_products(client: TestClient) -> None:
    store: _Store = client.store  # type: ignore[attr-defined]
    store.rows = {
        uuid4(): _row(product=WorkSessionProduct.METAR),
        uuid4(): _row(product=WorkSessionProduct.TAF),
        uuid4(): _row(product=WorkSessionProduct.VAA),
    }
    response = client.get(
        "/api/v1/work-sessions?limit=20",
        headers={"Authorization": "Bearer t"},
    )
    assert response.status_code == 200
    assert response.json()["total"] == 3


def test_migrate_sql_copies_legacy_product_defaults() -> None:
    """Smoke: cutover SQL maps missing conversion_params.product → metar."""
    from pathlib import Path

    migration = Path(__file__).resolve().parents[4] / "supabase/migrations/20260714000010_tac_work_sessions.sql"
    sql = migration.read_text(encoding="utf-8")
    assert "THEN 'metar'" in sql
    assert "FROM public.metar_work_sessions" in sql
    assert "DROP TABLE IF EXISTS public.metar_work_sessions" in sql
