"""Compatibility aliases for Canonical XML helpers (EV-layout-dx).

Prefer :mod:`iwxxm_validate.canonical_xml` and the names ``to_canonical_xml`` /
``canonical_xml_equal``. This module re-exports the same objects for one CalVer
window so existing ``from iwxxm_validate.c14n import …`` call sites keep working.

Canonical XML means W3C Canonical XML 1.0 (also called C14N).
"""

from __future__ import annotations

from iwxxm_validate.canonical_xml import (
    VOLATILE_ATTRS,
    c14n_equal,
    c14n_xml,
    canonical_xml_equal,
    to_canonical_xml,
)

__all__ = [
    "VOLATILE_ATTRS",
    "c14n_equal",
    "c14n_xml",
    "canonical_xml_equal",
    "to_canonical_xml",
]
