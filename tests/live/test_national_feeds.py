"""Live TAC and IWXXM check against free national feeds (TC-LIVE-FEEDS).

Run with ``make test-live-feeds``. This is not part of CI.

[Corpus: tests §TC-LIVE-FEEDS] [Corpus: product §F6] [Corpus: adr/ADR-009]
"""

from __future__ import annotations

import httpx
import pytest
from iwxxm_validate.api import validate
from tac_validate.api import lint
from tests.live.national_feeds import (
    USER_AGENT,
    FeedSample,
    canonical_report,
    ensure_product_keyword,
    fetch_knmi_metars,
    fetch_public_samples,
    iwxxm_root_local_name,
    knmi_api_key,
    observation_key,
)

from tac2iwxxm import convert

pytestmark = pytest.mark.live_api

_IWXXM_VERSION = "2025-2"


def _assert_converts(sample: FeedSample) -> None:
    tac = ensure_product_keyword(sample.raw, sample.product)
    report = lint(tac, product=sample.product, profile="annex3")
    errors = [issue for issue in report.issues if issue.severity == "error"]
    assert report.ok, f"{sample.source} {sample.station} TAC errors: {errors} :: {tac}"
    converted = convert(
        tac,
        product=sample.product,
        profile="annex3",
        iwxxm_version=_IWXXM_VERSION,
    )
    assert converted.ok, f"{sample.source} {sample.station} convert failed :: {tac}"
    assert converted.xml, f"{sample.source} {sample.station} produced no XML :: {tac}"
    validated = validate(
        converted.xml,
        iwxxm_version=_IWXXM_VERSION,
        profile="annex3",
        product=sample.product,
    )
    xsd_errors = [issue for issue in validated.issues if issue.severity == "error"]
    assert validated.ok, (
        f"{sample.source} {sample.station} IWXXM errors: {xsd_errors} :: {tac}"
    )
    assert iwxxm_root_local_name(converted.xml) == sample.product


@pytest.fixture(scope="module")
def public_samples() -> list[FeedSample]:
    try:
        with httpx.Client(
            timeout=30.0,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        ) as client:
            return fetch_public_samples(client)
    except httpx.HTTPError as exc:
        pytest.skip(f"national feed unreachable: {exc}")


def test_public_feeds_convert(public_samples: list[FeedSample]) -> None:
    """Each MET Norway and NOAA report lints, converts, and passes XSD."""
    assert public_samples
    for sample in public_samples:
        _assert_converts(sample)


def test_met_norway_matches_noaa_when_times_agree(
    public_samples: list[FeedSample],
) -> None:
    """Same observation time means the same weather groups."""
    grouped: dict[tuple[str, str], dict[str, FeedSample]] = {}
    for sample in public_samples:
        grouped.setdefault((sample.product, sample.station), {})[sample.source] = sample
    compared = 0
    for (product, station), pair in grouped.items():
        norway = pair.get("met.no")
        awc = pair.get("awc")
        if norway is None or awc is None:
            continue
        left_key = observation_key(norway.raw, product)
        right_key = observation_key(awc.raw, product)
        if left_key is None or left_key != right_key:
            continue
        compared += 1
        assert canonical_report(norway.raw) == canonical_report(awc.raw), (
            f"{station} {product} {left_key} differs\n"
            f"met.no: {norway.raw}\nawc: {awc.raw}"
        )
    assert compared >= 1, "no overlapping observation to compare"


def test_knmi_metar_when_key_present() -> None:
    """Dutch METAR file, only when KNMI_OPEN_DATA_API_KEY is set."""
    api_key = knmi_api_key()
    if api_key is None:
        pytest.skip(f"{'KNMI_OPEN_DATA_API_KEY'} is not set")
    try:
        with httpx.Client(
            timeout=30.0,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        ) as client:
            samples = fetch_knmi_metars(client, api_key)
    except httpx.HTTPError as exc:
        pytest.fail(f"KNMI request failed: {exc}")
    assert samples, "KNMI file contained no METAR or SPECI comment"
    for sample in samples:
        _assert_converts(sample)
