"""BUG-2026-06-24 — UserApprovalPanel hits Supabase directly with legacy browser key.

After login succeeds via merged API, admin User Approvals panel still queried
``user_profiles`` through the browser Supabase client (legacy anon JWT in
``config.json``), causing "Legacy API keys are disabled" when legacy keys are
off in Supabase.
"""

from __future__ import annotations

import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PANEL = REPO_ROOT / "apps/frontend/src/app/components/admin/UserApprovalPanel.tsx"


def test_user_approval_panel_does_not_import_browser_supabase_client() -> None:
    """Approval panel must use merged API /admin/*, not direct PostgREST."""
    source = PANEL.read_text(encoding="utf-8")
    assert "supabase" not in source.lower()
    assert "/admin/pending-users" in source or "adminUrl('/pending-users')" in source
    assert "/admin/approve-user" in source or "adminUrl('/approve-user')" in source
    assert "/admin/reject-user" in source or "adminUrl('/reject-user')" in source
