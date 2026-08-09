"""T6.1: poller fetches HTTPS fixture → N jobs (Q16=A / UJ-014)."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
import respx
from metar_worker.poller import fetch_jobs, safe_url_for_log

pytestmark = pytest.mark.unit

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ingest_feed.json"
FEED_URL = "https://ingest.example.test/feed.json"


@pytest.fixture
def feed_payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@respx.mock
def test_t61_poller_fetches_https_fixture_n_jobs(feed_payload: dict) -> None:
    respx.get(FEED_URL).mock(return_value=httpx.Response(200, json=feed_payload))

    jobs = fetch_jobs(FEED_URL)

    assert len(jobs) == 3
    assert [j.job_id for j in jobs] == [
        "fixture-metar-1",
        "fixture-metar-2",
        "fixture-speci-1",
    ]
    assert jobs[0].product == "METAR"
    assert "METAR KJFK" in jobs[0].tac
    assert jobs[2].product == "SPECI"
    assert all(j.source_url == FEED_URL for j in jobs)


@respx.mock
def test_t61_poller_empty_feed() -> None:
    respx.get(FEED_URL).mock(return_value=httpx.Response(200, json={"items": []}))
    assert fetch_jobs(FEED_URL) == []


@respx.mock
def test_t61_poller_http_error_raises() -> None:
    respx.get(FEED_URL).mock(return_value=httpx.Response(503, text="down"))
    with pytest.raises(httpx.HTTPStatusError):
        fetch_jobs(FEED_URL)


def test_t61_poller_rejects_non_https() -> None:
    with pytest.raises(ValueError, match="https://"):
        fetch_jobs("http://ingest.example.test/feed.json")


def test_t61_safe_url_for_log_strips_query_and_userinfo() -> None:
    assert (
        safe_url_for_log("https://user:tok@ingest.example.test/feed.json?token=secret")
        == "https://ingest.example.test/feed.json"
    )
    assert "token=secret" not in safe_url_for_log(
        "https://ingest.example.test/feed.json?token=secret"
    )
