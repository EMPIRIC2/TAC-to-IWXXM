"""T2.1 / TC-EV031-002 — Alembic layout under apps/backend (F30 / ADR-033).

Structural checks always run. Live empty→head + second upgrade idempotency lives in
``tests/integration/test_alembic_upgrade_idempotent.py``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND = _REPO_ROOT / "apps" / "backend"
_ALEMBIC_INI = _BACKEND / "alembic.ini"
_ALEMBIC_DIR = _BACKEND / "alembic"
_VERSIONS = _ALEMBIC_DIR / "versions"

REQUIRED_SESSION_COLUMNS = frozenset(
    {
        "id",
        "user_id",
        "product",
        "status",
        "title",
        "manual_tac",
        "pending_files",
        "converted_results",
        "errors",
        "issues",
        "conversion_params",
        "kv_upload_key",
        "deleted_at",
        "created_at",
        "updated_at",
    }
)

REQUIRED_PRODUCTS = frozenset(
    {"airmet", "metar", "sigmet", "speci", "taf", "vaa", "tca", "swxa"}
)


@pytest.mark.unit
def test_alembic_ini_and_env_exist() -> None:
    assert _ALEMBIC_INI.is_file(), f"missing {_ALEMBIC_INI}"
    assert (_ALEMBIC_DIR / "env.py").is_file(), "missing alembic/env.py"
    assert _VERSIONS.is_dir(), "missing alembic/versions/"


@pytest.mark.unit
def test_alembic_has_at_least_one_revision() -> None:
    revs = sorted(_VERSIONS.glob("*.py"))
    revs = [p for p in revs if p.name != "__init__.py"]
    assert revs, "expected at least one Alembic revision under alembic/versions/"


@pytest.mark.unit
def test_initial_revision_defines_tac_work_sessions_and_f8_tables() -> None:
    """ADR-020 wire shapes + F8 co-located tables (ADR-033 single DATABASE_URL)."""
    bodies = "\n".join(
        p.read_text(encoding="utf-8")
        for p in sorted(_VERSIONS.glob("*.py"))
        if p.name != "__init__.py"
    )
    assert "tac_work_sessions" in bodies
    assert "iwxxm_ingest_results" in bodies
    assert "iwxxm_ingest_quarantine" in bodies
    for col in REQUIRED_SESSION_COLUMNS:
        assert col in bodies, f"revision body missing column token {col!r}"
    for product in REQUIRED_PRODUCTS:
        assert product in bodies, f"revision body missing product {product!r}"
    # DO Postgres: no Supabase Auth user FK (Auth-only Supabase — ADR-033).
    assert "REFERENCES auth.users" not in bodies
    assert 'ForeignKey("auth.users' not in bodies
    assert "ForeignKey('auth.users" not in bodies
