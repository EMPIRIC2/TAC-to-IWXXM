"""IWXXM pin ↔ Schematron bundle match (TC-EVYFC-004 / D-YFC-05 / #1231).

Vendor Schematron remains SoT. Convert and validate paths must use the SCH
file that lives under the same pin tree as the IWXXM XSD, and the SCH must
declare the namespace URI for that pin.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from iwxxm_validate.paths import schematron_path, version_dir, xsd_path

# Directory pin → Schematron ``iwxxm`` namespace URI fragment after ``…/iwxxm/``.
_PIN_NS_FRAGMENT: dict[str, str] = {
    "2023-1": "2023-1",
    "2025-2": "2025-2",
    "3.0.0": "3.0",
}


class PinSchError(ValueError):
    """IWXXM pin and Schematron bundle do not match."""


@dataclass(frozen=True, slots=True)
class PinSchBundle:
    """Resolved XSD + Schematron paths for one IWXXM pin."""

    pin: str
    version_root: Path
    xsd: Path
    schematron: Path
    namespace_uri: str


# Process-local cache — pin trees are immutable at runtime; avoids re-reading SCH
# on every convert (converter PR gate / hot path).
_BUNDLE_CACHE: dict[str, PinSchBundle] = {}


def clear_pin_sch_cache() -> None:
    """Drop cached pin↔SCH bundles (tests / path monkeypatches)."""
    _BUNDLE_CACHE.clear()


def expected_iwxxm_namespace(iwxxm_version: str) -> str:
    """Return the ICAO IWXXM namespace URI expected for ``iwxxm_version``."""
    fragment = _PIN_NS_FRAGMENT.get(iwxxm_version.strip())
    if fragment is None:
        msg = f"unsupported IWXXM pin for pin↔SCH check: {iwxxm_version!r}"
        raise PinSchError(msg)
    return f"http://icao.int/iwxxm/{fragment}"


def assert_pin_schematron_match(iwxxm_version: str) -> PinSchBundle:
    """
    Fail-closed: Schematron for ``iwxxm_version`` must live under that pin tree
    and declare the matching ``iwxxm`` namespace URI.

    Parameters
    ----------
    iwxxm_version :
        Release pin (``2023-1``, ``2025-2``, ``3.0.0``).

    Returns
    -------
    PinSchBundle
        Resolved paths when the check passes.

    Raises
    ------
    PinSchError
        When the pin is unknown, files are missing, SCH is outside the pin tree,
        or the SCH namespace URI does not match the pin.
    """
    pin = iwxxm_version.strip()
    cached = _BUNDLE_CACHE.get(pin)
    if cached is not None:
        return cached

    ns_uri = expected_iwxxm_namespace(pin)
    try:
        root = version_dir(pin)
        xsd = xsd_path(pin)
        sch = schematron_path(pin)
    except FileNotFoundError as exc:
        raise PinSchError(str(exc)) from exc

    try:
        sch.resolve().relative_to(root.resolve())
        xsd.resolve().relative_to(root.resolve())
    except ValueError as exc:
        msg = f"XSD/SCH for pin {pin!r} must live under {root}: xsd={xsd} sch={sch}"
        raise PinSchError(msg) from exc

    try:
        head = sch.read_text(encoding="utf-8", errors="replace")[:8000]
    except OSError as exc:
        msg = f"cannot read Schematron for pin {pin!r}: {sch}"
        raise PinSchError(msg) from exc

    needle = f'uri="{ns_uri}"'
    alt = f"uri='{ns_uri}'"
    if needle not in head and alt not in head:
        msg = f"Schematron for pin {pin!r} must declare iwxxm namespace {ns_uri!r} (file={sch})"
        raise PinSchError(msg)

    bundle = PinSchBundle(
        pin=pin,
        version_root=root,
        xsd=xsd,
        schematron=sch,
        namespace_uri=ns_uri,
    )
    _BUNDLE_CACHE[pin] = bundle
    return bundle


__all__ = [
    "PinSchBundle",
    "PinSchError",
    "assert_pin_schematron_match",
    "clear_pin_sch_cache",
    "expected_iwxxm_namespace",
]
