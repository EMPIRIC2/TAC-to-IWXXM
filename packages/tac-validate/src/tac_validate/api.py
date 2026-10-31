"""Public ``lint()`` entrypoint for TAC parse gate + rule pack."""

from __future__ import annotations

import re
from collections.abc import Sequence

from tac_validate.ahl import lint_ahl_bulletin, looks_like_ahl
from tac_validate.lint_profile_catalog import apply_profile_deltas, lint_profile_spec
from tac_validate.match_port import DecodeMatch, MatchPort, match_port_spans, spans_from_port
from tac_validate.models import Issue, LintReport
from tac_validate.products import PRODUCTS
from tac_validate.profiles import (
    PROFILE_ANNEX3,
    PROFILE_CA_MSC_SIGMET,
    PROFILE_US_NWS_CONVECTIVE_SIGMET,
    PROFILE_US_NWS_G_AIRMET,
    PROFILE_US_NWS_VONA,
    ca_eccc_applicable,
    effective_lint_profile,
    in_imd_applicable,
    iwxxm_us_lint_applicable,
    normalize_profile,
)
from tac_validate.rules import check_parse_gate, check_product_rules
from tac_validate.station_scoped_policy import resolve_profile_for_station

_TAF_ICAO_RE = re.compile(r"(?is)^\s*TAF(?:\s+(?:AMD|COR))?\s+([A-Z][A-Z0-9]{3})\b")
_DEFAULT_PROFILES = frozenset({PROFILE_ANNEX3})


def _lint_tac_report(
    tac_text: str,
    product: str,
    profile: str,
) -> LintReport:
    """
    Internal helper ``_lint_tac_report``.

    Parameters
    ----------
    tac_text : object
        Argument ``tac_text``.
    product : object
        Argument ``product``.
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    product_u = product.upper()
    issues, fixes = check_parse_gate(tac_text, product_u, profile=profile)
    if not any(i.severity == "error" for i in issues):
        issues.extend(check_product_rules(tac_text, product_u, profile=profile))
    ok = not any(i.severity == "error" for i in issues)
    return LintReport(ok=ok, product=product_u, issues=issues, fixes=fixes)


def lint(
    tac_text: str,
    *,
    product: str = "METAR",
    profile: str = PROFILE_ANNEX3,
    match_port: MatchPort | Sequence[DecodeMatch] | None = None,
) -> LintReport:
    """
    Lint TAC text for ``product`` using the shared rule-pack skeleton.

    When ``tac_text`` starts with a WMO AHL, the heading is treated as
    communications format and each contained report is linted as ``product``.

    Parameters
    ----------
    tac_text : str
        TAC report, fragment, or WMO AHL bulletin.

    product : str, optional
        One of AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA, SWXA, VONA. By default ``'METAR'``.

    profile : str, optional
        ``annex3`` (default), ``iwxxm_us``, ``ca_eccc``, ``in_imd``, or another
        id in the lint profile catalog. Profiles that do not differ run the
        Annex 3 rules and keep the requested profile on the report. Calling a
        profile for a product it does not list raises ``ValueError``.

    match_port : MatchPort or Sequence[DecodeMatch] or None, optional
        Optional decode spans. ``None`` keeps the TAC scan. An empty sequence
        makes annex3 METAR theme packs emit ``MISSING_DECODE_MATCH``. By default ``None``.

    Returns
    -------
    LintReport
        ``ok`` is ``False`` when any error-severity issue is present.
        Optional ``fixes`` may suggest repairs (Q9=C).

    Raises
    ------
    ValueError
        Unsupported profile name, or ``iwxxm_us`` for a product without US profile.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (lint)
    2
    """
    profile_l = normalize_profile(profile)
    product_u = product.upper()
    if profile_l == PROFILE_US_NWS_CONVECTIVE_SIGMET:
        if product_u != "SIGMET":
            raise ValueError(f"profile {profile_l} is not applicable for product {product_u!r} (N/A - use annex3)")
        if "CONVECTIVE SIGMET" not in tac_text.upper():
            return LintReport(
                ok=False,
                product=product_u,
                issues=[
                    Issue(
                        severity="error",
                        code="NOT_CONVECTIVE_SIGMET",
                        message=(
                            "This profile checks United States convective SIGMET text, not an international SIGMET."
                        ),
                    )
                ],
                fixes=[],
            )
        return LintReport(ok=True, product=product_u, issues=[], fixes=[])
    refusal = _SOURCE_UNAVAILABLE_LINT.get(profile_l)
    if refusal is not None:
        allowed, message = refusal
        if product_u not in allowed:
            raise ValueError(f"profile {profile_l} is not applicable for product {product_u!r} (N/A - use annex3)")
        return LintReport(
            ok=False,
            product=product_u,
            issues=[Issue(severity="error", code="SOURCE_UNAVAILABLE", message=message)],
            fixes=[],
        )
    if profile_l == "iwxxm_us" and not iwxxm_us_lint_applicable(product_u):
        raise ValueError(f"profile iwxxm_us is not applicable for product {product_u!r} (N/A - use annex3)")
    if profile_l == "ca_eccc" and not ca_eccc_applicable(product_u):
        raise ValueError(f"profile ca_eccc is not applicable for product {product_u!r} (N/A - use annex3)")
    if profile_l == "in_imd" and not in_imd_applicable(product_u):
        raise ValueError(f"profile in_imd is not applicable for product {product_u!r} (N/A - use annex3)")
    if profile_l not in {"annex3", "iwxxm_us", "ca_eccc", "in_imd"}:
        spec = lint_profile_spec(profile_l)
        if spec is None or product_u not in spec.products:
            raise ValueError(f"profile {profile_l} is not applicable for product {product_u!r} (N/A - use annex3)")

    spans = spans_from_port(match_port)
    token = match_port_spans.set(spans) if spans is not None else None
    try:
        if looks_like_ahl(tac_text):
            report = lint_ahl_bulletin(
                tac_text,
                product=product_u,
                profile=profile_l,
                lint_report=_lint_tac_report,
            )
        else:
            report = _lint_tac_report(tac_text, product_u, profile_l)
        return apply_profile_deltas(report, profile=profile_l, product=product_u)
    finally:
        if token is not None:
            match_port_spans.reset(token)


def extract_station_icao(tac_text: str, product: str) -> str | None:
    """
    Return the station ICAO from a TAF body when present.

    Parameters
    ----------
    tac_text : str
        TAC text.
    product : str
        Product id.

    Returns
    -------
    str | None
        Four-letter ICAO, or ``None``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (extract_station_icao)
    2
    """
    if product.upper() != "TAF":
        return None
    matched = _TAF_ICAO_RE.match(tac_text or "")
    if matched is None:
        return None
    return matched.group(1).upper()


def prefer_station_profile(profile: str, product: str, icao: str | None) -> str:
    """
    When the caller uses annex3 and the ICAO is station-mapped, prefer that profile.

    Explicit national profiles are kept as requested.

    Parameters
    ----------
    profile : str
        Requested profile id.
    product : str
        Product id (station map applies to TAF only).
    icao : str or None
        Station ICAO.

    Returns
    -------
    str
        Profile id to lint with.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (prefer_station_profile)
    2
    """
    profile_l = normalize_profile(profile)
    if product.upper() != "TAF":
        return profile_l
    if profile_l not in _DEFAULT_PROFILES:
        return profile_l
    mapped = resolve_profile_for_station(icao or "")
    return mapped or profile_l


def lint_with_profile(
    tac_text: str,
    *,
    product: str = "METAR",
    profile: str = PROFILE_ANNEX3,
    icao: str | None = None,
    tac_policy: str | None = None,
    match_port: MatchPort | Sequence[DecodeMatch] | None = None,
    apply_policy: bool = True,
) -> LintReport:
    """
    Resolve profile (ICAO + inherits applicability), lint, then apply TAC policy.

    Parameters
    ----------
    tac_text : str
        TAC text.
    product : str, optional
        Product id. By default ``METAR``.
    profile : str, optional
        Requested semantic / lint profile. By default ``annex3``.
    icao : str or None, optional
        Optional station override; otherwise parsed from TAF.
    tac_policy : str or None, optional
        Optional TAC quality policy id override.
    match_port : MatchPort or Sequence[DecodeMatch] or None, optional
        Optional decode spans.
    apply_policy : bool, optional
        When True (default), apply the bound ADR-046 policy.

    Returns
    -------
    LintReport
        Policy-adjusted lint report.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (lint_with_profile)
    2
    """
    product_u = product.upper()
    station = (icao or "").strip().upper() or extract_station_icao(tac_text, product_u)
    profile_l = prefer_station_profile(profile, product_u, station)
    profile_l = effective_lint_profile(profile_l, product_u)
    report = lint(tac_text, product=product_u, profile=profile_l, match_port=match_port)
    if not apply_policy:
        return report
    try:
        from tac2iwxxm.profile_resolve import ProfileResolveError, resolve_validation_policies

        from tac_validate.policy import PolicyError, apply_policy_to_report
    except ImportError:
        return report
    try:
        policies = resolve_validation_policies(
            profile_l,
            product=product_u,
            tac_policy=tac_policy,
        )
        return apply_policy_to_report(
            report,
            policies.tac_quality_policy_id,
            profile=profile_l,
        )
    except (ProfileResolveError, PolicyError):
        return report


__all__ = [
    "PRODUCTS",
    "extract_station_icao",
    "lint",
    "lint_with_profile",
    "prefer_station_profile",
]

_SOURCE_UNAVAILABLE_LINT: dict[str, tuple[frozenset[str], str]] = {
    PROFILE_US_NWS_G_AIRMET: (
        frozenset({"AIRMET"}),
        "United States G-AIRMET checking is unavailable until a text bulletin is on file.",
    ),
    PROFILE_US_NWS_VONA: (
        frozenset({"VONA"}),
        "United States volcano observatory notice checking is unavailable until a complete notice is on file.",
    ),
    PROFILE_CA_MSC_SIGMET: (
        frozenset({"SIGMET"}),
        "Canadian SIGMET text checking is unavailable until a text source is on file.",
    ),
}
