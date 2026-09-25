"""TC-F6-040 — gzip bytes beside the IWXXM text when the name ends in .xml.gz.

[Corpus: product §F6] [Corpus: tests §TC-F6-040]
"""

from __future__ import annotations

import gzip
from datetime import UTC, datetime

from tac2iwxxm.exchange_output import build_ca_eccc_output_spec

from tac2iwxxm import convert, parse_ahl

_BULLETIN = "SAUS31 KZNY 121200\nMETAR KJFK 121151Z 18012KT 9999 FEW020 15/07 Q1013=\n"
_BARE = "METAR KJFK 121151Z 18012KT 9999 FEW020 15/07 Q1013="


def test_tc_f6_040_gzip_filename_returns_bytes_that_decompress_to_the_xml() -> None:
    """A .xml.gz name carries gzip bytes of the same document kept on xml."""
    result = convert(
        _BULLETIN,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok is True, result.issues
    name = result.suggested_filename or ""
    assert name.endswith(".xml.gz")
    assert result.xml is not None
    assert result.xml.startswith("<?xml")
    assert result.xml_gzip is not None
    assert gzip.decompress(result.xml_gzip).decode("utf-8") == result.xml


def test_tc_f6_040_canada_xml_name_stays_plain() -> None:
    """Canada's .xml name is not gzip, and convert keeps the document as text."""
    result = convert(
        _BULLETIN,
        product="METAR",
        profile="ca_eccc",
    )
    assert result.ok is True, result.issues
    assert result.suggested_filename is None
    assert result.xml_gzip is None
    assert result.xml is not None
    assert result.xml.startswith("<?xml")
    parts = parse_ahl("SAUS31 KZNY 121200")
    spec = build_ca_eccc_output_spec(
        product="METAR",
        parts=parts,
        issued_at=datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
    )
    assert spec.suggested_filename is not None
    assert spec.suggested_filename.endswith(".xml")
    assert not spec.suggested_filename.endswith(".xml.gz")


def test_tc_f6_040_no_heading_invents_no_filename() -> None:
    """A bare report still has no suggested filename and no gzip bytes."""
    result = convert(
        _BARE,
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok is True, result.issues
    assert result.suggested_filename is None
    assert result.xml_gzip is None


def test_tc_f6_040_plain_name_and_missing_xml_are_not_compressed() -> None:
    """A .xml name and a missing document do not produce gzip bytes."""
    from tac2iwxxm.convert import _xml_gzip

    assert _xml_gzip("<?xml version='1.0'?><iwxxm/>", "A_LAUS31.xml") is None
    assert _xml_gzip(None, "A_LAUS31.xml.gz") is None
