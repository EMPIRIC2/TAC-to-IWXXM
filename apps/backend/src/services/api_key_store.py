"""Hashed API key storage on DO Postgres (NFR-007 / D-029 / TP3)."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import MetaData, Table, create_engine, insert, select, update
from sqlalchemy.engine import Engine

_KEY_PREFIX = "t2i_"
_PREFIX_LEN = 12
_TOKEN_BYTES = 32
_engine: Engine | None = None
_keys_table: Table | None = None
_metadata = MetaData()


def _sync_database_url() -> str | None:
    """
    Normalize ``DATABASE_URL`` for sync SQLAlchemy, or None when unset.

    Returns
    -------
    str or None
        Sync URL, or None when product DB is unavailable.
    """
    raw = (os.environ.get("DATABASE_URL") or "").strip()
    if not raw:
        return None
    if raw.startswith("postgresql+asyncpg://"):
        url = "postgresql+psycopg://" + raw.removeprefix("postgresql+asyncpg://")
    elif raw.startswith("postgresql+psycopg2://"):
        url = "postgresql+psycopg://" + raw.removeprefix("postgresql+psycopg2://")
    elif raw.startswith("postgresql://"):
        url = "postgresql+psycopg://" + raw.removeprefix("postgresql://")
    else:
        url = raw
    if "ssl=require" in url and "sslmode=" not in url:
        url = url.replace("ssl=require", "sslmode=require")
    return url


def _get_engine() -> Engine | None:
    """
    Lazy process-wide engine, or None when ``DATABASE_URL`` is unset.

    Returns
    -------
    Engine or None
        Shared engine.
    """
    global _engine
    url = _sync_database_url()
    if url is None:
        return None
    if _engine is None:
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def _table() -> Table:
    """
    Reflect ``api_keys`` once.

    Returns
    -------
    Table
        SQLAlchemy table.
    """
    global _keys_table
    if _keys_table is None:
        engine = _get_engine()
        if engine is None:
            msg = "DATABASE_URL required for api_keys table"
            raise RuntimeError(msg)
        _keys_table = Table("api_keys", _metadata, autoload_with=engine)
    return _keys_table


def reset_api_key_store_for_tests() -> None:
    """
    Clear cached engine/table (unit tests).
    """
    global _engine, _keys_table
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _keys_table = None
    _metadata.clear()


def hash_api_key(plaintext: str) -> str:
    """
    Hash an API key for storage or lookup.

    Parameters
    ----------
    plaintext : str
        Raw key from the client.

    Returns
    -------
    str
        Hex SHA-256 digest (optionally HMAC-peppered).
    """
    pepper = (os.environ.get("API_KEY_PEPPER") or "").encode("utf-8")
    raw = plaintext.encode("utf-8")
    if pepper:
        return hmac.new(pepper, raw, hashlib.sha256).hexdigest()
    return hashlib.sha256(raw).hexdigest()


def generate_api_key_plaintext() -> tuple[str, str]:
    """
    Mint a new plaintext key and its display prefix.

    Returns
    -------
    tuple of str
        ``(plaintext, prefix)``.
    """
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    plaintext = f"{_KEY_PREFIX}{token}"
    prefix = plaintext[:_PREFIX_LEN]
    return plaintext, prefix


@dataclass(frozen=True, slots=True)
class IssuedApiKey:
    """One-time issue payload (plaintext returned once)."""

    id: UUID
    prefix: str
    api_key: str
    label: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class VerifiedApiKey:
    """Resolved key identity after successful auth."""

    id: str
    prefix: str
    source: str  # "demo" | "db"


def api_key_required_enabled() -> bool:
    """
    Whether middleware must reject missing/invalid keys.

    Returns
    -------
    bool
        True when enforcement is on (default).
    """
    raw = (os.environ.get("API_KEY_REQUIRED") or "true").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def demo_api_key() -> str:
    """
    Server-configured demo key (A-007), or empty when unset.

    Returns
    -------
    str
        Demo plaintext, possibly empty.
    """
    return (os.environ.get("DEMO_API_KEY") or "").strip()


def verify_plaintext_key(plaintext: str) -> VerifiedApiKey | None:
    """
    Accept demo env key or a non-revoked hashed DB row.

    Parameters
    ----------
    plaintext : str
        Client ``X-API-Key`` value.

    Returns
    -------
    VerifiedApiKey or None
        Identity when valid.
    """
    key = plaintext.strip()
    if not key:
        return None
    demo = demo_api_key()
    if demo and hmac.compare_digest(key, demo):
        return VerifiedApiKey(id="demo", prefix=key[:_PREFIX_LEN], source="demo")

    engine = _get_engine()
    if engine is None:
        return None
    digest = hash_api_key(key)
    try:
        table = _table()
        with engine.begin() as conn:
            row = conn.execute(
                select(table.c.id, table.c.key_prefix, table.c.revoked_at).where(table.c.key_hash == digest)
            ).one_or_none()
            if row is None:
                return None
            if row.revoked_at is not None:
                return None
            conn.execute(update(table).where(table.c.id == row.id).values(last_used_at=datetime.now(UTC)))
            return VerifiedApiKey(
                id=str(row.id),
                prefix=str(row.key_prefix),
                source="db",
            )
    except Exception:
        # Fail closed as invalid when product DB is unreachable.
        return None


def issue_api_key(*, label: str = "") -> IssuedApiKey:
    """
    Create a hashed key row and return plaintext once.

    Parameters
    ----------
    label : str, optional
        Operator label (max 128).

    Returns
    -------
    IssuedApiKey
        Issue payload.

    Raises
    ------
    RuntimeError
        When ``DATABASE_URL`` is unset.
    ValueError
        When label is invalid.
    """
    cleaned = (label or "").strip()
    if len(cleaned) > 128:
        msg = "label must be at most 128 characters"
        raise ValueError(msg)
    engine = _get_engine()
    if engine is None:
        msg = "DATABASE_URL required to issue API keys"
        raise RuntimeError(msg)
    plaintext, prefix = generate_api_key_plaintext()
    digest = hash_api_key(plaintext)
    table = _table()
    with engine.begin() as conn:
        row = conn.execute(
            insert(table)
            .values(key_prefix=prefix, key_hash=digest, label=cleaned)
            .returning(table.c.id, table.c.created_at)
        ).one()
    return IssuedApiKey(
        id=row.id,
        prefix=prefix,
        api_key=plaintext,
        label=cleaned,
        created_at=row.created_at,
    )


def revoke_api_key(*, key_id: UUID, plaintext: str) -> bool:
    """
    Soft-revoke a key when the caller presents matching plaintext.

    Parameters
    ----------
    key_id : UUID
        Row id.
    plaintext : str
        Caller ``X-API-Key``.

    Returns
    -------
    bool
        True when the key matched and is now revoked (including already revoked).
    """
    key = plaintext.strip()
    if not key:
        return False
    engine = _get_engine()
    if engine is None:
        return False
    digest = hash_api_key(key)
    table = _table()
    # Support UUID columns (Postgres) and text ids (sqlite unit tests).
    id_value: UUID | str = key_id
    with engine.begin() as conn:
        row = conn.execute(
            select(table.c.id, table.c.revoked_at).where(
                table.c.id == id_value,
                table.c.key_hash == digest,
            )
        ).one_or_none()
        if row is None and str(key_id) != key_id:
            row = conn.execute(
                select(table.c.id, table.c.revoked_at).where(
                    table.c.id == str(key_id),
                    table.c.key_hash == digest,
                )
            ).one_or_none()
            id_value = str(key_id)
        if row is None:
            return False
        if row.revoked_at is None:
            conn.execute(update(table).where(table.c.id == id_value).values(revoked_at=datetime.now(UTC)))
        return True


def issued_to_dict(issued: IssuedApiKey) -> dict[str, Any]:
    """
    JSON-shape for issue response.

    Parameters
    ----------
    issued : IssuedApiKey
        Issue payload.

    Returns
    -------
    dict
        Response body.
    """
    return {
        "id": str(issued.id),
        "prefix": issued.prefix,
        "api_key": issued.api_key,
        "label": issued.label,
        "created_at": issued.created_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
    }
