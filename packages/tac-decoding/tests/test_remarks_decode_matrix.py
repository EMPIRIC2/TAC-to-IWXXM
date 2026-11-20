"""Combinatorial test matrix for ICAO METAR/SPECI remarks decode.

Covers success / mutation / failure / validation permutations.
[Corpus: product §F9] [Corpus: domain] [Corpus: tests]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac_decoding import (
    REMARK_FAMILIES,
    RemarkDecodeResult,
    RemarkGroup,
    classify_remark_token,
    decode_remarks,
    decode_tac,
    segment_remarks,
)
from tac_decoding.cli import main
from tac_decoding.remarks_decode import shift_remark_groups

_BASE = "METAR KJFK 121755Z 18010KT 10SM FEW050 22/12 A2992"


def _by_code(result: RemarkDecodeResult) -> dict[str, RemarkGroup]:
    return {group.code.upper(): group for group in result.groups}


# --- Success paths ---


def test_success_segment_and_decode_core_code_groups() -> None:
    """Happy path: RMK segmenter finds SLP, T, AO, precip, PRESFR/PRESRR, ice."""
    tac = f"{_BASE} RMK AO2 SLP125 T02220117 P0003 PRESRR I1000="
    result = decode_remarks(tac)
    assert result.has_remarks is True
    by_code = _by_code(result)
    assert by_code["RMK"].family == "marker"
    assert by_code["AO2"].family == "sensor_ao"
    assert by_code["AO2"].valid is True
    assert by_code["SLP125"].family == "sea_level_pressure"
    assert "Sea-level" in by_code["SLP125"].explanation
    assert by_code["T02220117"].family == "temperature_tenths"
    assert by_code["P0003"].family == "precip_hourly"
    assert by_code["PRESRR"].family == "pressure_rapid"
    assert by_code["I1000"].family == "ice_accretion"
    assert by_code["I1000"].valid is True


def test_success_decode_tac_attaches_structured_remarks() -> None:
    """decode_tac attaches structured remarks for METAR/SPECI."""
    tac = f"{_BASE} RMK AO2 SLP125 PRESFR="
    metar = decode_tac(tac, product="METAR")
    assert metar.remarks
    families = {group.family for group in metar.remarks}
    assert "sensor_ao" in families
    assert "sea_level_pressure" in families
    assert "pressure_rapid" in families
    speci = decode_tac(tac.replace("METAR", "SPECI"), product="SPECI")
    assert speci.remarks
    assert any(group.code.upper() == "AO2" for group in speci.remarks)


def test_success_catalog_families_are_documented() -> None:
    """Catalog lists the code-group families used by the classifier."""
    assert "sea_level_pressure" in REMARK_FAMILIES
    assert "sensor_ao" in REMARK_FAMILIES
    assert "wx_begin_end" in REMARK_FAMILIES
    assert classify_remark_token("RAB19")[0] == "wx_begin_end"
    assert classify_remark_token("ST3CU1")[0] == "canadian_cloud"
    assert classify_remark_token("VCSH")[0] == "plain_national"
    assert classify_remark_token("DSNT")[0] == "prose"
    assert classify_remark_token("NE")[0] == "direction"


# --- Mutation modes (create / update / delete of remarks state) ---


def test_mutation_create_remarks_when_rmk_added() -> None:
    """Create: adding RMK creates structured remark groups."""
    bare = decode_tac(f"{_BASE}=", product="METAR")
    assert bare.remarks == []
    with_rmk = decode_tac(f"{_BASE} RMK AO2 SLP040=", product="METAR")
    assert with_rmk.remarks
    assert any(group.family == "sea_level_pressure" for group in with_rmk.remarks)


def test_mutation_update_remarks_when_groups_change() -> None:
    """Update: changing RMK tokens updates structured groups."""
    first = decode_remarks(f"{_BASE} RMK AO2 SLP040=")
    second = decode_remarks(f"{_BASE} RMK AO1 PRESFR P0000=")
    assert _by_code(first)["SLP040"].family == "sea_level_pressure"
    assert "SLP040" not in _by_code(second)
    assert _by_code(second)["AO1"].family == "sensor_ao"
    assert _by_code(second)["PRESFR"].family == "pressure_rapid"


def test_mutation_delete_remarks_when_rmk_removed() -> None:
    """Delete: removing RMK clears structured remarks."""
    with_rmk = decode_tac(f"{_BASE} RMK AO2=", product="METAR")
    assert with_rmk.remarks
    without = decode_tac(f"{_BASE}=", product="METAR")
    assert without.remarks == []
    assert decode_remarks(f"{_BASE}=").has_remarks is False


# --- Failure modes ---


def test_failure_unknown_token_marked_invalid() -> None:
    """Unknown remarks token is classified unknown and invalid."""
    result = decode_remarks(f"{_BASE} RMK ZZQX9=")
    group = _by_code(result)["ZZQX9"]
    assert group.family == "unknown"
    assert group.valid is False
    assert group.explanation == ""


def test_failure_no_rmk_returns_empty() -> None:
    """Absence of RMK is a clean empty result (not an exception)."""
    result = decode_remarks(f"{_BASE}=")
    assert result.has_remarks is False
    assert result.groups == []
    assert segment_remarks(f"{_BASE}=") == []


def test_failure_taf_does_not_attach_metar_remarks() -> None:
    """TAF path does not populate METAR/SPECI structured remarks."""
    taf = decode_tac("TAF KJFK 121730Z 1218/1324 18010KT P6SM FEW050=", product="TAF")
    assert taf.remarks == []


# --- Validation success / failure ---


@pytest.mark.parametrize(
    ("token", "family"),
    [
        ("SLP125", "sea_level_pressure"),
        ("SLPNO", "sea_level_pressure"),
        ("T02220117", "temperature_tenths"),
        ("P0003", "precip_hourly"),
        ("60003", "precip_period"),
        ("52032", "pressure_tendency"),
        ("PRESFR", "pressure_rapid"),
        ("I0000", "ice_accretion"),
        ("AO2A", "sensor_ao"),
        ("PWINO", "sensor_status"),
    ],
)
def test_validation_pass_known_shapes(token: str, family: str) -> None:
    """Valid coded shapes are accepted into their catalog family."""
    fam, ok = classify_remark_token(token)
    assert fam == family
    assert ok is True
    decoded = decode_remarks(f"{_BASE} RMK {token}=")
    group = _by_code(decoded)[token]
    assert group.family == family
    assert group.valid is True


@pytest.mark.parametrize(
    ("token", "family"),
    [
        ("SLPAB", "sea_level_pressure"),
        ("SLP1", "sea_level_pressure"),
        ("T12", "temperature_tenths"),
        ("I12", "ice_accretion"),
        ("P12", "precip_hourly"),
        ("5AB12", "pressure_tendency"),
    ],
)
def test_validation_fail_malformed_shapes(token: str, family: str) -> None:
    """Malformed coded shapes are rejected (validation failure)."""
    fam, ok = classify_remark_token(token)
    assert fam == family
    assert ok is False
    decoded = decode_remarks(f"{_BASE} RMK {token}=")
    group = _by_code(decoded)[token]
    assert group.valid is False


# --- Combinatorial create/update x validation ---


def test_create_validation_pass() -> None:
    """Create + validation pass: new valid SLP group appears."""
    result = decode_remarks(f"{_BASE} RMK SLP200=")
    assert _by_code(result)["SLP200"].valid is True


def test_create_validation_fail() -> None:
    """Create + validation fail: new malformed SLP is invalid."""
    result = decode_remarks(f"{_BASE} RMK SLPXZ=")
    assert _by_code(result)["SLPXZ"].valid is False


def test_update_validation_pass() -> None:
    """Update + validation pass: replace invalid group with valid."""
    bad = decode_remarks(f"{_BASE} RMK SLPXZ=")
    good = decode_remarks(f"{_BASE} RMK SLP200=")
    assert _by_code(bad)["SLPXZ"].valid is False
    assert _by_code(good)["SLP200"].valid is True


def test_update_validation_fail() -> None:
    """Update + validation fail: replace valid group with malformed."""
    good = decode_remarks(f"{_BASE} RMK I1000=")
    bad = decode_remarks(f"{_BASE} RMK I12=")
    assert _by_code(good)["I1000"].valid is True
    assert _by_code(bad)["I12"].valid is False


def test_delete_allowed_clears_groups() -> None:
    """Delete + allowed: stripping RMK clears groups."""
    assert decode_remarks(f"{_BASE} RMK AO2=").groups
    cleared = decode_remarks(f"{_BASE}=")
    assert cleared.groups == []


def test_read_query_happy_and_fault() -> None:
    """Read/query happy path and not-found (no RMK)."""
    found = segment_remarks(f"{_BASE} RMK AO2=")
    assert found
    assert found[0][2].upper() == "RMK"
    missing = segment_remarks("METAR KJFK 121755Z=")
    assert missing == []


def test_shift_remark_groups_offsets() -> None:
    """Offset shift for bulletin/COLLECT parent documents."""
    groups = decode_remarks(f"{_BASE} RMK AO2=").groups
    shifted = shift_remark_groups(groups, 10)
    assert shifted[0].start == groups[0].start + 10
    assert shifted[0].end == groups[0].end + 10
    assert shift_remark_groups(groups, 0)[0].start == groups[0].start


def test_cli_json_includes_remarks(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI JSON emits structured remarks when RMK is present."""
    path = tmp_path / "rmk.tac"
    path.write_text(f"{_BASE} RMK AO2 SLP125=", encoding="utf-8")
    assert main([str(path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "remarks" in payload
    assert any(row["family"] == "sensor_ao" for row in payload["remarks"])


def test_period_and_tendency_and_peak_wind() -> None:
    """Extra catalog families: period precip, tendency, peak wind token."""
    tac = f"{_BASE} RMK 60012 52032 28032/1542="
    by_code = _by_code(decode_remarks(tac))
    assert by_code["60012"].family == "precip_period"
    assert by_code["52032"].family == "pressure_tendency"
    assert by_code["28032/1542"].family == "peak_wind"


def test_known_family_without_explainer_uses_family_label(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When shape is ok but the explainer returns nothing, keep family label."""
    import tac_decoding.remarks_decode as remarks_mod

    monkeypatch.setattr(
        remarks_mod,
        "_explain_metar_speci",
        lambda *_args, **_kwargs: None,
    )
    result = decode_remarks(f"{_BASE} RMK AO2=")
    group = _by_code(result)["AO2"]
    assert group.family == "sensor_ao"
    assert group.valid is True
    assert group.explanation == "sensor ao"
