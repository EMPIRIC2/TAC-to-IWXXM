"""EV-080 coverage fills for scripts/ops/verify_supabase_to_do_migrate.py."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import scripts.ops.verify_supabase_to_do_migrate as verify_mod
from scripts.ops.verify_supabase_to_do_migrate import (
    TableSnapshot,
    compare_snapshots,
    fetch_table_snapshot,
    main,
    report_ok,
    row_fingerprint,
    sample_checksum,
    verify_urls,
)


def test_canon_and_fingerprint_edges() -> None:
    assert verify_mod._canon(None) == ""
    assert verify_mod._canon(b"\x01\x02") == "0102"
    with pytest.raises(ValueError, match="length mismatch"):
        row_fingerprint(("a",), ("a", "b"))


def test_sample_checksum_requires_positive_size() -> None:
    with pytest.raises(ValueError, match="sample_size"):
        sample_checksum([], ("id",), sample_size=0)


def test_normalize_database_url_rewrites_psycopg2_and_asyncpg() -> None:
    assert (
        verify_mod.normalize_database_url("postgresql+psycopg2://u:p@h/db")
        == "postgresql+psycopg://u:p@h/db"
    )
    assert (
        verify_mod.normalize_database_url("postgresql+asyncpg://u:p@h/db")
        == "postgresql+psycopg://u:p@h/db"
    )
    assert verify_mod.normalize_database_url("mysql://x") == "mysql://x"


def test_compare_snapshots_both_reasons() -> None:
    cols = ("id", "product")
    source = TableSnapshot(
        table="tac_work_sessions",
        row_count=2,
        sample_checksum=sample_checksum([("a", "metar")], cols),
    )
    target = TableSnapshot(
        table="tac_work_sessions",
        row_count=1,
        sample_checksum=sample_checksum([("a", "taf")], cols),
    )
    diff = compare_snapshots(source, target)
    assert diff.ok is False
    assert set(diff.reasons) == {"row_count", "sample_checksum"}
    a = TableSnapshot(table="a", row_count=1, sample_checksum="x")
    b = TableSnapshot(table="b", row_count=1, sample_checksum="x")
    with pytest.raises(ValueError, match="table name mismatch"):
        compare_snapshots(a, b)


def test_quote_ident_rejects_unsafe() -> None:
    with pytest.raises(ValueError, match="unsafe identifier"):
        verify_mod._quote_ident("x;y")


def test_fetch_table_snapshot() -> None:
    engine = MagicMock()
    conn = MagicMock()
    count_result = MagicMock()
    count_result.scalar_one.return_value = 2
    cols = verify_mod.CHECKSUM_COLUMNS["tac_work_sessions"]
    row = tuple(f"v{i}" for i in range(len(cols)))
    rows_result = MagicMock()
    rows_result.fetchall.return_value = [row]
    conn.execute.side_effect = [count_result, rows_result]
    engine.connect.return_value.__enter__.return_value = conn

    snap = fetch_table_snapshot(engine, "tac_work_sessions", sample_size=10)
    assert snap.row_count == 2
    assert len(snap.sample_checksum) == 64


def test_verify_urls_unknown_table() -> None:
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = MagicMock()
    with (
        patch.object(verify_mod, "create_engine", return_value=engine),
        pytest.raises(ValueError, match="unknown product table"),
    ):
        verify_urls("s", "t", tables=("nope",))


def test_verify_urls_happy_path() -> None:
    digest = sample_checksum([("a", "metar")], ("id", "product"))
    snap = TableSnapshot(table="tac_work_sessions", row_count=1, sample_checksum=digest)
    engine = MagicMock()
    with (
        patch.object(verify_mod, "create_engine", return_value=engine),
        patch.object(verify_mod, "fetch_table_snapshot", return_value=snap),
    ):
        diffs = verify_urls("s", "t", tables=("tac_work_sessions",))
    assert diffs[0].ok is True
    assert report_ok(diffs) is True


def test_main_cli_paths(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 1
    assert main(["--sample-size", "0", "--source-url", "s", "--target-url", "t"]) == 1

    ok_diff = verify_mod.TableDiff(
        table="tac_work_sessions",
        ok=True,
        source_row_count=1,
        target_row_count=1,
        source_checksum="abc123def456",
        target_checksum="abc123def456",
        reasons=(),
    )
    with patch.object(verify_mod, "verify_urls", return_value=[ok_diff]):
        assert main(["--source-url", "s", "--target-url", "t", "--json"]) == 0
    assert '"ok": true' in capsys.readouterr().out.lower()

    fail_diff = verify_mod.TableDiff(
        table="tac_work_sessions",
        ok=False,
        source_row_count=2,
        target_row_count=1,
        source_checksum="abc123def456",
        target_checksum="fed654cba321",
        reasons=("row_count", "sample_checksum"),
    )
    with patch.object(verify_mod, "verify_urls", return_value=[fail_diff]):
        assert main(["--source-url", "s", "--target-url", "t"]) == 1
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "reasons=" in out
    assert "VERIFY FAIL" in out

    with patch.object(verify_mod, "verify_urls", side_effect=RuntimeError("db")):
        assert main(["--source-url", "s", "--target-url", "t"]) == 2
    assert "database verify failed" in capsys.readouterr().err

    with (
        patch.dict(
            "os.environ", {"SUPABASE_DB_URL": "s", "MIGRATE_TARGET_DATABASE_URL": "t"}
        ),
        patch.object(verify_mod, "verify_urls", return_value=[ok_diff]),
    ):
        assert main([]) == 0
