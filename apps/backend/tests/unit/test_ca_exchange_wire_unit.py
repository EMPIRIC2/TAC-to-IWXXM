"""Unit tests for CA_ECCC exchange wire helpers (EV-073 M1)."""

from __future__ import annotations

from dissemination.collect_namespaces import is_collect_bulletin

from src.utilities.ca_exchange_wire import (
    apply_ca_eccc_collect_output,
    ca_collect_bulletin_identifier,
    ca_eccc_output_spec_for_request,
)

_INNER = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0" gml:id="x">\n'
    '  <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
    "</iwxxm:METAR>"
)

_BULLETIN = """\
SAUL31 CYUL 231800
METAR CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012=
"""


def test_ca_collect_bulletin_identifier_from_ahl() -> None:
    filename = ca_collect_bulletin_identifier(product="METAR", tac_input=_BULLETIN)
    assert filename
    assert filename.endswith(".xml")


def test_apply_ca_eccc_collect_output_wraps_when_requested() -> None:
    wrapped = apply_ca_eccc_collect_output(
        _INNER,
        semantic_canonical="ca_eccc",
        exchange_output=True,
        product="METAR",
        tac_input=_BULLETIN,
    )
    assert is_collect_bulletin(wrapped)


def test_apply_ca_eccc_collect_output_noop_without_flag() -> None:
    assert (
        apply_ca_eccc_collect_output(
            _INNER,
            semantic_canonical="ca_eccc",
            exchange_output=False,
            product="METAR",
            tac_input=_BULLETIN,
        )
        == _INNER
    )


def test_ca_eccc_output_spec_for_request_non_ca_profile() -> None:
    assert (
        ca_eccc_output_spec_for_request(
            semantic_canonical="icao_2025",
            product="METAR",
            sample_text=_BULLETIN,
        )
        is None
    )


def test_ca_eccc_output_spec_for_request_with_ahl() -> None:
    spec = ca_eccc_output_spec_for_request(
        semantic_canonical="ca_eccc",
        product="METAR",
        sample_text=_BULLETIN,
    )
    assert spec is not None
    assert spec.get("suggested_filename", "").endswith(".xml")


def test_ca_collect_bulletin_identifier_empty_input() -> None:
    assert ca_collect_bulletin_identifier(product="METAR", tac_input=None) is None
    assert ca_collect_bulletin_identifier(product="METAR", tac_input="   ") is None


def test_apply_ca_eccc_collect_output_uses_precomputed_identifier() -> None:
    wrapped = apply_ca_eccc_collect_output(
        _INNER,
        semantic_canonical="ca_eccc",
        exchange_output=True,
        product="METAR",
        tac_input=None,
        bulletin_identifier="precomputed.xml",
    )
    assert is_collect_bulletin(wrapped)
    assert "precomputed.xml" in wrapped


def test_apply_ca_eccc_collect_output_falls_back_to_bulletin_context() -> None:
    wrapped = apply_ca_eccc_collect_output(
        _INNER,
        semantic_canonical="ca_eccc",
        exchange_output=True,
        product="METAR",
        tac_input="METAR CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012=",
        bulletin_context=_BULLETIN,
    )
    assert is_collect_bulletin(wrapped)


def test_ca_eccc_output_spec_for_request_without_sample_text() -> None:
    spec = ca_eccc_output_spec_for_request(
        semantic_canonical="ca_eccc",
        product="METAR",
        sample_text=None,
    )
    assert spec is not None
    assert spec["semantic_profile"] == "CA_ECCC"


def test_ca_eccc_output_spec_for_request_tolerates_unsplitable_bulletin() -> None:
    spec = ca_eccc_output_spec_for_request(
        semantic_canonical="ca_eccc",
        product="METAR",
        sample_text="not a bulletin",
    )
    assert spec is not None
    assert spec["semantic_profile"] == "CA_ECCC"


def test_apply_ca_eccc_collect_output_noop_without_bulletin_id() -> None:
    assert (
        apply_ca_eccc_collect_output(
            _INNER,
            semantic_canonical="ca_eccc",
            exchange_output=True,
            product="METAR",
            tac_input="not a bulletin",
        )
        == _INNER
    )
