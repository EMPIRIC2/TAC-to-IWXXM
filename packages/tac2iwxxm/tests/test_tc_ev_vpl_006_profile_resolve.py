"""TC-EV-VPL-006 — conversion profile resolves policy ids (#1216 M5)."""

from __future__ import annotations

from pathlib import Path

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


def test_taf_product_swaps_to_taf_quality_policy() -> None:
    metar = resolve_validation_policies("annex3", product="METAR")
    taf = resolve_validation_policies("annex3", product="TAF")
    assert metar.tac_quality_policy_id == "annex3-metar-quality"
    assert taf.tac_quality_policy_id == "annex3-taf-quality"
    assert taf.iwxxm_output_policy_id == "annex3-iwxxm-output"
    us_taf = resolve_validation_policies("iwxxm_us", product="TAF")
    assert us_taf.tac_quality_policy_id == "annex3-taf-quality"


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


def test_profile_dir_layers_one_policy_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overlay = tmp_path / "profiles"
    overlay.mkdir()
    (overlay / "notes.txt").write_text("ignore", encoding="utf-8")
    (overlay / "ca.yaml").write_text(
        "\n".join(
            [
                "id: ca-binding",
                "profiles: [ca_eccc]",
                "extends: annex3",
                "iwxxm_output_policy_id: ca-iwxxm-output",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC2IWXXM_PROFILE_DIR", str(overlay))
    scoped = resolve_validation_policies("ca_eccc")
    assert scoped.iwxxm_output_policy_id == "ca-iwxxm-output"
    assert scoped.tac_quality_policy_id == "annex3-metar-quality"
    untouched = resolve_validation_policies("annex3")
    assert untouched.iwxxm_output_policy_id == "annex3-iwxxm-output"
    (overlay / "ca.yaml").write_text(
        "id: ca-binding\nprofiles: [ca_eccc]\nextends: annex3\ntac_quality_policy_id: ca-tac\n",
        encoding="utf-8",
    )
    tac_only = resolve_validation_policies("ca_eccc")
    assert tac_only.tac_quality_policy_id == "ca-tac"
    assert tac_only.iwxxm_output_policy_id == "annex3-iwxxm-output"
    (overlay / "other.yaml").write_text(
        "id: skipped\nprofiles: [ca_eccc]\nextends: iwxxm_us\niwxxm_output_policy_id: nope\n",
        encoding="utf-8",
    )
    assert resolve_validation_policies("ca_eccc").iwxxm_output_policy_id == "annex3-iwxxm-output"
    (overlay / "other.yaml").unlink()
    monkeypatch.delenv("TAC2IWXXM_PROFILE_DIR")
    assert resolve_validation_policies("ca_eccc").iwxxm_output_policy_id == "annex3-iwxxm-output"

    monkeypatch.setenv("TAC2IWXXM_PROFILE_DIR", str(tmp_path / "missing"))
    with pytest.raises(ProfileResolveError, match="not a folder"):
        resolve_validation_policies("annex3")

    (overlay / "ca.yaml").write_text("id: ca-binding\nprofiles: [ca_eccc]\nextends: not-a-profile\n", encoding="utf-8")
    monkeypatch.setenv("TAC2IWXXM_PROFILE_DIR", str(overlay))
    with pytest.raises(ProfileResolveError, match="unknown builtin"):
        resolve_validation_policies("ca_eccc")

    (overlay / "ca.yaml").write_text("- just-a-list\n", encoding="utf-8")
    with pytest.raises(ProfileResolveError, match="mapping"):
        resolve_validation_policies("annex3")

    (overlay / "ca.yaml").write_text(
        "id: ca-binding\nprofiles: [ca_eccc]\nextends: [annex3, iwxxm_us]\n",
        encoding="utf-8",
    )
    with pytest.raises(ProfileResolveError, match="must extend one builtin"):
        resolve_validation_policies("ca_eccc")

    (overlay / "ca.yaml").write_text(
        "id: ca-binding\nprofiles: [ca_eccc]\nextends: annex3\ntac_quality_policy_id: 1\n",
        encoding="utf-8",
    )
    with pytest.raises(ProfileResolveError, match="must be a string"):
        resolve_validation_policies("ca_eccc")

    (overlay / "ca.yaml").write_text("id: ca-binding\nprofiles: []\nextends: annex3\n", encoding="utf-8")
    with pytest.raises(ProfileResolveError, match="needs a profiles list"):
        resolve_validation_policies("ca_eccc")

    (overlay / "ca.yaml").write_text("id: ca-binding\nprofiles: ['  ']\nextends: annex3\n", encoding="utf-8")
    with pytest.raises(ProfileResolveError, match="needs a profiles list"):
        resolve_validation_policies("ca_eccc")
