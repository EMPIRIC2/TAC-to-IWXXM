"""TC: registration is FE-direct; Auth proxy remains available as a library (F31)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from metar_auth.proxy import AuthProxyError, SupabaseAuthProxy


@pytest.mark.unit
def test_proxy_sign_up_success() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.sign_up.return_value = {
        "user": {"id": "1", "email": "a@b.com", "metadata": {}},
        "session": None,
    }
    result = proxy.sign_up("a@b.com", "Password1")
    assert result["user"]["email"] == "a@b.com"
    proxy.sign_up.assert_called_once()


@pytest.mark.unit
def test_proxy_sign_up_maps_error() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.sign_up.side_effect = AuthProxyError("registration failed", status_code=400)
    with pytest.raises(AuthProxyError):
        proxy.sign_up("a@b.com", "Password1")
