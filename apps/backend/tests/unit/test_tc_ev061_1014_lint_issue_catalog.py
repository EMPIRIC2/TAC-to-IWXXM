"""T5.1 / TC-EV061-1014 — lint + IWXXM catalog additive fields (#1014).

Spec: docs/test-plan.md TC-EV061-1014-002..004; docs/api-contract.md §lint-issue-catalog;
UJ-068; [Corpus: api] [Corpus: tests] [Corpus: product §F15]
"""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

# Operator-visible planning vocabulary (EV-048) — must not appear in attribution.
_INTERNAL_DOC_REF = re.compile(
    r"(?:\[Corpus:|\bADR-\d+\b|\bEV-\d+\b|\bS0\d+\b|\bTC-[A-Z0-9-]+\b|"
    r"\bE\d{2}-\d+\b|(?<!\w)#\d{3,}\b|\bF\d+\b|docs/sessions/|docs/feature-list)"
)

# Semantic vocabulary paths must not be the operator href when status=verified.
_SEMANTIC_ONLY_HREF = re.compile(
    r"^https?://codes\.wmo\.int/(?:49-2|common/nil|iwxxm/nil)",
    re.IGNORECASE,
)


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token() -> dict[str, str]:
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_tc_ev061_1014_002_catalog_includes_lint_and_iwxxm_rows(
    client: TestClient,
) -> None:
    """Catalog lists TAC lint and IWXXM validation checks with additive fields."""
    response = client.get("/api/v1/lint-issue-catalog")
    assert response.status_code == 200
    issues = response.json()["issues"]
    assert len(issues) >= 2

    families = {row.get("family") for row in issues}
    assert "lint" in families
    assert "iwxxm" in families

    lint_rows = [row for row in issues if row.get("family") == "lint"]
    iwxxm_rows = [row for row in issues if row.get("family") == "iwxxm"]
    assert lint_rows
    assert iwxxm_rows

    for row in issues:
        assert row.get("code")
        assert row.get("severity")
        assert row.get("message_template")
        assert row.get("family") in {"lint", "iwxxm"}
        # Additive source metadata (D-S071-api)
        assert "source_type" in row
        assert "status" in row

    filtered = client.get("/api/v1/lint-issue-catalog", params={"family": "iwxxm"})
    assert filtered.status_code == 200
    only_iwxxm = filtered.json()["issues"]
    assert only_iwxxm
    assert all(row.get("family") == "iwxxm" for row in only_iwxxm)


def test_tc_ev061_1014_003_verified_source_hrefs_are_landings(
    client: TestClient,
) -> None:
    """Operator source_url for status=verified must be HTTP landings, not semantic-only."""
    response = client.get("/api/v1/lint-issue-catalog")
    assert response.status_code == 200

    verified_with_url = [
        row for row in response.json()["issues"] if row.get("status") == "verified" and row.get("source_url")
    ]
    assert verified_with_url, "expected at least one verified row with source_url"

    for row in verified_with_url:
        url = row["source_url"]
        assert isinstance(url, str)
        assert url.startswith("http://") or url.startswith("https://"), row["code"]
        assert not _SEMANTIC_ONLY_HREF.match(url), (
            f"{row['code']}: semantic codes.wmo.int path must not be operator href (got {url!r})"
        )


def test_tc_ev061_1014_004_attribution_has_no_planning_ids(
    client: TestClient,
) -> None:
    """Operator-facing source_attribution free of planning vocabulary (EV-048)."""
    response = client.get("/api/v1/lint-issue-catalog")
    assert response.status_code == 200

    for row in response.json()["issues"]:
        value = row.get("source_attribution")
        if not isinstance(value, str):
            continue
        hit = _INTERNAL_DOC_REF.search(value)
        assert hit is None, f"{row.get('code')} source_attribution has planning id: {hit.group(0)!r}"
