"""Assert writer-contract rows after live F16 dissemination send (EV-039 / AC2).

Playwright invokes this module via ``python -m dissemination.live_write_assert``
after UI success (S05.M3 - async drivers in-package; no FastAPI imports).

[Corpus: product §F16] [Corpus: tests] TC-F16-LIVE [Corpus: adr/ADR-030]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from dissemination.db_preflight import dialect_for_sink, normalize_sqlalchemy_uri
from dissemination.writer_contract import CONTRACT_TABLE


async def count_iwxxm_rows(
    engine: AsyncEngine,
    *,
    upload_key: str | None = None,
) -> int:
    """
    Return the number of rows in ``iwxxm_reports`` (optionally filtered by upload_key).

    Parameters
    ----------
    engine :
        Async SQLAlchemy engine pointed at the destination DB.
    upload_key :
        When set, count only rows with this ``upload_key``.

    Returns
    -------
    int
        Matching row count.
    """
    if upload_key:
        sql = text(f"SELECT COUNT(*) FROM {CONTRACT_TABLE} WHERE upload_key = :upload_key")
        params: dict[str, Any] = {"upload_key": upload_key}
    else:
        sql = text(f"SELECT COUNT(*) FROM {CONTRACT_TABLE}")
        params = {}
    async with engine.connect() as conn:
        result = await conn.execute(sql, params)
        return int(result.scalar_one())


async def assert_live_write(
    *,
    sink_type: str,
    uri: str,
    upload_key: str | None = None,
    min_rows: int = 1,
) -> int:
    """
    Assert at least ``min_rows`` writer-contract rows exist after a live send.

    Parameters
    ----------
    sink_type :
        ``postgres`` / ``mysql`` / ``sqlserver`` / ``sqlite``.
    uri :
        Destination URI (sync or async driver prefix accepted).
    upload_key :
        Optional ``kv_upload_key`` from the send response.
    min_rows :
        Minimum expected row count (default 1).

    Returns
    -------
    int
        Actual row count.

    Raises
    ------
    AssertionError
        When fewer than ``min_rows`` matching rows are present.
    ValueError
        When ``sink_type`` is not a DB sink.
    """
    dialect = dialect_for_sink(sink_type)
    sa_uri = normalize_sqlalchemy_uri(uri, sink_type)
    engine = create_async_engine(sa_uri)
    try:
        count = await count_iwxxm_rows(engine, upload_key=upload_key)
    finally:
        await engine.dispose()

    if count < min_rows:
        raise AssertionError(
            f"expected ≥{min_rows} row(s) in {CONTRACT_TABLE} ({dialect})"
            + (f" with upload_key={upload_key!r}" if upload_key else "")
            + f"; found {count}"
        )
    return count


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m dissemination.live_write_assert",
        description="Assert iwxxm_reports rows after F16 live Disseminate (EV-039).",
    )
    parser.add_argument("--sink-type", required=True, choices=("postgres", "mysql", "sqlserver", "sqlite"))
    parser.add_argument("--uri", required=True, help="Destination DB URI")
    parser.add_argument("--upload-key", default=None, help="Optional kv_upload_key filter")
    parser.add_argument("--min-rows", type=int, default=1)
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry - exit 0 on success, 1 on assertion failure, 2 on usage/error."""
    args = _build_parser().parse_args(argv)
    try:
        count = asyncio.run(
            assert_live_write(
                sink_type=args.sink_type,
                uri=args.uri,
                upload_key=args.upload_key,
                min_rows=args.min_rows,
            )
        )
    except AssertionError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, "count": count}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
