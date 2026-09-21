"""Schematron assert inventory for a primary IWXXM pin (ADR-046 / #1216 M4).

Ids are ``sch:pattern/@id`` values from the pin's ``*.sch`` files. Vendor Schematron
remains the executable source of truth; this set is the policy membership list.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from iwxxm_validate.paths import vendor_iwxxm_root

_PATTERN_ID = re.compile(r"""<(?:[\w.-]+:)?pattern\b[^>]*\bid\s*=\s*["']([^"']+)["']""")


class InventoryError(ValueError):
    """Assert inventory could not be loaded for a pin."""


def _collect_pattern_ids(pin_root: Path) -> frozenset[str]:
    ids: set[str] = set()
    for path in sorted(pin_root.rglob("*.sch")):
        text = path.read_text(encoding="utf-8", errors="replace")
        ids.update(_PATTERN_ID.findall(text))
    return frozenset(ids)


@lru_cache(maxsize=8)
def load_assert_inventory(pin: str) -> frozenset[str]:
    """
    Return Schematron pattern ids for ``pin`` (for example ``2025-2``).

    Parameters
    ----------
    pin :
        IWXXM release directory name under the schema root.
    """
    pin_root = vendor_iwxxm_root() / pin
    if not pin_root.is_dir():
        msg = f"IWXXM pin directory not found: {pin}"
        raise InventoryError(msg)
    ids = _collect_pattern_ids(pin_root)
    if not ids:
        msg = f"no Schematron pattern ids under pin {pin}"
        raise InventoryError(msg)
    return ids


def load_assert_inventory_from(pin_root: Path) -> frozenset[str]:
    """Load pattern ids from an explicit pin directory (tests and overlays)."""
    if not pin_root.is_dir():
        msg = f"IWXXM pin directory not found: {pin_root}"
        raise InventoryError(msg)
    ids = _collect_pattern_ids(pin_root)
    if not ids:
        msg = f"no Schematron pattern ids under {pin_root}"
        raise InventoryError(msg)
    return ids


__all__ = [
    "InventoryError",
    "load_assert_inventory",
    "load_assert_inventory_from",
]
