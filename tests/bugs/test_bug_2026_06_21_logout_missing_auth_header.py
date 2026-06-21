"""BUG-2026-06-21 — production logout fails: signOutWithScope omits Bearer token.

User report: console "Logout failed:" (empty statusText) on every logout click in
production. POST /auth/logout requires Authorization: Bearer per api-contract.md;
signOutWithScope in apps/frontend must send the stored access token.
"""

from __future__ import annotations

import pathlib
import sys

from fastapi.testclient import TestClient

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "apps" / "backend"
FRONTEND_LOGOUT = (
    REPO_ROOT / "apps" / "frontend" / "src" / "utils" / "supabase" / "logout.ts"
)

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.api import app  # noqa: E402


def test_auth_logout_requires_bearer_token() -> None:
    """POST /auth/logout without Authorization returns 401 (api-contract)."""
    client = TestClient(app)
    response = client.post("/auth/logout", json={"scope": "local"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authorization header"


def test_sign_out_with_scope_sends_bearer_token() -> None:
    """Frontend scoped logout must attach Authorization like authService.logout()."""
    source = FRONTEND_LOGOUT.read_text(encoding="utf-8")
    assert "Authorization" in source, (
        "signOutWithScope must send Authorization: Bearer <access_token> — "
        "POST /auth/logout rejects unauthenticated requests (401)"
    )
    assert "getAccessToken" in source or "access_token" in source, (
        "signOutWithScope must read the stored access token before calling /auth/logout"
    )
