"""Compatibility wrapper for auth.database imports."""

import importlib

import database as _database

# Reload to honor env overrides in tests that reload auth.database.
_database = importlib.reload(_database)

DATABASE_URL = _database.DATABASE_URL
engine = _database.engine
SessionLocal = _database.SessionLocal
Base = _database.Base
_ensure_models_imported = _database._ensure_models_imported


def init_db():
    _ensure_models_imported()
    Base.metadata.create_all(bind=engine)


__all__ = getattr(_database, "__all__", [])
