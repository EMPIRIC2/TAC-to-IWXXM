"""BUG-2026-06-21 - production logout fails: signOutWithScope omits Bearer token.

User report: console "Logout failed:" (empty statusText) on every logout click in
production. POST /auth/logout requires Authorization: Bearer per api-contract.md;
signOutWithScope in apps/frontend must send the stored access token.

F21 / ADR-031 (S023 / EV-017): operator Auth routes and logout UX removed.
Historical assertions live in git history; module skipped for ci-prepush.
"""

from __future__ import annotations

import pytest

pytest.skip(
    "F21/ADR-031: operator Auth / DISABLE_AUTH dual path removed - bug N/A",
    allow_module_level=True,
)
