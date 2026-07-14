"""T5.1 — Unified tac_work_sessions schema: product field + one-WIP-total (ADR-020)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.schemas.work_session import (
    WorkSession,
    WorkSessionCreate,
    WorkSessionProduct,
    WorkSessionStatus,
    WorkSessionUpdate,
)


def test_work_session_product_enum_covers_seven_f6_products() -> None:
    values = {p.value for p in WorkSessionProduct}
    assert values == {
        "airmet",
        "metar",
        "sigmet",
        "speci",
        "taf",
        "vaa",
        "tca",
    }


def test_work_session_create_requires_product() -> None:
    with pytest.raises(ValidationError):
        WorkSessionCreate(manual_tac="METAR KJFK")


def test_work_session_create_accepts_product_case_insensitive() -> None:
    payload = WorkSessionCreate(product="TAF", manual_tac="TAF KJFK")
    assert payload.product == WorkSessionProduct.TAF


def test_work_session_model_includes_product() -> None:
    now = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
    row = WorkSession(
        id=uuid4(),
        user_id=uuid4(),
        product=WorkSessionProduct.METAR,
        status=WorkSessionStatus.DRAFT,
        title="KJFK",
        created_at=now,
        updated_at=now,
    )
    assert row.model_dump()["product"] == "metar"


def test_work_session_update_may_change_product() -> None:
    payload = WorkSessionUpdate(product="speci")
    assert payload.product == WorkSessionProduct.SPECI
