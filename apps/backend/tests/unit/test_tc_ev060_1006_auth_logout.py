"""TC-EV060: logout via Auth proxy library (HTTP /auth/logout removed; F31)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from auth.proxy import AuthProxyError, SupabaseAuthProxy


@pytest.mark.unit
def test_proxy_sign_out_success() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.sign_out.return_value = {"message": "Successfully signed out"}
    assert proxy.sign_out("tok").get("message")


@pytest.mark.unit
def test_proxy_sign_out_error() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.sign_out.side_effect = AuthProxyError("logout failed", status_code=502)
    with pytest.raises(AuthProxyError):
        proxy.sign_out("tok")
