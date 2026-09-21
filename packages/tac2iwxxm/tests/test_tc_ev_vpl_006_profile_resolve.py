"""TC-EV-VPL-006 — conversion profile resolves policy ids (#1216 M5)."""

from __future__ import annotations

import pytest
from tac2iwxxm.profile_resolve import (
    ProfileResolveError,
    resolve_validation_policies,
)


def test_annex3_alias_and_canonical_bind_builtin_policies() -> None:
    alias = resolve_validation_policies("annex3")
    canonical = resolve_validation_policies("ICAO_2025")
    assert alias.emit_key == "annex3"
    assert canonical.canonical == "icao_2025"
    assert alias.tac_quality_policy_id == "annex3-metar-quality"
    assert alias.iwxxm_output_policy_id == "annex3-iwxxm-output"
    assert canonical.tac_quality_policy_id == alias.tac_quality_policy_id


def test_policy_overrides_replace_one_slot() -> None:
    resolved = resolve_validation_policies("us_faa_nws", tac_policy=" custom-tac ", iwxxm_policy="  ")
    assert resolved.emit_key == "iwxxm_us"
    assert resolved.tac_quality_policy_id == "custom-tac"
    assert resolved.iwxxm_output_policy_id == "annex3-iwxxm-output"
    both = resolve_validation_policies("ca_eccc", iwxxm_policy="custom-iwxxm")
    assert both.iwxxm_output_policy_id == "custom-iwxxm"
    assert both.tac_quality_policy_id == "annex3-metar-quality"


def test_unknown_profile_and_missing_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ProfileResolveError, match="unknown conversion profile"):
        resolve_validation_policies("not-a-profile")
    monkeypatch.setattr("tac2iwxxm.profile_resolve._POLICY_BY_EMIT", {})
    with pytest.raises(ProfileResolveError, match="no policy binding"):
        resolve_validation_policies("annex3")
