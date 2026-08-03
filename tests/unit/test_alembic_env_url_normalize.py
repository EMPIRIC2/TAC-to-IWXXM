"""Unit tests for Alembic DATABASE_URL normalization (asyncpg → psycopg)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_ENV_PY = (
    Path(__file__).resolve().parents[2] / "apps" / "backend" / "alembic" / "env.py"
)


def _load_normalize():
    """Load ``_normalize_sync_url`` without running Alembic online migrations."""
    spec = importlib.util.spec_from_file_location("alembic_env_under_test", _ENV_PY)
    assert spec is not None and spec.loader is not None
    # Avoid executing module top-level (would connect). Import by compiling helpers only.
    source = _ENV_PY.read_text(encoding="utf-8")
    ns: dict = {}
    # Execute only the helper function definition block via isolated eval of the file
    # after stubbing alembic/sqlalchemy side effects — simpler: exec file with stubs.
    import sys
    import types

    alembic_mod = types.ModuleType("alembic")
    alembic_context = types.ModuleType("alembic.context")
    alembic_context.config = types.SimpleNamespace(
        config_file_name=None,
        config_ini_section="alembic",
        get_main_option=lambda *_a, **_k: "",
        get_section=lambda *_a, **_k: {},
    )
    alembic_mod.context = alembic_context
    sys.modules["alembic"] = alembic_mod
    sys.modules["alembic.context"] = alembic_context

    # Prevent online migrate at import
    patched = source.replace(
        "if context.is_offline_mode():\n    run_migrations_offline()\nelse:\n    run_migrations_online()\n",
        "\n",
    )
    exec(compile(patched, str(_ENV_PY), "exec"), ns)
    return ns["_normalize_sync_url"]


@pytest.mark.unit
def test_normalize_asyncpg_ssl_to_psycopg_sslmode() -> None:
    normalize = _load_normalize()
    out = normalize("postgresql+asyncpg://u:p@host:25060/db?ssl=require")
    assert out.startswith("postgresql+psycopg://")
    assert "sslmode=require" in out
    assert "ssl=require" not in out


@pytest.mark.unit
def test_normalize_plain_postgresql() -> None:
    normalize = _load_normalize()
    out = normalize("postgresql://u:p@host/db")
    assert out == "postgresql+psycopg://u:p@host/db"
