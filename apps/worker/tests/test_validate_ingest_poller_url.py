"""EV-033 — reject placeholder / non-https INGEST_POLLER_URL (F8 harden)."""

from __future__ import annotations

import pytest
from metar_worker.poller_url import (
    DEFAULT_FIXTURE_INGEST_POLLER_URL,
    validate_ingest_poller_url,
)


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "   ",
        "REPLACE_ME_INGEST_POLLER_URL",
        "https://REPLACE_ME.example/feed.json",
        "http://ingest.example.test/feed.json",
        "ftp://ingest.example.test/feed.json",
    ],
)
def test_validate_ingest_poller_url_rejects_bad(bad: str) -> None:
    with pytest.raises(ValueError, match="INGEST_POLLER_URL"):
        validate_ingest_poller_url(bad)


def test_validate_ingest_poller_url_accepts_https() -> None:
    url = "https://ingest.example.test/feed.json"
    assert validate_ingest_poller_url(url) == url
    assert validate_ingest_poller_url(f"  {url}  ") == url


def test_default_fixture_url_is_https_raw_github() -> None:
    assert DEFAULT_FIXTURE_INGEST_POLLER_URL.startswith("https://")
    assert "EMPIRIC2/TAC-to-IWXXM" in DEFAULT_FIXTURE_INGEST_POLLER_URL
    assert DEFAULT_FIXTURE_INGEST_POLLER_URL.endswith(
        "apps/worker/tests/fixtures/ingest_feed.json"
    )
    assert validate_ingest_poller_url(DEFAULT_FIXTURE_INGEST_POLLER_URL) == (
        DEFAULT_FIXTURE_INGEST_POLLER_URL
    )
