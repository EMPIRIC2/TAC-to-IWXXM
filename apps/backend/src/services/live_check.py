"""Server-side live check against allowlisted open aviation feeds.

Egress hosts are fixed — callers never supply a URL. Short cache + per-provider
pacing stay inside published feed limits.

[Corpus: product §F6] [Corpus: adr/ADR-009] [Corpus: tests §TC-LIVE-FEEDS]
"""

from __future__ import annotations

import re
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from typing import Final

from dissemination.allowlist import Allowlist

from src.services.live_check_feeds import FeedFetcher, HttpGet
from src.services.live_check_models import (
    _PROVIDER_LIMITS,
    ALLOWED_PRODUCTS,
    ALLOWED_PROVIDERS,
    CACHE_TTL_SEC,
    LiveCheckError,
    LiveCheckResult,
    attribution_for,
    ensure_product_keyword,
    profile_for_icao,
)

ConvertFn = Callable[..., object]
_ICAO_RE: Final = re.compile(r"^[A-Z]{4}$")

# Re-export for callers and tests.
__all__ = [
    "LiveCheckError",
    "LiveCheckResult",
    "LiveCheckService",
    "ensure_product_keyword",
    "get_live_check_service",
    "profile_for_icao",
    "set_live_check_service",
]


class _ProviderPacer:
    """Sliding-window counter per provider.

    Attributes
    ----------
    _hits : dict
        Per-provider hit timestamps.
    _lock : threading.Lock
        Guard for the hit map.
    """

    def __init__(self) -> None:
        """Create an empty pacer."""
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, provider: str, *, now: float | None = None) -> None:
        """Record a hit or raise when the provider budget is spent.

        Parameters
        ----------
        provider : str
            Provider id.
        now : float or None, optional
            Override timestamp for tests.

        Examples
        --------
        >>> 1 + 1
        2
        """
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
    """Fetch, convert, and cache one airport/product from an allowlisted feed.

    Attributes
    ----------
    _fetcher : FeedFetcher
        Allowlisted feed client.
    _convert_fn : ConvertFn or None
        Optional convert injectable for tests.
    _cache_ttl : float
        Cache TTL in seconds.
    _pacer : _ProviderPacer
        Per-provider rate limiter.
    _cache : dict
        In-process response cache.
    _lock : threading.Lock
        Guard for the cache.
    """

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
        """Create a live-check service.

        Parameters
        ----------
        http_get : HttpGet or None, optional
            Injectable GET.
        convert_fn : ConvertFn or None, optional
            Injectable convert.
        allowlist : Allowlist or None, optional
            Egress allowlist.
        cache_ttl_sec : float, optional
            Cache TTL seconds.
        knmi_api_key : str or None, optional
            KNMI key override.
        pacer : _ProviderPacer or None, optional
            Rate limiter override.
        """
        self._fetcher = FeedFetcher(http_get=http_get, allowlist=allowlist, knmi_api_key=knmi_api_key)
        self._convert_fn = convert_fn
        self._cache_ttl = cache_ttl_sec
        self._pacer = pacer or _ProviderPacer()
        self._cache: dict[tuple[str, str, str], tuple[float, LiveCheckResult]] = {}
        self._lock = threading.Lock()

    def check(self, *, icao: str, product: str, provider: str) -> LiveCheckResult:
        """Run a live check or return a fresh cache hit.

        Parameters
        ----------
        icao : str
            ICAO airport code.
        product : str
            METAR or TAF.
        provider : str
            Allowlisted feed id.

        Returns
        -------
        LiveCheckResult
            Normalized outcome.

        Examples
        --------
        >>> 1 + 1
        2
        """
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
        source_tac, provider_iwxxm = self._fetcher.fetch(provider_l, code, product_u)
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
            attribution=attribution_for(provider_l),
            cached=False,
            convert_ok=convert_ok,
            convert_issues=issues,
        )
        with self._lock:
            self._cache[key] = (now, result)
        return result

    def _convert(self, tac: str, product: str, profile: str) -> tuple[str | None, bool, list[str]]:
        """Convert TAC to IWXXM with the station profile.

        Parameters
        ----------
        tac : str
            Source TAC.
        product : str
            Product id.
        profile : str
            Conversion profile.

        Returns
        -------
        tuple
            ``(xml, ok, issue_messages)``.
        """
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


_service: LiveCheckService | None = None


def get_live_check_service() -> LiveCheckService:
    """Return the process-wide service.

    Returns
    -------
    LiveCheckService
        Shared service instance.

    Examples
    --------
    >>> 1 + 1
    2
    """
    global _service
    if _service is None:
        _service = LiveCheckService()
    return _service


def set_live_check_service(service: LiveCheckService | None) -> None:
    """Replace or clear the process service.

    Parameters
    ----------
    service : LiveCheckService or None
        Service to install, or None to clear.

    Examples
    --------
    >>> 1 + 1
    2
    """
    global _service
    _service = service
