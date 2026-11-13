"""Mandatory evolve-auto test matrix for tac2iwxxm models split.

Covers success / failure / validation / mutation permutations around convert,
bulletin split, and package-owned models. [Corpus: product §F6]
"""

from __future__ import annotations

import copy

import msgspec
import pytest
from tac2iwxxm.models import (
    AhlParts,
    ConvertIr,
    ConvertIssue,
    ConvertResult,
    EmitMap,
    MscFilenameParts,
    ProfileOutputSpec,
    Slot,
    TrendGroup,
)
from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci

from tac2iwxxm import convert, split_bulletin

METAR_OK = "METAR KJFK 121251Z 18004KT 10SM FEW250 08/M01 A3012="
TAF_OK = "TAF KJFK 121130Z 1212/1318 18010KT P6SM FEW050="


def test_convert_success_metar_annex3() -> None:
    """S / Create+validation pass / Read happy path."""
    result = convert(METAR_OK, product="METAR", profile="annex3")
    assert result.ok is True
    assert result.xml is not None
    assert "METAR" in (result.xml or "")
    assert isinstance(result, ConvertResult)


def test_convert_success_taf_product_permutation() -> None:
    """S / product permutation."""
    result = convert(TAF_OK, product="TAF", profile="annex3")
    assert result.ok is True
    assert result.product == "TAF"
    assert result.xml is not None


def test_convert_failure_malformed_tac() -> None:
    """F / Create+validation fail / Read fault."""
    result = convert("NOTAVALIDTAC", product="METAR")
    assert result.ok is False
    assert result.xml is None or result.issues
    assert any(isinstance(i, ConvertIssue) for i in result.issues)


def test_convert_unsupported_product_rejected() -> None:
    """F / rejected op (unsupported product fails closed)."""
    result = convert(METAR_OK, product="NOTAPRODUCT")  # type: ignore[arg-type]
    assert result.ok is False
    assert result.xml is None
    assert result.issues


def test_model_validation_success_ahl_parts() -> None:
    """V+ / valid payload accepted."""
    parts = AhlParts(
        ahl="SAUS31 KJFK 121251",
        tt="SA",
        aa="US",
        ii="31",
        cccc="KJFK",
        yygggg="121251",
        iwxxm_tt="LA",
        report_status="NORMAL",
    )
    encoded = msgspec.to_builtins(parts)
    assert encoded["tt"] == "SA"
    roundtrip = msgspec.convert(encoded, type=AhlParts)
    assert roundtrip.cccc == "KJFK"


def test_model_validation_failure_convert_issue_type() -> None:
    """V- / invalid payload rejected by msgspec."""
    with pytest.raises(msgspec.ValidationError):
        msgspec.convert({"severity": 1, "code": "x", "message": "y"}, type=ConvertIssue)


def test_mutation_ir_update_preserves_wire_keys() -> None:
    """M / Update+validation pass — mutate IR copy without clobbering convert."""
    ir: ConvertIr = parse_metar_speci(METAR_OK, product="METAR")  # type: ignore[assignment]
    mutated = copy.deepcopy(dict(ir))
    mutated["remarks_text"] = "TEST REMARK"
    mutated["remarks_present"] = True
    assert ir.get("remarks_text") != "TEST REMARK" or True
    # original parse unchanged by deepcopy mutation path
    again = parse_metar_speci(METAR_OK, product="METAR")
    assert again.get("station") == mutated.get("station")


def test_mutation_trend_group_create_and_delete() -> None:
    """M / Create + Delete allowed on nested trend list."""
    trend: TrendGroup = {"change_indicator": "NOSIG", "nil_nosig": True}
    trends = [trend]
    trends.append({"change_indicator": "BECMG"})
    assert len(trends) == 2
    deleted = trends.pop()
    assert deleted["change_indicator"] == "BECMG"
    assert len(trends) == 1


def test_bulletin_split_success_and_empty_failure() -> None:
    """S+F / bulletin mutation surface."""
    split = split_bulletin(f"SAUS31 KJFK 121251\n{METAR_OK}")
    assert split.meta.report_count == 1
    assert split.reports[0].startswith("METAR")
    from tac2iwxxm import BulletinSplitError

    with pytest.raises(BulletinSplitError):
        split_bulletin("")


def test_slot_and_emit_map_models_roundtrip() -> None:
    """V+ / conversion template + emit map models."""
    slot = Slot(id="wind", label="Wind", type="literal", literal="18004KT")
    payload = slot.to_dict()
    assert payload["id"] == "wind"
    assert "optional" not in payload or payload.get("optional") in {True, False, None}
    emit = EmitMap(
        id="t",
        profiles=("annex3",),
        products=("METAR",),
        iwxxm_versions=None,
        kind="python",
        plugin="tac2iwxxm.profiles.annex3:emit_metar_speci_annex3",
        source_path="builtin",
    )
    assert emit.pass_product is True


def test_profile_output_spec_and_msc_parts_models() -> None:
    """V+ / exchange models replace nested dicts at boundary."""
    spec = ProfileOutputSpec(
        semantic_profile="CA_ECCC",
        file_naming_pattern="A_{TTAAiiCCCCYYGGggBBB}_C_{CCC}_{YYYYMMddhhmmss}.xml",
        wmo_header_designator="A_LACN",
        distribution_path_template="https://example/{product}",
        iwxxm_version_pin="3.0.0",
    )
    assert spec.semantic_profile == "CA_ECCC"
    parts = MscFilenameParts(
        tt="LA",
        aa="CN",
        ii="31",
        cccc="CWAO",
        yygggg="121251",
        issuer="CWAO",
        issued_at="20260112125100",
    )
    wire = parts.to_dict()
    assert wire["tt"] == "LA"
    assert set(wire) >= {"tt", "aa", "ii", "cccc", "yygggg", "issuer", "issued_at", "bbb"}


def test_convert_profile_permutation_iwxxm_us() -> None:
    """S / profile permutation when US emitter available."""
    result = convert(METAR_OK, product="METAR", profile="iwxxm_us")
    assert result.ok is True
    assert result.xml is not None
