"""T5.2 / TC-EV031-001 — verify script row counts + sample checksums."""

from __future__ import annotations

from typing import Any

import pytest
from scripts.ops.verify_supabase_to_do_migrate import (
    PRODUCT_TABLES,
    TableDiff,
    TableSnapshot,
    compare_snapshots,
    normalize_database_url,
    report_ok,
    row_fingerprint,
    sample_checksum,
)


@pytest.mark.unit
def test_product_tables_match_ops_map() -> None:
    assert PRODUCT_TABLES == (
        "tac_work_sessions",
        "iwxxm_ingest_results",
        "iwxxm_ingest_quarantine",
    )


@pytest.mark.unit
def test_normalize_database_url_rewrites_asyncpg_and_plain() -> None:
    assert (
        normalize_database_url("postgresql+asyncpg://u:p@h/db")
        == "postgresql+psycopg://u:p@h/db"
    )
    assert (
        normalize_database_url("postgresql://u:p@h/db")
        == "postgresql+psycopg://u:p@h/db"
    )
    assert (
        normalize_database_url("postgresql+psycopg://u:p@h/db")
        == "postgresql+psycopg://u:p@h/db"
    )


@pytest.mark.unit
def test_row_fingerprint_is_stable_for_same_values() -> None:
    cols = ("id", "product", "status")
    a = row_fingerprint(cols, ("u1", "metar", "draft"))
    b = row_fingerprint(cols, ("u1", "metar", "draft"))
    c = row_fingerprint(cols, ("u1", "taf", "draft"))
    assert a == b
    assert a != c


@pytest.mark.unit
def test_sample_checksum_orders_by_id_and_limits() -> None:
    cols = ("id", "product")
    rows_a: list[tuple[Any, ...]] = [
        ("b", "metar"),
        ("a", "taf"),
        ("c", "speci"),
    ]
    rows_b: list[tuple[Any, ...]] = [
        ("c", "speci"),
        ("a", "taf"),
        ("b", "metar"),
    ]
    assert sample_checksum(rows_a, cols, sample_size=10) == sample_checksum(
        rows_b, cols, sample_size=10
    )
    # Different sample window → different digest when rows differ beyond limit.
    small = sample_checksum(rows_a, cols, sample_size=1)
    large = sample_checksum(rows_a, cols, sample_size=3)
    assert small != large


@pytest.mark.unit
def test_compare_snapshots_row_count_mismatch() -> None:
    cols = ("id", "product")
    source = TableSnapshot(
        table="tac_work_sessions",
        row_count=2,
        sample_checksum=sample_checksum([("a", "metar"), ("b", "taf")], cols),
    )
    target = TableSnapshot(
        table="tac_work_sessions",
        row_count=1,
        sample_checksum=sample_checksum([("a", "metar")], cols),
    )
    diff = compare_snapshots(source, target)
    assert diff.ok is False
    assert "row_count" in diff.reasons


@pytest.mark.unit
def test_compare_snapshots_checksum_mismatch() -> None:
    cols = ("id", "product")
    source = TableSnapshot(
        table="iwxxm_ingest_results",
        row_count=1,
        sample_checksum=sample_checksum([("a", "metar")], cols),
    )
    target = TableSnapshot(
        table="iwxxm_ingest_results",
        row_count=1,
        sample_checksum=sample_checksum([("a", "taf")], cols),
    )
    diff = compare_snapshots(source, target)
    assert diff.ok is False
    assert "sample_checksum" in diff.reasons


@pytest.mark.unit
def test_compare_snapshots_match_and_report_ok() -> None:
    cols = ("id", "product")
    digest = sample_checksum([("a", "metar")], cols)
    source = TableSnapshot(
        table="iwxxm_ingest_quarantine",
        row_count=1,
        sample_checksum=digest,
    )
    target = TableSnapshot(
        table="iwxxm_ingest_quarantine",
        row_count=1,
        sample_checksum=digest,
    )
    diffs: list[TableDiff] = [compare_snapshots(source, target)]
    assert diffs[0].ok is True
    assert report_ok(diffs) is True
