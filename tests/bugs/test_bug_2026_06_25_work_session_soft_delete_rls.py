"""BUG-2026-06-25 - work-session soft-delete 502 (RLS 42501).

PostgreSQL enforces a SELECT policy's USING expression as an implicit WITH CHECK
on UPDATE. The original ``metar_work_sessions_select_own`` policy required
``deleted_at IS NULL``, so setting ``deleted_at`` (soft-delete) produced a row
that failed SELECT and the UPDATE was rejected (42501).

Fix: SELECT policy is scoped to ownership only; ``deleted_at`` filtering happens
in the app/query layer. Migration ``20250625000008_metar_work_sessions_softdelete_rls.sql``.
"""

from __future__ import annotations

import os
import pathlib
import re

import pytest

MIGRATIONS = pathlib.Path(__file__).resolve().parents[2] / "supabase" / "migrations"
SOFT_DELETE_MIGRATION = (
    MIGRATIONS / "20250625000008_metar_work_sessions_softdelete_rls.sql"
)


def _select_policy_body(sql: str) -> str | None:
    """Return the body of the most recent SELECT policy on metar_work_sessions."""
    pattern = re.compile(
        r"CREATE POLICY\s+metar_work_sessions_select_own.*?FOR\s+SELECT.*?USING\s*\((.*?)\);",
        re.IGNORECASE | re.DOTALL,
    )
    matches = pattern.findall(sql)
    return matches[-1] if matches else None


def test_softdelete_migration_exists() -> None:
    assert SOFT_DELETE_MIGRATION.is_file(), "soft-delete RLS fix migration missing"


def test_select_policy_does_not_gate_on_deleted_at() -> None:
    """The SELECT policy must not require deleted_at IS NULL (that blocks soft-delete UPDATE)."""
    body = _select_policy_body(SOFT_DELETE_MIGRATION.read_text(encoding="utf-8"))
    assert body is not None, "SELECT policy not found in soft-delete migration"
    assert "deleted_at" not in body.lower(), (
        "SELECT policy USING must not reference deleted_at - it is enforced as a "
        "WITH CHECK on UPDATE and blocks soft-delete (BUG-2026-06-25)"
    )


@pytest.mark.skipif(
    not (
        (os.environ.get("E2E_USER_EMAIL") or os.environ.get("ADMIN_EMAIL"))
        and (os.environ.get("E2E_USER_PASSWORD") or os.environ.get("ADMIN_PASSWORD"))
    ),
    reason="E2E_USER_EMAIL/E2E_USER_PASSWORD required for live soft-delete/restore check",
)
def test_live_soft_delete_and_restore_round_trip() -> None:
    """Live: create -> soft-delete (200) -> restore (200) against the deployed API."""
    import httpx

    base = os.environ.get(
        "LIVE_API_URL", "https://metar-to-iwxxm-api.onrender.com"
    ).rstrip("/")
    email = os.environ.get("E2E_USER_EMAIL") or os.environ["ADMIN_EMAIL"]
    password = os.environ.get("E2E_USER_PASSWORD") or os.environ["ADMIN_PASSWORD"]
    login = httpx.post(
        f"{base}/auth/login",
        json={
            "email": email,
            "password": password,
        },
        timeout=30.0,
    )
    if login.status_code != 200:
        pytest.skip(f"login failed: {login.status_code}")
    payload = login.json()
    token = (payload.get("session") or {}).get("access_token") or payload.get(
        "access_token"
    )
    headers = {"Authorization": f"Bearer {token}"}

    created = httpx.post(
        f"{base}/api/v1/work-sessions",
        json={"manual_tac": "RLS ROUNDTRIP", "product": "METAR"},
        headers=headers,
        timeout=30.0,
    )
    if created.status_code == 503:
        pytest.skip(f"work-sessions unavailable on live API: {created.text[:200]}")
    assert created.status_code == 201, created.text
    sid = created.json()["id"]
    try:
        deleted = httpx.request(
            "DELETE",
            f"{base}/api/v1/work-sessions/{sid}",
            headers=headers,
            timeout=30.0,
        )
        assert deleted.status_code == 200, (
            f"soft-delete failed: {deleted.status_code} {deleted.text}"
        )
        restored = httpx.post(
            f"{base}/api/v1/work-sessions/{sid}/restore", headers=headers, timeout=30.0
        )
        assert restored.status_code == 200, (
            f"restore failed: {restored.status_code} {restored.text}"
        )
    finally:
        httpx.request(
            "DELETE",
            f"{base}/api/v1/work-sessions/{sid}",
            headers=headers,
            timeout=30.0,
        )
