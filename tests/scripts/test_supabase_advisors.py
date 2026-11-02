"""Unit coverage for scripts/security/supabase_advisors.py."""

from __future__ import annotations

import io
import json
from typing import Any
from unittest.mock import MagicMock

import pytest
from tests.scripts.conftest import load_script


@pytest.fixture
def advisors():
    return load_script("security/supabase_advisors.py", "supabase_advisors_mod")


def _http_response(payload: object, status: int = 200) -> MagicMock:
    raw = json.dumps(payload).encode("utf-8")
    resp = MagicMock()
    resp.status = status
    resp.read.return_value = raw
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = None
    return resp


@pytest.mark.unit
def test_normalize_level_aliases(advisors) -> None:
    assert advisors.normalize_level("error") == "ERROR"
    assert advisors.normalize_level("WARNING") == "WARN"
    assert advisors.normalize_level("CRITICAL") == "ERROR"
    assert advisors.normalize_level("HIGH") == "ERROR"
    assert advisors.normalize_level(None) == "INFO"


@pytest.mark.unit
def test_parse_lints_payload_shapes(advisors) -> None:
    assert advisors.parse_lints_payload({"lints": [{"name": "a"}]}) == [{"name": "a"}]
    assert advisors.parse_lints_payload([{"name": "b"}]) == [{"name": "b"}]
    assert advisors.parse_lints_payload({"lints": "nope"}) == []


@pytest.mark.unit
def test_failing_lints_error_threshold(advisors) -> None:
    lints = [
        {"level": "INFO", "name": "i"},
        {"level": "WARN", "name": "w"},
        {"level": "ERROR", "name": "e"},
    ]
    bad = advisors.failing_lints(lints, "error")
    assert [x["name"] for x in bad] == ["e"]
    assert [x["name"] for x in advisors.failing_lints(lints, "warn")] == ["w", "e"]
    assert advisors.failing_lints(lints, "none") == []


@pytest.mark.unit
def test_advisor_url_security_adds_lint_type(advisors) -> None:
    url = advisors.advisor_url(
        "https://api.supabase.com/v1", "ktvxijislbtgqapllmuk", "security"
    )
    assert url.endswith("/advisors/security?lint_type=sql")
    perf = advisors.advisor_url(
        "https://api.supabase.com/v1", "ktvxijislbtgqapllmuk", "performance"
    )
    assert perf.endswith("/advisors/performance")
    assert "lint_type" not in perf


@pytest.mark.unit
def test_run_advisors_skips_missing_health_and_fails_on_error(advisors) -> None:
    import urllib.error

    def opener(req: Any, timeout: float = 60.0) -> MagicMock:
        url = req.full_url if hasattr(req, "full_url") else str(req.get_full_url())
        if "/advisors/health" in url:
            raise urllib.error.HTTPError(
                url, 404, "Not Found", hdrs=None, fp=io.BytesIO(b"{}")
            )
        if "/advisors/security" in url:
            return _http_response(
                {
                    "lints": [
                        {
                            "name": "rls_disabled_in_public",
                            "title": "RLS disabled",
                            "level": "ERROR",
                            "categories": ["SECURITY"],
                            "detail": "public.t",
                            "remediation": "enable RLS",
                        }
                    ]
                }
            )
        if "/advisors/performance" in url:
            return _http_response(
                {
                    "lints": [
                        {
                            "name": "unindexed_foreign_keys",
                            "title": "FK",
                            "level": "INFO",
                            "categories": ["PERFORMANCE"],
                        }
                    ]
                }
            )
        raise AssertionError(f"unexpected url {url}")

    code, lines = advisors.run_advisors(
        project_ref="ktvxijislbtgqapllmuk",
        token="sbp_test",
        opener=opener,
        fail_on="error",
    )
    text = "\n".join(lines)
    assert code == 1
    assert "skip health" in text
    assert "FAIL:" in text
    assert "rls_disabled_in_public" in text


@pytest.mark.unit
def test_run_advisors_pass_when_only_warn(advisors) -> None:
    def opener(req: Any, timeout: float = 60.0) -> MagicMock:
        return _http_response(
            {"lints": [{"name": "x", "level": "WARN", "categories": ["SECURITY"]}]}
        )

    code, lines = advisors.run_advisors(
        project_ref="abc",
        token="tok",
        advisor_types=("security",),
        fail_on="error",
        opener=opener,
    )
    assert code == 0
    assert any("PASS:" in line for line in lines)


@pytest.mark.unit
def test_run_advisors_auth_error_fails(advisors) -> None:
    import urllib.error

    def opener(req: Any, timeout: float = 60.0) -> MagicMock:
        raise urllib.error.HTTPError(
            "https://api.supabase.com/v1/projects/x/advisors/security",
            401,
            "Unauthorized",
            hdrs=None,
            fp=io.BytesIO(b'{"message":"Invalid access token"}'),
        )

    code, lines = advisors.run_advisors(
        project_ref="x",
        token="bad",
        advisor_types=("security",),
        opener=opener,
    )
    assert code == 1
    assert any("Invalid access token" in line for line in lines)


@pytest.mark.unit
def test_main_requires_token(advisors, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("SUPABASE_TOKEN", raising=False)
    assert advisors.main(["--project-ref", "ktvxijislbtgqapllmuk"]) == 1
