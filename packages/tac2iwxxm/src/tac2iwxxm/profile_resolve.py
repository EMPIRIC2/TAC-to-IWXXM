"""Map a conversion profile to TAC quality and IWXXM output policy ids (ADR-046 / #1216 M5).

Validators stay dumb loaders. This module only resolves document ids.
"""

from __future__ import annotations

from dataclasses import dataclass

from tac2iwxxm.profile_registry import resolve_semantic_profile

_ANNEX3_POLICIES = ("annex3-metar-quality", "annex3-iwxxm-output")

# National emit keys share the annex3 policy documents until a profile ships its own ids.
_POLICY_BY_EMIT: dict[str, tuple[str, str]] = {
    "annex3": _ANNEX3_POLICIES,
    "iwxxm_us": _ANNEX3_POLICIES,
    "ca_eccc": _ANNEX3_POLICIES,
    "au_bom": _ANNEX3_POLICIES,
    "nz_caa_met": _ANNEX3_POLICIES,
    "uk_metoffice": _ANNEX3_POLICIES,
    "br_decea": _ANNEX3_POLICIES,
    "kr_kma": _ANNEX3_POLICIES,
    "jp_jma": _ANNEX3_POLICIES,
    "in_imd": _ANNEX3_POLICIES,
    "hk_hko": _ANNEX3_POLICIES,
}


class ProfileResolveError(ValueError):
    """Conversion profile id is unknown or has no policy binding."""


@dataclass(frozen=True, slots=True)
class ResolvedValidationPolicies:
    """Policy document ids bound to one conversion profile."""

    canonical: str
    emit_key: str
    tac_quality_policy_id: str
    iwxxm_output_policy_id: str


def resolve_validation_policies(
    profile: str,
    *,
    tac_policy: str | None = None,
    iwxxm_policy: str | None = None,
) -> ResolvedValidationPolicies:
    """
    Resolve ``profile`` to TAC quality and IWXXM output policy ids.

    Parameters
    ----------
    profile :
        Canonical conversion profile id or legacy alias (``ICAO_2025``, ``annex3``).
    tac_policy :
        Optional override for the TAC quality policy id (CLI ``--policy``).
    iwxxm_policy :
        Optional override for the IWXXM output policy id (CLI ``--policy``).
    """
    resolved = resolve_semantic_profile(profile)
    if resolved is None:
        msg = f"unknown conversion profile {profile!r}"
        raise ProfileResolveError(msg)
    pair = _POLICY_BY_EMIT.get(resolved.emit_key)
    if pair is None:
        msg = f"no policy binding for profile {resolved.canonical!r}"
        raise ProfileResolveError(msg)
    tac_id, iwxxm_id = pair
    tac_override = tac_policy.strip() if isinstance(tac_policy, str) and tac_policy.strip() else ""
    iwxxm_override = iwxxm_policy.strip() if isinstance(iwxxm_policy, str) and iwxxm_policy.strip() else ""
    return ResolvedValidationPolicies(
        canonical=resolved.canonical,
        emit_key=resolved.emit_key,
        tac_quality_policy_id=tac_override or tac_id,
        iwxxm_output_policy_id=iwxxm_override or iwxxm_id,
    )


__all__ = [
    "ProfileResolveError",
    "ResolvedValidationPolicies",
    "resolve_validation_policies",
]
