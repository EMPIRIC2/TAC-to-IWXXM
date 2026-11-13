"""Server-side live check against allowlisted open aviation feeds.

Egress hosts are fixed — callers never supply a URL. Short cache + per-provider
pacing stay inside published feed limits.

[Corpus: product §F6] [Corpus: adr/ADR-009] [Corpus: tests §TC-LIVE-FEEDS]
"""

from __future__ import annotations

import os
import re
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final, cast
from urllib.parse import urlparse

import httpx
from dissemination.allowlist import Allowlist, EgressDenied, parse_allowlist, validate_egress_host

USER_AGENT: Final = "TAC-to-IWXXM-live-check/1.0 github.com/EMPIRIC2/TAC-to-IWXXM"
KNMI_API_KEY_ENV: Final = "KNMI_OPEN_DATA_API_KEY"
CACHE_TTL_SEC: Final = 60.0
DEFAULT_ALLOWLIST: Final = "aviationweather.gov,api.met.no,api.dataplatform.knmi.nl"
_KNMI_DOWNLOAD_SUFFIXES: Final = (".knmi.nl", ".blob.core.windows.net", ".amazonaws.com")
ALLOWED_PROVIDERS: Final = frozenset({"noaa", "met_no", "knmi"})
ALLOWED_PRODUCTS: Final = frozenset({"METAR", "TAF"})
_PROVIDER_LIMITS: Final[dict[str, tuple[int, float]]] = {
    "noaa": (90, 60.0),
    "met_no": (30, 60.0),
    "knmi": (15, 60.0),
}
_ATTRIBUTION: Final[dict[str, str]] = {
    "noaa": "NOAA Aviation Weather Center — US public data",
    "met_no": "MET Norway tafmetar — NLOD 2.0 / CC BY 4.0",
    "knmi": "KNMI Open Data METAR — CC BY 4.0",
}
_AWC = {
    "METAR": "https://aviationweather.gov/api/data/metar",
    "TAF": "https://aviationweather.gov/api/data/taf",
}
_MET_NO = {
    "METAR": "https://api.met.no/weatherapi/tafmetar/1.0/metar.txt",
    "TAF": "https://api.met.no/weatherapi/tafmetar/1.0/taf.txt",
}
_KNMI_FILES = "https://api.dataplatform.knmi.nl/open-data/v1/datasets/metar/versions/1.0/files"
_ICAO_RE = re.compile(r"^[A-Z]{4}$")
_KNMI_TAC_COMMENT = re.compile(r"<!--\s*((?:METAR|SPECI)\s+[A-Z]{4}\b.*?)\s*-->", re.DOTALL)
_PRODUCT_KEYWORDS = frozenset({"METAR", "SPECI", "TAF"})

HttpGet = Callable[..., httpx.Response]
ConvertFn = Callable[..., object]


class LiveCheckError(Exception):
    """Mapped to an HTTP error by the router."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass(frozen=True, slots=True)
class LiveCheckResult:
    """Normalized live-check outcome."""

    icao: str
    product: str
    provider: str
    profile: str
    source_tac: str
    our_iwxxm: str | None
    provider_iwxxm: str | None
    attribution: str | None
    cached: bool
    convert_ok: bool
    convert_issues: list[str]


def profile_for_icao(icao: str) -> str:
    """US ``K*`` → ``iwxxm_us``, Canadian ``CY*`` → ``ca_eccc``, else Annex 3."""
    code = icao.strip().upper()
    if code.startswith("K"):
        return "iwxxm_us"
    if code.startswith("CY"):
        return "ca_eccc"
    return "annex3"


def ensure_product_keyword(text: str, product: str) -> str:
    """Prepend the product keyword when the feed omits it."""
    stripped = " ".join(text.split())
    return stripped if stripped.startswith(f"{product} ") else f"{product} {stripped}"


def _canonical_station(text: str) -> str:
    parts = text.replace("=", " ").split()
    if parts and parts[0] in _PRODUCT_KEYWORDS:
        parts = parts[1:]
    return parts[0] if parts else ""


def _station_line(body: str, icao: str, *, newest: bool) -> str | None:
    found: str | None = None
    for raw in body.splitlines():
        line = raw.strip()
        if line and _canonical_station(line) == icao:
            found = line
            if not newest:
                return found
    return found


class _ProviderPacer:
    """Sliding-window counter per provider."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, provider: str, *, now: float | None = None) -> None:
        max_hits, window = _PROVIDER_LIMITS[provider]
        ts = time.time() if now is None else now
        with self._lock:
            q = self._hits[provider]
            while q and q[0] < ts - window:
                q.popleft()
            if len(q) >= max_hits:
                raise LiveCheckError(429, f"Live check rate limit for {provider} exceeded")
            q.append(ts)


class LiveCheckService:
    """Fetch, convert, and cache one airport/product from an allowlisted feed."""

    def __init__(
        self,
        *,
        http_get: HttpGet | None = None,
        convert_fn: ConvertFn | None = None,
        allowlist: Allowlist | None = None,
        cache_ttl_sec: float = CACHE_TTL_SEC,
        knmi_api_key: str | None = None,
        pacer: _ProviderPacer | None = None,
    ) -> None:
        self._http_get = http_get or self._default_http_get
        self._convert_fn = convert_fn
        self._allowlist = allowlist or parse_allowlist(os.environ.get("LIVE_CHECK_EGRESS_ALLOWLIST", DEFAULT_ALLOWLIST))
        self._cache_ttl = cache_ttl_sec
        self._knmi_key = knmi_api_key
        self._pacer = pacer or _ProviderPacer()
        self._cache: dict[tuple[str, str, str], tuple[float, LiveCheckResult]] = {}
        self._lock = threading.Lock()

    def check(self, *, icao: str, product: str, provider: str) -> LiveCheckResult:
        """Run a live check or return a fresh cache hit."""
        code, product_u, provider_l = (
            icao.strip().upper(),
            product.strip().upper(),
            provider.strip().lower(),
        )
        if not _ICAO_RE.match(code):
            raise LiveCheckError(400, "icao must be a four-letter ICAO code")
        if product_u not in ALLOWED_PRODUCTS:
            raise LiveCheckError(400, "product must be METAR or TAF")
        if provider_l not in ALLOWED_PROVIDERS:
            raise LiveCheckError(400, "provider is not allowlisted")
        if provider_l == "knmi" and product_u != "METAR":
            raise LiveCheckError(400, "knmi supports METAR only")

        key = (provider_l, code, product_u)
        now = time.time()
        with self._lock:
            hit = self._cache.get(key)
            if hit is not None and now - hit[0] < self._cache_ttl:
                c = hit[1]
                return LiveCheckResult(
                    icao=c.icao,
                    product=c.product,
                    provider=c.provider,
                    profile=c.profile,
                    source_tac=c.source_tac,
                    our_iwxxm=c.our_iwxxm,
                    provider_iwxxm=c.provider_iwxxm,
                    attribution=c.attribution,
                    cached=True,
                    convert_ok=c.convert_ok,
                    convert_issues=list(c.convert_issues),
                )

        self._pacer.check(provider_l, now=now)
        source_tac, provider_iwxxm = self._fetch(provider_l, code, product_u)
        profile = profile_for_icao(code)
        our_iwxxm, convert_ok, issues = self._convert(source_tac, product_u, profile)
        result = LiveCheckResult(
            icao=code,
            product=product_u,
            provider=provider_l,
            profile=profile,
            source_tac=source_tac,
            our_iwxxm=our_iwxxm,
            provider_iwxxm=provider_iwxxm,
            attribution=_ATTRIBUTION[provider_l],
            cached=False,
            convert_ok=convert_ok,
            convert_issues=issues,
        )
        with self._lock:
            self._cache[key] = (now, result)
        return result

    def _convert(self, tac: str, product: str, profile: str) -> tuple[str | None, bool, list[str]]:
        convert = self._convert_fn
        if convert is None:
            from tac2iwxxm import convert as tac2iwxxm_convert

            convert = tac2iwxxm_convert
        outcome = convert(
            ensure_product_keyword(tac, product),
            product=product,
            profile=profile,
            iwxxm_version="2025-2",
        )
        ok = bool(getattr(outcome, "ok", False))
        xml = getattr(outcome, "xml", None)
        messages = [
            f"{getattr(i, 'code', 'ISSUE')}: {getattr(i, 'message', i)}" for i in (getattr(outcome, "issues", ()) or ())
        ]
        return (str(xml) if xml else None, ok, messages)

    def _fetch(self, provider: str, icao: str, product: str) -> tuple[str, str | None]:
        if provider == "noaa":
            return self._fetch_noaa(icao, product)
        if provider == "met_no":
            return self._fetch_met_no(icao, product)
        return self._fetch_knmi(icao)

    def _fetch_noaa(self, icao: str, product: str) -> tuple[str, str | None]:
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
        tac = _station_line(self._get_text(_MET_NO[product], params={"icao": icao}), icao, newest=True)
        if tac is None:
            raise LiveCheckError(404, f"met_no returned no {product} for {icao}")
        return tac, None

    def _fetch_knmi(self, icao: str) -> tuple[str, str | None]:
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
        host = urlparse(url).hostname
        if not host:
            raise LiveCheckError(400, "feed URL missing host")
        try:
            validate_egress_host(host, allowlist=self._allowlist)
        except EgressDenied as exc:
            raise LiveCheckError(403, "feed host is not allowlisted") from exc

    def _assert_knmi_download_host(self, url: str) -> None:
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
        merged = {"User-Agent": USER_AGENT, **(headers or {})}
        with httpx.Client(timeout=30.0, follow_redirects=False) as client:
            return client.get(url, params=params, headers=merged)


_service: LiveCheckService | None = None


def get_live_check_service() -> LiveCheckService:
    """Process-wide service (tests may replace via ``set_live_check_service``)."""
    global _service
    if _service is None:
        _service = LiveCheckService()
    return _service


def set_live_check_service(service: LiveCheckService | None) -> None:
    """Replace or clear the process service."""
    global _service
    _service = service
