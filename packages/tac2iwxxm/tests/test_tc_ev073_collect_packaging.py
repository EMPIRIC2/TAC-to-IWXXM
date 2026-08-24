"""TC-EV073-001..005 — CA_ECCC COLLECT envelope packaging (EV-073 M1).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV073]
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import lxml.etree as etree
import pytest

from tac2iwxxm import convert, parse_ahl
from tac2iwxxm.ca_collect_packaging import is_ca_collect_bulletin, wrap_ca_eccc_collect
from tac2iwxxm.ca_ops_corpus import extract_iwxxm_from_collect, load_ops_manifest, ops_fixture_root
from tac2iwxxm.exchange_output import ca_msc_filename, issued_at_from_yygggg

_REPO = Path(__file__).resolve().parents[3]
FIXTURES = ops_fixture_root(_REPO)
MANIFEST = load_ops_manifest(FIXTURES / "ops_manifest.json")
PROFILE = "ca_eccc"
IWXXM_VERSION = "3.0.0"
_ISSUED = datetime(2026, 8, 24, 12, 0, 0, tzinfo=UTC)


def _inner_from_golden(product: str, tac_path: str, golden_path: str) -> str:
    tac = (_REPO / "packages/tac2iwxxm/tests/fixtures/profiles/CA_ECCC" / tac_path).read_text(encoding="utf-8")
    result = convert(tac, profile=PROFILE, iwxxm_version=IWXXM_VERSION, product=product)
    assert result.ok, result.issues
    return result.xml


def test_is_ca_collect_bulletin_invalid_xml() -> None:
    assert is_ca_collect_bulletin("not xml") is False


def test_tc_ev073_001_wrap_idempotent_for_collect() -> None:
    ops_xml = (FIXTURES / "TAF/ops/taf_cwao_12_001.xml").read_text(encoding="utf-8")
    assert is_ca_collect_bulletin(ops_xml)
    assert wrap_ca_eccc_collect(ops_xml, bulletin_identifier="A_TEST.xml") == ops_xml


def test_tc_ev073_002_msc_bulletin_identifier() -> None:
    parts = parse_ahl("SAUL31 CYUL 231800")
    filename = ca_msc_filename(parts, issued_at=_ISSUED)
    inner = _inner_from_golden(
        "METAR",
        "METAR/valid/metar_basic.tac",
        "METAR/valid/metar_basic.golden.xml",
    )
    wrapped = wrap_ca_eccc_collect(inner, bulletin_identifier=filename)
    root = etree.fromstring(wrapped.encode("utf-8"))
    bid = root.find(f"{{{_COLLECT_NS}}}bulletinIdentifier")
    assert bid is not None
    assert bid.text == filename


def test_tc_ev073_003_inner_product_round_trip() -> None:
    inner = _inner_from_golden(
        "TAF",
        "TAF/valid/taf_amd.tac",
        "TAF/valid/taf_amd.golden.xml",
    )
    parts = parse_ahl("FTUL31 CYUL 231800")
    filename = ca_msc_filename(parts, issued_at=issued_at_from_yygggg(parts.yygggg, reference=_ISSUED))
    wrapped = wrap_ca_eccc_collect(inner, bulletin_identifier=filename)
    extracted = extract_iwxxm_from_collect(wrapped)
    assert extracted is not None
    inner_root = etree.fromstring(inner.encode("utf-8"))
    extracted_root = etree.fromstring(extracted.encode("utf-8"))
    assert etree.QName(inner_root).localname == etree.QName(extracted_root).localname == "TAF"
    gml_id = "{http://www.opengis.net/gml/3.2}id"
    assert inner_root.get(gml_id) == extracted_root.get(gml_id)


_COLLECT_NS = "http://def.wmo.int/collect/2014"


@pytest.mark.parametrize(
    "case",
    [c for c in MANIFEST["cases"] if c["id"] in ("taf_cwao_12_001", "airmet_czul_05_001")],
    ids=lambda c: c["id"],
)
def test_tc_ev073_004_ops_fixture_shell_parity(case: dict) -> None:
    """Single-member ops fixtures share COLLECT shell shape with wrapped encoder output."""
    ops_raw = (FIXTURES / case["ops_xml"]).read_text(encoding="utf-8")
    ops_root = etree.fromstring(ops_raw.encode("utf-8"))
    inner = extract_iwxxm_from_collect(ops_raw)
    assert inner is not None
    assert case.get("source_filename")
    wrapped = wrap_ca_eccc_collect(inner, bulletin_identifier=case["source_filename"])
    wrap_root = etree.fromstring(wrapped.encode("utf-8"))
    assert etree.QName(wrap_root).localname == "MeteorologicalBulletin"
    wrap_infos = wrap_root.findall(f"{{{_COLLECT_NS}}}meteorologicalInformation")
    ops_infos = ops_root.findall(f"{{{_COLLECT_NS}}}meteorologicalInformation")
    assert len(wrap_infos) == 1
    assert len(ops_infos) >= 1
    wrap_bid = wrap_root.find(f"{{{_COLLECT_NS}}}bulletinIdentifier")
    ops_bid = ops_root.find(f"{{{_COLLECT_NS}}}bulletinIdentifier")
    assert wrap_bid is not None and ops_bid is not None
    assert wrap_bid.text.lower() == ops_bid.text.lower()


def test_tc_ev073_005_catalog_collect_envelope_implemented() -> None:
    """Catalog documents COLLECT envelope as EV-073 implemented."""
    text = (_REPO / "docs/domain/profiles/catalog.yaml").read_text(encoding="utf-8")
    assert "collect_envelope:" in text
    assert "ev_cycle: EV-073" in text
    assert "status: implemented" in text.split("collect_envelope:")[1][:200]
