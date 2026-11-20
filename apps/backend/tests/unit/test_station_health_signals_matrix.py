"""Station health signals matrix - maintenance, formats, issues, retention, centennial.

Combinatorial coverage for F39 evolve-auto test matrix:
success x failure x validation x mutation permutations.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.services.station_health_centennial import (
    STATUS_AVAILABLE,
    STATUS_INSUFFICIENT,
    build_centennial_metrics,
    observing_continuity_metric,
)
from src.services.station_health_signals import (
    detect_file_format,
    extract_maintenance_tags,
    normalize_issue_codes,
)
from src.services.station_health_store import StationHealthStore, set_station_health_store
from src.services.station_health_types import StationMeta


@pytest.fixture
def client() -> TestClient:
    store = StationHealthStore()
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010000Z AUTO 18008KT 10SM FEW040 15/07 A3005 RMK AO2 $ FZRANO=",
        source="ingest",
        name="John F Kennedy International",
        issue_codes=["INVALID_WIND", "MISSING_GROUP"],
    )
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010100Z 18008KT 10SM FEW040 15/07 A3005=",
        source="convert",
        issue_codes=["INVALID_WIND"],
    )
    store.record_observation(
        icao="EHAM",
        product="metar",
        tac_text=("SAUK31 EGRR 010000\nMETAR EHAM 010000Z 24010KT 9999 FEW020 12/08 Q1013="),
        source="ingest",
        name="Amsterdam Airport Schiphol",
    )
    set_station_health_store(store)
    with TestClient(api_module.app) as test_client:
        yield test_client
    set_station_health_store(None)


@pytest.mark.parametrize(
    ("tac", "expected"),
    [
        ("METAR KJFK 010000Z RMK $ =", ("$",)),
        ("METAR KJFK 010000Z RMK AO2 FZRANO TSNO =", ("FZRANO", "TSNO")),
        ("METAR KJFK 010000Z 18008KT 10SM FEW040=", ()),
    ],
)
def test_extract_maintenance_tags_validation(tac: str, expected: tuple[str, ...]) -> None:
    assert extract_maintenance_tags(tac) == expected


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ("METAR KJFK 010000Z 18008KT=", "tac"),
        ("SAUK31 EGRR 010000\nMETAR KJFK 010000Z=", "bulletin"),
        ('<?xml version="1.0"?><iwxxm:MeteorologicalAerodromeObservationReport/>', "iwxxm_xml"),
        ("", "unknown"),
    ],
)
def test_detect_file_format_validation(payload: str, expected: str) -> None:
    assert detect_file_format(payload) == expected


@pytest.mark.parametrize(
    ("codes", "expected"),
    [
        (["invalid_wind", "INVALID_WIND", ""], ("INVALID_WIND",)),
        (None, ()),
        ([], ()),
    ],
)
def test_normalize_issue_codes_validation(codes: list[str] | None, expected: tuple[str, ...]) -> None:
    assert normalize_issue_codes(codes) == expected


def test_centennial_continuity_available_and_insufficient() -> None:
    ok = observing_continuity_metric(availability_score=95.0, expected_count=10, actual_count=10)
    assert ok["status"] == STATUS_AVAILABLE
    assert ok["score"] == 95.0
    missing = observing_continuity_metric(availability_score=0.0, expected_count=0, actual_count=0)
    assert missing["status"] == STATUS_INSUFFICIENT


def test_centennial_build_includes_deferred_insufficient() -> None:
    meta = StationMeta(icao="KJFK", name="JFK", country="US", latitude=40.6, longitude=-73.7)
    rows: list[object] = []
    metrics = build_centennial_metrics(
        meta=meta,
        rows=rows,  # type: ignore[arg-type]
        availability_score=92.0,
        expected_count=10,
        actual_count=9,
        solidus_rate=0.0,
        missing_digit_rate=0.0,
        lint_severity_score=100.0,
    )
    ids = {row["id"] for row in metrics}
    assert "centennial_continuity" in ids
    assert "centennial_metadata" in ids
    assert "centennial_quality" in ids
    deferred = [row for row in metrics if row["status"] == STATUS_INSUFFICIENT]
    assert len(deferred) >= 5


@pytest.mark.parametrize(
    ("path", "params", "status_code", "checks"),
    [
        (
            "/api/v1/station-health",
            {"window": "90d"},
            200,
            ("has_kjfk", "has_maintenance", "has_formats", "has_issues", "has_centennial"),
        ),
        (
            "/api/v1/station-health",
            {"window": "6h", "region": "IV"},
            200,
            ("region_ok",),
        ),
        (
            "/api/v1/station-health/KJFK",
            {},
            200,
            ("detail_signals",),
        ),
        (
            "/api/v1/station-health/metrics",
            {},
            200,
            ("metrics_registry",),
        ),
    ],
)
def test_station_health_read_success_matrix(
    client: TestClient,
    path: str,
    params: dict[str, object],
    status_code: int,
    checks: tuple[str, ...],
) -> None:
    response = client.get(path, params=params or None)
    assert response.status_code == status_code
    body = response.json()
    if "has_kjfk" in checks:
        kjfk = next(row for row in body["stations"] if row["icao"] == "KJFK")
        assert kjfk["maintenance_tag_counts"].get("$", 0) >= 1
        assert kjfk["maintenance_tag_counts"].get("FZRANO", 0) >= 1
        assert kjfk["file_format_counts"].get("tac", 0) >= 1
        assert kjfk["issue_code_counts"].get("INVALID_WIND", 0) >= 1
        assert any(m["id"] == "centennial_continuity" for m in kjfk["centennial_metrics"])
    if "has_maintenance" in checks:
        assert any(row.get("maintenance_tag_counts") for row in body["stations"])
    if "has_formats" in checks:
        assert any(row.get("file_format_counts") for row in body["stations"])
    if "has_issues" in checks:
        assert any(row.get("issue_code_counts") for row in body["stations"])
    if "has_centennial" in checks:
        assert any(row.get("centennial_metrics") for row in body["stations"])
    if "region_ok" in checks:
        assert all(row["wmo_region"] == "IV" for row in body["stations"]) or body["stations"] == []
    if "detail_signals" in checks:
        assert "90d" in body["windows"]
        assert body["windows"]["90d"]["maintenance_tag_counts"].get("$", 0) >= 1
        assert body["issue_code_counts"].get("INVALID_WIND", 0) >= 1
        assert body["centennial_metrics"]
    if "metrics_registry" in checks:
        ids = {row["id"] for row in body["metrics"]}
        assert "maintenance_tags" in ids
        assert "centennial_continuity" in ids


@pytest.mark.parametrize(
    ("params", "status_code", "detail_substr"),
    [
        ({"window": "2h"}, 400, "Window"),
        ({"window": "90d", "region": "VII"}, 400, "Region"),
        ({"window": "99d"}, 400, "Window"),
    ],
)
def test_station_health_read_validation_failure_matrix(
    client: TestClient,
    params: dict[str, object],
    status_code: int,
    detail_substr: str,
) -> None:
    response = client.get("/api/v1/station-health", params=params)
    assert response.status_code == status_code
    assert detail_substr in str(response.json().get("detail", ""))


def test_station_health_detail_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/station-health/ZZZZ")
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("icao", "tac", "issue_codes", "expect_ok"),
    [
        ("KJFK", "METAR KJFK 010200Z 18008KT 10SM FEW040 15/07 A3005 $ =", ["LINT_A"], True),
        ("BAD", "METAR BAD 010200Z=", [], False),
        ("KJFK", "METAR KJFK 010200Z=", None, True),
    ],
)
def test_record_observation_mutation_matrix(
    icao: str,
    tac: str,
    issue_codes: list[str] | None,
    expect_ok: bool,
) -> None:
    store = StationHealthStore()
    row = store.record_observation(
        icao=icao,
        product="metar",
        tac_text=tac,
        source="ingest",
        issue_codes=issue_codes,
    )
    assert (row is not None) is expect_ok
    if expect_ok and row is not None:
        assert row.file_format in {"tac", "bulletin", "iwxxm_xml", "unknown"}
        if "$" in tac:
            assert "$" in row.maintenance_tags


def test_retention_purges_records_older_than_90_days() -> None:
    store = StationHealthStore()
    old = datetime.now(UTC) - timedelta(days=100)
    rejected = store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005=",
        source="ingest",
        observed_at=old,
    )
    assert rejected is None
    recent = store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005 $ =",
        source="ingest",
    )
    assert recent is not None
    from src.services.station_health_types import StationRecord

    # Inject an expired row then purge.
    store._records.append(
        StationRecord(
            icao=recent.icao,
            product=recent.product,
            observed_at=old,
            ingested_at=old,
            tac_text=recent.tac_text,
            source=recent.source,
            solidus_count=recent.solidus_count,
            missing_digit_count=recent.missing_digit_count,
            lint_error_count=recent.lint_error_count,
            lint_warning_count=recent.lint_warning_count,
            convert_ok=recent.convert_ok,
            character_count=recent.character_count,
            file_format=recent.file_format,
            maintenance_tags=recent.maintenance_tags,
            issue_codes=recent.issue_codes,
        )
    )
    removed = store.purge_expired()
    assert removed >= 1
    payload = store.list_stations(window_key="90d")
    assert payload["summary"]["station_count"] >= 1


def test_update_style_second_observation_mutates_counts() -> None:
    store = StationHealthStore()
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005=",
        source="ingest",
    )
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010100Z 18008KT 10SM FEW040 15/07 A3005 RMK $ =",
        source="ingest",
        issue_codes=["XSD_FAIL"],
    )
    detail = store.get_station("KJFK")
    assert detail is not None
    assert detail["record_count"] == 2
    assert detail["maintenance_tag_counts"].get("$", 0) == 1
    assert detail["issue_code_counts"].get("XSD_FAIL", 0) == 1
    assert detail["file_format_counts"].get("tac", 0) == 2
