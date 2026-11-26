"""TC-SH-013 — Station health eval-benchmark from FR-045 (FR-047 / FR-072)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.services.live_map_eval_store import LiveMapEvalStore, set_live_map_eval_store
from src.services.station_health_eval import (
    build_eval_benchmark,
    filter_failure_locations,
    normalize_icao_filter,
    product_failure_breakdown,
)


@pytest.fixture
def eval_client() -> TestClient:
    store = LiveMapEvalStore()
    store.write_snapshot(
        {
            "computed_at": "2026-11-26T12:00:00Z",
            "window_hours": 24,
            "products": ["metar", "taf"],
            "partial_decode_count": 1,
            "lint_count": 3,
            "top_lint_codes": [{"code": "INVALID_WIND", "count": 2}],
            "convert_failure_count": 2,
            "iwxxm_validation": {"pass": 10, "fail": 2, "skip": 1},
            "failure_locations": [
                {
                    "place_key": "KJFK",
                    "product": "metar",
                    "stage": "lint",
                    "code": "INVALID_WIND",
                },
                {
                    "place_key": "KJFK",
                    "product": "metar",
                    "stage": "convert",
                    "code": "TRANSLATION_FAILED",
                },
                {
                    "place_key": "KLAX",
                    "product": "taf",
                    "stage": "lint",
                    "code": "INVALID_VISIBILITY",
                },
            ],
        }
    )
    set_live_map_eval_store(store)
    with TestClient(api_module.app) as client:
        yield client
    set_live_map_eval_store(None)


def test_normalize_icao_filter_success_and_failure() -> None:
    assert normalize_icao_filter(None) is None
    assert normalize_icao_filter("  kjfk ") == "KJFK"
    with pytest.raises(ValueError, match="four-letter"):
        normalize_icao_filter("KJ")
    with pytest.raises(ValueError, match="four-letter"):
        normalize_icao_filter("KJ1K")


def test_filter_and_product_breakdown() -> None:
    rows = [
        {"place_key": "kjfk", "product": "METAR", "stage": "lint", "code": "A"},
        {"place_key": "KLAX", "product": "taf", "stage": "convert", "code": "B"},
    ]
    filtered = filter_failure_locations(rows, icao="KJFK")
    assert len(filtered) == 1
    assert filtered[0]["place_key"] == "kjfk"
    assert product_failure_breakdown(filtered) == [
        {"product": "metar", "failure_count": 1},
    ]


def test_build_eval_benchmark_reads_store(eval_client: TestClient) -> None:
    del eval_client
    body = build_eval_benchmark(icao="KJFK")
    assert body["icao_filter"] == "KJFK"
    assert body["lint_count"] == 3
    assert len(body["failure_locations"]) == 2
    assert body["product_breakdown"][0]["product"] == "metar"


@pytest.mark.parametrize(
    ("params", "status_code", "expect"),
    [
        ({}, 200, "full_snapshot"),
        ({"icao": "KJFK"}, 200, "kjfk_only"),
        ({"icao": "ZZZZ"}, 200, "empty_failures"),
        ({"icao": "BAD"}, 400, "invalid_icao"),
    ],
)
def test_eval_benchmark_http_matrix(
    eval_client: TestClient,
    params: dict[str, str],
    status_code: int,
    expect: str,
) -> None:
    resp = eval_client.get("/api/v1/station-health/eval-benchmark", params=params)
    assert resp.status_code == status_code
    if status_code != 200:
        assert "icao" in resp.json()["detail"].lower()
        return
    body = resp.json()
    assert body["computed_at"] == "2026-11-26T12:00:00Z"
    assert body["convert_failure_count"] == 2
    assert body["iwxxm_validation"]["pass"] == 10
    if expect == "full_snapshot":
        assert len(body["failure_locations"]) == 3
        assert body["icao_filter"] is None
        products = {row["product"] for row in body["product_breakdown"]}
        assert products == {"metar", "taf"}
    elif expect == "kjfk_only":
        assert body["icao_filter"] == "KJFK"
        assert all(row["place_key"].upper() == "KJFK" for row in body["failure_locations"])
        assert body["product_breakdown"] == [{"product": "metar", "failure_count": 2}]
    else:
        assert body["failure_locations"] == []
        assert body["product_breakdown"] == []


def test_eval_benchmark_mutation_create_update_read(eval_client: TestClient) -> None:
    """Store create then update; GET reflects latest (mutation x success)."""
    store = LiveMapEvalStore()
    set_live_map_eval_store(store)
    store.write_snapshot(
        {
            "computed_at": "2026-11-26T13:00:00Z",
            "window_hours": 24,
            "products": ["metar"],
            "partial_decode_count": 0,
            "lint_count": 0,
            "top_lint_codes": [],
            "convert_failure_count": 0,
            "iwxxm_validation": {"pass": 1, "fail": 0, "skip": 0},
            "failure_locations": [],
        }
    )
    first = eval_client.get("/api/v1/station-health/eval-benchmark").json()
    assert first["computed_at"] == "2026-11-26T13:00:00Z"
    store.write_snapshot(
        {
            "computed_at": "2026-11-26T13:15:00Z",
            "window_hours": 24,
            "products": ["metar"],
            "partial_decode_count": 0,
            "lint_count": 9,
            "top_lint_codes": [{"code": "X", "count": 9}],
            "convert_failure_count": 0,
            "iwxxm_validation": {"pass": 2, "fail": 0, "skip": 0},
            "failure_locations": [],
        }
    )
    second = eval_client.get("/api/v1/station-health/eval-benchmark").json()
    assert second["computed_at"] == "2026-11-26T13:15:00Z"
    assert second["lint_count"] == 9
    set_live_map_eval_store(None)
