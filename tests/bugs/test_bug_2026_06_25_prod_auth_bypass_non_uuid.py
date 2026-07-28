"""BUG-2026-06-25 — F5 work-session persist 502 caused by prod auth bypass.

Production ran with ``DISABLE_AUTH=true`` and ``ADMIN_USER_ID=dev-user-12345``.
``verify_supabase_token`` bypassed auth and returned the non-UUID dev user id,
which PostgREST rejected on insert.

F21 / ADR-031 (S023 / EV-017): DISABLE_AUTH dual path and operator Auth removed.
Historical assertions live in git history; module skipped for ci-prepush.
"""

from __future__ import annotations

import pytest

pytest.skip(
    "F21/ADR-031: operator Auth / DISABLE_AUTH dual path removed — bug N/A",
    allow_module_level=True,
)
