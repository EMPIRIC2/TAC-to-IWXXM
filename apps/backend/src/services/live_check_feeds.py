"""Allowlisted feed fetch helpers for live check.

[Corpus: product §F6] [Corpus: adr/ADR-009]
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from typing import Final, cast
from urllib.parse import urlparse

import httpx
from dissemination.allowlist import Allowlist, EgressDenied, parse_allowlist, validate_egress_host

from src.services.live_check_models import LiveCheckError

USER_AGENT: Final = "TAC-to-IWXXM-live-check/1.0 github.com/EMPIRIC2/TAC-to-IWXXM"
KNMI_API_KEY_ENV: Final = "KNMI_OPEN_DATA_API_KEY"
DEFAULT_ALLOWLIST: Final = "aviationweather.gov,api.met.no,api.dataplatform.knmi.nl"
_KNMI_DOWNLOAD_SUFFIXES: Final = (".knmi.nl", ".blob.core.windows.net", ".amazonaws.com")
_AWC = {
    "METAR": "https://aviationweather.gov/api/data/metar",
    "TAF": "https://aviationweather.gov/api/data/taf",
}
_MET_NO = {
    "METAR": "https://api.met.no/weatherapi/tafmetar/1.0/metar.txt",
    "TAF": "https://api.met.no/weatherapi/tafmetar/1.0/taf.txt",
}
_KNMI_FILES = "https://api.dataplatform.knmi.nl/open-data/v1/datasets/metar/versions/1.0/files"
_KNMI_TAC_COMMENT = re.compile(r"<!--\s*((?:METAR|SPECI)\s+[A-Z]{4}\b.*?)\s*-->", re.DOTALL)
_PRODUCT_KEYWORDS = frozenset({"METAR", "SPECI", "TAF"})

HttpGet = Callable[..., httpx.Response]


def _canonical_station(text: str) -> str:
    """Return the ICAO token from a TAC line.

    Parameters
    ----------
    text : str
        Raw TAC line.

    Returns
    -------
    str
        Four-letter station id, or empty string.
    """
    parts = text.replace("=", " ").split()
    if parts and parts[0] in _PRODUCT_KEYWORDS:
        parts = parts[1:]
    return parts[0] if parts else ""


def _station_line(body: str, icao: str, *, newest: bool) -> str | None:
    """Pick the first or last line for ``icao`` from a multi-line body.

    Parameters
    ----------
    body : str
        Feed text body.
    icao : str
        Station id.
    newest : bool
        When True, keep the last match; otherwise return the first.

    Returns
    -------
    str or None
        Matching line, or None.
    """
    found: str | None = None
    for raw in body.splitlines():
        line = raw.strip()
        if line and _canonical_station(line) == icao:
            found = line
            if not newest:
                return found
    return found


class FeedFetcher:
    """HTTP fetch against fixed allowlisted aviation feed hosts.

    Attributes
    ----------
    _http_get : HttpGet
        Injectable GET callable.
    _allowlist : Allowlist
        Egress allowlist for host checks.
    _knmi_key : str or None
        Optional KNMI API key override.
    """

    def __init__(
        self,
        *,
        http_get: HttpGet | None = None,
        allowlist: Allowlist | None = None,
        knmi_api_key: str | None = None,
    ) -> None:
        """Create a fetcher.

        Parameters
        ----------
        http_get : HttpGet or None, optional
            Injectable GET. By default uses httpx.
        allowlist : Allowlist or None, optional
            Egress allowlist. By default from env or built-in hosts.
        knmi_api_key : str or None, optional
            KNMI key override. By default ``None``.
        """
        self._http_get = http_get or self._default_http_get
        self._allowlist = allowlist or parse_allowlist(os.environ.get("LIVE_CHECK_EGRESS_ALLOWLIST", DEFAULT_ALLOWLIST))
        self._knmi_key = knmi_api_key

    def fetch(self, provider: str, icao: str, product: str) -> tuple[str, str | None]:
        """Fetch source TAC and optional provider IWXXM.

        Parameters
        ----------
        provider : str
            Allowlisted provider id.
        icao : str
            Station id.
        product : str
            METAR or TAF.

        Returns
        -------
        tuple of (str, str or None)
            Source TAC and optional provider IWXXM.

        Examples
        --------
        >>> 1 + 1
        2
        """
        if provider == "noaa":
            return self._fetch_noaa(icao, product)
        if provider == "met_no":
            return self._fetch_met_no(icao, product)
        return self._fetch_knmi(icao)

    def _fetch_noaa(self, icao: str, product: str) -> tuple[str, str | None]:
        """Fetch NOAA AWC TAC and optional IWXXM.

        Parameters
        ----------
        icao : str
            Station id.
        product : str
            METAR or TAF.

        Returns
        -------
        tuple of (str, str or None)
            TAC and optional IWXXM.
        """
        params: dict[str, str] = {"ids": icao, "format": "raw"}
        if product == "METAR":
            params["hours"] = "6"
        tac = _station_line(self._get_text(_AWC[product], params=params), icao, newest=False)
        if tac is None:
            raise LiveCheckError(404, f"noaa returned no {product} for {icao}")
        try:
            xml_body = self._get_text(_AWC[product], params={**params, "format": "iwxxm"}).strip()
            return tac, xml_body or None
        except LiveCheckError:
            return tac, None

    def _fetch_met_no(self, icao: str, product: str) -> tuple[str, str | None]:
        """Fetch MET Norway TAC (no provider IWXXM).

        Parameters
        ----------
        icao : str
            Station id.
        product : str
            METAR or TAF.

        Returns
        -------
        tuple of (str, str or None)
            TAC and None.
        """
        tac = _station_line(self._get_text(_MET_NO[product], params={"icao": icao}), icao, newest=True)
        if tac is None:
            raise LiveCheckError(404, f"met_no returned no {product} for {icao}")
        return tac, None

    def _fetch_knmi(self, icao: str) -> tuple[str, str | None]:
        """Fetch KNMI METAR TAC embedded in IWXXM comments.

        Parameters
        ----------
        icao : str
            Station id.

        Returns
        -------
        tuple of (str, str or None)
            TAC and enclosing provider XML when present.
        """
        key = self._knmi_key
        if key is None:
            key = os.environ.get(KNMI_API_KEY_ENV, "").strip() or None
        if not key:
            raise LiveCheckError(503, "KNMI open data key is not configured")
        headers = {"Authorization": key}
        listing = self._get_json(
            _KNMI_FILES,
            params={"maxKeys": "1", "orderBy": "created", "sorting": "desc"},
            headers=headers,
        )
        files = listing.get("files")
        if not isinstance(files, list) or not files or not isinstance(files[0], dict):
            raise LiveCheckError(502, "KNMI file list was empty")
        filename = cast("dict[str, object]", files[0]).get("filename")
        if not isinstance(filename, str) or not filename:
            raise LiveCheckError(502, "KNMI file entry had no filename")
        url_payload = self._get_json(f"{_KNMI_FILES}/{filename}/url", headers=headers)
        download = url_payload.get("temporaryDownloadUrl")
        if not isinstance(download, str) or not download:
            raise LiveCheckError(502, "KNMI did not return a download URL")
        self._assert_knmi_download_host(download)
        body = self._get_text(download, check_host=False)
        for match in _KNMI_TAC_COMMENT.finditer(body):
            text = " ".join(match.group(1).split())
            if _canonical_station(text) != icao:
                continue
            start = body.rfind("<?xml", 0, match.start())
            end = body.find("</iwxxm:METAR>", match.end())
            xml = body[start : end + len("</iwxxm:METAR>")].strip() if start >= 0 and end > start else None
            return text, xml
        raise LiveCheckError(404, f"knmi returned no METAR for {icao}")

    def _assert_host(self, url: str) -> None:
        """Deny non-allowlisted hosts.

        Parameters
        ----------
        url : str
            Absolute URL to check.
        """
        host = urlparse(url).hostname
        if not host:
            raise LiveCheckError(400, "feed URL missing host")
        try:
            validate_egress_host(host, allowlist=self._allowlist)
        except EgressDenied as exc:
            raise LiveCheckError(403, "feed host is not allowlisted") from exc

    def _assert_knmi_download_host(self, url: str) -> None:
        """Validate a KNMI temporary download URL host.

        Parameters
        ----------
        url : str
            Temporary download URL from KNMI.
        """
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme != "https" or not host:
            raise LiveCheckError(403, "KNMI download host denied")
        try:
            validate_egress_host(host, allowlist=self._allowlist)
            return
        except EgressDenied:
            pass
        if not any(host == s.lstrip(".") or host.endswith(s) for s in _KNMI_DOWNLOAD_SUFFIXES):
            raise LiveCheckError(403, "KNMI download host is not allowlisted")
        try:
            validate_egress_host(host, allowlist=parse_allowlist(f"{DEFAULT_ALLOWLIST},{host}"))
        except EgressDenied as exc:
            raise LiveCheckError(403, "KNMI download host denied") from exc

    def _get_text(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        check_host: bool = True,
    ) -> str:
        """GET a text body from an allowlisted host.

        Parameters
        ----------
        url : str
            Request URL.
        params : dict or None, optional
            Query params.
        headers : dict or None, optional
            Extra headers.
        check_host : bool, optional
            When False, skip allowlist (already validated).

        Returns
        -------
        str
            Response text.
        """
        if check_host:
            self._assert_host(url)
        response = self._http_get(url, params=params, headers=headers)
        if response.status_code >= 400:
            raise LiveCheckError(502, f"feed request failed ({response.status_code})")
        return response.text

    def _get_json(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        """GET a JSON object from an allowlisted host.

        Parameters
        ----------
        url : str
            Request URL.
        params : dict or None, optional
            Query params.
        headers : dict or None, optional
            Extra headers.

        Returns
        -------
        dict of str to object
            Parsed JSON object.
        """
        self._assert_host(url)
        response = self._http_get(url, params=params, headers=headers)
        if response.status_code >= 400:
            raise LiveCheckError(502, f"feed request failed ({response.status_code})")
        data = response.json()
        if not isinstance(data, dict):
            raise LiveCheckError(502, "feed returned a non-object JSON body")
        return cast("dict[str, object]", data)

    @staticmethod
    def _default_http_get(
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Perform a synchronous httpx GET without following redirects.

        Parameters
        ----------
        url : str
            Request URL.
        params : dict or None, optional
            Query params.
        headers : dict or None, optional
            Extra headers.

        Returns
        -------
        httpx.Response
            HTTP response.
        """
        merged = {"User-Agent": USER_AGENT, **(headers or {})}
        with httpx.Client(timeout=30.0, follow_redirects=False) as client:
            return client.get(url, params=params, headers=merged)
