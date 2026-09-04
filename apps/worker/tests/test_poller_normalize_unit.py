"""Unit coverage for poller normalize / safe_url edge cases (EV-047 T2.5.4)."""

from __future__ import annotations

import httpx
import pytest
import respx
from metar_worker.poller import _normalize_items, fetch_jobs, safe_url_for_log

pytestmark = pytest.mark.unit

FEED_URL = "https://ingest.example.test:8443/feed.json"


def test_safe_url_for_log_includes_non_default_port() -> None:
    assert (
        safe_url_for_log("https://user:tok@ingest.example.test:8443/path?q=1")
        == "https://ingest.example.test:8443/path"
    )


def test_normalize_items_accepts_top_level_list() -> None:
    jobs = _normalize_items(
        [{"id": "a", "product": "taf", "tac": "TAF KJFK 231720Z 2318/2424 18010KT="}],
        source_url=FEED_URL,
    )
    assert len(jobs) == 1
    assert jobs[0].job_id == "a"
    assert jobs[0].product == "TAF"
    assert jobs[0].source_url == FEED_URL


def test_normalize_items_rejects_non_list_or_items_dict() -> None:
    with pytest.raises(ValueError, match=r"JSON list or \{items"):
        _normalize_items({"not": "items"}, source_url=FEED_URL)


def test_normalize_items_rejects_items_not_list() -> None:
    with pytest.raises(ValueError, match="items must be a list"):
        _normalize_items({"items": "nope"}, source_url=FEED_URL)


def test_normalize_items_rejects_non_object_item() -> None:
    with pytest.raises(ValueError, match="must be an object"):
        _normalize_items({"items": ["bad"]}, source_url=FEED_URL)


def test_normalize_items_rejects_missing_tac() -> None:
    with pytest.raises(ValueError, match="missing tac"):
        _normalize_items(
            {"items": [{"id": "x", "product": "METAR"}]}, source_url=FEED_URL
        )


def test_normalize_items_default_job_id_and_product() -> None:
    jobs = _normalize_items(
        {"items": [{"tac": "METAR KJFK 231751Z NIL="}]},
        source_url=FEED_URL,
    )
    assert jobs[0].job_id == "job-1"
    assert jobs[0].product == "METAR"


@respx.mock
def test_fetch_jobs_reuses_injected_client() -> None:
    respx.get(FEED_URL).mock(
        return_value=httpx.Response(
            200, json={"items": [{"tac": "METAR KJFK 231751Z NIL="}]}
        )
    )
    with httpx.Client() as client:
        jobs = fetch_jobs(FEED_URL, client=client)
    assert len(jobs) == 1
    assert jobs[0].job_id == "job-1"
