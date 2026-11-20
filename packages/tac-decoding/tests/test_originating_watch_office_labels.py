"""Originating watch office decode labels (operator-facing STE-plain copy).

Evolve-auto test matrix: success, mutation, failure, and validation permutations
for MWO segment explanations on SIGMET / AIRMET families.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest
from tac_decoding import DecodeResult, decode_tac, set_location_name_resolver

_OLD_PHRASE = "meteorological watch office"
_NEW_PHRASE = "Originating watch office"

_OFFICE_CODES = ("KKCI", "YUSO", "NZKL", "EGGX", "RJTD")

TacBuilder = Callable[[str], str]


@pytest.fixture(autouse=True)
def _clear_location_resolver() -> Iterator[None]:
    set_location_name_resolver(None)
    yield
    set_location_name_resolver(None)


def _mwo_explanations(result: DecodeResult) -> dict[str, str]:
    """Map hyphenated MWO codes to explanations."""
    out: dict[str, str] = {}
    for seg in result.segments:
        code = seg.code
        if code.endswith("-") and "watch office" in seg.explanation.lower():
            out[code] = seg.explanation
    return out


def _sigmet(office: str, fir: str = "YUDD") -> str:
    return (
        f"{fir} SIGMET 2 VALID 101200/101600 {office}-\n"
        f"{fir} SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 "
        f"TOP FL390 MOV E 20KT WKN="
    )


def _airmet(office: str, fir: str = "YUDD") -> str:
    return (
        f"{fir} AIRMET 1 VALID 151520/151800 {office}- {fir} SHANLON FIR ISOL TS OBS N OF S50 TOP ABV FL100 STNR WKN="
    )


@pytest.mark.parametrize("office", _OFFICE_CODES)
@pytest.mark.parametrize(("product", "builder"), [("SIGMET", _sigmet), ("AIRMET", _airmet)])
def test_success_originating_watch_office_label(
    office: str,
    product: str,
    builder: TacBuilder,
) -> None:
    """S / V+: valid ICAO MWO token gets the locked plain-language role label."""
    result = decode_tac(builder(office), product=product)
    code = f"{office}-"
    by_code = {seg.code: seg.explanation for seg in result.segments}
    assert code in by_code
    explanation = by_code[code]
    assert _NEW_PHRASE in explanation
    assert _OLD_PHRASE not in explanation.lower()
    assert f"({office})" in explanation


def test_success_place_name_variant_uses_new_label() -> None:
    """S / V+: when a place name resolves, keep the new role label."""
    set_location_name_resolver(
        lambda icao: "Kansas City" if icao == "KKCI" else None,
    )
    result = decode_tac(_sigmet("KKCI"), product="SIGMET")
    explanation = {seg.code: seg.explanation for seg in result.segments}["KKCI-"]
    assert explanation == "Originating watch office KKCI (Kansas City)"
    assert _OLD_PHRASE not in explanation.lower()


@pytest.mark.parametrize(("product", "builder"), [("SIGMET", _sigmet), ("AIRMET", _airmet)])
def test_mutation_redecode_swaps_office_label(
    product: str,
    builder: TacBuilder,
) -> None:
    """M x S / V+: re-decode after TAC office change; old label stays absent."""
    first = decode_tac(builder("KKCI"), product=product)
    first_by = {seg.code: seg.explanation for seg in first.segments}
    assert _NEW_PHRASE in first_by["KKCI-"]
    assert "YUSO-" not in first_by

    second = decode_tac(builder("YUSO"), product=product)
    second_by = {seg.code: seg.explanation for seg in second.segments}
    assert _NEW_PHRASE in second_by["YUSO-"]
    assert "KKCI-" not in second_by
    joined = " ".join(seg.explanation for seg in second.segments)
    assert _OLD_PHRASE not in joined.lower()


def test_mutation_product_switch_sigmet_to_airmet() -> None:
    """M x S: same office on a different product still uses the new label."""
    sig = decode_tac(_sigmet("NZKL"), product="SIGMET")
    air = decode_tac(_airmet("NZKL"), product="AIRMET")
    for result in (sig, air):
        explanation = {seg.code: seg.explanation for seg in result.segments}["NZKL-"]
        assert _NEW_PHRASE in explanation
        assert _OLD_PHRASE not in explanation.lower()


def test_failure_short_invalid_office_token_does_not_crash() -> None:
    """F / V-: non-ICAO short token is not labeled as MWO; decode stays safe."""
    tac = "YUDD SIGMET 2 VALID 101200/101600 AB- YUDD FIR TS="
    result = decode_tac(tac, product="SIGMET")
    explanations = [seg.explanation for seg in result.segments]
    joined = " ".join(explanations)
    assert _OLD_PHRASE not in joined.lower()
    # Short AB- is not a 4-letter ICAO MWO designator.
    assert not any(seg.code.rstrip("-") == "AB" and _NEW_PHRASE in seg.explanation for seg in result.segments)
    assert any(seg.code == "=" for seg in result.segments)


def test_failure_unknown_but_valid_icao_office_still_labels() -> None:
    """F / S: unknown designator (no place name) still gets designator-only copy."""
    result = decode_tac(_sigmet("XXXX"), product="SIGMET")
    explanation = {seg.code: seg.explanation for seg in result.segments}["XXXX-"]
    assert explanation == "Originating watch office (XXXX)"
    assert _OLD_PHRASE not in explanation.lower()


def test_validation_reject_path_missing_hyphen_office_still_safe() -> None:
    """V- / F: malformed header without hyphenated MWO does not crash."""
    tac = "YUDD SIGMET 2 VALID 101200/101600 YUSO YUDD FIR TS FCST="
    result = decode_tac(tac, product="SIGMET")
    joined = " ".join(seg.explanation for seg in result.segments)
    # May still classify a 4-letter token as watch office after VALID.
    if _NEW_PHRASE in joined:
        assert _OLD_PHRASE not in joined.lower()
    assert result.segments  # non-empty, no crash


def test_validation_all_products_old_phrase_absent() -> None:
    """Permutation: SIGMET + AIRMET x offices - old phrase never appears."""
    for product, builder in (("SIGMET", _sigmet), ("AIRMET", _airmet)):
        for office in _OFFICE_CODES:
            result = decode_tac(builder(office), product=product)
            joined = " ".join(seg.explanation for seg in result.segments)
            assert _OLD_PHRASE not in joined.lower()
            assert any(_NEW_PHRASE in seg.explanation and seg.code == f"{office}-" for seg in result.segments)


def test_read_query_mwo_map_nonempty_for_valid_header() -> None:
    """Read/query happy path: helper finds MWO explanations for a valid TAC."""
    result = decode_tac(_sigmet("KKCI"), product="SIGMET")
    found = _mwo_explanations(result)
    assert found == {"KKCI-": "Originating watch office (KKCI)"}


def test_mutation_location_resolver_create_update_clear() -> None:
    """M x S / V+: create place enrichment, update it, then clear (delete)."""
    set_location_name_resolver(lambda icao: "Kansas City" if icao == "KKCI" else None)
    created = decode_tac(_sigmet("KKCI"), product="SIGMET")
    assert {seg.code: seg.explanation for seg in created.segments}["KKCI-"] == (
        "Originating watch office KKCI (Kansas City)"
    )

    set_location_name_resolver(lambda icao: "KC ARTCC" if icao == "KKCI" else None)
    updated = decode_tac(_sigmet("KKCI"), product="SIGMET")
    assert {seg.code: seg.explanation for seg in updated.segments}["KKCI-"] == (
        "Originating watch office KKCI (KC ARTCC)"
    )

    set_location_name_resolver(None)
    cleared = decode_tac(_sigmet("KKCI"), product="SIGMET")
    assert {seg.code: seg.explanation for seg in cleared.segments}["KKCI-"] == ("Originating watch office (KKCI)")


def test_failure_empty_and_garbage_tac_stay_safe() -> None:
    """F / V-: empty or non-header TAC does not emit the old phrase or crash."""
    for tac in ("", "NOT A SIGMET", "METAR KJFK 101200Z="):
        result = decode_tac(tac, product="SIGMET")
        joined = " ".join(seg.explanation for seg in result.segments)
        assert _OLD_PHRASE not in joined.lower()
        assert not any(_NEW_PHRASE in seg.explanation for seg in result.segments)


def test_read_query_fault_no_mwo_when_header_missing() -> None:
    """Read/query fault: helper map is empty when no hyphenated MWO appears."""
    result = decode_tac("YUDD SIGMET 2 VALID 101200/101600 YUDD FIR TS=", product="SIGMET")
    assert _mwo_explanations(result) == {}


@pytest.mark.parametrize("office", ["KKCI", "YUSO"])
def test_validation_place_and_designator_forms(office: str) -> None:
    """V+: designator-only and place-resolved forms both keep the new label."""
    bare = decode_tac(_sigmet(office), product="SIGMET")
    bare_expl = {seg.code: seg.explanation for seg in bare.segments}[f"{office}-"]
    assert bare_expl == f"Originating watch office ({office})"

    set_location_name_resolver(lambda icao: "Named Place" if icao == office else None)
    named = decode_tac(_sigmet(office), product="SIGMET")
    named_expl = {seg.code: seg.explanation for seg in named.segments}[f"{office}-"]
    assert named_expl == f"Originating watch office {office} (Named Place)"
    assert _OLD_PHRASE not in named_expl.lower()
