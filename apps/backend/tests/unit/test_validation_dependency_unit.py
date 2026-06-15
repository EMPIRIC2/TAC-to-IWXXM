"""Unit tests for validation dependency helpers."""

import pytest
from fastapi import HTTPException

from src.utilities import validation_dependency as vd


class _FakeService:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def validate(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.result


class _FakeValidationService:
    def __init__(self):
        self.created = True


def test_get_validation_service_singleton(monkeypatch) -> None:
    vd._validation_service = None
    monkeypatch.setattr(vd, "ValidationService", _FakeValidationService)

    first = vd.get_validation_service()
    second = vd.get_validation_service()

    assert isinstance(first, _FakeValidationService)
    assert first is second


@pytest.mark.asyncio
async def test_validate_metar_input_rejects_empty_content() -> None:
    with pytest.raises(HTTPException) as exc:
        await vd.validate_metar_input("   ")

    assert exc.value.status_code == 400
    assert "cannot be empty" in exc.value.detail


@pytest.mark.asyncio
async def test_validate_metar_input_calls_service_with_trimmed_content(monkeypatch) -> None:
    fake_service = _FakeService(result={"ok": True})
    monkeypatch.setattr(vd, "get_validation_service", lambda: fake_service)

    result = await vd.validate_metar_input("  METAR TEST  ", layers=["layer"], iwxxm_version="2025-2")

    assert result == {"ok": True}
    assert fake_service.calls == [
        {
            "content": "METAR TEST",
            "content_type": "tac",
            "layers": ["layer"],
            "iwxxm_version": "2025-2",
        }
    ]


@pytest.mark.asyncio
async def test_validate_metar_input_maps_value_error_to_400(monkeypatch) -> None:
    fake_service = _FakeService(error=ValueError("bad input"))
    monkeypatch.setattr(vd, "get_validation_service", lambda: fake_service)

    with pytest.raises(HTTPException) as exc:
        await vd.validate_metar_input("METAR TEST")

    assert exc.value.status_code == 400
    assert "Validation error" in exc.value.detail


@pytest.mark.asyncio
async def test_validate_metar_input_maps_generic_error_to_500(monkeypatch) -> None:
    fake_service = _FakeService(error=RuntimeError("boom"))
    monkeypatch.setattr(vd, "get_validation_service", lambda: fake_service)

    with pytest.raises(HTTPException) as exc:
        await vd.validate_metar_input("METAR TEST")

    assert exc.value.status_code == 500
    assert "Validation service error" in exc.value.detail


@pytest.mark.asyncio
async def test_validate_iwxxm_input_rejects_empty_content() -> None:
    with pytest.raises(HTTPException) as exc:
        await vd.validate_iwxxm_input("   ")

    assert exc.value.status_code == 400
    assert "cannot be empty" in exc.value.detail


@pytest.mark.asyncio
async def test_validate_iwxxm_input_maps_generic_error_to_500(monkeypatch) -> None:
    fake_service = _FakeService(error=RuntimeError("boom"))
    monkeypatch.setattr(vd, "get_validation_service", lambda: fake_service)

    with pytest.raises(HTTPException) as exc:
        await vd.validate_iwxxm_input("<iwxxm />")

    assert exc.value.status_code == 500
    assert "Validation service error" in exc.value.detail


@pytest.mark.asyncio
async def test_validate_iwxxm_input_calls_service_with_xml_type(monkeypatch) -> None:
    fake_service = _FakeService(result={"xml": True})
    monkeypatch.setattr(vd, "get_validation_service", lambda: fake_service)

    result = await vd.validate_iwxxm_input("  <iwxxm/>  ")

    assert result == {"xml": True}
    assert fake_service.calls[0]["content"] == "<iwxxm/>"
    assert fake_service.calls[0]["content_type"] == "xml"
