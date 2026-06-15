"""M4 auth middleware unit tests — test-plan.md TC-M005 prep, ADR-002.

Exercises JWT header parsing and token utilities that migrate with packages/auth.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from tests.migration.auth_baseline import load_api_supabase_module, load_security_module


@pytest.mark.migration
class TestM4AuthMiddleware:
    """Auth library middleware behavior (legacy auth/ or packages/auth)."""

    def test_jwt_create_and_decode_roundtrip(self) -> None:
        security = load_security_module()
        token = security.create_access_token("user-123")
        assert isinstance(token, str)
        assert security.decode_access_token(token) == "user-123"

    def test_jwt_decode_rejects_invalid_token(self) -> None:
        security = load_security_module()
        assert security.decode_access_token("not-a-valid-jwt") is None

    def test_get_token_from_header_accepts_bearer(self) -> None:
        api_supabase = load_api_supabase_module()
        assert api_supabase.get_token_from_header("Bearer abc.def.ghi") == "abc.def.ghi"

    @pytest.mark.parametrize(
        "header_value",
        [None, "", "Token abc", "Bearer"],
    )
    def test_get_token_from_header_rejects_invalid(self, header_value: str | None) -> None:
        api_supabase = load_api_supabase_module()
        with pytest.raises(HTTPException) as exc_info:
            api_supabase.get_token_from_header(header_value)
        assert exc_info.value.status_code == 401

    def test_validate_email_permissive_accepts_dev_domain(self) -> None:
        api_supabase = load_api_supabase_module()
        assert api_supabase.validate_email_permissive("user@example.test") == "user@example.test"

    def test_validate_email_permissive_rejects_malformed(self) -> None:
        api_supabase = load_api_supabase_module()
        with pytest.raises(ValueError, match="Invalid email"):
            api_supabase.validate_email_permissive("not-an-email")
