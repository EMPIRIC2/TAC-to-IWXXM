"""Connectivity gate H0c — CORS policy unit tests.

Validates ``METAR_CORS_ORIGINS`` parsing contract via ``metar_shared``.
In-process CORSMiddleware tests against ``apps/backend`` follow in T5.4.

See docs/test-plan.md §Connectivity and docs/deploy.md §Runbook.
"""

from __future__ import annotations

import os

import pytest

from metar_shared import METAR_CORS_ORIGINS_ENV, parse_comma_separated_origins


@pytest.mark.unit
class TestMetarCorsOriginsPolicy:
    """H0c — METAR_CORS_ORIGINS env contract."""

    def test_env_constant_matches_deploy_spec(self) -> None:
        assert METAR_CORS_ORIGINS_ENV == "METAR_CORS_ORIGINS"

    def test_parse_single_origin(self) -> None:
        assert parse_comma_separated_origins("https://app.example.com") == [
            "https://app.example.com"
        ]

    def test_parse_multiple_with_whitespace(self) -> None:
        raw = "https://a.example.com, https://b.example.com ,https://c.example.com"
        assert parse_comma_separated_origins(raw) == [
            "https://a.example.com",
            "https://b.example.com",
            "https://c.example.com",
        ]

    def test_parse_empty_returns_empty_list(self) -> None:
        assert parse_comma_separated_origins("") == []
        assert parse_comma_separated_origins("   ") == []
        assert parse_comma_separated_origins(None) == []

    def test_staging_origin_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When set, METAR_CORS_ORIGINS must be parseable for API CORS middleware."""
        monkeypatch.setenv(
            METAR_CORS_ORIGINS_ENV, "https://staging-frontend.onrender.com"
        )
        assert os.environ[METAR_CORS_ORIGINS_ENV] == "https://staging-frontend.onrender.com"
        assert parse_comma_separated_origins(os.environ[METAR_CORS_ORIGINS_ENV]) == [
            "https://staging-frontend.onrender.com"
        ]

    @pytest.mark.skip(reason="Awaiting apps/backend CORS middleware wiring (T5.4)")
    def test_backend_cors_middleware_uses_metar_cors_origins(self) -> None:
        """Import apps.backend and assert CORSMiddleware allow_origins from env."""
        pytest.importorskip("apps.backend")
