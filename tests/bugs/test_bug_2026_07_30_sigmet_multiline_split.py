"""BUG-2026-07-30 - SIGMET/AIRMET multi-line manual TAC must not be line-split.

WMO ``sigmet-A6-1a-TS`` is two lines (header ``…YUSO-`` + body ``…=``). Line-splitting
yields ``manual_input_2`` → ``PARSE_ERROR: unable to parse SIGMET header`` and a
soft-preview with nil geometry - matching production UI Failed-TAC on the catalog demo.
"""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src import api as api_module  # noqa: E402
from src.utilities.security import verify_supabase_token  # noqa: E402

SIGMET_A6_1A_TS = (
    "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
    "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=\n"
)

AIRMET_A6_1A_TS = (
    "YUDD AIRMET 1 VALID 101200/101600 YUSO-\n"
    "YUDD SHANLON FIR/UIR ISOL TS FCST N OF S50 TOP FL350 MOV E 20KT WKN=\n"
)


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token():
        return {"sub": str(uuid4()), "aud": "test-project"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_split_manual_entries_keeps_sigmet_airmet_multiline() -> None:
    """Product-aware split must preserve SIGMET/AIRMET as one document (like VAA/TCA)."""
    sigmet_entries = api_module.split_manual_entries(SIGMET_A6_1A_TS, product="SIGMET")
    assert len(sigmet_entries) == 1, (
        f"SIGMET must stay one entry; got {len(sigmet_entries)}: {sigmet_entries!r}"
    )
    assert "SHANLON" in sigmet_entries[0]
    assert "YUSO-" in sigmet_entries[0]

    airmet_entries = api_module.split_manual_entries(AIRMET_A6_1A_TS, product="AIRMET")
    assert len(airmet_entries) == 1, (
        f"AIRMET must stay one entry; got {len(airmet_entries)}: {airmet_entries!r}"
    )

    # METAR batching by line remains unchanged.
    metars = api_module.split_manual_entries(
        "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015=\n"
        "METAR EGLL 161220Z 09010KT 9999 SCT030 10/05 Q1018=\n",
        product="METAR",
    )
    assert len(metars) == 2


def test_sigmet_a6_1a_soft_preview_no_header_parse_error(client: TestClient) -> None:
    """Soft-preview of WMO A6-1a-TS must not emit header PARSE_ERROR from line 2."""
    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": SIGMET_A6_1A_TS,
            "product": "SIGMET",
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "preview": "true",
            "stop_on_error": "false",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    spans = payload.get("failed_spans") or []
    header_errors = [
        s
        for s in spans
        if s.get("code") == "PARSE_ERROR"
        and "unable to parse SIGMET header" in (s.get("message") or "")
    ]
    assert header_errors == [], (
        "two-line SIGMET was line-split; body line failed header parse: "
        f"{header_errors!r}; all spans={spans!r}"
    )
    results = payload.get("results") or []
    assert len(results) == 1, f"expected one IWXXM result, got {len(results)}"
    xml = results[0].get("content") or ""
    assert "posList" in xml or "AirspaceVolume" in xml, (
        "expected geometry from body line; soft-preview looks header-only"
    )
    assert 'intensityChange="WEAKEN"' in xml or "WEAKEN" in xml
