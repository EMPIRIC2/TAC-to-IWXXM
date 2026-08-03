"""Alembic environment — targets ``DATABASE_URL`` (DigitalOcean Postgres / CI)."""

from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _normalize_sync_url(raw: str) -> str:
    """
    Rewrite async/driver URL to sync ``postgresql+psycopg`` and SSL query params.

    Parameters
    ----------
    raw : str
        Runtime ``DATABASE_URL`` (often ``postgresql+asyncpg://…?ssl=require``).

    Returns
    -------
    str
        Sync SQLAlchemy URL safe for Alembic / psycopg.
    """
    url = raw
    if url.startswith("postgresql+asyncpg://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql+asyncpg://")
    elif url.startswith("postgresql+psycopg2://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql+psycopg2://")
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql://")
    # asyncpg uses ``ssl=require``; psycopg expects ``sslmode=require``.
    if "ssl=require" in url and "sslmode=" not in url:
        url = url.replace("ssl=require", "sslmode=require")
    return url


def _database_url() -> str:
    """
    Resolve sync SQLAlchemy URL for migrations.

    Prefers ``DATABASE_URL`` / ``ALEMBIC_DATABASE_URL``. Rewrites asyncpg → psycopg.
    """
    raw = (
        os.environ.get("ALEMBIC_DATABASE_URL", "").strip()
        or os.environ.get("DATABASE_URL", "").strip()
        or config.get_main_option("sqlalchemy.url")
        or ""
    )
    if not raw or raw.startswith("driver://") or raw.startswith("REPLACE_ME"):
        msg = "DATABASE_URL (or ALEMBIC_DATABASE_URL) must be set for alembic"
        raise RuntimeError(msg)
    return _normalize_sync_url(raw)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = _database_url()
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
