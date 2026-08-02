"""T5.1 / T5.2 — Snapshot checks for expand-cutover migration to tac_work_sessions."""

from pathlib import Path

# apps/backend/tests/unit → repo root (CI runs pytest with cwd=apps/backend)
_REPO_ROOT = Path(__file__).resolve().parents[4]
MIGRATION = _REPO_ROOT / "supabase/migrations/20260714000010_tac_work_sessions.sql"


def test_tac_work_sessions_migration_exists() -> None:
    assert MIGRATION.is_file(), f"missing expand-cutover migration at {MIGRATION}"


def test_tac_work_sessions_migration_expand_cutover() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS public.tac_work_sessions" in sql
    assert "product TEXT NOT NULL" in sql
    assert "tac_work_sessions_one_wip_per_user" in sql
    assert "INSERT INTO public.tac_work_sessions" in sql
    assert "FROM public.metar_work_sessions" in sql
    assert "DROP TABLE IF EXISTS public.metar_work_sessions" in sql
    assert "ENABLE ROW LEVEL SECURITY" in sql
    # ADR-020 / ADR-021: owner-only RLS (no admin browse USING clause)
    assert "public.is_admin()" not in sql
    assert "purge_stale_tac_work_sessions" in sql
    for product in ("metar", "speci", "taf", "sigmet", "airmet", "vaa", "tca"):
        assert product in sql


def test_tac_work_sessions_swxa_product_migration() -> None:
    """F28 / T11.5 — CHECK constraint expanded for product=swxa."""
    migration = _REPO_ROOT / "supabase/migrations/20260802000011_tac_work_sessions_swxa.sql"
    assert migration.is_file(), f"missing SWXA product migration at {migration}"
    sql = migration.read_text(encoding="utf-8")
    assert "swxa" in sql
    assert "tac_work_sessions_product_check" in sql
