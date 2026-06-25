"""BUG-2026-06-25 — Docker Compose backend cannot create DB tables (#671).

The local-dev Docker Compose stack shipped no database and passed an empty
``DATABASE_URL=${DATABASE_URL:-}`` to the backend. An empty string is falsy in
Python, so ``get_database_url`` fell back to
``postgresql+asyncpg://postgres:@localhost:5432/postgres`` — but nothing listens
on ``localhost:5432`` inside the backend container, so startup logged::

    Failed to create database tables: Multiple exceptions:
    [Errno 111] Connect call failed ('127.0.0.1', 5432)

Two defects are guarded here:

1. ``get_database_url`` must treat a blank / whitespace-only ``DATABASE_URL``
   (or ``SUPABASE_DB_URL``) as unset and emit an actionable warning — never
   return the blank value as a connection URL.
2. ``docker-compose.yml`` must bundle a Postgres ``db`` service and default the
   backend ``DATABASE_URL`` to it (non-empty, not ``localhost``), gated on the
   DB being healthy.
"""

from __future__ import annotations

import pathlib
import sys

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.services import database as db  # noqa: E402

COMPOSE = ROOT / "docker-compose.yml"

# The hotfix locks the bundled Postgres service to this name; the backend's
# default DATABASE_URL and depends_on both reference it by name (#671).
DB_SERVICE = "db"


# --- Defect 1: get_database_url env normalization -----------------------------


@pytest.mark.parametrize("blank", ["", "   ", "\t", "\n"])
def test_blank_database_url_is_treated_as_unset(monkeypatch, blank) -> None:
    """A blank/whitespace ``DATABASE_URL`` must never be returned as a URL."""
    monkeypatch.setenv("DATABASE_URL", blank)
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    monkeypatch.delenv("POSTGRES_HOST", raising=False)

    url = db.get_database_url()

    # Must fall back to the component-built default, not the blank value.
    assert url.strip() != ""
    assert url.strip() != blank.strip()
    assert url.startswith("postgresql+asyncpg://")


def test_blank_database_url_emits_actionable_warning(monkeypatch, caplog) -> None:
    """When ``DATABASE_URL`` is set but blank, warn naming the variable."""
    monkeypatch.setenv("DATABASE_URL", "   ")
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)

    with caplog.at_level("WARNING"):
        db.get_database_url()

    assert "DATABASE_URL" in caplog.text


# --- Defect 2: docker-compose bundles a database ------------------------------


def _compose() -> dict:
    return yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))


def _db_service(services: dict) -> dict:
    """Return the bundled ``db`` service, asserting its name and image contract.

    The fix for #671 commits to a service literally named ``db`` (referenced by
    the backend's default ``DATABASE_URL`` and ``depends_on``). Asserting the
    name explicitly — rather than inferring it from a ``"postgres"`` substring —
    makes the contract clear and failures easy to interpret if it is renamed.
    """
    svc = services.get(DB_SERVICE)
    assert svc is not None, (
        f"docker-compose.yml defines no '{DB_SERVICE}' service — the backend has "
        "no database to connect to (root cause of #671)."
    )
    image = str(svc.get("image", ""))
    assert "postgres" in image.lower(), (
        f"the '{DB_SERVICE}' service must run a Postgres image, got {image!r} (#671)."
    )
    return svc


def _env_value(env, key: str) -> str | None:
    """Return the value for ``key`` from a list- or dict-style compose env block."""
    if isinstance(env, dict):
        return None if env.get(key) is None else str(env[key])
    for item in env or []:
        name, _, value = str(item).partition("=")
        if name == key:
            return value
    return None


def test_compose_defines_postgres_service() -> None:
    services = _compose()["services"]
    svc = _db_service(services)
    assert svc.get("healthcheck"), "bundled Postgres service must define a healthcheck"


def test_backend_database_url_defaults_to_bundled_db() -> None:
    services = _compose()["services"]
    _db_service(services)  # asserts the bundled 'db' Postgres service exists
    backend_url = _env_value(services["backend"].get("environment"), "DATABASE_URL")

    assert backend_url is not None, "backend must receive a DATABASE_URL env var"
    # Must not default to an empty string (the #671 footgun) or localhost.
    assert backend_url not in ("${DATABASE_URL:-}", ""), (
        "backend DATABASE_URL defaults to an empty string — falls back to "
        "localhost:5432 where no Postgres listens (#671)."
    )
    assert "localhost" not in backend_url and "127.0.0.1" not in backend_url
    assert DB_SERVICE in backend_url, (
        f"backend DATABASE_URL default must point at the bundled '{DB_SERVICE}' service"
    )


def test_backend_depends_on_db_health() -> None:
    services = _compose()["services"]
    _db_service(services)  # asserts the bundled 'db' Postgres service exists
    depends = services["backend"].get("depends_on", {})

    assert DB_SERVICE in depends, "backend must depend_on the bundled Postgres service"
    if isinstance(depends, dict):
        assert depends[DB_SERVICE].get("condition") == "service_healthy", (
            "backend must wait for the DB to be service_healthy before starting"
        )
