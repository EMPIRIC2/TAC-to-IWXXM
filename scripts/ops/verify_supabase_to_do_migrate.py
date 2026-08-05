#!/usr/bin/env python3
"""Verify Supabase → DO product-table restore (T5.2 / TC-EV031-001).

Compares **row counts** and a **sample SHA-256 checksum** between a legacy source
Postgres (Supabase product DB) and the DigitalOcean target (``DATABASE_URL``).

Usage::

    uv run python scripts/ops/verify_supabase_to_do_migrate.py \\
      --source-url \"$MIGRATE_SOURCE_DATABASE_URL\" \\
      --target-url \"$DATABASE_URL\"

Env fallbacks: ``MIGRATE_SOURCE_DATABASE_URL`` / ``SUPABASE_DB_URL`` (source),
``MIGRATE_TARGET_DATABASE_URL`` / ``DATABASE_URL`` (target).

Exit codes: ``0`` all tables match; ``1`` mismatch or usage error; ``2`` DB error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

PRODUCT_TABLES: tuple[str, ...] = (
    "tac_work_sessions",
    "iwxxm_ingest_results",
    "iwxxm_ingest_quarantine",
)

# Columns included in the sample fingerprint (stable ops map — T5.1).
CHECKSUM_COLUMNS: Mapping[str, tuple[str, ...]] = {
    "tac_work_sessions": (
        "id",
        "user_id",
        "product",
        "status",
        "title",
        "manual_tac",
        "deleted_at",
        "updated_at",
    ),
    "iwxxm_ingest_results": (
        "id",
        "job_id",
        "product",
        "profile",
        "source_url",
        "tac_input",
        "stage_failed",
        "created_at",
    ),
    "iwxxm_ingest_quarantine": (
        "id",
        "job_id",
        "product",
        "profile",
        "source_url",
        "tac_input",
        "stage_failed",
        "created_at",
    ),
}

DEFAULT_SAMPLE_SIZE = 100


@dataclass(frozen=True)
class TableSnapshot:
    """Row-count + sample checksum for one product table."""

    table: str
    row_count: int
    sample_checksum: str


@dataclass(frozen=True)
class TableDiff:
    """Comparison result for one table."""

    table: str
    ok: bool
    source_row_count: int
    target_row_count: int
    source_checksum: str
    target_checksum: str
    reasons: tuple[str, ...]


def normalize_database_url(url: str) -> str:
    """
    Rewrite Postgres URLs to the sync ``psycopg`` SQLAlchemy dialect.

    Parameters
    ----------
    url : str
        Raw database URL (asyncpg / plain / psycopg2 / psycopg).

    Returns
    -------
    str
        URL suitable for ``create_engine`` with ``postgresql+psycopg``.
    """
    raw = url.strip()
    if raw.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgresql+asyncpg://")
    if raw.startswith("postgresql+psycopg2://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgresql+psycopg2://")
    if raw.startswith("postgresql://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgresql://")
    return raw


def _canon(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.hex()
    return str(value)


def row_fingerprint(columns: Sequence[str], values: Sequence[object]) -> str:
    """
    SHA-256 fingerprint for one ordered row.

    Parameters
    ----------
    columns : Sequence[str]
        Column names (must align with ``values``).
    values : Sequence[object]
        Cell values in the same order as ``columns``.

    Returns
    -------
    str
        Hex digest.
    """
    if len(columns) != len(values):
        msg = f"column/value length mismatch: {len(columns)} vs {len(values)}"
        raise ValueError(msg)
    parts = [f"{col}={_canon(val)}" for col, val in zip(columns, values, strict=True)]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def sample_checksum(
    rows: Sequence[Sequence[object]],
    columns: Sequence[str],
    *,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
) -> str:
    """
    Order rows by ``id`` (first column), take up to ``sample_size``, hash fingerprints.

    Parameters
    ----------
    rows : Sequence[Sequence[object]]
        Row tuples; first element must be the primary ``id``.
    columns : Sequence[str]
        Column names for each row.
    sample_size : int
        Max rows included in the sample (default 100).

    Returns
    -------
    str
        Hex digest over ordered row fingerprints (empty sample → empty-string digest).
    """
    if sample_size < 1:
        msg = "sample_size must be >= 1"
        raise ValueError(msg)
    ordered = sorted(rows, key=lambda r: _canon(r[0]))
    sample = ordered[:sample_size]
    digests = [row_fingerprint(columns, row) for row in sample]
    payload = "\n".join(digests).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def compare_snapshots(source: TableSnapshot, target: TableSnapshot) -> TableDiff:
    """
    Compare source vs target snapshots for one table.

    Parameters
    ----------
    source : TableSnapshot
        Legacy Supabase (or dry-run source) snapshot.
    target : TableSnapshot
        DigitalOcean restore snapshot.

    Returns
    -------
    TableDiff
        ``ok`` True when row counts and sample checksums match.
    """
    if source.table != target.table:
        msg = f"table name mismatch: {source.table!r} vs {target.table!r}"
        raise ValueError(msg)
    reasons: list[str] = []
    if source.row_count != target.row_count:
        reasons.append("row_count")
    if source.sample_checksum != target.sample_checksum:
        reasons.append("sample_checksum")
    return TableDiff(
        table=source.table,
        ok=not reasons,
        source_row_count=source.row_count,
        target_row_count=target.row_count,
        source_checksum=source.sample_checksum,
        target_checksum=target.sample_checksum,
        reasons=tuple(reasons),
    )


def report_ok(diffs: Sequence[TableDiff]) -> bool:
    """Return True when every table diff is ok."""
    return all(d.ok for d in diffs)


def _quote_ident(name: str) -> str:
    if not name.replace("_", "").isalnum():
        msg = f"refusing unsafe identifier: {name!r}"
        raise ValueError(msg)
    return f'"{name}"'


def fetch_table_snapshot(
    engine: Engine,
    table: str,
    *,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
) -> TableSnapshot:
    """
    Load row count + sample checksum for ``table`` from ``engine``.

    Parameters
    ----------
    engine : Engine
        Sync SQLAlchemy engine.
    table : str
        Product table name.
    sample_size : int
        Sample window for checksum.

    Returns
    -------
    TableSnapshot
        Snapshot for comparison.
    """
    columns = CHECKSUM_COLUMNS[table]
    col_sql = ", ".join(_quote_ident(c) for c in columns)
    table_sql = _quote_ident(table)
    with engine.connect() as conn:
        count = int(
            conn.execute(text(f"SELECT COUNT(*) FROM {table_sql}")).scalar_one()
        )
        result = conn.execute(
            text(
                f"SELECT {col_sql} FROM {table_sql} "
                f"ORDER BY {_quote_ident('id')}::text "
                f"LIMIT :lim"
            ),
            {"lim": sample_size},
        )
        rows = [tuple(row) for row in result.fetchall()]
    return TableSnapshot(
        table=table,
        row_count=count,
        sample_checksum=sample_checksum(rows, columns, sample_size=sample_size),
    )


def verify_urls(
    source_url: str,
    target_url: str,
    *,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    tables: Sequence[str] = PRODUCT_TABLES,
) -> list[TableDiff]:
    """
    Connect to both databases and compare product tables.

    Parameters
    ----------
    source_url : str
        Legacy Supabase Postgres URL.
    target_url : str
        DigitalOcean ``DATABASE_URL``.
    sample_size : int
        Checksum sample size.
    tables : Sequence[str]
        Tables to verify (default: product map).

    Returns
    -------
    list[TableDiff]
        Per-table diffs.
    """
    source_engine = create_engine(
        normalize_database_url(source_url), pool_pre_ping=True
    )
    target_engine = create_engine(
        normalize_database_url(target_url), pool_pre_ping=True
    )
    diffs: list[TableDiff] = []
    try:
        for table in tables:
            if table not in CHECKSUM_COLUMNS:
                msg = f"unknown product table: {table}"
                raise ValueError(msg)
            source = fetch_table_snapshot(source_engine, table, sample_size=sample_size)
            target = fetch_table_snapshot(target_engine, table, sample_size=sample_size)
            diffs.append(compare_snapshots(source, target))
    finally:
        source_engine.dispose()
        target_engine.dispose()
    return diffs


def _resolve_url(cli_value: str | None, env_keys: Sequence[str]) -> str:
    if cli_value and cli_value.strip():
        return cli_value.strip()
    for key in env_keys:
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return ""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify Supabase → DO product restore (row counts + sample checksum). "
            "TC-EV031-001 / T5.2."
        )
    )
    parser.add_argument(
        "--source-url",
        default=None,
        help="Legacy Supabase Postgres URL (or MIGRATE_SOURCE_DATABASE_URL / SUPABASE_DB_URL)",
    )
    parser.add_argument(
        "--target-url",
        default=None,
        help="DO Postgres URL (or MIGRATE_TARGET_DATABASE_URL / DATABASE_URL)",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help=f"Rows included in sample checksum (default {DEFAULT_SAMPLE_SIZE})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON report on stdout",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint. Returns process exit code."""
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    source = _resolve_url(
        args.source_url,
        ("MIGRATE_SOURCE_DATABASE_URL", "SUPABASE_DB_URL"),
    )
    target = _resolve_url(
        args.target_url,
        ("MIGRATE_TARGET_DATABASE_URL", "DATABASE_URL"),
    )
    if not source or not target:
        print(
            "error: need --source-url (or MIGRATE_SOURCE_DATABASE_URL/SUPABASE_DB_URL) "
            "and --target-url (or MIGRATE_TARGET_DATABASE_URL/DATABASE_URL)",
            file=sys.stderr,
        )
        return 1
    if args.sample_size < 1:
        print("error: --sample-size must be >= 1", file=sys.stderr)
        return 1

    try:
        diffs = verify_urls(source, target, sample_size=args.sample_size)
    except Exception as exc:
        print(f"error: database verify failed: {exc}", file=sys.stderr)
        return 2

    ok = report_ok(diffs)
    payload: dict[str, Any] = {
        "ok": ok,
        "sample_size": args.sample_size,
        "tables": [asdict(d) for d in diffs],
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for diff in diffs:
            status = "OK" if diff.ok else "FAIL"
            print(
                f"[{status}] {diff.table}: "
                f"rows {diff.source_row_count}→{diff.target_row_count} "
                f"checksum {diff.source_checksum[:12]}…→{diff.target_checksum[:12]}…"
                + (f" reasons={list(diff.reasons)}" if diff.reasons else "")
            )
        print("VERIFY PASS" if ok else "VERIFY FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
