"""Unit tests for national extension token wire (EV-068 M5)."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from src.utilities.extension_wire import (
    IWXXM_CA_TOKEN,
    ca_eccc_validate_product,
    parse_extension_tokens,
    validate_extension_tokens,
)


def test_parse_extension_tokens_repeated_form_values() -> None:
    tokens = parse_extension_tokens(["IWXXM_CA", "iwxxm-ca"])
    assert tokens == [IWXXM_CA_TOKEN]


def test_parse_extension_tokens_json_array() -> None:
    tokens = parse_extension_tokens(['["IWXXM_CA"]'])
    assert tokens == [IWXXM_CA_TOKEN]


def test_validate_extension_tokens_rejects_unknown() -> None:
    with pytest.raises(HTTPException) as exc:
        validate_extension_tokens(["IWXXM_US_3"])
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "invalid_extensions"


def test_ca_eccc_validate_product_requires_iwxxm_ca_token() -> None:
    assert ca_eccc_validate_product("ca_eccc", [], "METAR") is None
    assert ca_eccc_validate_product("ca_eccc", [IWXXM_CA_TOKEN], "METAR") == "METAR"
    assert ca_eccc_validate_product("annex3", [IWXXM_CA_TOKEN], "METAR") is None
