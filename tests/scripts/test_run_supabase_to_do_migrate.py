"""EV-080 coverage fills for scripts/ops/run_supabase_to_do_migrate.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import scripts.ops.run_supabase_to_do_migrate as migrate_mod
from scripts.ops.run_supabase_to_do_migrate import (
    TableMigratePlan,
    adapt_row_values,
    build_insert_sql,
    copy_table_rows,
    fetch_missing_count,
    fetch_row_count,
    main,
    migrate_pg_dump,
    migrate_sqlalchemy,
    run_migrate,
    urls_are_same_database,
)
from scripts.ops.verify_supabase_to_do_migrate import TableDiff


class _FakeResult:
    def __init__(
        self,
        *,
        scalar: Any = None,
        rows: list[tuple[Any, ...]] | None = None,
    ) -> None:
        self._scalar = scalar
        self._rows = rows or []

    def scalar_one(self) -> Any:
        return self._scalar

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self._rows

    def __iter__(self):
        return iter(self._rows)


class _FakeConn:
    def __init__(
        self,
        *,
        counts: dict[str, int],
        ids: dict[str, list[str]],
        full_rows: dict[str, list[tuple[Any, ...]]],
    ) -> None:
        self.counts = counts
        self.ids = ids
        self.full_rows = full_rows
        self.insert_batches: list[list[dict[str, Any]]] = []

    def execute(self, stmt: Any, params: Any = None) -> _FakeResult:
        sql = str(stmt)
        if "COUNT(*)" in sql:
            for table, count in self.counts.items():
                if f'"{table}"' in sql:
                    return _FakeResult(scalar=count)
            return _FakeResult(scalar=0)
        if "SELECT id FROM" in sql:
            for table, id_list in self.ids.items():
                if f'"{table}"' in sql:
                    return _FakeResult(rows=[(i,) for i in id_list])
            return _FakeResult(rows=[])
        if params is not None and isinstance(params, list):
            self.insert_batches.append(params)
            return _FakeResult()
        if "SELECT" in sql and "FROM" in sql:
            for table, data in self.full_rows.items():
                if f'"{table}"' in sql:
                    return _FakeResult(rows=data)
        return _FakeResult()


def test_quote_ident_rejects_unsafe() -> None:
    with pytest.raises(ValueError, match="unsafe identifier"):
        migrate_mod._quote_ident("bad;drop")


def test_resolve_url_and_strip_dialect() -> None:
    assert migrate_mod._resolve_url("  pg://a ", ("ENV",)) == "pg://a"
    with patch.dict("os.environ", {"ENV": "pg://env"}, clear=False):
        assert migrate_mod._resolve_url(None, ("ENV",)) == "pg://env"
    assert migrate_mod._resolve_url(None, ("MISSING",)) == ""
    assert (
        migrate_mod._strip_sqlalchemy_dialect("postgresql+psycopg://h")
        == "postgresql://h"
    )
    assert (
        migrate_mod._strip_sqlalchemy_dialect("postgresql+psycopg2://h")
        == "postgresql://h"
    )
    assert (
        migrate_mod._strip_sqlalchemy_dialect("postgresql+asyncpg://h")
        == "postgresql://h"
    )
    assert migrate_mod._strip_sqlalchemy_dialect("postgresql://h") == "postgresql://h"


def test_urls_are_same_database_edge_cases() -> None:
    assert urls_are_same_database("noscheme", "noscheme") is True
    assert (
        urls_are_same_database("postgresql://host/db", "postgresql://host/db") is True
    )


def test_fetch_row_count_and_missing() -> None:
    conn = _FakeConn(
        counts={"tac_work_sessions": 3},
        ids={},
        full_rows={},
    )
    assert fetch_row_count(conn, "tac_work_sessions") == 3  # type: ignore[arg-type]
    source = _FakeConn(
        counts={},
        ids={"tac_work_sessions": ["a", "b"]},
        full_rows={},
    )
    target = _FakeConn(
        counts={},
        ids={"tac_work_sessions": ["a"]},
        full_rows={},
    )
    assert fetch_missing_count(source, target, "tac_work_sessions") == 1  # type: ignore[arg-type]
    empty = _FakeConn(counts={}, ids={"tac_work_sessions": []}, full_rows={})
    assert fetch_missing_count(empty, empty, "tac_work_sessions") == 0  # type: ignore[arg-type]


def test_adapt_row_values_non_jsonb_and_null() -> None:
    adapted = adapt_row_values(
        "tac_work_sessions", {"id": "x", "title": "t", "pending_files": None}
    )
    assert adapted["pending_files"] is None
    assert adapted["title"] == "t"


def test_copy_table_rows_dry_run_and_apply_batches() -> None:
    columns = migrate_mod.COPY_COLUMNS["tac_work_sessions"]
    row = tuple(f"v{i}" for i in range(len(columns)))
    source = _FakeConn(
        counts={"tac_work_sessions": 3},
        ids={"tac_work_sessions": ["1", "2", "3"]},
        full_rows={"tac_work_sessions": [row, row, row]},
    )
    target = _FakeConn(
        counts={"tac_work_sessions": 0},
        ids={"tac_work_sessions": []},
        full_rows={},
    )
    src_n, tgt_n, missing, inserted = copy_table_rows(
        source,
        target,
        "tac_work_sessions",
        batch_size=2,
        apply=False,  # type: ignore[arg-type]
    )
    assert (src_n, tgt_n, missing, inserted) == (3, 0, 3, 0)
    src_n, tgt_n, missing, inserted = copy_table_rows(
        source,
        target,
        "tac_work_sessions",
        batch_size=2,
        apply=True,  # type: ignore[arg-type]
    )
    assert inserted == 3
    assert len(target.insert_batches) == 2


def test_build_insert_sql_requires_id() -> None:
    with pytest.raises(ValueError, match="must include id"):
        build_insert_sql("tac_work_sessions", ("user_id", "product"))


def test_copy_table_rows_zero_missing_skips_insert() -> None:
    columns = migrate_mod.COPY_COLUMNS["tac_work_sessions"]
    row = tuple(f"v{i}" for i in range(len(columns)))
    source = _FakeConn(
        counts={"tac_work_sessions": 1},
        ids={"tac_work_sessions": ["1"]},
        full_rows={"tac_work_sessions": [row]},
    )
    target = _FakeConn(
        counts={"tac_work_sessions": 1},
        ids={"tac_work_sessions": ["1"]},
        full_rows={},
    )
    _, _, missing, inserted = copy_table_rows(
        source,
        target,
        "tac_work_sessions",
        batch_size=1,
        apply=True,  # type: ignore[arg-type]
    )
    assert missing == 0
    assert inserted == 0
    assert target.insert_batches == []


def test_migrate_pg_dump_same_database_raises() -> None:
    with (
        patch.object(migrate_mod, "_pg_client_available", return_value=True),
        pytest.raises(ValueError, match="same database"),
    ):
        migrate_pg_dump("postgresql://u@h/db", "postgresql://u@h/db", mode="dry-run")


def test_run_migrate_skips_verify_on_dry_run() -> None:
    plan = TableMigratePlan(
        table="tac_work_sessions",
        source_row_count=0,
        target_row_count_before=0,
        missing_on_target=0,
        inserted=0,
        mode="dry-run",
    )
    with patch.object(migrate_mod, "migrate_sqlalchemy", return_value=[plan]) as ms:
        report = run_migrate("s", "t", mode="dry-run", verify_after=True)
    assert report["verify"] is None
    ms.assert_called_once()


def test_copy_table_rows_exact_batch_multiple_no_final_flush() -> None:
    """When row count divides batch_size, final `if batch:` is false (343->346)."""
    columns = migrate_mod.COPY_COLUMNS["tac_work_sessions"]
    row = tuple(f"v{i}" for i in range(len(columns)))
    source = _FakeConn(
        counts={"tac_work_sessions": 2},
        ids={"tac_work_sessions": ["1", "2"]},
        full_rows={"tac_work_sessions": [row, row]},
    )
    target = _FakeConn(
        counts={"tac_work_sessions": 0},
        ids={"tac_work_sessions": []},
        full_rows={},
    )
    _, _, missing, inserted = copy_table_rows(
        source,
        target,
        "tac_work_sessions",
        batch_size=2,
        apply=True,  # type: ignore[arg-type]
    )
    assert missing == 2
    assert inserted == 2
    assert len(target.insert_batches) == 1


def test_module_inserts_repo_root_on_import() -> None:
    root = str(migrate_mod._REPO_ROOT)
    saved_path = sys.path.copy()
    saved_mod = sys.modules.get("scripts.ops.run_supabase_to_do_migrate")
    name = "ev080_run_migrate_reimport"
    sys.modules.pop(name, None)
    try:
        while root in sys.path:
            sys.path.remove(root)
        spec = importlib.util.spec_from_file_location(name, migrate_mod.__file__)
        assert spec is not None
        assert spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        assert root in sys.path
    finally:
        sys.path[:] = saved_path
        sys.modules.pop(name, None)
        if saved_mod is not None:
            sys.modules["scripts.ops.run_supabase_to_do_migrate"] = saved_mod


def test_copy_table_rows_single_row_final_batch() -> None:
    columns = migrate_mod.COPY_COLUMNS["iwxxm_ingest_results"]
    row = tuple(f"v{i}" for i in range(len(columns)))
    source = _FakeConn(
        counts={"iwxxm_ingest_results": 1},
        ids={"iwxxm_ingest_results": ["1"]},
        full_rows={"iwxxm_ingest_results": [row]},
    )
    target = _FakeConn(
        counts={"iwxxm_ingest_results": 0},
        ids={"iwxxm_ingest_results": []},
        full_rows={},
    )
    _, _, missing, inserted = copy_table_rows(
        source,
        target,
        "iwxxm_ingest_results",
        batch_size=5,
        apply=True,  # type: ignore[arg-type]
    )
    assert missing == 1
    assert inserted == 1
    assert len(target.insert_batches) == 1


def test_migrate_sqlalchemy_branches() -> None:
    with pytest.raises(ValueError, match="same database"):
        migrate_sqlalchemy("postgresql://u@h/db", "postgresql://u@h/db", mode="dry-run")

    plan = TableMigratePlan(
        table="tac_work_sessions",
        source_row_count=1,
        target_row_count_before=0,
        missing_on_target=1,
        inserted=0,
        mode="dry-run",
    )

    source_conn = MagicMock()
    target_conn = MagicMock()
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = source_conn
    engine.connect.return_value.__exit__.return_value = None
    engine.begin.return_value.__enter__.return_value = target_conn
    engine.begin.return_value.__exit__.return_value = None
    with (
        patch.object(migrate_mod, "create_engine", return_value=engine),
        patch.object(migrate_mod, "copy_table_rows", return_value=(1, 0, 1, 0)),
    ):
        plans = migrate_sqlalchemy(
            "postgresql://u@src/db",
            "postgresql://u@tgt/db",
            mode="dry-run",
            tables=("tac_work_sessions",),
        )
    assert plans == [plan]

    with (
        patch.object(migrate_mod, "create_engine", return_value=engine),
        patch.object(migrate_mod, "copy_table_rows", return_value=(1, 0, 1, 1)),
    ):
        apply_plans = migrate_sqlalchemy(
            "postgresql://u@src/db",
            "postgresql://u@tgt/db",
            mode="apply",
        )
    assert apply_plans[0].inserted == 1

    with (
        patch.object(migrate_mod, "create_engine", return_value=engine),
        pytest.raises(ValueError, match="unknown product table"),
    ):
        migrate_sqlalchemy(
            "postgresql://u@src/db",
            "postgresql://u@tgt/db",
            mode="dry-run",
            tables=("not_a_table",),
        )


def test_pg_client_and_migrate_pg_dump_paths() -> None:
    with patch.object(migrate_mod.shutil, "which", return_value=None):
        assert migrate_mod._pg_client_available() is False
        with pytest.raises(RuntimeError, match="pg_dump"):
            migrate_pg_dump("postgresql://s", "postgresql://t", mode="dry-run")

    with patch.object(migrate_mod.shutil, "which", return_value="/bin/pg"):
        assert migrate_mod._pg_client_available() is True

    dry_plan = [
        TableMigratePlan(
            table="tac_work_sessions",
            source_row_count=2,
            target_row_count_before=1,
            missing_on_target=1,
            inserted=0,
            mode="dry-run",
        )
    ]
    with (
        patch.object(migrate_mod, "_pg_client_available", return_value=True),
        patch.object(migrate_mod, "migrate_sqlalchemy", return_value=dry_plan) as ms,
    ):
        out = migrate_pg_dump("postgresql://s", "postgresql://t", mode="dry-run")
    assert out[0].mode == "dry-run-pg-dump"
    ms.assert_called_once()

    after_plan = [
        TableMigratePlan(
            table="tac_work_sessions",
            source_row_count=2,
            target_row_count_before=2,
            missing_on_target=0,
            inserted=0,
            mode="dry-run",
        )
    ]
    with (
        patch.object(migrate_mod, "_pg_client_available", return_value=True),
        patch.object(
            migrate_mod, "migrate_sqlalchemy", side_effect=[dry_plan, after_plan]
        ),
        patch.object(migrate_mod.subprocess, "run") as run,
    ):
        apply_out = migrate_pg_dump(
            "postgresql+psycopg://s/db",
            "postgresql+psycopg2://t/db",
            mode="apply",
        )
    assert run.call_count == 2
    assert apply_out[0].inserted == 1
    assert apply_out[0].mode == "apply-pg-dump"

    fallback_plan = [
        TableMigratePlan(
            table="tac_work_sessions",
            source_row_count=2,
            target_row_count_before=2,
            missing_on_target=0,
            inserted=1,
            mode="apply",
        )
    ]
    with (
        patch.object(migrate_mod, "_pg_client_available", return_value=True),
        patch.object(
            migrate_mod,
            "migrate_sqlalchemy",
            side_effect=[dry_plan, fallback_plan],
        ),
        patch.object(migrate_mod.subprocess, "run") as run,
    ):
        run.side_effect = [
            MagicMock(),
            subprocess.CalledProcessError(1, "pg_restore"),
        ]
        fb = migrate_pg_dump("postgresql://s", "postgresql://t", mode="apply")
    assert fb[0].inserted == 1


def test_run_migrate_verify_after() -> None:
    plan = TableMigratePlan(
        table="tac_work_sessions",
        source_row_count=1,
        target_row_count_before=1,
        missing_on_target=0,
        inserted=0,
        mode="apply",
    )
    ok_diff = TableDiff(
        table="tac_work_sessions",
        ok=True,
        source_row_count=1,
        target_row_count=1,
        source_checksum="a",
        target_checksum="a",
        reasons=(),
    )
    bad_diff = TableDiff(
        table="tac_work_sessions",
        ok=False,
        source_row_count=1,
        target_row_count=0,
        source_checksum="a",
        target_checksum="b",
        reasons=("row_count",),
    )
    with (
        patch.object(migrate_mod, "migrate_sqlalchemy", return_value=[plan]),
        patch.object(migrate_mod, "verify_urls", return_value=[ok_diff]),
    ):
        ok_report = run_migrate("s", "t", mode="apply", verify_after=True)
    assert ok_report["ok"] is True
    assert ok_report["verify"]["ok"] is True

    with (
        patch.object(migrate_mod, "migrate_pg_dump", return_value=[plan]),
        patch.object(migrate_mod, "verify_urls", return_value=[bad_diff]),
    ):
        bad_report = run_migrate(
            "s", "t", mode="apply", use_pg_dump=True, verify_after=True
        )
    assert bad_report["ok"] is False


def test_main_cli_paths(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 1
    assert main(["--batch-size", "0", "--source-url", "s", "--target-url", "t"]) == 1

    plan = TableMigratePlan(
        table="tac_work_sessions",
        source_row_count=1,
        target_row_count_before=0,
        missing_on_target=1,
        inserted=0,
        mode="dry-run",
    )
    with patch.object(
        migrate_mod, "run_migrate", return_value={"ok": True, "tables": [plan.__dict__]}
    ):
        assert main(["--source-url", "s", "--target-url", "t", "--json"]) == 0
    out = capsys.readouterr().out
    assert "tac_work_sessions" in out

    with patch.object(
        migrate_mod,
        "run_migrate",
        return_value={"ok": True, "tables": [plan.__dict__], "verify": {"ok": True}},
    ):
        assert main(["--source-url", "s", "--target-url", "t", "--verify"]) == 0
    text = capsys.readouterr().out
    assert "VERIFY PASS" in text
    assert "MIGRATE PASS" in text

    with patch.object(migrate_mod, "run_migrate", side_effect=ValueError("bad urls")):
        assert main(["--source-url", "s", "--target-url", "t"]) == 1
    assert "bad urls" in capsys.readouterr().err

    with patch.object(migrate_mod, "run_migrate", side_effect=RuntimeError("db down")):
        assert main(["--source-url", "s", "--target-url", "t"]) == 2

    fail_plan = {**plan.__dict__, "inserted": 0}
    with patch.object(
        migrate_mod,
        "run_migrate",
        return_value={"ok": False, "tables": [fail_plan], "verify": {"ok": False}},
    ):
        assert main(["--source-url", "s", "--target-url", "t"]) == 1
    fail_text = capsys.readouterr().out
    assert "VERIFY FAIL" in fail_text
    assert "MIGRATE FAIL" in fail_text

    with (
        patch.dict(
            "os.environ", {"MIGRATE_SOURCE_DATABASE_URL": "s", "DATABASE_URL": "t"}
        ),
        patch.object(
            migrate_mod,
            "run_migrate",
            return_value={"ok": True, "tables": [plan.__dict__]},
        ),
    ):
        assert main([]) == 0
