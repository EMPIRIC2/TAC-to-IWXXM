"""Product constants and keyword map for F6 TAC forms plus F28 SWXA / F32 VONA."""

from __future__ import annotations

PRODUCTS: tuple[str, ...] = (
    "AIRMET",
    "METAR",
    "SIGMET",
    "SPECI",
    "TAF",
    "VAA",
    "TCA",
    "SWXA",
    "VONA",
)

# Leading TAC keywords / bulletin markers used by the parse-gate skeleton.
PRODUCT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "AIRMET": ("AIRMET",),
    "METAR": ("METAR",),
    "SIGMET": ("SIGMET",),
    "SPECI": ("SPECI",),
    "TAF": ("TAF",),
    "VAA": ("VA ADVISORY", "VAA"),
    "TCA": ("TC ADVISORY", "TCA"),
    "SWXA": ("SWX ADVISORY", "SWXA"),
    "VONA": ("VONA",),
}

__all__ = ["PRODUCTS", "PRODUCT_KEYWORDS"]
