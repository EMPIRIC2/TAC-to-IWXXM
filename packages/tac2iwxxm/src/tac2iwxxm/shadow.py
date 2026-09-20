"""Shadow convert: run a pack match beside the legacy parser.

XML still comes from :func:`tac2iwxxm.convert.convert`. Pack IR is projected
beside the legacy parser IR. The pack does not choose ``iwxxm_version`` or
``profile``. [Corpus: adr/ADR-045]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tac_decoding.ir import project_ir
from tac_decoding.match import MatchContext, MatchResult, match_tac
from tac_decoding.packs import load_packs

from tac2iwxxm.convert import convert

_SHADOW_PRODUCTS = frozenset({"METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA", "SWXA", "VONA"})
_SIGMET_PACKS = {
    "TropicalCycloneSIGMET": "tc_sigmet",
    "VolcanicAshSIGMET": "va_sigmet",
}


@dataclass(frozen=True, slots=True)
class ShadowResult:
    """Legacy convert output plus an optional pack match and pack IR."""

    ok: bool
    xml: str | None
    iwxxm_version: str
    profile: str
    match: MatchResult | None
    pack_id: str | None
    pack_ir: dict[str, object] | None
    legacy_ir: dict[str, Any] | None


def convert_shadow(
    tac: str,
    *,
    product: str,
    profile: str = "annex3",
    iwxxm_version: str | None = None,
) -> ShadowResult:
    """
    Convert with the legacy parser and, for a shadow product, also match the pack.

    Parameters
    ----------
    tac :
        TAC text.
    product :
        Product id. METAR, SPECI, TAF, AIRMET, SIGMET, VAA, TCA, SWXA, and VONA
        run the pack. SIGMET stays one id; the legacy parse selects the ordinary,
        volcanic-ash, or tropical-cyclone pack.
    profile :
        Caller profile. The pack does not select this.
    iwxxm_version :
        Caller pin. The pack does not select this.

    Returns
    -------
    ShadowResult
        ``xml`` and ``legacy_ir`` come from the legacy convert. ``pack_ir`` is the
        pack projection when that convert succeeded for a shadow product.
    """
    result = convert(tac, product=product, profile=profile, iwxxm_version=iwxxm_version)
    matched: MatchResult | None = None
    pack_id: str | None = None
    pack_ir: dict[str, object] | None = None
    product_u = product.upper()
    if product_u in _SHADOW_PRODUCTS and result.ok:
        pack_id = _pack_id(product_u, result.ir)
        packs = {item.id: item for item in load_packs()}
        matched = match_tac(
            tac,
            packs[pack_id],
            context=MatchContext(iwxxm_version=result.iwxxm_version, profile=result.profile),
        )
        pack_ir = project_ir(matched, product=product_u, pack_id=pack_id)
    return ShadowResult(
        ok=result.ok,
        xml=result.xml,
        iwxxm_version=result.iwxxm_version,
        profile=result.profile,
        match=matched,
        pack_id=pack_id,
        pack_ir=pack_ir,
        legacy_ir=result.ir,
    )


def _pack_id(product: str, ir: dict[str, object] | None) -> str:
    """Map a convert product to a pack. SIGMET stays one product id."""
    if product != "SIGMET":
        return product.lower()
    root = ""
    if ir is not None:
        raw = ir.get("iwxxm_root")
        if isinstance(raw, str):
            root = raw
    return _SIGMET_PACKS.get(root, "sigmet")
