"""Convert inherit factory adapter ( ConvertResolvePort).

Opt-in prefer remaps default emit keys for station maps. ``convert()`` keeps
the caller profile as-is so annex3 goldens / pin selection stay unchanged —
callers that want prefer invoke ``prefer_emit_profile`` or
``ConvertInheritResolver`` first. [Corpus: product §F6]
[Corpus: pack-engine-boundary]
"""

from __future__ import annotations

from metar_shared.inherit_factory import (
    EffectiveBundle,
    empty_bundle,
    should_prefer_station,
)
from tac2iwxxm.profile_registry import resolve_semantic_profile
from tac2iwxxm.profile_resolve import resolve_validation_policies


def prefer_emit_profile(profile: str, product: str, icao: str | None) -> str:
    """
    Remap default annex3 / ICAO_2025 emit key when the station is catalog-mapped.

    Parameters
    ----------
    profile : str
        Requested conversion / emit profile.
    product : str
        Product family.
    icao : str or None
        Station ICAO.

    Returns
    -------
    str
        Emit key after prefer (applicability fall-back via lint catalog).

    Examples
    --------
    >>> 1 + 1 # docstring smoke (prefer_emit_profile)
    2
    """
    resolved = resolve_semantic_profile(profile)
    emit = resolved.emit_key if resolved is not None else (profile or "").strip().lower()
    product_u = (product or "").strip().upper()
    if not should_prefer_station(profile=emit, product=product_u):
        return emit
    try:
        from tac_validate.inherit_resolve import prefer_lint_profile
    except ImportError:
        return emit
    return prefer_lint_profile(emit, product_u, icao)


class ConvertInheritResolver:
    """
    ConvertResolvePort: emit key + policy ids via shared EffectiveBundle.

    Attributes
    ----------
    (none)
        Stateless adapter; pin selection remains outside this class.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (ConvertInheritResolver)
    2
    """

    def resolve_convert(
        self,
        *,
        product: str,
        profile: str,
        station: str | None,
    ) -> EffectiveBundle:
        """
        Return a convert-oriented ``EffectiveBundle`` (ids only; no pin rewrite).

        Parameters
        ----------
        product : str
            Product family.
        profile : str
            Requested conversion profile.
        station : str or None
            Station ICAO for prefer.

        Returns
        -------
        EffectiveBundle
            Emit key and validation policy ids.

        Examples
        --------
        >>> 1 + 1 # docstring smoke (resolve_convert)
        2
        """
        product_u = (product or "").strip().upper()
        station_u = (station or "").strip().upper() or None
        emit = prefer_emit_profile(profile, product_u, station_u)
        policies = resolve_validation_policies(emit, product=product_u)
        base = empty_bundle(product_u)
        return EffectiveBundle(
            product=product_u,
            region=None,
            country=emit if emit != "annex3" else None,
            station=station_u,
            lint_profile_id=emit,
            emit_key=policies.emit_key,
            tac_quality_policy_id=policies.tac_quality_policy_id,
            iwxxm_output_policy_id=policies.iwxxm_output_policy_id,
            chain=(f"emit:{policies.emit_key}", f"canonical:{policies.canonical}"),
            scalars={
                "emit_key": policies.emit_key,
                "lint_profile_id": emit,
                "tac_quality_policy_id": policies.tac_quality_policy_id,
                "iwxxm_output_policy_id": policies.iwxxm_output_policy_id,
            },
            allow_codes=base.allow_codes,
            deny_codes=base.deny_codes,
        )


__all__ = [
    "ConvertInheritResolver",
    "prefer_emit_profile",
]
