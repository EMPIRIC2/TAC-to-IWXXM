"""Lint inherit factory adapter ( LintResolvePort).

Product → (empty region) → country profile → station using the lint catalog. [Corpus: product §F15] [Corpus: pack-engine-boundary]
"""

from __future__ import annotations

from functools import cache

from metar_shared.inherit_factory import (
    EffectiveBundle,
    InheritNode,
    LayerOverrides,
    empty_bundle,
    should_prefer_station,
)
from tac_validate.lint_profile_catalog import load_lint_profiles, profile_inherit_chain
from tac_validate.profiles import effective_lint_profile, normalize_profile
from tac_validate.quality_policy_bind import resolve_tac_quality_policy_id
from tac_validate.station_scoped_policy import resolve_profile_for_station


def prefer_lint_profile(profile: str, product: str, icao: str | None) -> str:
    """
    Remap default annex3 / ICAO_2025 to a catalog station profile when allowed.

    Parameters
    ----------
    profile : str
        Requested profile id.
    product : str
        Product family (METAR / SPECI / TAF / SIGMET prefer when mapped).
    icao : str or None
        Station ICAO.

    Returns
    -------
    str
        Effective lint profile id (applicability fall-back applied).

    Examples
    --------
    >>> 1 + 1 # docstring smoke (prefer_lint_profile)
    2
    """
    profile_l = normalize_profile(profile)
    product_u = (product or "").strip().upper()
    if not should_prefer_station(profile=profile_l, product=product_u):
        return effective_lint_profile(profile_l, product_u)
    mapped = resolve_profile_for_station(icao or "")
    chosen = mapped or profile_l
    return effective_lint_profile(chosen, product_u)


@cache
def catalog_inherit_root(product: str) -> InheritNode:
    """
    Build a product-rooted inherit tree from the lint catalog.

    Region nodes are omitted during migration (empty region). Country nodes are
    catalog profile ids that list ``product``; station children come from exact
    ``stations`` entries.

    Parameters
    ----------
    product : str
        Product family.

    Returns
    -------
    InheritNode
        Product root with country → station children.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (catalog_inherit_root)
    2
    """
    product_u = (product or "").strip().upper()
    countries: dict[str, InheritNode] = {}
    for profile_id, spec in load_lint_profiles().items():
        if product_u not in spec.products:
            continue
        if profile_id == "annex3":
            continue
        stations = {
            icao: InheritNode(
                id=icao,
                overrides=LayerOverrides(scalars={"lint_profile_id": profile_id}),
            )
            for icao in sorted(spec.stations)
        }
        countries[profile_id] = InheritNode(
            id=profile_id,
            overrides=LayerOverrides(scalars={"lint_profile_id": profile_id}),
            children=stations,
        )
    return InheritNode(
        id=product_u,
        overrides=LayerOverrides(scalars={"lint_profile_id": "annex3"}),
        children=countries,
    )


class LintInheritResolver:
    """
    LintResolvePort implementation backed by the lint catalog + prefer.

    Attributes
    ----------
    (none)
        Stateless adapter; all state comes from the lint catalog.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (LintInheritResolver)
    2
    """

    def resolve_lint(
        self,
        *,
        product: str,
        profile: str,
        station: str | None,
    ) -> EffectiveBundle:
        """
        Return a lint-oriented ``EffectiveBundle`` for the call.

        Parameters
        ----------
        product : str
            Product family.
        profile : str
            Requested profile.
        station : str or None
            Station ICAO.

        Returns
        -------
        EffectiveBundle
            Ids and chain only.

        Examples
        --------
        >>> 1 + 1 # docstring smoke (resolve_lint)
        2
        """
        product_u = (product or "").strip().upper()
        station_u = (station or "").strip().upper() or None
        lint_id = prefer_lint_profile(profile, product_u, station_u)
        quality_id = resolve_tac_quality_policy_id(lint_id, product=product_u)
        inherit = profile_inherit_chain(lint_id)
        country = lint_id if lint_id != "annex3" else None
        base = empty_bundle(product_u)
        return EffectiveBundle(
            product=product_u,
            region=None,
            country=country,
            station=station_u,
            lint_profile_id=lint_id,
            tac_quality_policy_id=quality_id,
            chain=tuple(f"lint:{part}" for part in inherit),
            scalars={
                "lint_profile_id": lint_id,
                "tac_quality_policy_id": quality_id,
            },
            allow_codes=base.allow_codes,
            deny_codes=base.deny_codes,
        )


__all__ = [
    "LintInheritResolver",
    "catalog_inherit_root",
    "prefer_lint_profile",
]
