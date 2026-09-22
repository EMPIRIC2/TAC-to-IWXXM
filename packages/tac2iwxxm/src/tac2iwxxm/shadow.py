"""Shadow convert: run a pack match beside convert.

``xml`` matches :func:`tac2iwxxm.convert.convert` at the resolved IR source.
``legacy_ir`` always comes from ``ir_source=legacy`` when that path succeeds.
[Corpus: adr/ADR-045]
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
    """
    Convert output plus an optional pack match and pack IR.

    Attributes
    ----------
    _ : object
        See implementation.
    """

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
    Convert at the default IR source and, for a shadow product, also match the pack.

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
        ``xml`` matches default :func:`convert`. ``legacy_ir`` is from
        ``ir_source=legacy`` when that convert succeeds.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (convert_shadow)
    2
    """
    result = convert(tac, product=product, profile=profile, iwxxm_version=iwxxm_version)
    legacy = convert(
        tac,
        product=product,
        profile=profile,
        iwxxm_version=iwxxm_version,
        ir_source="legacy",
    )
    matched: MatchResult | None = None
    pack_id: str | None = None
    pack_ir: dict[str, object] | None = None
    product_u = product.upper()
    # Prefer legacy IR for SIGMET pack selection; fall back to default IR.
    select_ir = legacy.ir if legacy.ok else result.ir
    if product_u in _SHADOW_PRODUCTS and result.ok:
        pack_id = _pack_id(product_u, select_ir)
        packs = {item.id: item for item in load_packs(result.profile)}
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
        legacy_ir=legacy.ir if legacy.ok else None,
    )


def _pack_id(product: str, ir: dict[str, object] | None) -> str:
    """
    Internal helper ``_pack_id``.

    Parameters
    ----------
    product : object
        Argument ``product``.
    ir : object
        Argument ``ir``.

    Returns
    -------
    object
        Return value.
    """
    if product != "SIGMET":
        return product.lower()
    root = ""
    if ir is not None:
        raw = ir.get("iwxxm_root")
        if isinstance(raw, str):
            root = raw
    return _SIGMET_PACKS.get(root, "sigmet")
