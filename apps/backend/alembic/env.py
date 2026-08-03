"""Alembic environment — targets ``DATABASE_URL`` (DigitalOcean Postgres / CI)."""

from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


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
    if not raw or raw.startswith("driver://"):
        msg = "DATABASE_URL (or ALEMBIC_DATABASE_URL) must be set for alembic"
        raise RuntimeError(msg)
    if raw.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgresql+asyncpg://")
    if raw.startswith("postgresql+psycopg2://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgresql+psycopg2://")
    if raw.startswith("postgresql://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgresql://")
    return raw


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
