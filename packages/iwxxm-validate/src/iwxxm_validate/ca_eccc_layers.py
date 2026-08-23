"""CA_ECCC layered validation stages (EV-068 / #1035).

Stage ids align with ``docs/domain/profiles/catalog.yaml`` ``validation_stages``.
M1 scaffold: bundle resolution + stage registry; full pipeline wired EV-068–069.
"""

from __future__ import annotations

from pathlib import Path

from iwxxm_validate.ca_eccc_bundle import (
    CA_ECCC_EXTENSION_TAG as CA_EXTENSION_TAG,
)
from iwxxm_validate.ca_eccc_bundle import (
    CA_ECCC_IWXXM_VERSION as CA_IWXXM_VERSION,
)
from iwxxm_validate.ca_eccc_bundle import (
    ca_eccc_bundle_available,
)
from iwxxm_validate.paths import vendor_iwxxm_ca_root

STAGE_WELLFORMED = "wellformed"
STAGE_WMO_XSD = "wmo_xsd"
STAGE_WMO_SCH = "wmo_schematron"
STAGE_CA_XSD = "ca_xsd"
STAGE_CODE_CA = "code_ca"
STAGE_EXCHANGE = "exchange"

CA_VALIDATION_STAGES: tuple[str, ...] = (
    STAGE_WELLFORMED,
    STAGE_WMO_XSD,
    STAGE_WMO_SCH,
    STAGE_CA_XSD,
    STAGE_CODE_CA,
    STAGE_EXCHANGE,
)

CA_STAGE_LABELS: dict[str, str] = {
    STAGE_WELLFORMED: "Well-formed XML",
    STAGE_WMO_XSD: "WMO IWXXM 3.0.0 schema",
    STAGE_WMO_SCH: "WMO IWXXM 3.0.0 rules",
    STAGE_CA_XSD: "Canadian extension schema",
    STAGE_CODE_CA: "Canadian code lists",
    STAGE_EXCHANGE: "Exchange packaging checks",
}

CA_PRODUCT_XSD: dict[str, str] = {
    "METAR": "metar-speci-ca.xsd",
    "SPECI": "metar-speci-ca.xsd",
    "TAF": "taf-ca.xsd",
    "AIRMET": "airmet-ca.xsd",
}

# EV-068: layers 1–4; EV-069: layers 5–6 (#1033 / #1032).
IMPLEMENTED_CA_STAGES: frozenset[str] = frozenset(
    {
        STAGE_WELLFORMED,
        STAGE_WMO_XSD,
        STAGE_WMO_SCH,
        STAGE_CA_XSD,
        STAGE_CODE_CA,
        STAGE_EXCHANGE,
    }
)


def ca_iwxxm_core_xsd_path() -> Path | None:
    """Return vendored IWXXM 3.0.0 core ``iwxxm.xsd`` when present."""
    from iwxxm_validate.ca_eccc_bundle import resolve_ca_eccc_bundle

    bundle = resolve_ca_eccc_bundle()
    return bundle.core_xsd if bundle is not None else None


def ca_product_xsd_path(product: str, *, tag: str = CA_EXTENSION_TAG) -> Path | None:
    """
    Resolve product-specific Canadian extension XSD for layer 4.

    Parameters
    ----------
    product :
        API product enum (``METAR``, ``SPECI``, ``TAF``, ``AIRMET``).
    tag :
        MSC pin subdirectory (default ``3.0``).
    """
    xsd_name = CA_PRODUCT_XSD.get(product.upper())
    if xsd_name is None:
        return None
    root = vendor_iwxxm_ca_root()
    candidates = [root / tag / xsd_name, root / xsd_name]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def pending_ca_stages() -> tuple[str, ...]:
    """Return CA validation stages not yet implemented in the layered pipeline."""
    return tuple(stage for stage in CA_VALIDATION_STAGES if stage not in IMPLEMENTED_CA_STAGES)


__all__ = [
    "CA_EXTENSION_TAG",
    "CA_IWXXM_VERSION",
    "CA_PRODUCT_XSD",
    "CA_STAGE_LABELS",
    "CA_VALIDATION_STAGES",
    "IMPLEMENTED_CA_STAGES",
    "STAGE_CA_XSD",
    "STAGE_CODE_CA",
    "STAGE_EXCHANGE",
    "STAGE_WELLFORMED",
    "STAGE_WMO_SCH",
    "STAGE_WMO_XSD",
    "ca_eccc_bundle_available",
    "ca_iwxxm_core_xsd_path",
    "ca_product_xsd_path",
    "pending_ca_stages",
]
