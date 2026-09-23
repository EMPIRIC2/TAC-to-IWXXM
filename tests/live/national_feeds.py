"""Helpers for the manual national-feed check (TC-LIVE-FEEDS).

[Corpus: tests §TC-LIVE-FEEDS] [Corpus: product §F6] [Corpus: adr/ADR-009]
"""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import cast

import httpx

USER_AGENT = "TAC-to-IWXXM-live-feeds/1.0 github.com/EMPIRIC2/TAC-to-IWXXM"
MET_NO_METAR = "https://api.met.no/weatherapi/tafmetar/1.0/metar.txt"
MET_NO_TAF = "https://api.met.no/weatherapi/tafmetar/1.0/taf.txt"
AWC_METAR = "https://aviationweather.gov/api/data/metar"
AWC_TAF = "https://aviationweather.gov/api/data/taf"
KNMI_FILES = (
    "https://api.dataplatform.knmi.nl/open-data/v1/datasets/metar/versions/1.0/files"
)
KNMI_API_KEY_ENV = "KNMI_OPEN_DATA_API_KEY"

METAR_STATIONS = ("ENGM", "EDDF", "EGLL", "LFPG", "LSZH", "VHHH")
TAF_STATIONS = ("ENGM", "EGLL", "VHHH")

_PRODUCT_KEYWORDS = frozenset({"METAR", "SPECI", "TAF"})
_TAF_MODIFIERS = frozenset({"AMD", "COR"})
_OBS_TIME = re.compile(r"^\d{6}Z$")
_TAF_PERIOD = re.compile(r"^\d{4}/\d{4}$")


@dataclass(frozen=True)
class FeedSample:
    """One TAC report from a named feed."""

    source: str
    station: str
    product: str
    raw: str


def canonical_report(text: str) -> str:
    """Drop the product keyword, ``AUTO``, ``AMD``/``COR``, and the ``=`` terminator."""
    parts = text.replace("=", " ").split()
    if parts and parts[0] in _PRODUCT_KEYWORDS:
        parts = parts[1:]
    if parts and parts[0] in _TAF_MODIFIERS:
        parts = parts[1:]
    return " ".join(part for part in parts if part != "AUTO")


def observation_key(text: str, product: str) -> str | None:
    """Shared clock token: METAR ``ddhhmmZ`` or TAF validity ``ddhh/ddhh``."""
    pattern = _OBS_TIME if product == "METAR" else _TAF_PERIOD
    for token in canonical_report(text).split():
        if pattern.match(token):
            return token
    return None


def ensure_product_keyword(text: str, product: str) -> str:
    """Prepend ``product`` when the feed omits it."""
    stripped = " ".join(text.split())
    if stripped.startswith(f"{product} "):
        return stripped
    return f"{product} {stripped}"


def join_report_lines(body: str) -> list[str]:
    """Join TAF continuation lines onto the report that starts with an ICAO id."""
    reports: list[list[str]] = []
    for raw in body.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        head = canonical_report(stripped).split(" ", 1)[0]
        starts_report = len(head) == 4 and head.isalpha()
        if starts_report or not reports:
            reports.append([stripped])
        else:
            reports[-1].append(stripped)
    return [" ".join(parts) for parts in reports]


def reports_by_station(
    body: str, stations: tuple[str, ...], *, newest: str
) -> dict[str, str]:
    """Map each station to one raw report. ``newest`` is ``first`` or ``last``."""
    lines = join_report_lines(body)
    ordered = lines if newest == "first" else list(reversed(lines))
    found: dict[str, str] = {}
    wanted = set(stations)
    for line in ordered:
        token = canonical_report(line).split(" ", 1)[0] if line else ""
        if token in wanted and token not in found:
            found[token] = line
    return found


def iwxxm_root_local_name(xml: str) -> str:
    """Local name of the document element."""
    root = ET.fromstring(xml)
    return root.tag.rsplit("}", 1)[-1]


_KNMI_TAC_COMMENT = re.compile(
    r"<!--\s*((?:METAR|SPECI)\s+[A-Z]{4}\b.*?)\s*-->",
    re.DOTALL,
)


def extract_knmi_tac(body: str) -> list[str]:
    """TAC reports embedded in KNMI IWXXM comments."""
    reports: list[str] = []
    for match in _KNMI_TAC_COMMENT.finditer(body):
        text = " ".join(match.group(1).split())
        if text:
            reports.append(text)
    return reports


def knmi_latest_filename(payload: dict[str, object]) -> str:
    """Filename of the first file in a KNMI list response."""
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        message = "KNMI file list was empty"
        raise ValueError(message)
    first: object = cast("object", files[0])
    if not isinstance(first, dict):
        message = "KNMI file entry was not an object"
        raise ValueError(message)
    filename = cast("dict[str, object]", first).get("filename")
    if not isinstance(filename, str) or not filename:
        message = "KNMI file entry had no filename"
        raise ValueError(message)
    return filename


def _get_text(
    client: httpx.Client, url: str, params: dict[str, str] | None = None
) -> str:
    response = client.get(url, params=params)
    response.raise_for_status()
    return response.text


def fetch_public_samples(client: httpx.Client) -> list[FeedSample]:
    """Latest METAR and TAF lines from MET Norway and NOAA AWC."""
    samples: list[FeedSample] = []
    empty: dict[str, str] = {}
    pairs: tuple[tuple[str, tuple[str, ...], str, str, dict[str, str]], ...] = (
        ("METAR", METAR_STATIONS, MET_NO_METAR, AWC_METAR, {"hours": "6"}),
        ("TAF", TAF_STATIONS, MET_NO_TAF, AWC_TAF, empty),
    )
    for product, stations, met_no_url, awc_url, extra in pairs:
        awc_params = {"ids": ",".join(stations), "format": "raw", **extra}
        awc_body = _get_text(client, awc_url, awc_params)
        awc_lines = reports_by_station(awc_body, stations, newest="first")
        for station in stations:
            norway = _get_text(client, met_no_url, {"icao": station})
            norway_lines = reports_by_station(norway, (station,), newest="last")
            if station not in norway_lines:
                message = f"MET Norway returned no {product} for {station}"
                raise ValueError(message)
            if station not in awc_lines:
                message = f"NOAA AWC returned no {product} for {station}"
                raise ValueError(message)
            samples.append(
                FeedSample("met.no", station, product, norway_lines[station])
            )
            samples.append(FeedSample("awc", station, product, awc_lines[station]))
    return samples


def fetch_knmi_metars(client: httpx.Client, api_key: str) -> list[FeedSample]:
    """Latest Dutch METAR file from the KNMI Open Data API."""
    listing = client.get(
        KNMI_FILES,
        params={"maxKeys": "1", "orderBy": "created", "sorting": "desc"},
        headers={"Authorization": api_key},
    )
    listing.raise_for_status()
    filename = knmi_latest_filename(cast("dict[str, object]", listing.json()))
    url_response = client.get(
        f"{KNMI_FILES}/{filename}/url",
        headers={"Authorization": api_key},
    )
    url_response.raise_for_status()
    download_url = cast("dict[str, object]", url_response.json()).get(
        "temporaryDownloadUrl"
    )
    if not isinstance(download_url, str) or not download_url:
        message = "KNMI did not return a download URL"
        raise ValueError(message)
    body = _get_text(client, download_url)
    return [
        FeedSample("knmi", canonical_report(tac).split(" ", 1)[0], "METAR", tac)
        for tac in extract_knmi_tac(body)
    ]


def knmi_api_key() -> str | None:
    """Registered KNMI key, when the operator has set it."""
    value = os.environ.get(KNMI_API_KEY_ENV, "").strip()
    return value or None
