"""Shared types and helpers for the live-check service.

[Corpus: product §F6]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

ALLOWED_PROVIDERS: Final = frozenset({"noaa", "met_no", "knmi"})
ALLOWED_PRODUCTS: Final = frozenset({"METAR", "TAF"})
_ATTRIBUTION: Final[dict[str, str]] = {
    "noaa": "NOAA Aviation Weather Center — US public data",
    "met_no": "MET Norway tafmetar — NLOD 2.0 / CC BY 4.0",
    "knmi": "KNMI Open Data METAR — CC BY 4.0",
}
_PROVIDER_LIMITS: Final[dict[str, tuple[int, float]]] = {
    "noaa": (90, 60.0),
    "met_no": (30, 60.0),
    "knmi": (15, 60.0),
}
CACHE_TTL_SEC: Final = 60.0


class LiveCheckError(Exception):
    """Mapped to an HTTP error by the router.

    Attributes
    ----------
    status_code : int
        HTTP status to return.
    detail : str
        Operator-safe error detail.
    """

    def __init__(self, status_code: int, detail: str) -> None:
        """Store status and detail.

        Parameters
        ----------
        status_code : int
            HTTP status.
        detail : str
            Error detail text.
        """
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass(frozen=True, slots=True)
class LiveCheckResult:
    """Normalized live-check outcome.

    Attributes
    ----------
    icao : str
        Station id.
    product : str
        METAR or TAF.
    provider : str
        Feed id.
    profile : str
        Conversion profile.
    source_tac : str
        Source TAC text.
    our_iwxxm : str or None
        Converted IWXXM.
    provider_iwxxm : str or None
        Provider IWXXM when present.
    attribution : str or None
        License attribution.
    cached : bool
        Cache hit flag.
    convert_ok : bool
        Conversion success flag.
    convert_issues : list of str
        Convert issue messages.
    """

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
    """Choose conversion profile from the ICAO station id.

    Parameters
    ----------
    icao : str
        Station id.

    Returns
    -------
    str
        ``iwxxm_us``, ``ca_eccc``, or ``annex3``.

    Examples
    --------
    >>> profile_for_icao("KJFK")
    'iwxxm_us'
    """
    code = icao.strip().upper()
    if code.startswith("K"):
        return "iwxxm_us"
    if code.startswith("CY"):
        return "ca_eccc"
    return "annex3"


def ensure_product_keyword(text: str, product: str) -> str:
    """Prepend the product keyword when the feed omits it.

    Parameters
    ----------
    text : str
        Raw TAC.
    product : str
        Product keyword.

    Returns
    -------
    str
        TAC with a leading product keyword.

    Examples
    --------
    >>> ensure_product_keyword("KJFK 231751Z", "METAR").startswith("METAR ")
    True
    """
    stripped = " ".join(text.split())
    return stripped if stripped.startswith(f"{product} ") else f"{product} {stripped}"


def attribution_for(provider: str) -> str:
    """Return attribution text for a provider.

    Parameters
    ----------
    provider : str
        Allowlisted provider id.

    Returns
    -------
    str
        Attribution string.

    Examples
    --------
    >>> "KNMI" in attribution_for("knmi")
    True
    """
    return _ATTRIBUTION[provider]
