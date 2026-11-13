"""WMO-No. 782 extended METAR/SPECI combination emitters (family modules)."""

from __future__ import annotations

__all__ = ["check_wmo782_extended"]


def __getattr__(name: str) -> object:
    if name == "check_wmo782_extended":
        from tac_validate.product_rules_pkg.wmo782.check import check_wmo782_extended

        return check_wmo782_extended
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
