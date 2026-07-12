"""Product constants and keyword map for the seven F6 TAC forms."""

from __future__ import annotations

PRODUCTS: tuple[str, ...] = ("AIRMET", "METAR", "SIGMET", "SPECI", "TAF", "VAA", "TCA")

# Leading TAC keywords / bulletin markers used by the parse-gate skeleton.
PRODUCT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "AIRMET": ("AIRMET",),
    "METAR": ("METAR",),
    "SIGMET": ("SIGMET",),
    "SPECI": ("SPECI",),
    "TAF": ("TAF",),
    "VAA": ("VA ADVISORY", "VAA"),
    "TCA": ("TC ADVISORY", "TCA"),
}

__all__ = ["PRODUCT_KEYWORDS", "PRODUCTS"]
