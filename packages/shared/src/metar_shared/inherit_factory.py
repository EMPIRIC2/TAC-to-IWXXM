"""Product → region → country → station inheritance factory .

Shared **merge** helpers and resolve walk; types/ports live in
``inherit_factory_types``. [Corpus: pack-engine-boundary]
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping

from metar_shared.inherit_factory_types import (
    ConvertResolvePort,
    DecodeResolvePort,
    EffectiveBundle,
    InheritNode,
    IwxxmPolicyPort,
    LayerOverrides,
    LintResolvePort,
)

# Products eligible for ICAO / national prefer when catalog rows map them.
PREFER_PRODUCTS: frozenset[str] = frozenset({"METAR", "SPECI", "TAF", "SIGMET"})

# Caller profiles treated as "default" for prefer remap (case-normalized).
DEFAULT_PROFILE_IDS: frozenset[str] = frozenset({"annex3", "icao_2025"})


def normalize_product(product: str) -> str:
    """
    Return uppercase product id.

    Parameters
    ----------
    product : str
        Raw product token.

    Returns
    -------
    str
        Uppercased stripped product.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (normalize_product)
    2
    """
    return (product or "").strip().upper()


def normalize_profile_id(profile: str) -> str:
    """
    Return lowercase profile id for default/prefer checks.

    Parameters
    ----------
    profile : str
        Raw profile token.

    Returns
    -------
    str
        Lowercased stripped id.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (normalize_profile_id)
    2
    """
    return (profile or "").strip().lower()


def should_prefer_station(*, profile: str, product: str) -> bool:
    """
    Return True when ICAO prefer may remap a default profile for ``product``.

    Parameters
    ----------
    profile : str
        Caller-requested profile.
    product : str
        Product family.

    Returns
    -------
    bool
        True when prefer is allowed for this call.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (should_prefer_station)
    2
    """
    product_u = normalize_product(product)
    if product_u not in PREFER_PRODUCTS:
        return False
    return normalize_profile_id(profile) in DEFAULT_PROFILE_IDS


def merge_scalar_maps(
    parent: Mapping[str, str],
    child: Mapping[str, str],
) -> dict[str, str]:
    """
    Merge scalar maps with child-wins.

    Parameters
    ----------
    parent : Mapping[str, str]
        Parent scalars.
    child : Mapping[str, str]
        Child scalars.

    Returns
    -------
    dict[str, str]
        Merged map.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (merge_scalar_maps)
    2
    """
    out: dict[str, str] = dict(parent)
    out.update(child)
    return out


def merge_code_sets(
    parent: frozenset[str],
    child: frozenset[str],
    *,
    replace: bool,
) -> frozenset[str]:
    """
    Merge allow/deny sets (union unless ``replace``).

    Parameters
    ----------
    parent : frozenset[str]
        Parent set.
    child : frozenset[str]
        Child set.
    replace : bool
        When True, return ``child`` only.

    Returns
    -------
    frozenset[str]
        Merged set.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (merge_code_sets)
    2
    """
    if replace:
        return frozenset(child)
    return frozenset(parent | child)


def merge_overrides(parent: LayerOverrides, child: LayerOverrides) -> LayerOverrides:
    """
    Merge two override bags per rules.

    Parameters
    ----------
    parent : LayerOverrides
        Parent layer.
    child : LayerOverrides
        Child layer.

    Returns
    -------
    LayerOverrides
        Merged bag.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (merge_overrides)
    2
    """
    return LayerOverrides(
        scalars=merge_scalar_maps(parent.scalars, child.scalars),
        allow_codes=merge_code_sets(
            parent.allow_codes,
            child.allow_codes,
            replace=child.replace_allow,
        ),
        deny_codes=merge_code_sets(
            parent.deny_codes,
            child.deny_codes,
            replace=child.replace_deny,
        ),
        replace_allow=False,
        replace_deny=False,
    )


def _bundle_from_merged(
    *,
    product: str,
    region: str | None,
    country: str | None,
    station: str | None,
    merged: LayerOverrides,
    chain: tuple[str, ...],
) -> EffectiveBundle:
    """
    Build ``EffectiveBundle`` from merged overrides.

    Parameters
    ----------
    product : str
        Product id.
    region : str or None
        Region id.
    country : str or None
        Country id.
    station : str or None
        Station ICAO.
    merged : LayerOverrides
        Merged overrides.
    chain : tuple[str, ...]
        Echo labels.

    Returns
    -------
    EffectiveBundle
        Ids-only bundle.
    """
    scalars = dict(merged.scalars)
    return EffectiveBundle(
        product=product,
        region=region,
        country=country,
        station=station,
        lint_profile_id=scalars.get("lint_profile_id"),
        emit_key=scalars.get("emit_key"),
        tac_quality_policy_id=scalars.get("tac_quality_policy_id"),
        iwxxm_output_policy_id=scalars.get("iwxxm_output_policy_id"),
        decode_pack_id=scalars.get("decode_pack_id"),
        chain=chain,
        allow_codes=merged.allow_codes,
        deny_codes=merged.deny_codes,
        scalars=scalars,
    )


def resolve_inherit_tree(
    root: InheritNode,
    *,
    product: str,
    region: str | None = None,
    country: str | None = None,
    station: str | None = None,
) -> EffectiveBundle:
    """
    Walk ``product → region → country → station`` merging overrides.

    Parameters
    ----------
    root : InheritNode
        Product-rooted tree.
    product : str
        Product id.
    region : str or None, optional
        Region id.
    country : str or None, optional
        Country id.
    station : str or None, optional
        Station ICAO.

    Returns
    -------
    EffectiveBundle
        Resolved bundle.

    Raises
    ------
    ValueError
        When ``root.id`` does not match ``product``.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (resolve_inherit_tree)
    2
    """
    product_u = normalize_product(product)
    if normalize_product(root.id) != product_u:
        msg = f"inherit root id {root.id!r} does not match product {product_u!r}"
        raise ValueError(msg)

    merged = root.overrides
    chain: list[str] = [f"product:{product_u}"]
    node = root

    steps: list[tuple[str, str | None]] = [
        ("region", (region or "").strip() or None),
        ("country", (country or "").strip() or None),
        ("station", (station or "").strip() or None),
    ]
    for layer_name, key in steps:
        if key is None:
            continue
        child = node.children.get(key) or node.children.get(key.lower())
        if child is None and layer_name == "station":
            child = node.children.get(key.upper())
        if child is None:
            label = key.upper() if layer_name == "station" else key
            chain.append(f"{layer_name}:{label}")
            continue
        merged = merge_overrides(merged, child.overrides)
        chain.append(f"{layer_name}:{child.id}")
        node = child

    return _bundle_from_merged(
        product=product_u,
        region=(region or "").strip() or None,
        country=(country or "").strip() or None,
        station=(station or "").strip().upper() or None,
        merged=merged,
        chain=tuple(chain),
    )


def empty_bundle(product: str) -> EffectiveBundle:
    """
    Return a minimal bundle for ``product`` (adapter stub helper).

    Parameters
    ----------
    product : str
        Product id.

    Returns
    -------
    EffectiveBundle
        Bundle with product and chain only.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (empty_bundle)
    2
    """
    product_u = normalize_product(product)
    return EffectiveBundle(product=product_u, chain=(f"product:{product_u}",))


def apply_scalar_keys(
    bundle: EffectiveBundle,
    updates: Mapping[str, str],
) -> EffectiveBundle:
    """
    Return a copy of ``bundle`` with child-wins scalar updates.

    Parameters
    ----------
    bundle : EffectiveBundle
        Base bundle.
    updates : Mapping[str, str]
        Scalar overlays.

    Returns
    -------
    EffectiveBundle
        Updated bundle.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (apply_scalar_keys)
    2
    """
    scalars: MutableMapping[str, str] = dict(bundle.scalars)
    scalars.update(updates)
    return EffectiveBundle(
        product=bundle.product,
        region=bundle.region,
        country=bundle.country,
        station=bundle.station,
        lint_profile_id=scalars.get("lint_profile_id", bundle.lint_profile_id),
        emit_key=scalars.get("emit_key", bundle.emit_key),
        tac_quality_policy_id=scalars.get(
            "tac_quality_policy_id",
            bundle.tac_quality_policy_id,
        ),
        iwxxm_output_policy_id=scalars.get(
            "iwxxm_output_policy_id",
            bundle.iwxxm_output_policy_id,
        ),
        decode_pack_id=scalars.get("decode_pack_id", bundle.decode_pack_id),
        chain=bundle.chain,
        allow_codes=bundle.allow_codes,
        deny_codes=bundle.deny_codes,
        scalars=dict(scalars),
    )


__all__ = [
    "DEFAULT_PROFILE_IDS",
    "PREFER_PRODUCTS",
    "ConvertResolvePort",
    "DecodeResolvePort",
    "EffectiveBundle",
    "InheritNode",
    "IwxxmPolicyPort",
    "LayerOverrides",
    "LintResolvePort",
    "apply_scalar_keys",
    "empty_bundle",
    "merge_code_sets",
    "merge_overrides",
    "merge_scalar_maps",
    "normalize_product",
    "normalize_profile_id",
    "resolve_inherit_tree",
    "should_prefer_station",
]
