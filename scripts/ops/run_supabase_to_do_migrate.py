#!/usr/bin/env python3
"""Run Supabase → DO product-table migrate (T5.3 / TC-EV031-001).

Copies legacy product rows via SQLAlchemy ``SELECT`` + idempotent
``INSERT … ON CONFLICT (id) DO NOTHING`` (SQL export path). Optional
``pg_dump``/``pg_restore`` when ``--use-pg-dump`` and client tools exist.

Usage::

    # Plan only (default) — no writes
    uv run python scripts/ops/run_supabase_to_do_migrate.py \\
      --source-url \"$MIGRATE_SOURCE_DATABASE_URL\" \\
      --target-url \"$MIGRATE_TARGET_DATABASE_URL\" \\
      --mode dry-run

    # Apply cut (idempotent)
    uv run python scripts/ops/run_supabase_to_do_migrate.py \\
      --source-url \"$MIGRATE_SOURCE_DATABASE_URL\" \\
      --target-url \"$MIGRATE_TARGET_DATABASE_URL\" \\
      --mode apply

Env fallbacks: ``MIGRATE_SOURCE_DATABASE_URL`` / ``SUPABASE_DB_URL`` (source),
``MIGRATE_TARGET_DATABASE_URL`` / ``DATABASE_URL`` (target).

Exit codes: ``0`` success; ``1`` usage / plan failure; ``2`` DB error.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.ops.verify_supabase_to_do_migrate import (  # noqa: E402
    PRODUCT_TABLES,
    normalize_database_url,
    verify_urls,
)

MigrateMode = Literal["dry-run", "apply"]

# Full column sets for T5.1 map / Alembic ``20260803_0001`` (copy as-is).
COPY_COLUMNS: Mapping[str, tuple[str, ...]] = {
    "tac_work_sessions": (
        "id",
        "user_id",
        "product",
        "status",
        "title",
        "manual_tac",
        "pending_files",
        "converted_results",
        "errors",
        "issues",
        "conversion_params",
        "kv_upload_key",
        "deleted_at",
        "created_at",
        "updated_at",
    ),
    "iwxxm_ingest_results": (
        "id",
        "job_id",
        "product",
        "profile",
        "source_url",
        "tac_input",
        "iwxxm_xml",
        "issues",
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
        "iwxxm_xml",
        "issues",
        "stage_failed",
        "created_at",
    ),
}

DEFAULT_BATCH_SIZE = 500


@dataclass(frozen=True)
class TableMigratePlan:
    """Per-table migrate plan / result."""

    table: str
    source_row_count: int
    target_row_count_before: int
    missing_on_target: int
    inserted: int
    mode: str


def _quote_ident(name: str) -> str:
    if not name.replace("_", "").isalnum():
        msg = f"refusing unsafe identifier: {name!r}"
        raise ValueError(msg)
    return f'"{name}"'


def _resolve_url(cli_value: str | None, env_keys: Sequence[str]) -> str:
    if cli_value and cli_value.strip():
        return cli_value.strip()
    for key in env_keys:
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return ""


def _strip_sqlalchemy_dialect(url: str) -> str:
    """Return a libpq-compatible URL (no ``+psycopg`` / ``+asyncpg``)."""
    raw = url.strip()
    for prefix in (
        "postgresql+psycopg://",
        "postgresql+psycopg2://",
        "postgresql+asyncpg://",
    ):
        if raw.startswith(prefix):
            return "postgresql://" + raw.removeprefix(prefix)
    return raw


def urls_are_same_database(source_url: str, target_url: str) -> bool:
    """
    Return True when source and target resolve to the same host/db/user.

    Used as a safety guard — refuse migrate when both point at the same DB
    (common when ``DATABASE_URL`` is still the legacy Supabase pooler).

    Parameters
    ----------
    source_url : str
        Legacy source URL.
    target_url : str
        Target URL.

    Returns
    -------
    bool
        True when the normalized endpoints match.
    """
    a = normalize_database_url(source_url)
    b = normalize_database_url(target_url)

    # Compare without password: dialect://user:***@host/db
    def _endpoint(url: str) -> str:
        if "://" not in url:
            return url
        scheme, rest = url.split("://", 1)
        if "@" not in rest:
            return f"{scheme}://{rest}"
        cred, hostpart = rest.split("@", 1)
        user = cred.split(":", 1)[0]
        return f"{scheme}://{user}@{hostpart}"

    return _endpoint(a) == _endpoint(b)


def fetch_row_count(conn: Connection, table: str) -> int:
    """Return ``COUNT(*)`` for ``table``."""
    table_sql = _quote_ident(table)
    return int(conn.execute(text(f"SELECT COUNT(*) FROM {table_sql}")).scalar_one())


def fetch_missing_count(source: Connection, target: Connection, table: str) -> int:
    """
    Count source rows whose ``id`` is absent on target.

    Parameters
    ----------
    source : Connection
        Source DB connection.
    target : Connection
        Target DB connection.
    table : str
        Product table name.

    Returns
    -------
    int
        Number of source ids not present on target.
    """
    table_sql = _quote_ident(table)
    source_ids = {
        str(row[0])
        for row in source.execute(text(f"SELECT id FROM {table_sql}")).fetchall()
    }
    if not source_ids:
        return 0
    target_ids = {
        str(row[0])
        for row in target.execute(text(f"SELECT id FROM {table_sql}")).fetchall()
    }
    return len(source_ids - target_ids)


def build_insert_sql(table: str, columns: Sequence[str]) -> str:
    """
    Build idempotent INSERT SQL for one product table.

    Parameters
    ----------
    table : str
        Table name.
    columns : Sequence[str]
        Column list (must include ``id``).

    Returns
    -------
    str
        Parameterized ``INSERT … ON CONFLICT (id) DO NOTHING`` statement.
    """
    if "id" not in columns:
        msg = f"{table}: COPY_COLUMNS must include id"
        raise ValueError(msg)
    cols_sql = ", ".join(_quote_ident(c) for c in columns)
    binds = ", ".join(f":{c}" for c in columns)
    table_sql = _quote_ident(table)
    return (
        f"INSERT INTO {table_sql} ({cols_sql}) VALUES ({binds}) "
        f"ON CONFLICT ({_quote_ident('id')}) DO NOTHING"
    )


def copy_table_rows(
    source: Connection,
    target: Connection,
    table: str,
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    apply: bool,
) -> tuple[int, int, int, int]:
    """
    Plan or copy one table from source → target.

    Parameters
    ----------
    source : Connection
        Source connection.
    target : Connection
        Target connection.
    table : str
        Product table.
    batch_size : int
        Rows per INSERT batch when applying.
    apply : bool
        When False, do not write; only compute plan counts.

    Returns
    -------
    tuple[int, int, int, int]
        ``(source_count, target_before, missing, inserted)``.
    """
    columns = COPY_COLUMNS[table]
    col_sql = ", ".join(_quote_ident(c) for c in columns)
    table_sql = _quote_ident(table)
    source_count = fetch_row_count(source, table)
    target_before = fetch_row_count(target, table)
    missing = fetch_missing_count(source, target, table)
    if not apply or missing == 0:
        return source_count, target_before, missing, 0

    insert_sql = text(build_insert_sql(table, columns))
    result = source.execute(
        text(f"SELECT {col_sql} FROM {table_sql} ORDER BY {_quote_ident('id')}::text")
    )
    inserted = 0
    batch: list[dict[str, Any]] = []
    for row in result:
        batch.append(dict(zip(columns, tuple(row), strict=True)))
        if len(batch) >= batch_size:
            target.execute(insert_sql, batch)
            inserted += len(batch)
            batch.clear()
    if batch:
        target.execute(insert_sql, batch)
        inserted += len(batch)
    return source_count, target_before, missing, inserted


def migrate_sqlalchemy(
    source_url: str,
    target_url: str,
    *,
    mode: MigrateMode,
    tables: Sequence[str] = PRODUCT_TABLES,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[TableMigratePlan]:
    """
    Migrate product tables via SQLAlchemy (SQL export path).

    Parameters
    ----------
    source_url : str
        Legacy Supabase Postgres URL.
    target_url : str
        DigitalOcean ``DATABASE_URL``.
    mode : {"dry-run", "apply"}
        ``dry-run`` plans only; ``apply`` inserts missing rows.
    tables : Sequence[str]
        Tables to migrate (default product map).
    batch_size : int
        INSERT batch size.

    Returns
    -------
    list[TableMigratePlan]
        Per-table results.

    Raises
    ------
    ValueError
        If URLs point at the same database or an unknown table is requested.
    """
    if urls_are_same_database(source_url, target_url):
        msg = (
            "source and target URLs resolve to the same database; "
            "set MIGRATE_TARGET_DATABASE_URL / DATABASE_URL to DigitalOcean Postgres"
        )
        raise ValueError(msg)

    apply = mode == "apply"
    source_engine = create_engine(
        normalize_database_url(source_url), pool_pre_ping=True
    )
    target_engine = create_engine(
        normalize_database_url(target_url), pool_pre_ping=True
    )
    plans: list[TableMigratePlan] = []
    try:
        with source_engine.connect() as source_conn:
            target_ctx = target_engine.begin() if apply else target_engine.connect()
            with target_ctx as target_conn:
                for table in tables:
                    if table not in COPY_COLUMNS:
                        msg = f"unknown product table: {table}"
                        raise ValueError(msg)
                    src_n, tgt_n, missing, inserted = copy_table_rows(
                        source_conn,
                        target_conn,
                        table,
                        batch_size=batch_size,
                        apply=apply,
                    )
                    plans.append(
                        TableMigratePlan(
                            table=table,
                            source_row_count=src_n,
                            target_row_count_before=tgt_n,
                            missing_on_target=missing,
                            inserted=inserted if apply else 0,
                            mode=mode,
                        )
                    )
    finally:
        source_engine.dispose()
        target_engine.dispose()
    return plans


def _pg_client_available() -> bool:
    return (
        shutil.which("pg_dump") is not None and shutil.which("pg_restore") is not None
    )


def migrate_pg_dump(
    source_url: str,
    target_url: str,
    *,
    mode: MigrateMode,
    tables: Sequence[str] = PRODUCT_TABLES,
) -> list[TableMigratePlan]:
    """
    Migrate via ``pg_dump --data-only`` + ``pg_restore`` (optional path).

    Parameters
    ----------
    source_url : str
        Legacy source URL.
    target_url : str
        Target URL.
    mode : {"dry-run", "apply"}
        ``dry-run`` dumps to a temp file and reports sizes only.
    tables : Sequence[str]
        Tables to include.

    Returns
    -------
    list[TableMigratePlan]
        Approximate plan (row counts from SQLAlchemy; dump is side artifact).

    Raises
    ------
    RuntimeError
        If ``pg_dump`` / ``pg_restore`` are missing.
    ValueError
        If URLs point at the same database.
    """
    if not _pg_client_available():
        msg = "pg_dump/pg_restore not found on PATH (install libpq / Brewfile)"
        raise RuntimeError(msg)
    if urls_are_same_database(source_url, target_url):
        msg = (
            "source and target URLs resolve to the same database; "
            "set MIGRATE_TARGET_DATABASE_URL / DATABASE_URL to DigitalOcean Postgres"
        )
        raise ValueError(msg)

    # Plan counts always via SQLAlchemy (accurate missing ids).
    plans = migrate_sqlalchemy(source_url, target_url, mode="dry-run", tables=tables)
    if mode == "dry-run":
        return [
            TableMigratePlan(
                table=p.table,
                source_row_count=p.source_row_count,
                target_row_count_before=p.target_row_count_before,
                missing_on_target=p.missing_on_target,
                inserted=0,
                mode="dry-run-pg-dump",
            )
            for p in plans
        ]

    src = _strip_sqlalchemy_dialect(source_url)
    tgt = _strip_sqlalchemy_dialect(target_url)
    with tempfile.TemporaryDirectory(prefix="supabase-to-do-") as tmp:
        dump_path = Path(tmp) / "product.dump"
        dump_cmd = [
            "pg_dump",
            "--format=custom",
            "--data-only",
            "--no-owner",
            "--no-privileges",
            f"--dbname={src}",
            f"--file={dump_path}",
        ]
        for table in tables:
            dump_cmd.extend(["--table", table])
        subprocess.run(dump_cmd, check=True, capture_output=True, text=True)
        restore_cmd = [
            "pg_restore",
            "--data-only",
            "--no-owner",
            "--no-privileges",
            "--exit-on-error",
            f"--dbname={tgt}",
            str(dump_path),
        ]
        # Prefer continue-on-duplicate when available; custom format uses exit-on-error.
        # Idempotency for re-runs: fall back to SQLAlchemy path if restore fails on PK.
        try:
            subprocess.run(restore_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            # Fall back to idempotent SQL insert for missing rows.
            return migrate_sqlalchemy(
                source_url, target_url, mode="apply", tables=tables
            )

    # Refresh inserted estimates after restore.
    after = migrate_sqlalchemy(source_url, target_url, mode="dry-run", tables=tables)
    out: list[TableMigratePlan] = []
    for before, post in zip(plans, after, strict=True):
        out.append(
            TableMigratePlan(
                table=before.table,
                source_row_count=before.source_row_count,
                target_row_count_before=before.target_row_count_before,
                missing_on_target=before.missing_on_target,
                inserted=max(
                    0, post.target_row_count_before - before.target_row_count_before
                ),
                mode="apply-pg-dump",
            )
        )
    return out


def run_migrate(
    source_url: str,
    target_url: str,
    *,
    mode: MigrateMode,
    use_pg_dump: bool = False,
    verify_after: bool = False,
    tables: Sequence[str] = PRODUCT_TABLES,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> dict[str, Any]:
    """
    Execute migrate plan or apply and optionally verify.

    Parameters
    ----------
    source_url : str
        Source Postgres URL.
    target_url : str
        Target Postgres URL.
    mode : {"dry-run", "apply"}
        Execution mode.
    use_pg_dump : bool
        Prefer ``pg_dump``/``pg_restore`` when True.
    verify_after : bool
        Run T5.2 verify after apply (ignored for dry-run).
    tables : Sequence[str]
        Tables to migrate.
    batch_size : int
        SQLAlchemy batch size.

    Returns
    -------
    dict[str, Any]
        Machine-readable report.
    """
    if use_pg_dump:
        plans = migrate_pg_dump(source_url, target_url, mode=mode, tables=tables)
    else:
        plans = migrate_sqlalchemy(
            source_url,
            target_url,
            mode=mode,
            tables=tables,
            batch_size=batch_size,
        )

    report: dict[str, Any] = {
        "ok": True,
        "mode": mode,
        "use_pg_dump": use_pg_dump,
        "tables": [asdict(p) for p in plans],
        "verify": None,
    }
    if mode == "apply" and verify_after:
        diffs = verify_urls(source_url, target_url, tables=tables)
        report["verify"] = {
            "ok": all(d.ok for d in diffs),
            "tables": [asdict(d) for d in diffs],
        }
        report["ok"] = bool(report["verify"]["ok"])
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Migrate Supabase product tables → DO Postgres "
            "(dry-run then apply). TC-EV031-001 / T5.3."
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
        "--mode",
        choices=("dry-run", "apply"),
        default="dry-run",
        help="dry-run (default, no writes) or apply (idempotent INSERT)",
    )
    parser.add_argument(
        "--use-pg-dump",
        action="store_true",
        help="Use pg_dump/pg_restore when available (else SQLAlchemy path)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="After apply, run verify_supabase_to_do_migrate (row counts + checksum)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"SQLAlchemy INSERT batch size (default {DEFAULT_BATCH_SIZE})",
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
    if args.batch_size < 1:
        print("error: --batch-size must be >= 1", file=sys.stderr)
        return 1

    mode: MigrateMode = args.mode
    try:
        report = run_migrate(
            source,
            target,
            mode=mode,
            use_pg_dump=bool(args.use_pg_dump),
            verify_after=bool(args.verify),
            batch_size=args.batch_size,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: migrate failed: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, default=str))
    else:
        for row in report["tables"]:
            print(
                f"[{row['mode']}] {row['table']}: "
                f"source={row['source_row_count']} "
                f"target_before={row['target_row_count_before']} "
                f"missing={row['missing_on_target']} "
                f"inserted={row['inserted']}"
            )
        if report.get("verify") is not None:
            print(
                "VERIFY PASS" if report["verify"]["ok"] else "VERIFY FAIL",
            )
        print("MIGRATE PASS" if report["ok"] else "MIGRATE FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
