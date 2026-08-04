"""Official WMO IWXXM TAC peer inventory for EV-027 / #815 (TC-EV027-001).

SoT: ``vendor/schemas/iwxxm/2025-2/IWXXM/examples/*.tac`` under the current pin.
Every in-scope stem is either registered in the FE sample catalog or explicitly deferred.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_PIN_EXAMPLES = _REPO_ROOT / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples"
_ANNEX3 = Path(__file__).resolve().parent / "annex3_golden"

# F6 + F28 + F32 — product prefixes / stems that belong on the WMO happy-path inventory.
_IN_SCOPE_PREFIXES = (
    "metar-",
    "speci-",
    "taf-",
    "sigmet-",
    "airmet-",
    "va-advisory-",
    "tc-advisory-",
    "spacewx-",
    "vona-",
)

_OUT_OF_HAPPY_PATH_SUBSTRINGS = ("translation-failed",)


@dataclass(frozen=True, slots=True)
class OfficialTacPeer:
    """One official WMO TAC peer stem from the vendor pin."""

    stem: str  # e.g. metar-A3-1
    disposition: str  # registered | deferred
    catalog_id: str | None = None
    annex3_tac: str | None = None  # filename under annex3_golden
    product: str | None = None
    deferral_reason: str | None = None
    issue: str | None = None


# Explicit inventory (checked, not inventing stems beyond the pin).
OFFICIAL_TAC_PEERS: tuple[OfficialTacPeer, ...] = (
    OfficialTacPeer(
        "metar-A3-1",
        "registered",
        catalog_id="metar_a3_1",
        annex3_tac="metar_a3_1.tac",
        product="METAR",
    ),
    OfficialTacPeer(
        "speci-A3-2",
        "registered",
        catalog_id="speci_a3_2",
        annex3_tac="speci_a3_2.tac",
        product="SPECI",
    ),
    OfficialTacPeer(
        "taf-A5-1",
        "registered",
        catalog_id="taf_a5_1",
        annex3_tac="taf_a5_1.tac",
        product="TAF",
    ),
    OfficialTacPeer(
        "taf-A5-2",
        "registered",
        catalog_id="taf_a5_2",
        annex3_tac="taf_a5_2.tac",
        product="TAF",
    ),
    OfficialTacPeer(
        "sigmet-A6-1a-TS",
        "registered",
        catalog_id="sigmet_a6_1a_ts",
        annex3_tac="sigmet_a6_1a_ts.tac",
        product="SIGMET",
    ),
    OfficialTacPeer(
        "sigmet-A6-1b-CNL",
        "registered",
        catalog_id="sigmet_a6_1b_cnl",
        annex3_tac="sigmet_a6_1b_cnl.tac",
        product="SIGMET",
    ),
    OfficialTacPeer(
        "sigmet-VA-EGGX",
        "registered",
        catalog_id="sigmet_va_eggx",
        annex3_tac="sigmet_va_eggx.tac",
        product="SIGMET",
    ),
    OfficialTacPeer(
        "sigmet-multi-location-VA",
        "registered",
        catalog_id="sigmet_multi_location_va",
        annex3_tac="sigmet_multi_location_va.tac",
        product="SIGMET",
    ),
    OfficialTacPeer(
        "sigmet-A6-2-TC",
        "registered",
        catalog_id="sigmet_a6_2_tc",
        annex3_tac="sigmet_a6_2_tc.tac",
        product="SIGMET",
    ),
    OfficialTacPeer(
        "airmet-A6-1a-TS",
        "registered",
        catalog_id="airmet_a6_1a_ts",
        annex3_tac="airmet_a6_1a_ts.tac",
        product="AIRMET",
    ),
    OfficialTacPeer(
        "va-advisory-A7-2",
        "registered",
        catalog_id="vaa_a7_2",
        annex3_tac="vaa_a7_2.tac",
        product="VAA",
    ),
    OfficialTacPeer(
        "tc-advisory-A2-2",
        "registered",
        catalog_id="tca_a2_2",
        annex3_tac="tca_a2_2.tac",
        product="TCA",
    ),
    OfficialTacPeer(
        "spacewx-A7-3",
        "registered",
        catalog_id="swxa_a7_3",
        annex3_tac="swxa_a7_3.tac",
        product="SWXA",
    ),
    OfficialTacPeer(
        "vona-A7-1",
        "registered",
        catalog_id="vona_a7_1",
        annex3_tac="vona_a7_1.tac",
        product="VONA",
    ),
    OfficialTacPeer(
        "spacewx-A7-4",
        "deferred",
        deferral_reason="Second/third WMO SWXA — single-seed catalog (F28 / TC-F28-005)",
        issue="#740",
    ),
    OfficialTacPeer(
        "spacewx-A7-5",
        "deferred",
        deferral_reason="Second/third WMO SWXA — single-seed catalog (F28 / TC-F28-005)",
        issue="#740",
    ),
    OfficialTacPeer(
        "metar-NIL-collect",
        "deferred",
        deferral_reason="COLLECT / validate shape — not sample-menu happy-path (EV-024)",
        issue="EV-024",
    ),
    OfficialTacPeer(
        "taf-NIL-collect",
        "deferred",
        deferral_reason="COLLECT / validate shape — not sample-menu happy-path (EV-024)",
        issue="EV-024",
    ),
)


def discover_pin_tac_stems() -> set[str]:
    """Return ``*.tac`` stems under the 2025-2 examples directory."""
    if not _PIN_EXAMPLES.is_dir():
        return set()
    return {p.stem for p in _PIN_EXAMPLES.glob("*.tac")}


def in_scope_pin_stems(pin_stems: set[str] | None = None) -> set[str]:
    """Filter pin stems to F6+F28 happy-path candidates (excludes quarantine products)."""
    stems = pin_stems if pin_stems is not None else discover_pin_tac_stems()
    out: set[str] = set()
    for stem in stems:
        low = stem.lower()
        if any(s in low for s in _OUT_OF_HAPPY_PATH_SUBSTRINGS):
            continue
        if not any(low.startswith(p) for p in _IN_SCOPE_PREFIXES):
            continue
        out.add(stem)
    return out


def registered_peers() -> tuple[OfficialTacPeer, ...]:
    return tuple(p for p in OFFICIAL_TAC_PEERS if p.disposition == "registered")


def annex3_path(peer: OfficialTacPeer) -> Path:
    if not peer.annex3_tac:
        raise ValueError(f"{peer.stem} has no annex3_tac")
    return _ANNEX3 / peer.annex3_tac
