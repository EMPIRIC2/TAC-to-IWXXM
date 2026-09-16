"""TC-EVPYL-REGEX / CROSS — library YAML + regex diagnostics (Phase C)."""

from __future__ import annotations

from tac2iwxxm.library_yaml import diagnose_regex, validate_library_yaml


def test_tc_evpyl_regex_001_compile_and_captures() -> None:
    diag = diagnose_regex(r"(?P<wind>\d{5})KT", sample="18004KT", path="rules[0].pattern")
    assert diag.severity == "ok"
    assert diag.sample_matched is True
    assert diag.captures[0].name == "wind"


def test_tc_evpyl_regex_002_fail_does_not_compile() -> None:
    diag = diagnose_regex(r"(unclosed", path="rules[0].pattern")
    assert diag.severity == "fail"
    assert "compile" in diag.message.lower()


def test_tc_evpyl_regex_003_fail_empty_sample_match() -> None:
    diag = diagnose_regex(r"^TAF ", sample="METAR KJFK", path="rules[0].pattern")
    assert diag.severity == "fail"
    assert diag.sample_matched is False


def test_tc_evpyl_regex_warn_nested_quantifier() -> None:
    diag = diagnose_regex(r"(a+)+b")
    assert diag.severity == "warn"


def test_tc_evpyl_cross_001_invalid_yaml_blocks_activate() -> None:
    report = validate_library_yaml("kind: conversion\n  bad indent", expected_kind="conversion")
    assert report.valid_yaml is False
    assert report.can_activate is False
    assert report.fail_count >= 1


def test_tc_evpyl_cross_002_fail_allows_draft_not_activate() -> None:
    raw = """
kind: tac_validation
name: Broken wind
rules:
  - pattern: "(unclosed"
    sample: "18004KT"
"""
    report = validate_library_yaml(raw, expected_kind="tac_validation", lifecycle="draft")
    assert report.valid_yaml is True
    assert report.fail_count >= 1
    assert report.can_activate is False


def test_tc_evpyl_cross_003_warn_allows_activate() -> None:
    raw = """
kind: tac_validation
name: Risky but compiling
rules:
  - pattern: "(a+)+b"
"""
    report = validate_library_yaml(raw, expected_kind="tac_validation")
    assert report.valid_yaml is True
    assert report.fail_count == 0
    assert report.warn_count >= 1
    assert report.can_activate is True


def test_tc_evpyl_dissem_rejects_secret_uri() -> None:
    raw = """
kind: dissemination
name: Bad sink
transforms:
  - id: envelope
    uri: https://example.invalid/push
"""
    report = validate_library_yaml(raw, expected_kind="dissemination")
    assert report.valid_yaml is False
    assert "credential" in (report.yaml_error or "").lower() or "uri" in (report.yaml_error or "").lower()


def test_validate_library_yaml_to_dict_roundtrip() -> None:
    raw = """
kind: decoding
name: Gloss
entries:
  - token: BR
    explanation: mist
"""
    report = validate_library_yaml(raw, expected_kind="decoding")
    payload = report.to_dict()
    assert payload["valid_yaml"] is True
    assert payload["can_activate"] is True
    assert payload["kind"] == "decoding"
    assert payload["data"]["kind"] == "decoding"


def test_empty_and_wrong_kind_and_missing_name() -> None:
    empty = validate_library_yaml("   ")
    assert empty.valid_yaml is False
    mapping = validate_library_yaml("- just a list")
    assert mapping.valid_yaml is False
    kind = validate_library_yaml("kind: nope\nname: x", expected_kind="conversion")
    assert kind.valid_yaml is False
    mismatch = validate_library_yaml("kind: decoding\nname: x", expected_kind="conversion")
    assert mismatch.valid_yaml is False
    nameless = validate_library_yaml("kind: conversion\nblocks: []", expected_kind="conversion")
    assert nameless.valid_yaml is False


def test_extracts_patterns_for_all_five_kinds() -> None:
    conversion = validate_library_yaml(
        """
kind: conversion
name: Wind
rules:
  - not-a-mapping
  - pattern: "(?P<dir>\\\\d{3})"
    sample: "180"
""",
        expected_kind="conversion",
    )
    assert conversion.valid_yaml is True
    assert conversion.diagnostics[0].captures[0].name == "dir"

    iwxxm = validate_library_yaml(
        """
kind: iwxxm_validation
name: Custom XML
rules:
  - regex: "visibility.+"
    sample: "visibility 10km"
  - xpath: "iwxxm:METAR"
""",
        expected_kind="iwxxm_validation",
    )
    assert iwxxm.valid_yaml is True
    assert iwxxm.fail_count == 0

    decoding = validate_library_yaml(
        """
kind: decoding
name: Token regex
entries:
  - not-a-mapping
  - token: BR
    explanation: mist
  - regex: "TSRA|TS"
    sample: "TSRA"
""",
        expected_kind="decoding",
    )
    assert decoding.valid_yaml is True
    assert any(item.path.startswith("entries") for item in decoding.diagnostics)

    dissem = validate_library_yaml(
        """
kind: dissemination
name: Filename
transforms:
  - not-a-mapping
  - id: topic_filename
    pattern: "A_[A-Z]{4}"
    sample: "A_KJFK"
""",
        expected_kind="dissemination",
    )
    assert dissem.valid_yaml is True
    assert dissem.can_activate is True


def test_positional_groups_are_named_and_skipped_non_patterns() -> None:
    diag = diagnose_regex(r"(abc)(def)")
    assert diag.severity == "warn"
    assert [c.name for c in diag.captures] == ["group1", "group2"]
    tac = validate_library_yaml(
        """
kind: tac_validation
name: Empty rules
rules:
  - severity: error
  - regex: "(?P<vis>\\\\d{4})"
    sample: "9999"
""",
        expected_kind="tac_validation",
    )
    assert tac.valid_yaml is True
    assert any(item.path.endswith("pattern") for item in tac.diagnostics)

    iwxxm_xpath = validate_library_yaml(
        """
kind: iwxxm_validation
name: XPath only
custom_rules:
  - regex: "/iwxxm:METAR"
  - regex: "iwxxm:Cloud"
""",
        expected_kind="iwxxm_validation",
    )
    assert iwxxm_xpath.valid_yaml is True
    assert iwxxm_xpath.diagnostics == ()

    decode_plain = validate_library_yaml(
        """
kind: decoding
name: Plain token
entries:
  - token: BR
""",
        expected_kind="decoding",
    )
    assert decode_plain.valid_yaml is True
    assert decode_plain.diagnostics == ()


def test_yaml_parser_error_is_fail() -> None:
    report = validate_library_yaml("kind: conversion\nname: x\nfoo: [")
    assert report.valid_yaml is False
    assert report.can_activate is False
