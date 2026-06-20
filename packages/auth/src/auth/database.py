"""Compatibility wrapper for auth.database imports."""

from __future__ import annotations

import importlib
import sys

import database as _database

# True when importlib.reload(auth.database) re-executes this module.
_is_reload = hasattr(sys.modules.get(__name__), "DATABASE_URL")


def _bind_database_module(db_module: object) -> None:
    global DATABASE_URL, engine, SessionLocal, Base, _ensure_models_imported, __all__
    DATABASE_URL = db_module.DATABASE_URL
    engine = db_module.engine
    SessionLocal = db_module.SessionLocal
    Base = db_module.Base
    _ensure_models_imported = db_module._ensure_models_imported
    __all__ = getattr(db_module, "__all__", [])


def _reload_database_and_models() -> None:
    global _database
    _database = importlib.reload(_database)
    import models

    importlib.reload(models)
    _database._ensure_models_imported()
    _bind_database_module(_database)


def init_db():
    _ensure_models_imported()
    Base.metadata.create_all(bind=engine)


if _is_reload:
    _reload_database_and_models()
else:
    _bind_database_module(_database)
    _database._ensure_models_imported()
