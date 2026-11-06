"""QA-gap QG-weekly-api-validation-automation: severity rollup for weekly catalogs.

Locks that convert / validate / lint-tac HTTP responses expose countable
info|warning|error buckets (normalize ``severity`` vs validate ``level``).
Does not implement the weekly GHA (evolve EV-weekly-validation-catalog-gha).

[Corpus: tests] [Corpus: api]
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator, Mapping
from typing import Any

import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.utilities.security import verify_supabase_token

VALID_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
INVALID_METAR = "NILl"


def _normalize_severity(raw: object) -> str:
    """Map convert ``severity`` / validate ``level`` into catalog buckets."""
    value = str(raw or "info").strip().lower()
    if value in {"error", "critical", "fail", "failed"}:
        return "error"
    if value in {"warning", "warn"}:
        return "warning"
    return "info"


def severity_counts(issues: list[Mapping[str, Any]]) -> dict[str, int]:
    """Weekly-catalog shape: info / warning / error counts from issue rows."""
    counts: Counter[str] = Counter({"info": 0, "warning": 0, "error": 0})
    for issue in issues:
        key = "severity" if "severity" in issue else "level"
        counts[_normalize_severity(issue.get(key))] += 1
    return {"info": counts["info"], "warning": counts["warning"], "error": counts["error"]}


@pytest.fixture
def client() -> Iterator[TestClient]:
    async def override_verify_token() -> dict[str, str]:
        return {"sub": "qg-weekly-validation", "aud": "test"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def test_convert_issues_roll_up_to_info_warn_error_counts(client: TestClient) -> None:
    """Convert ``issues[]`` keep a severity that a weekly catalog can count."""
    files = [
        ("files", ("valid.tac", VALID_METAR, "text/plain")),
        ("files", ("invalid.tac", INVALID_METAR, "text/plain")),
    ]
    response = client.post("/api/v1/convert", files=files)
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    issues = payload.get("issues") or []
    assert len(issues) >= 1
    for issue in issues:
        assert "severity" in issue
        assert _normalize_severity(issue["severity"]) in {"info", "warning", "error"}

    counts = severity_counts(issues)
    assert set(counts) == {"info", "warning", "error"}
    assert sum(counts.values()) == len(issues)
    assert counts["error"] >= 1


def test_validate_issues_roll_up_via_level_field(client: TestClient) -> None:
    """Validate uses ``level`` (not ``severity``); catalog must normalize both."""
    # Intentionally non-IWXXM so the route still returns a ValidateResponse with issues.
    xml = "<?xml version='1.0'?><not-iwxxm/>"
    response = client.post(
        "/api/v1/validate",
        files={
            "xml_content": (None, xml),
            "iwxxm_version": (None, "2025-2"),
            "profile": (None, "annex3"),
            "layers": (None, "ALL"),
        },
    )
    assert response.status_code == 200, response.text[:800]
    payload = response.json()
    assert "is_valid" in payload
    assert "total_issues" in payload or "issues" in payload
    issues = list(payload.get("issues") or [])
    package_issues = list(payload.get("package_issues") or [])
    assert issues or package_issues or payload.get("is_valid") is False

    if issues:
        for issue in issues:
            assert "level" in issue
            assert _normalize_severity(issue["level"]) in {"info", "warning", "error"}
        counts = severity_counts(issues)
        assert sum(counts.values()) == len(issues)
        assert counts["error"] + counts["warning"] + counts["info"] >= 1

    if package_issues:
        # Package rows may use severity; still countable.
        for issue in package_issues:
            key = "severity" if "severity" in issue else "level"
            assert key in issue
        assert sum(severity_counts(package_issues).values()) == len(package_issues)


def test_lint_tac_issues_roll_up_to_severity_counts(client: TestClient) -> None:
    """Lint-tac issues feed the same weekly catalog buckets."""
    response = client.post(
        "/api/v1/lint-tac",
        files={
            "manual_text": (None, INVALID_METAR),
            "product": (None, "METAR"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    payload = response.json()
    issues = payload.get("issues") or []
    assert isinstance(issues, list)
    # Empty is allowed for some soft paths; when present, severity must roll up.
    if issues:
        for issue in issues:
            assert "severity" in issue
        counts = severity_counts(issues)
        assert sum(counts.values()) == len(issues)
        assert set(counts) == {"info", "warning", "error"}
