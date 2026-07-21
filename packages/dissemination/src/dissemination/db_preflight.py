"""DB sink preflight orchestration (allowlist + writer-contract)."""

from __future__ import annotations

from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from dissemination.allowlist import EgressDenied, load_allowlist_from_env, validate_egress_host
from dissemination.models import PreflightRequest, PreflightResponse, SchemaDiffItem
from dissemination.redact import redact_secrets
from dissemination.writer_contract import (
    apply_writer_contract,
    diff_writer_contract,
)


def uri_hostname(uri: str) -> str | None:
    """Return hostname from ``uri``, or ``None`` for hostless schemes (e.g. sqlite memory)."""
    parsed = urlparse(uri)
    return parsed.hostname


def dialect_for_sink(sink_type: str) -> str:
    mapping = {
        "postgres": "postgresql",
        "mysql": "mysql",
        "sqlserver": "mssql",
        "sqlite": "sqlite",
    }
    if sink_type not in mapping:
        raise ValueError(f"sink_type {sink_type!r} is not a DB sink")
    return mapping[sink_type]


def normalize_sqlalchemy_uri(uri: str, sink_type: str) -> str:
    """Ensure async driver prefix for SQLAlchemy."""
    if sink_type == "postgres" and uri.startswith("postgresql://"):
        return "postgresql+asyncpg://" + uri.removeprefix("postgresql://")
    if sink_type == "mysql" and uri.startswith("mysql://"):
        return "mysql+aiomysql://" + uri.removeprefix("mysql://")
    if sink_type == "sqlite" and uri.startswith("sqlite://"):
        return "sqlite+aiosqlite://" + uri.removeprefix("sqlite://")
    return uri


async def run_db_preflight(req: PreflightRequest) -> PreflightResponse:
    """
    Validate egress + optional writer-contract against a DB URI.

    Raises
    ------
    EgressDenied
        When allowlist/SSRF checks fail.
    ValueError
        When the request is incomplete or unsupported.
    """
    if not req.uri:
        raise ValueError("uri is required for DB sink preflight")

    host = uri_hostname(req.uri)
    if host:
        validate_egress_host(host, allowlist=load_allowlist_from_env())

    dialect = dialect_for_sink(req.sink_type)
    sa_uri = normalize_sqlalchemy_uri(req.uri, req.sink_type)
    engine: AsyncEngine = create_async_engine(sa_uri)
    try:
        if req.ddl:
            await apply_writer_contract(engine, dialect=dialect)
        diffs_raw = await diff_writer_contract(engine, dialect=dialect)
        diffs = [
            SchemaDiffItem(
                kind=str(d.kind),
                table=d.table,
                detail=d.detail,
                column=d.column,
            )
            for d in diffs_raw
        ]
        ok = len(diffs) == 0
        return PreflightResponse(
            ok=ok,
            connectivity_ok=True,
            diffs=diffs,
            detail=None if ok else "writer-contract mismatches",
        )
    except Exception as exc:
        raise ValueError(redact_secrets(str(exc))) from exc
    finally:
        await engine.dispose()


# Re-export for callers that catch allowlist failures.
__all__ = [
    "EgressDenied",
    "dialect_for_sink",
    "normalize_sqlalchemy_uri",
    "run_db_preflight",
    "uri_hostname",
]
