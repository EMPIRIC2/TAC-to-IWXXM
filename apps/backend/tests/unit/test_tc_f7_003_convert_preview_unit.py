"""T3.1 / TC-F7-003: soft-preview via preview=true on POST /api/v1/convert (S011 / EV-008).

Spec: docs/adr/ADR-022-convert-preview-flag.md; docs/api-contract.md Soft-preview;
docs/test-plan.md TC-F7-003; UJ-016.
Expected red until T3.2 implements the preview form flag + soft-preview path.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

FIXTURES = Path(__file__).resolve().parents[4] / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "product_matrix"

# Injectably invalid TAC: hard convert fails parse; soft-preview must still 200.
BAD_METAR_TAC = "METAR XXXX NOT_A_REAL_REPORT GARBAGE="


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _multipart_convert(
    client: TestClient,
    *,
    manual_text: str,
    product: str = "METAR",
    preview: str | None = None,
    lint: str = "false",
):
    """POST /api/v1/convert as multipart/form-data."""
    files: dict[str, tuple[None, str]] = {
        "manual_text": (None, manual_text),
        "product": (None, product),
        "profile": (None, "annex3"),
        "lint": (None, lint),
    }
    if preview is not None:
        files["preview"] = (None, preview)
    return client.post("/api/v1/convert", files=files)


def _assert_failed_spans(payload: dict) -> None:
    assert "failed_spans" in payload
    spans = payload["failed_spans"]
    assert isinstance(spans, list)
    assert len(spans) >= 1
    for span in spans:
        assert isinstance(span["start"], int)
        assert isinstance(span["end"], int)
        assert 0 <= span["start"] <= span["end"]
        # code / message optional per api-contract


def test_convert_preview_partial_failure_returns_200_failed_spans_and_xml(
    client: TestClient,
) -> None:
    """ADR-022: preview=true → HTTP 200, ok=false, failed_spans, best-effort IWXXM."""
    response = _multipart_convert(client, manual_text=BAD_METAR_TAC, preview="true")
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload.get("ok") is False
    _assert_failed_spans(payload)

    results = payload.get("results") or []
    assert results, "soft-preview must return best-effort XML in results"
    xml = results[0].get("content") or ""
    assert "<" in xml and "iwxxm" in xml.lower(), "best-effort body must look like IWXXM XML"


def test_convert_without_preview_unreliable_tac_quarantines(client: TestClient) -> None:
    """EV-023 / TC-EV023-003: product-shaped unreliable TAC → quarantine (not soft-preview).

    Default convert emits ``translationFailedTAC`` shell with HTTP 200 / successful=1.
    Soft-preview ``ok:false`` + ``failed_spans`` remains preview=true only (ADR-022).
    """
    response = _multipart_convert(client, manual_text=BAD_METAR_TAC, preview=None)
    assert response.status_code == 200, response.text[:500]
    body = response.json()
    assert body.get("successful", 0) >= 1
    assert not body.get("failed_spans")
    xml = (body.get("results") or [{}])[0].get("content") or ""
    assert "translationFailedTAC" in xml
    assert body.get("ok") is not False  # not soft-preview envelope


def test_convert_preview_false_unreliable_tac_quarantines(client: TestClient) -> None:
    """Explicit preview=false still quarantines unreliable METAR (EV-023), not soft-preview."""
    response = _multipart_convert(client, manual_text=BAD_METAR_TAC, preview="false")
    assert response.status_code == 200, response.text[:500]
    body = response.json()
    assert body.get("successful", 0) >= 1
    xml = (body.get("results") or [{}])[0].get("content") or ""
    assert "translationFailedTAC" in xml
    assert body.get("ok") is not False


def test_convert_without_preview_keeps_hard_fail_for_unsupported_product(
    client: TestClient,
) -> None:
    """ADR-022: non-quarantine failures still hard-fail when preview is omitted."""
    response = _multipart_convert(
        client,
        manual_text="METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        product="NOTAPRODUCT",
        preview=None,
    )
    assert response.status_code in {400, 422}, response.text[:500]


def test_convert_preview_false_keeps_hard_fail_for_unsupported_product(
    client: TestClient,
) -> None:
    """Explicit preview=false retains hard-fail for non-quarantine convert errors."""
    response = _multipart_convert(
        client,
        manual_text="METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        product="NOTAPRODUCT",
        preview="false",
    )
    assert response.status_code in {400, 422}, response.text[:500]


def test_convert_preview_success_ok_true(client: TestClient) -> None:
    """Valid TAC with preview=true still succeeds (ok true or empty failed_spans)."""
    tac = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8").strip()
    response = _multipart_convert(client, manual_text=tac, preview="true")
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload.get("ok") is True
    assert payload.get("successful", 0) >= 1
    spans = payload.get("failed_spans") or []
    assert spans == []
    assert payload["results"]
    assert "<" in payload["results"][0]["content"]


def test_convert_preview_layer12_spans_copied(client: TestClient, monkeypatch) -> None:
    """When Layer 1–2 issues carry offsets, soft-preview copies them into failed_spans."""
    from types import SimpleNamespace

    from src.services import validation as validation_mod

    issues = [
        SimpleNamespace(
            level="critical",
            message="Unknown ICAO code: XXXX",
            suggestion=None,
            code="ICAO_VALIDATION_FAILED",
            layer="airport_icao",
            location=None,
            start=6,
            end=10,
        ),
        SimpleNamespace(
            level="info",
            message="Informational TAC note",
            suggestion=None,
            code="INFO_NOTE",
            layer="tac_syntax",
            location=None,
            start=None,
            end=None,
        ),
    ]
    layer_result = SimpleNamespace(issues=issues)
    aggregated = SimpleNamespace(passed=False, total_issues=2, results=[layer_result])

    monkeypatch.setattr(
        validation_mod.ValidationService,
        "validate_all_layers",
        lambda self, tac_text: aggregated,
    )

    response = _multipart_convert(client, manual_text=BAD_METAR_TAC, preview="true")
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload.get("ok") is False
    spans = payload.get("failed_spans") or []
    assert any(s.get("start") == 6 and s.get("end") == 10 for s in spans)


def test_convert_preview_json_body_partial_failure(client: TestClient) -> None:
    """JSON metars[] + preview=true soft-fails without hard 400."""
    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [BAD_METAR_TAC],
            "product": "METAR",
            "profile": "annex3",
            "preview": True,
            "validation_level": "basic",
        },
    )
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload.get("ok") is False
    assert payload.get("failed_spans")
    assert payload.get("results")


def test_convert_preview_validation_service_error(client: TestClient, monkeypatch) -> None:
    """ValidationServiceError in soft-preview still yields best-effort convert."""
    from src.services import validation as validation_mod
    from src.services.validation import ValidationError as ValidationServiceError

    def _boom(self, tac_text):
        raise ValidationServiceError("simulated validation service failure")

    monkeypatch.setattr(validation_mod.ValidationService, "validate_all_layers", _boom)

    response = _multipart_convert(client, manual_text=BAD_METAR_TAC, preview="true")
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload.get("ok") is False
    assert payload.get("results")
    assert payload.get("failed_spans")


def test_convert_preview_json_validation_service_error(client: TestClient, monkeypatch) -> None:
    """JSON path ValidationServiceError + preview still soft-fails."""
    from src.services import validation as validation_mod
    from src.services.validation import ValidationError as ValidationServiceError

    def _boom(self, tac_text):
        raise ValidationServiceError("simulated validation service failure")

    monkeypatch.setattr(validation_mod.ValidationService, "validate_all_layers", _boom)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [BAD_METAR_TAC],
            "product": "METAR",
            "profile": "annex3",
            "preview": True,
            "validation_level": "basic",
        },
    )
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload.get("ok") is False
    assert payload.get("results")


def test_convert_preview_file_validation_service_error(client: TestClient, monkeypatch) -> None:
    """File-upload ValidationServiceError + preview still soft-fails."""
    from src.services import validation as validation_mod
    from src.services.validation import ValidationError as ValidationServiceError

    def _boom(self, tac_text):
        raise ValidationServiceError("simulated validation service failure")

    monkeypatch.setattr(validation_mod.ValidationService, "validate_all_layers", _boom)

    files = {
        "files": ("bad.metar", BAD_METAR_TAC.encode("utf-8"), "text/plain"),
        "product": (None, "METAR"),
        "profile": (None, "annex3"),
        "preview": (None, "true"),
        "lint": (None, "false"),
    }
    response = client.post("/api/v1/convert", files=files)
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload.get("ok") is False
    assert payload.get("results")


def test_convert_preview_file_upload_soft_fail(client: TestClient) -> None:
    """File upload + preview=true returns soft-fail envelope."""
    files = {
        "files": ("bad.metar", BAD_METAR_TAC.encode("utf-8"), "text/plain"),
        "product": (None, "METAR"),
        "profile": (None, "annex3"),
        "preview": (None, "true"),
        "lint": (None, "false"),
    }
    response = client.post("/api/v1/convert", files=files)
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    assert payload.get("ok") is False
    assert payload.get("results")
    assert payload.get("failed_spans")


def test_convert_preview_multiline_failed_spans_use_buffer_offsets(client: TestClient) -> None:
    """Multi-line manual_text spans must align to the full editor buffer (BUG-2026-07-15)."""
    good = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
    bad = "METAR XXXX NOT_A_REAL_REPORT GARBAGE="
    buf = f"{good}\n{bad}"
    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, buf),
            "preview": (None, "true"),
            "iwxxm_version": (None, "2023-1"),
            "product": (None, "METAR"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200
    spans = response.json().get("failed_spans") or []
    assert spans
    bad_start = buf.index(bad)
    assert any(int(s["start"]) >= bad_start for s in spans)


@pytest.mark.asyncio
async def test_convert_preview_soft_fail_logs_failed_not_success(client: TestClient, monkeypatch) -> None:
    """Soft-preview partial converts must not emit SUCCESS translation webhooks."""
    from src import api as api_module
    from src.schemas.icao_opmet import TranslationStatus

    statuses: list[TranslationStatus] = []
    failed_hooks: list[str] = []
    success_hooks: list[str] = []

    async def fake_log_translation(**kwargs):
        statuses.append(kwargs["translation_status"])
        return "tid-1"

    async def fake_notify_failed(**kwargs):
        failed_hooks.append(kwargs.get("error_type") or "failed")

    async def fake_notify_success(**kwargs):
        success_hooks.append("success")

    async def fake_notify_completed(**kwargs):
        success_hooks.append("completed")

    monkeypatch.setattr(api_module.statistics_service, "log_translation", fake_log_translation)
    monkeypatch.setattr(api_module.webhook_service, "notify_translation_failed", fake_notify_failed)
    monkeypatch.setattr(api_module.webhook_service, "notify_translation_success", fake_notify_success)
    if hasattr(api_module.webhook_service, "notify_translation_completed"):
        monkeypatch.setattr(api_module.webhook_service, "notify_translation_completed", fake_notify_completed)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, BAD_METAR_TAC),
            "preview": (None, "true"),
            "product": (None, "METAR"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200
    assert TranslationStatus.FAILED in statuses
    assert "soft_preview_partial" in failed_hooks or failed_hooks
    assert not success_hooks
