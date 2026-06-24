"""Snapshot test for metar_work_sessions migration SQL."""

from pathlib import Path


def test_metar_work_sessions_migration_contains_rls_and_wip_index() -> None:
    migration = Path(
        "supabase/migrations/20250623000007_metar_work_sessions.sql"
    ).read_text()
    assert "CREATE TABLE IF NOT EXISTS public.metar_work_sessions" in migration
    assert "metar_work_sessions_one_wip_per_user" in migration
    assert "ENABLE ROW LEVEL SECURITY" in migration
    assert "purge_stale_metar_work_sessions" in migration
    assert "status IN ('draft', 'wip', 'finished', 'failed')" in migration
