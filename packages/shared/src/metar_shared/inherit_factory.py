"""Product → region → country → station inheritance factory (ADR-055).

Shared **types**, pure **merge** helpers, and **Protocol** ports only.
Engine packages implement ports; this module does not load YAML or run
validators. [Corpus: adr/ADR-055] [Corpus: pack-engine-boundary]
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, field
from typing import Protocol

# Products eligible for ICAO / national prefer when catalog rows map them.
PREFER_PRODUCTS: frozenset[str] = frozenset({"METAR", "SPECI", "TAF", "SIGMET"})

# Caller profiles treated as "default" for prefer remap (case-normalized).
DEFAULT_PROFILE_IDS: frozenset[str] = frozenset({"annex3", "icao_2025"})


@dataclass(frozen=True, slots=True)
class LayerOverrides:
    """
    Override bag at one DAG node.

    Parameters
    ----------
    scalars : Mapping[str, str]
        Child-wins string fields (e.g. lint_profile_id, emit_key).
    allow_codes : frozenset[str]
        Additive allow / enable set unless ``replace_allow`` is True.
    deny_codes : frozenset[str]
        Additive deny / suppress set unless ``replace_deny`` is True.
    replace_allow : bool
        When True, ``allow_codes`` replaces the parent set.
    replace_deny : bool
        When True, ``deny_codes`` replaces the parent set.
    """

    scalars: Mapping[str, str] = field(default_factory=lambda: dict[str, str]())
    allow_codes: frozenset[str] = frozenset()
    deny_codes: frozenset[str] = frozenset()
    replace_allow: bool = False
    replace_deny: bool = False


@dataclass(frozen=True, slots=True)
class InheritNode:
    """
    One node in a product-rooted inherit tree.

    Parameters
    ----------
    id : str
        Node id (product code, region id, country profile id, or ICAO).
    overrides : LayerOverrides
        Overrides applied at this node.
    children : Mapping[str, InheritNode]
        Child layer keyed by next-layer id.
    """

    id: str
    overrides: LayerOverrides = field(default_factory=LayerOverrides)
    children: Mapping[str, InheritNode] = field(
        default_factory=lambda: dict[str, InheritNode]()
    )


@dataclass(frozen=True, slots=True)
class EffectiveBundle:
    """
    Resolved ids for engines (ids only — no runtime payloads).

    Parameters
    ----------
    product : str
        Product family (METAR, TAF, …).
    region : str or None
        Semantic region id, if any.
    country : str or None
        Country / national profile id, if any.
    station : str or None
        Station ICAO, if any.
    lint_profile_id : str or None
        Effective lint profile id.
    emit_key : str or None
        Effective convert emit key.
    tac_quality_policy_id : str or None
        TAC quality policy document id.
    iwxxm_output_policy_id : str or None
        IWXXM output policy document id.
    decode_pack_id : str or None
        Decode pack id (resolution only).
    chain : tuple[str, ...]
        Resolved layer labels for optional HTTP/SDK echo.
    allow_codes : frozenset[str]
        Merged allow set.
    deny_codes : frozenset[str]
        Merged deny / suppress set.
    scalars : Mapping[str, str]
        Merged scalar map after child-wins.
    """

    product: str
    region: str | None = None
    country: str | None = None
    station: str | None = None
    lint_profile_id: str | None = None
    emit_key: str | None = None
    tac_quality_policy_id: str | None = None
    iwxxm_output_policy_id: str | None = None
    decode_pack_id: str | None = None
    chain: tuple[str, ...] = ()
    allow_codes: frozenset[str] = frozenset()
    deny_codes: frozenset[str] = frozenset()
    scalars: Mapping[str, str] = field(default_factory=lambda: dict[str, str]())


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
    """
    if replace:
        return frozenset(child)
    return frozenset(parent | child)


def merge_overrides(parent: LayerOverrides, child: LayerOverrides) -> LayerOverrides:
    """
    Merge two override bags per ADR-055 rules.

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
    """Build ``EffectiveBundle`` from merged overrides."""
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

    ``root`` must be the product node (``root.id`` matches ``product`` ignoring case).
    Missing optional layers skip; only declared child keys are followed.

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


class LintResolvePort(Protocol):
    """Port for tac-validate lint + prefer resolve."""

    def resolve_lint(
        self,
        *,
        product: str,
        profile: str,
        station: str | None,
    ) -> EffectiveBundle:
        """Return lint-oriented bundle for the call."""
        ...


class ConvertResolvePort(Protocol):
    """Port for tac2iwxxm emit / policy id selection."""

    def resolve_convert(
        self,
        *,
        product: str,
        profile: str,
        station: str | None,
    ) -> EffectiveBundle:
        """Return convert-oriented bundle for the call."""
        ...


class IwxxmPolicyPort(Protocol):
    """Port for iwxxm-validate policy id acceptance."""

    def resolve_iwxxm_policy(
        self,
        *,
        policy_id: str | None,
        product: str,
    ) -> str | None:
        """Return output policy id to load (or None for default)."""
        ...


class DecodeResolvePort(Protocol):
    """Port for tac-decoding pack / MatchPort resolution only."""

    def resolve_decode(
        self,
        *,
        product: str,
        profile: str | None,
    ) -> EffectiveBundle:
        """Return decode pack id in ``EffectiveBundle.decode_pack_id``."""
        ...


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
