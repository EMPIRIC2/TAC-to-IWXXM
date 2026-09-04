"""EV-981 / #981 — propagate decode residuals into remarks / HRT (TC-EV981-001/002/005)."""

from __future__ import annotations

from tac2iwxxm.convert import convert, resolve_propagate_residuals_to_remarks

# Undecoded body token becomes a decode residual; RMK still present for UJ-026 fence.
_TAC_WITH_RESIDUAL = "METAR KJFK 251451Z 18005KT 10SM FEW050 ZZZZ 22/12 A2992 RMK AO2 SLP123="
_TAC_RMK_ONLY = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP176="


def test_tc_ev981_001_default_off_preserves_annex3_remarks_excluded() -> None:
    """Omitted / false flag must not change annex3 REMARKS_EXCLUDED (UJ-026 fence)."""
    baseline = convert(_TAC_RMK_ONLY, product="METAR", profile="annex3", iwxxm_version="2025-2")
    omitted = convert(_TAC_RMK_ONLY, product="METAR", profile="annex3", iwxxm_version="2025-2")
    explicit_off = convert(
        _TAC_RMK_ONLY,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        propagate_residuals_to_remarks=False,
    )
    assert baseline.ok
    assert omitted.ok
    assert explicit_off.ok
    for result in (baseline, omitted, explicit_off):
        codes = [i.code for i in result.issues]
        assert "REMARKS_EXCLUDED" in codes
        assert "RESIDUALS_PROPAGATED_TO_REMARKS" not in codes
        assert result.xml
        assert "humanReadableText" not in result.xml
        assert "ZZZZ" not in (result.xml or "")


def test_tc_ev981_005_profile_default_wire_annex3_off() -> None:
    """Omitted → annex3/ICAO_2025 default off; explicit true/false override wins."""
    assert resolve_propagate_residuals_to_remarks("annex3", None) is False
    assert resolve_propagate_residuals_to_remarks("icao_2025", None) is False
    assert resolve_propagate_residuals_to_remarks("ICAO_2025", None) is False
    assert resolve_propagate_residuals_to_remarks("annex3", False) is False
    assert resolve_propagate_residuals_to_remarks("annex3", True) is True
    # No other profile defaults enabled this cycle — unknown emit keys resolve False.
    assert resolve_propagate_residuals_to_remarks("iwxxm_us", None) is False
    assert resolve_propagate_residuals_to_remarks("ca_eccc", None) is False

    annex3_on = convert(
        _TAC_WITH_RESIDUAL,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
        propagate_residuals_to_remarks=True,
    )
    assert annex3_on.ok
    assert annex3_on.xml
    assert "ZZZZ" not in annex3_on.xml  # no invented annex3 free-text remarks
    assert "humanReadableText" not in annex3_on.xml
    prop = [i for i in annex3_on.issues if i.code == "RESIDUALS_PROPAGATED_TO_REMARKS"]
    assert len(prop) == 1
    assert prop[0].severity == "info"
    msg = (prop[0].message or "").lower()
    assert "no xml" in msg


def test_tc_ev981_002_flag_on_folds_residuals_into_iwxxm_us_hrt() -> None:
    """Flag true on iwxxm_us appends residual text into humanReadableText + issue."""
    off = convert(
        _TAC_WITH_RESIDUAL,
        product="METAR",
        profile="iwxxm_us",
        iwxxm_version="2025-2",
        propagate_residuals_to_remarks=False,
    )
    on = convert(
        _TAC_WITH_RESIDUAL,
        product="METAR",
        profile="iwxxm_us",
        iwxxm_version="2025-2",
        propagate_residuals_to_remarks=True,
    )
    assert off.ok
    assert on.ok
    assert off.xml
    assert on.xml
    assert "ZZZZ" not in off.xml
    assert "RESIDUALS_PROPAGATED_TO_REMARKS" not in [i.code for i in off.issues]
    assert "ZZZZ" in on.xml
    assert "iwxxm-us:humanReadableText" in on.xml
    prop = [i for i in on.issues if i.code == "RESIDUALS_PROPAGATED_TO_REMARKS"]
    assert len(prop) == 1
    assert prop[0].severity == "info"
    # Dedup: RMK free-text path must not double-count AO2/SLP into residual append alone.
    free = (on.ir or {}).get("remarks_free_text") or ""
    assert "ZZZZ" in str(free)


def test_tc_ev981_002_dedup_skips_residual_already_in_remarks_free_text() -> None:
    """Residual text already present in remarks_free_text is not appended twice."""
    # VIRGA NE is RMK remainder → remarks_free_text; ensure flag-on does not duplicate.
    tac = "METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK AO2 VIRGA NE="
    result = convert(
        tac,
        product="METAR",
        profile="iwxxm_us",
        iwxxm_version="2025-2",
        propagate_residuals_to_remarks=True,
    )
    assert result.ok
    assert result.xml
    free = str((result.ir or {}).get("remarks_free_text") or "")
    assert free.count("VIRGA NE") == 1


def test_tc_ev981_resolve_semantic_alias_and_empty_residual_paths() -> None:
    """Cover semantic-alias resolve fallthrough, blank residual skip, and no-residual fold."""
    from tac2iwxxm.convert import _residual_texts_to_append

    # Semantic id resolves emit_key but canonical is not in the defaults table.
    assert resolve_propagate_residuals_to_remarks("US_FAA_NWS", None) is False
    assert resolve_propagate_residuals_to_remarks("CA_ECCC", None) is False
    # Unresolved emit key → defaults table miss (resolved is None).
    assert resolve_propagate_residuals_to_remarks("unknown_profile_xyz", None) is False

    assert _residual_texts_to_append(["  ", "\t", "KEEP"], remarks_free_text="") == ["KEEP"]
    assert _residual_texts_to_append(["ZZZZ"], remarks_free_text="prefix ZZZZ suffix") == []

    clean = convert(
        _TAC_RMK_ONLY,
        product="METAR",
        profile="iwxxm_us",
        iwxxm_version="2025-2",
        propagate_residuals_to_remarks=True,
    )
    assert clean.ok
    assert "RESIDUALS_PROPAGATED_TO_REMARKS" not in [i.code for i in clean.issues]
