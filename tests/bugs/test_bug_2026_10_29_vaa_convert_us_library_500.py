"""BUG-2026-10-29 — VAA convert with US_FAA_NWS libraries must not 500.

Staging browser Convert of Tokyo VA Advisory (product=VAA) with
``LIB.CONVERSION.US_FAA_NWS`` (and sibling library ids) returned opaque HTTP 500
because default-on pre-convert lint used emit profile ``iwxxm_us``, which is N/A
for VAA.

[Corpus: product §F6] [Corpus: product §F10] [Corpus: api] [Corpus: tests]
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

VAA_TOKYO = (
    ROOT / "packages/tac2iwxxm/tests/fixtures/profiles/JP_JMA/VAA/valid/vaa_tokyo.tac"
).read_text(encoding="utf-8")


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token():
        return {"sub": str(uuid4()), "aud": "test-project"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    # Match staging: unhandled convert errors become HTTP 500 (not TestClient re-raise).
    test_client = TestClient(api_module.app, raise_server_exceptions=False)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_bug_2026_10_29_vaa_convert_us_faa_nws_libraries_not_500(
    client: TestClient,
) -> None:
    """Browser-shaped multipart VAA + US libraries must return non-500 (prefer 200)."""
    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, VAA_TOKYO),
            "product": (None, "VAA"),
            "conversion_library_id": (None, "LIB.CONVERSION.US_FAA_NWS"),
            "tac_validation_library_id": (None, "LIB.TAC_VALIDATION.US_FAA_NWS"),
            "iwxxm_validation_library_id": (None, "LIB.IWXXM_VALIDATION.US_FAA_NWS"),
            "dissemination_library_id": (None, "LIB.DISSEMINATION.US_FAA_NWS"),
            "decoding_library_id": (None, "LIB.DECODING.US_FAA_NWS"),
            "iwxxm_version": (None, "2025-2"),
            "validate_output": (None, "false"),
            "validation_level": (None, "basic"),
            "stop_on_error": (None, "false"),
            "include_nil_reasons": (None, "true"),
            "log_level": (None, "INFO"),
            "preview": (None, "true"),
            "propagate_residuals_to_remarks": (None, "false"),
        },
    )
    assert response.status_code != 500, response.text[:800]
    assert response.status_code == 200, response.text[:800]
    body = response.json()
    assert body.get("successful", 0) >= 1 or body.get("results"), body
    content = (body.get("results") or [{}])[0].get("content") or ""
    assert "VolcanicAshAdvisory" in content


def test_bug_2026_10_29_effective_lint_profile_falls_back_for_vaa() -> None:
    """US emit profile must resolve to annex3 lint for VAA (N/A national lint)."""
    from tac_validate.profiles import effective_lint_profile

    assert effective_lint_profile("iwxxm_us", "VAA") == "annex3"
    assert effective_lint_profile("iwxxm_us", "METAR") == "iwxxm_us"
