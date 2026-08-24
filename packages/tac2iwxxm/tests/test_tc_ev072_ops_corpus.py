"""TC-EV072-007..010 — CA_ECCC MSC datamart ops corpus (EV-072 M2 / #1036).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV072]
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tac2iwxxm.ca_ops_corpus import (
    extract_iwxxm_from_collect,
    load_ops_manifest,
    manifest_checksum,
    msc_filename_from_url,
    ops_fixture_root,
)
from tac2iwxxm.exchange_output import ca_wmo_header_designator

_REPO = Path(__file__).resolve().parents[3]
FIXTURES = ops_fixture_root(_REPO)
MANIFEST_PATH = FIXTURES / "ops_manifest.json"
HARVEST_SCRIPT = _REPO / "scripts" / "iwxxm" / "harvest_ca_eccc_ops.py"

_AHL_FROM_FILENAME = re.compile(
    r"^A_([A-Z]{2})([A-Z]{2})(\d{2})([A-Z]{4})(\d{6})(?:[A-Z0-9]{3})?_C_[A-Z]{4}_\d{14}\.xml$"
)


def _expected_wmo_ahl(source_filename: str, product: str) -> str | None:
    match = _AHL_FROM_FILENAME.match(source_filename)
    if not match:
        return None
    tt, aa, ii, cccc, yygggg = match.groups()
    designator = ca_wmo_header_designator(product)
    return f"{designator}{ii} {cccc} {yygggg}"


def _cases_by_product(manifest: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for case in manifest["cases"]:
        grouped.setdefault(case["product"], []).append(case)
    return grouped


def test_extract_iwxxm_from_collect_invalid_xml_returns_none() -> None:
    assert extract_iwxxm_from_collect("not xml") is None


def test_extract_iwxxm_from_collect_unknown_root_returns_none() -> None:
    xml = '<?xml version="1.0"?><foo xmlns="http://example.com"/>'
    assert extract_iwxxm_from_collect(xml) is None


def test_extract_iwxxm_from_collect_empty_bulletin_returns_none() -> None:
    xml = '<?xml version="1.0"?><collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/2014"/>'
    assert extract_iwxxm_from_collect(xml) is None


def test_extract_iwxxm_from_collect_skips_non_information_children() -> None:
    xml = (
        '<?xml version="1.0"?>'
        '<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/2014">'
        "<collect:header/>"
        "<collect:meteorologicalInformation>"
        '<iwxxm:TAF xmlns:iwxxm="http://icao.int/iwxxm/3.0"/>'
        "</collect:meteorologicalInformation>"
        "</collect:MeteorologicalBulletin>"
    )
    inner = extract_iwxxm_from_collect(xml)
    assert inner is not None
    assert "<iwxxm:TAF" in inner


def test_extract_iwxxm_from_collect_ca_substitution_root() -> None:
    xml = '<?xml version="1.0"?><ca:LWIS xmlns:ca="https://dd.meteo.gc.ca/today/aviation/iwxxm/"/>'
    assert extract_iwxxm_from_collect(xml) == xml


def test_extract_iwxxm_from_collect_standalone_metar_passthrough() -> None:
    xml = '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0"/>'
    assert extract_iwxxm_from_collect(xml) == xml


def test_extract_iwxxm_from_collect_non_ops_product_returns_none() -> None:
    xml = (
        '<?xml version="1.0"?>'
        '<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/2014">'
        "<collect:meteorologicalInformation>"
        '<iwxxm:SpaceWeatherAdvisory xmlns:iwxxm="http://icao.int/iwxxm/3.0"/>'
        "</collect:meteorologicalInformation>"
        "</collect:MeteorologicalBulletin>"
    )
    assert extract_iwxxm_from_collect(xml) is None


def test_msc_filename_from_url_valid_and_invalid() -> None:
    valid = "https://dd.weather.gc.ca/today/aviation/iwxxm/taf/cwao/12/A_LTCN22CWAO241200_C_CWAO_20260824120000.xml"
    assert msc_filename_from_url(valid) == "A_LTCN22CWAO241200_C_CWAO_20260824120000.xml"
    assert msc_filename_from_url("https://example.com/not_msc.xml") is None


def test_load_ops_manifest_rejects_missing_cases(tmp_path: Path) -> None:
    bad = tmp_path / "ops_manifest.json"
    bad.write_text('{"pin_date": "2026-08-24"}', encoding="utf-8")
    with pytest.raises(ValueError, match="missing cases"):
        load_ops_manifest(bad)


def test_ops_fixture_root_default_resolves_ca_eccc() -> None:
    root = ops_fixture_root()
    assert root.name == "CA_ECCC"
    assert (root / "ops_manifest.json").is_file()


def test_tc_ev072_007_harvest_script_pin_date_reproducibility() -> None:
    """Harvest script documents pin date + stable manifest checksum (offline)."""
    assert HARVEST_SCRIPT.is_file(), f"missing harvest script: {HARVEST_SCRIPT}"
    text = HARVEST_SCRIPT.read_text(encoding="utf-8")
    assert "rate_limit" in text
    assert "pin_date" in text
    assert "dd.weather.gc.ca" in text or "dd.meteo.gc.ca" in text

    manifest = load_ops_manifest(MANIFEST_PATH)
    assert manifest["pin_date"] == "2026-08-24"
    assert manifest["rate_limit_seconds"] >= 1.0
    assert manifest["manifest_sha256"] == manifest_checksum(manifest)

    on_disk = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert on_disk["manifest_sha256"] == manifest["manifest_sha256"]


def test_tc_ev072_008_ops_metar_fixture_count() -> None:
    """≥5 METAR ops fixtures with wmoReference tier in manifest."""
    manifest = load_ops_manifest(MANIFEST_PATH)
    metar_cases = _cases_by_product(manifest)["METAR"]
    assert len(metar_cases) >= 5
    for case in metar_cases:
        assert case["tier"] == "wmoReference"
        ops_path = FIXTURES / case["ops_xml"]
        assert ops_path.is_file(), f"missing METAR ops fixture: {ops_path}"


def test_tc_ev072_009_ops_speci_taf_airmet_fixture_counts() -> None:
    """≥2 ops fixtures each for SPECI, TAF, and AIRMET."""
    manifest = load_ops_manifest(MANIFEST_PATH)
    grouped = _cases_by_product(manifest)
    for product in ("SPECI", "TAF", "AIRMET"):
        cases = grouped.get(product, [])
        assert len(cases) >= 2, f"{product} ops count {len(cases)} < 2"
        for case in cases:
            assert case["tier"] == "wmoReference"
            assert (FIXTURES / case["ops_xml"]).is_file()


@pytest.mark.parametrize("case", load_ops_manifest(MANIFEST_PATH)["cases"], ids=lambda c: c["id"])
def test_tc_ev072_010_ops_iwxxm_packaging_checks(case: dict) -> None:
    """Ops IWXXM passes layer-6 packaging checks or documents an explicit waiver."""
    if case["product"] in {"SIGMET", "VAA"}:
        pytest.skip("EV-074 validate-first: no CA exchange emit for SIGMET/VAA")
    from iwxxm_validate.ca_exchange_validate import validate_ca_exchange_packaging

    raw = (FIXTURES / case["ops_xml"]).read_text(encoding="utf-8")
    inner = extract_iwxxm_from_collect(raw)
    assert inner is not None, f"could not extract IWXXM product from {case['ops_xml']}"

    ahl_header = None
    expected_filename = case.get("source_filename")
    if expected_filename:
        ahl_header = _expected_wmo_ahl(expected_filename, case["product"])

    issues = validate_ca_exchange_packaging(
        inner,
        product=case["product"],
        ahl_header=ahl_header,
        expected_filename=expected_filename,
        require_translation_centre=case.get("packaging_waiver") is None,
    )
    waiver = case.get("packaging_waiver")
    if waiver:
        assert isinstance(waiver, str) and waiver
        # Encoder reference fixtures may lack translation centre — packaging attrs only.
        blocking = [issue for issue in issues if issue.code != "CA_EXCHANGE_TRANSLATION_CENTRE"]
        assert blocking == [], [(issue.code, issue.message) for issue in blocking]
    else:
        assert issues == [], [(issue.code, issue.message) for issue in issues]
