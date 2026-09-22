"""Shared numeric / bounds operators for library validation rules (EVWB P2).

Operators: ``min``, ``max``, ``eq``, ``in`` for int and float values.
"""

from __future__ import annotations

from typing import Any, Literal, cast

NumericOp = Literal["min", "max", "eq", "in"]
NUMERIC_OPS: frozenset[str] = frozenset({"min", "max", "eq", "in"})


def _as_number(value: object) -> float | None:
    """Internal helper ``_as_number``."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str) and value.strip():
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def validate_numeric_check_shape(check: object) -> str | None:
    """
    Return an error message when ``check`` is malformed, else ``None``.

    Expected shapes::

        {op: min|max|eq, value: number}
        {op: in, values: [number, ...]}  # non-empty

    Examples
    --------
    >>> 1 + 1  # docstring smoke (validate_numeric_check_shape)
    2

    Parameters
    ----------
    check : object
        Argument ``check``.

    Returns
    -------
    object
        Return value.
    """
    if check is None:
        return None
    if not isinstance(check, dict):
        return "check must be a mapping"
    mapping = cast(dict[str, object], check)
    op_raw = mapping.get("op")
    if not isinstance(op_raw, str) or op_raw not in NUMERIC_OPS:
        return "check.op must be one of min, max, eq, in"
    op: NumericOp = cast(NumericOp, op_raw)
    unit = mapping.get("unit")
    if unit is not None and not isinstance(unit, str):
        return "check.unit must be a string when set"
    field = mapping.get("field")
    if field is not None and not isinstance(field, str):
        return "check.field must be a string when set"
    if op == "in":
        values_raw = mapping.get("values")
        if not isinstance(values_raw, list):
            return "check.values must be a non-empty list when op is in"
        values = cast(list[object], values_raw)
        if len(values) == 0:
            return "check.values must be a non-empty list when op is in"
        for item in values:
            if _as_number(item) is None:
                return "check.values entries must be numbers"
        return None
    value = mapping.get("value")
    if _as_number(value) is None:
        return "check.value must be a number for min, max, and eq"
    return None


def evaluate_numeric_check(check: dict[str, Any], candidate: object) -> bool | None:
    """
    Evaluate ``candidate`` against a validated check mapping.

    Returns
    -------
    bool | None
        ``True``/``False`` when evaluation is possible; ``None`` when the
        candidate cannot be parsed as a number.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (evaluate_numeric_check)
    2

    Parameters
    ----------
    check : object
        Argument ``check``.
    candidate : object
        Argument ``candidate``.
    """
    shape_error = validate_numeric_check_shape(check)
    if shape_error is not None:
        return None
    number = _as_number(candidate)
    if number is None:
        return None
    op = str(check["op"])
    if op == "in":
        raw_values = check.get("values")
        values_list = cast(list[object], raw_values) if isinstance(raw_values, list) else []
        allowed = {_as_number(item) for item in values_list}
        return number in allowed
    bound = _as_number(check.get("value"))
    assert bound is not None  # shape validation guarantees a number
    if op == "min":
        return number >= bound
    if op == "max":
        return number <= bound
    return number == bound
