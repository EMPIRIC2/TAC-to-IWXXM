"""Types and Protocol ports for inherit factory. [Corpus: pack-engine-boundary]
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class LayerOverrides:
    """
    Override bag at one DAG node.

    Parameters
    ----------
    scalars : Mapping[str, str]
        Child-wins string fields (e.g. lint_profile_id, emit_key).
    allow_codes : frozenset[str]
        Additive allow set unless ``replace_allow`` is True.
    deny_codes : frozenset[str]
        Additive deny set unless ``replace_deny`` is True.
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
        Node id (product, region, country, or ICAO).
    overrides : LayerOverrides
        Overrides at this node.
    children : Mapping[str, InheritNode]
        Next-layer children keyed by id.
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
        Product family.
    region : str or None
        Semantic region id.
    country : str or None
        Country / national profile id.
    station : str or None
        Station ICAO.
    lint_profile_id : str or None
        Effective lint profile id.
    emit_key : str or None
        Effective convert emit key.
    tac_quality_policy_id : str or None
        TAC quality policy id.
    iwxxm_output_policy_id : str or None
        IWXXM output policy id.
    decode_pack_id : str or None
        Decode pack id (resolution only).
    chain : tuple[str, ...]
        Resolved layer labels for optional echo.
    allow_codes : frozenset[str]
        Merged allow set.
    deny_codes : frozenset[str]
        Merged deny set.
    scalars : Mapping[str, str]
        Merged scalar map.
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


__all__ = [
    "ConvertResolvePort",
    "DecodeResolvePort",
    "EffectiveBundle",
    "InheritNode",
    "IwxxmPolicyPort",
    "LayerOverrides",
    "LintResolvePort",
]
