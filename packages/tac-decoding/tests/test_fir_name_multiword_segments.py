"""Multi-word FIR names emit one decode segment (evolve-auto test matrix).

Combinatorial coverage: success / failure / validation / mutation for FIR-name
span joining in ``tac-decoding``. Cite evolve-auto ``test-matrix.md``.
"""

from __future__ import annotations

from tac_decoding.decode import (
    _extend_fir_name_span,
    _fir_name_continuation_token,
    decode_tac,
)


def _by_code(tac: str, product: str = "SIGMET") -> dict[str, str]:
    result = decode_tac(tac, product=product)
    return {segment.code: segment.explanation for segment in result.segments}


def _fir_name_segments(tac: str, product: str = "SIGMET") -> list[tuple[str, str]]:
    result = decode_tac(tac, product=product)
    return [
        (segment.code, segment.explanation)
        for segment in result.segments
        if segment.explanation.startswith("FIR name (")
    ]


# --- Success paths ---


def test_multiword_new_york_emits_one_fir_name_segment() -> None:
    """S: NEW YORK before OCEANIC FIR is one FIR name segment."""
    tac = "KZWY SIGMET BRAVO 3 VALID 051310/051710 KKCI- NEW YORK OCEANIC FIR EMBD TS="
    names = _fir_name_segments(tac)
    assert names == [("NEW YORK", "FIR name (NEW YORK)")]
    codes = _by_code(tac)
    assert "NEW" not in codes
    assert "YORK" not in codes
    assert codes["OCEANIC"] == "Oceanic FIR qualifier"
    assert codes["FIR"] == "Flight information region"


def test_multiword_la_paz_and_kota_kinabalu_emit_one_segment_each() -> None:
    """S: Other multi-word FIR names join; single-word SAL stays one token."""
    la_paz = _fir_name_segments(
        "SLLP SIGMET A2 VALID 051300/051600 SLLP- SLLF LA PAZ FIR EMBD TS=",
    )
    assert la_paz == [("LA PAZ", "FIR name (LA PAZ)")]
    kota = _fir_name_segments(
        "WBFC SIGMET 6 VALID 050916/051130 WBKK- WBFC KOTA KINABALU FIR EMBD TS=",
    )
    assert kota == [("KOTA KINABALU", "FIR name (KOTA KINABALU)")]
    sal = _fir_name_segments(
        "GVSC SIGMET 1 VALID 051703/052103 GVAC- GVSC SAL OCEANIC FIR/UIR EMBD TS=",
    )
    assert sal == [("SAL", "FIR name (SAL)")]


def test_single_word_fir_name_unchanged() -> None:
    """S: Single-token FIR names stay one segment."""
    codes = _by_code("SPIM SIGMET A9 VALID 052132/052350 SPJC- SPIM LIMA FIR EMBD TS=")
    assert codes["LIMA"] == "FIR name (LIMA)"
    assert _fir_name_segments(
        "NFFF SIGMET 1 VALID 051200/051600 NFFN- NFFF AUCKLAND FIR EMBD TS=",
    ) == [("AUCKLAND", "FIR name (AUCKLAND)")]


def test_two_separate_oceanic_fir_names_not_merged_across_fir_marker() -> None:
    """S: MIAMI … FIR HOUSTON … FIR stay two FIR names (after_fir restart)."""
    tac = (
        "WSNT12 KKCI 042305\n"
        "KZMA KZHU SIGMET LIMA 4 VALID 042305/050305 KKCI-\n"
        "MIAMI OCEANIC FIR HOUSTON OCEANIC FIR FRQ TS OBS AT 2305Z="
    )
    names = _fir_name_segments(tac)
    assert names == [
        ("MIAMI", "FIR name (MIAMI)"),
        ("HOUSTON", "FIR name (HOUSTON)"),
    ]


# --- Failure modes ---


def test_unknown_tokens_before_hazard_do_not_falsely_merge_into_fir_name() -> None:
    """F: Glossary / hazard tokens after FIR name stop the span."""
    tac = "YUDD SIGMET 1 VALID 101200/101600 YUSO- YUDD SHANLON FIR EMBD TS="
    names = _fir_name_segments(tac)
    assert names == [("SHANLON", "FIR name (SHANLON)")]
    codes = _by_code(tac)
    assert codes["EMBD"] != "FIR name (EMBD)"
    assert "TS" in codes


def test_malformed_empty_and_non_sigmet_stay_safe() -> None:
    """F: Empty / junk TAC does not raise; METAR does not invent FIR names."""
    empty = decode_tac("", product="SIGMET")
    assert empty.segments == []
    junk = decode_tac("NOT A REAL REPORT !!!", product="SIGMET")
    # Junk may pick up residual alphabetic tokens; must not invent a joined span.
    assert all(s.code != "REAL REPORT" for s in junk.segments)
    metar = decode_tac("METAR KJFK 051251Z 18010KT 10SM FEW250 20/10 A2992=", product="METAR")
    assert all(not s.explanation.startswith("FIR name (") for s in metar.segments)


# --- Validation success / failure (boundary cases) ---


def test_hyphenated_single_token_fir_name_accepted() -> None:
    """V+: Hyphenated FIR name token remains one segment."""
    tac = "UUWV SIGMET 1 VALID 101200/101600 UUWW- UUWV ROSTOV-NA-DONU FIR EMBD TS="
    names = _fir_name_segments(tac)
    assert names == [("ROSTOV-NA-DONU", "FIR name (ROSTOV-NA-DONU)")]


def test_trailing_new_alone_and_york_alone_are_single_segments() -> None:
    """V+: Lone NEW is a one-token FIR name; lone YORK stays ICAO-shaped ATS region."""
    assert _fir_name_segments(
        "KZWY SIGMET 1 VALID 051310/051710 KKCI- NEW FIR EMBD TS=",
    ) == [("NEW", "FIR name (NEW)")]
    york = _by_code("KZWY SIGMET 1 VALID 051310/051710 KKCI- YORK FIR EMBD TS=")
    assert york["YORK"] == "Affected FIR / ATS region (YORK)"
    assert (
        _fir_name_segments(
            "KZWY SIGMET 1 VALID 051310/051710 KKCI- YORK FIR EMBD TS=",
        )
        == []
    )


def test_new_york_at_end_of_line_before_fir() -> None:
    """V+: NEW YORK at end of line still joins across whitespace/newline."""
    tac = "KZWY SIGMET BRAVO 3 VALID 051310/051710 KKCI-\nNEW YORK\nOCEANIC FIR EMBD TS="
    names = _fir_name_segments(tac)
    assert len(names) == 1
    assert names[0][1] == "FIR name (NEW YORK)"
    assert "NEW" in names[0][0]
    assert "YORK" in names[0][0]


def test_icao_location_indicators_not_absorbed_into_fir_name() -> None:
    """V-: ICAO designators stay station/MWO/FIR-icao, not multi-word FIR name."""
    tac = "KZWY SIGMET 1 VALID 051310/051710 KKCI- KZWY FIR EMBD TS="
    result = decode_tac(tac, product="SIGMET")
    by_code_list = [(s.code, s.explanation) for s in result.segments]
    assert any(code == "KZWY" and ("location indicator" in expl or "ATS region" in expl) for code, expl in by_code_list)
    assert any(code == "KKCI-" and "watch office" in expl.lower() for code, expl in by_code_list)
    fir_names = _fir_name_segments(tac)
    assert all("KZWY" not in code for code, _ in fir_names)


# --- Mutation (re-decode after TAC edit) ---


def test_mutation_join_then_split_fir_name_region() -> None:
    """M: Re-decode after joining/splitting the name region updates segments."""
    split_tac = "KZWY SIGMET 1 VALID 051310/051710 KKCI- NEW FIR EMBD TS="
    joined_tac = "KZWY SIGMET 1 VALID 051310/051710 KKCI- NEW YORK FIR EMBD TS="
    assert _fir_name_segments(split_tac) == [("NEW", "FIR name (NEW)")]
    assert _fir_name_segments(joined_tac) == [("NEW YORK", "FIR name (NEW YORK)")]
    assert _fir_name_segments(split_tac) == [("NEW", "FIR name (NEW)")]


def test_mutation_insert_second_oceanic_fir_name() -> None:
    """M: Creating a second FIR block after FIR marker yields a new name segment."""
    one = "KZMA SIGMET 1 VALID 042305/050305 KKCI- MIAMI OCEANIC FIR FRQ TS="
    two = "KZMA SIGMET 1 VALID 042305/050305 KKCI- MIAMI OCEANIC FIR HOUSTON OCEANIC FIR FRQ TS="
    assert _fir_name_segments(one) == [("MIAMI", "FIR name (MIAMI)")]
    assert _fir_name_segments(two) == [
        ("MIAMI", "FIR name (MIAMI)"),
        ("HOUSTON", "FIR name (HOUSTON)"),
    ]

# --- Helper branch coverage (CI 100% gate) ---


def test_extend_fir_name_span_rejects_out_of_range_index() -> None:
    """Guard: index past the token list returns None without raising."""
    assert _extend_fir_name_span([], 0, tac="") is None
    assert _extend_fir_name_span([(0, 3, "NEW")], 1, tac="NEW") is None


def test_extend_fir_name_span_joins_through_end_of_token_list() -> None:
    """While-loop exit when continuation tokens run to the end of the list."""
    tac = "NEW YORK"
    tokens = [(0, 3, "NEW"), (4, 8, "YORK")]
    span = _extend_fir_name_span(tokens, 0, tac=tac)
    assert span is not None
    start, end, code, explanation, count = span
    assert (start, end, code, explanation, count) == (
        0,
        8,
        "NEW YORK",
        "FIR name (NEW YORK)",
        2,
    )


def test_fir_name_continuation_rejects_stop_and_glossary_tokens() -> None:
    """Continuation helper stops on FIR markers and glossary-backed words."""
    assert _fir_name_continuation_token("YORK") is True
    assert _fir_name_continuation_token("FIR") is False
    assert _fir_name_continuation_token("OCEANIC") is False
    assert _fir_name_continuation_token("EMBD") is False
    assert _fir_name_continuation_token("X") is False

