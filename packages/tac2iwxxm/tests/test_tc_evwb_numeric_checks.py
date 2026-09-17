"""Tests for shared numeric check operators (EVWB P2 / TC-EVWB-TAC)."""

from tac2iwxxm.library_yaml import validate_library_yaml
from tac2iwxxm.numeric_checks import (
    _as_number,
    evaluate_numeric_check,
    validate_numeric_check_shape,
)


def test_as_number_rejects_bool_and_junk() -> None:
    assert _as_number(True) is None
    assert _as_number("not-a-number") is None
    assert _as_number(None) is None
    assert _as_number(12) == 12.0


def test_validate_numeric_check_shape_ops() -> None:
    assert validate_numeric_check_shape(None) is None
    assert validate_numeric_check_shape({"op": "min", "value": 0}) is None
    assert validate_numeric_check_shape({"op": "max", "value": 99.5}) is None
    assert validate_numeric_check_shape({"op": "eq", "value": "12"}) is None
    assert validate_numeric_check_shape({"op": "in", "values": [1, 2.5]}) is None
    assert validate_numeric_check_shape({"op": "nope", "value": 1}) is not None
    assert validate_numeric_check_shape({"op": "in", "values": []}) is not None
    assert validate_numeric_check_shape({"op": "in", "values": "x"}) is not None
    assert validate_numeric_check_shape({"op": "in", "values": ["x"]}) is not None
    assert validate_numeric_check_shape({"op": "min", "value": "x"}) is not None
    assert validate_numeric_check_shape({"op": "min", "value": 1, "unit": 3}) is not None
    assert validate_numeric_check_shape({"op": "min", "value": 1, "field": 3}) is not None
    assert validate_numeric_check_shape("x") is not None


def test_evaluate_numeric_check_min_max_eq_in() -> None:
    assert evaluate_numeric_check({"op": "min", "value": 10}, "12") is True
    assert evaluate_numeric_check({"op": "min", "value": 10}, "8") is False
    assert evaluate_numeric_check({"op": "max", "value": 10}, "8") is True
    assert evaluate_numeric_check({"op": "eq", "value": 5}, 5) is True
    assert evaluate_numeric_check({"op": "in", "values": [1, 2, 3]}, "2") is True
    assert evaluate_numeric_check({"op": "in", "values": [1, 2, 3]}, "9") is False
    assert evaluate_numeric_check({"op": "eq", "value": 1}, "abc") is None
    assert evaluate_numeric_check({"op": "nope", "value": 1}, "1") is None
    # Shape-valid dict with non-numeric value key bypasses shape when value missing
    # after op validation — force bound None via empty string value after cast path.
    assert evaluate_numeric_check({"op": "eq", "value": ""}, "1") is None


def test_library_yaml_rejects_bad_numeric_check() -> None:
    report = validate_library_yaml(
        """
kind: tac_validation
name: Bad check
rules:
  - id: CUSTOM.X
    pattern: "(?P<value>\\\\d+)"
    sample: "12"
    check:
      op: nope
      value: 1
""",
        expected_kind="tac_validation",
    )
    assert report.valid_yaml is True
    assert report.fail_count >= 1
    assert any("check.op" in item.message for item in report.diagnostics)


def test_library_yaml_sample_fails_numeric_max() -> None:
    report = validate_library_yaml(
        """
kind: tac_validation
name: Bound check
rules:
  - id: CUSTOM.WIND
    pattern: "(?P<value>\\\\d+)"
    sample: "120"
    check:
      op: max
      value: 99
      field: value
""",
        expected_kind="tac_validation",
    )
    assert report.fail_count >= 1
    assert any("numeric check" in item.message for item in report.diagnostics)


def test_library_yaml_numeric_check_ok() -> None:
    report = validate_library_yaml(
        """
kind: tac_validation
name: Bound check ok
rules:
  - id: CUSTOM.WIND
    pattern: "(?P<value>\\\\d+)"
    sample: "12"
    check:
      op: max
      value: 99
      field: value
      unit: KT
""",
        expected_kind="tac_validation",
    )
    assert report.valid_yaml is True
    assert report.can_activate is True


def test_library_yaml_numeric_null_check_and_no_sample() -> None:
    report = validate_library_yaml(
        """
kind: tac_validation
name: Null check
rules:
  - id: CUSTOM.A
    pattern: "(?P<value>\\\\d+)"
    check: null
  - id: CUSTOM.B
    pattern: "(?P<value>\\\\d+)"
    check:
      op: min
      value: 1
""",
        expected_kind="tac_validation",
    )
    assert report.valid_yaml is True


def test_library_yaml_numeric_branch_edges() -> None:
    report = validate_library_yaml(
        """
kind: tac_validation
name: Branch edges
rules:
  - skip-scalar
  - {}
  - id: CUSTOM.NOSAMPLEFIELD
    sample: "12"
    check:
      op: eq
      value: 12
  - id: CUSTOM.NOMATCH
    pattern: "abc"
    sample: "zzz"
    check:
      op: eq
      value: 1
      field: value
""",
        expected_kind="tac_validation",
    )
    assert report.valid_yaml is True

    report = validate_library_yaml(
        """
kind: iwxxm_validation
name: IWXXM custom
custom_rules:
  - id: CUSTOM.BADPAT
    regex: "(?P<"
    sample: "12"
    check:
      op: eq
      value: 12
      field: value
  - id: CUSTOM.MISSGROUP
    regex: "(?P<other>\\\\d+)"
    sample: "12"
    check:
      op: eq
      value: 12
      field: missing
  - id: CUSTOM.OK
    regex: "(?P<value>\\\\d+)"
    sample: "12"
    check:
      op: eq
      value: 12
      field: value
""",
        expected_kind="iwxxm_validation",
    )
    assert report.valid_yaml is True
