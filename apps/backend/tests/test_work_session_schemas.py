"""Unit tests for F5 work session schemas."""

from uuid import uuid4

from src.schemas.work_session import (
    WorkSession,
    WorkSessionCreate,
    WorkSessionStatus,
    WorkSessionUpdate,
)


def test_work_session_create_defaults_to_draft_status_when_omitted() -> None:
    payload = WorkSessionCreate(manual_tac="METAR TEST")
    assert payload.status is None
    assert payload.manual_tac == "METAR TEST"


def test_work_session_status_enum_values() -> None:
    assert WorkSessionStatus.DRAFT.value == "draft"
    assert WorkSessionStatus.WIP.value == "wip"
    assert WorkSessionStatus.FINISHED.value == "finished"
    assert WorkSessionStatus.FAILED.value == "failed"


def test_work_session_model_round_trip() -> None:
    session_id = uuid4()
    user_id = uuid4()
    row = WorkSession(
        id=session_id,
        user_id=user_id,
        status=WorkSessionStatus.WIP,
        title="KJFK 2026-06-23",
        manual_tac="METAR KJFK",
        pending_files=[],
        converted_results=[],
        errors=[],
        issues=[],
        conversion_params={"iwxxm_version": "2025-2"},
        kv_upload_key=None,
        deleted_at=None,
        created_at="2026-06-23T12:00:00Z",
        updated_at="2026-06-23T12:00:00Z",
    )
    assert row.status == WorkSessionStatus.WIP
    dumped = row.model_dump()
    assert dumped["status"] == "wip"


def test_work_session_update_partial_fields() -> None:
    payload = WorkSessionUpdate(status=WorkSessionStatus.FAILED, errors=["parse error"])
    data = payload.model_dump(exclude_unset=True)
    assert data == {"status": WorkSessionStatus.FAILED, "errors": ["parse error"]}
