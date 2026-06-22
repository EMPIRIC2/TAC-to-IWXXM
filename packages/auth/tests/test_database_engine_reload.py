"""Tests for database engine branches via importlib.reload."""

from __future__ import annotations

import builtins
import importlib
import os
from unittest import mock

import pytest

_DEFAULT_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")


def _reload_database(url: str) -> object:
    """Reload the top-level database module with a new DATABASE_URL."""
    with mock.patch.dict(os.environ, {"DATABASE_URL": url}, clear=False):
        import database

        return importlib.reload(database)


def _restore_database() -> None:
    _reload_database(_DEFAULT_URL)


@pytest.fixture(autouse=True)
def _restore_database_after_test() -> None:
    yield
    _restore_database()


class TestDatabaseEngineReload:
    def test_sqlite_engine_branch(self) -> None:
        mod = _reload_database("sqlite:///:memory:")
        assert "sqlite" in str(mod.engine.url)
        mod.engine.dispose()

    def test_postgres_standard_engine(self) -> None:
        mod = _reload_database("postgresql://user:pass@localhost:5432/testdb")
        assert mod.engine.pool is not None
        mod.engine.dispose()

    def test_postgres_with_sslmode_in_url(self) -> None:
        mod = _reload_database("postgresql://user:pass@localhost:5432/testdb?sslmode=disable")
        assert mod.engine.pool is not None
        mod.engine.dispose()

    def test_supabase_transaction_pooler_engine(self) -> None:
        url = "postgresql://user:pass@db.pooler.supabase.com:6543/postgres"
        mod = _reload_database(url)
        assert mod.engine.pool is not None
        mod.engine.dispose()

    def test_supabase_session_pooler_engine(self) -> None:
        url = "postgresql://user:pass@db.pooler.supabase.com:5432/postgres"
        mod = _reload_database(url)
        assert mod.engine.pool is not None
        mod.engine.dispose()

    def test_init_db_runs_without_error(self) -> None:
        mod = _reload_database("sqlite:///:memory:")
        mod.init_db()
        mod.engine.dispose()

    def test_dotenv_import_error_is_handled(self) -> None:
        real_import = builtins.__import__

        def import_hook(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "dotenv":
                raise ImportError("dotenv unavailable")
            return real_import(name, globals, locals, fromlist, level)

        with mock.patch("builtins.__import__", import_hook):
            mod = _reload_database("sqlite:///:memory:")
            assert mod.DATABASE_URL.startswith("sqlite")
            mod.engine.dispose()

    def test_ensure_models_imported_when_models_missing(self) -> None:
        real_import = builtins.__import__

        def import_hook(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "models":
                raise ImportError("models unavailable")
            if name == "auth" and fromlist and "models" in fromlist:
                raise ImportError("auth.models unavailable")
            return real_import(name, globals, locals, fromlist, level)

        with mock.patch("builtins.__import__", import_hook):
            mod = _reload_database("sqlite:///:memory:")
            mod._ensure_models_imported()
            mod.engine.dispose()

    def test_ensure_models_imported_auth_models_fallback(self) -> None:
        mod = _reload_database("sqlite:///:memory:")
        mod._ensure_models_imported()
        mod.engine.dispose()
