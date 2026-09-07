"""TC-EV062 - issue_catalog_meta + attribution source_locator/source_access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import tac_validate.catalog_attribution as ca
from tac_validate.issue_catalog_meta import (
    classify_issue_type,
    human_source_cite,
    source_access_for,
    source_locator_for,
)


@pytest.fixture(autouse=True)
def _clear_attribution_cache() -> object:
    ca._load.cache_clear()
    yield
    ca._load.cache_clear()


def test_classify_issue_type_amd_present_is_presence() -> None:
    assert classify_issue_type(code="AMD_PRESENT", tags=("modifier", "taf"), family="lint") == "presence"


def test_classify_issue_type_present_token_in_code() -> None:
    assert classify_issue_type(code="FOO_PRESENT_BAR", tags=(), family="lint") == "presence"


def test_classify_issue_type_nil_report_presence() -> None:
    assert classify_issue_type(code="NIL_REPORT", tags=("nil", "metar"), family="lint") == "presence"


def test_classify_issue_type_structure_from_tags_and_codes() -> None:
    assert classify_issue_type(code="CUSTOM", tags=("parse_gate",), family="lint") == "structure"
    assert classify_issue_type(code="EMPTY_TAC", tags=(), family="lint") == "structure"
    assert classify_issue_type(code="MISSING_TERMINATOR", tags=(), family="lint") == "structure"


def test_classify_issue_type_nsc_exclusivity_is_consistency() -> None:
    assert (
        classify_issue_type(
            code="NSC_WITH_CLOUD_LAYERS",
            tags=("cloud", "metar"),
            family="lint",
        )
        == "consistency"
    )
    assert classify_issue_type(code="X", tags=("exclusivity",), family="lint") == "consistency"


def test_classify_issue_type_content_and_other() -> None:
    assert classify_issue_type(code="INVALID_WIND", tags=(), family="lint") == "content"
    assert classify_issue_type(code="MISSING_FIR", tags=(), family="lint") == "content"
    assert classify_issue_type(code="CLOUD_CB_OR_TCU", tags=("cloud",), family="lint") == ("content")
    assert classify_issue_type(code="ORPHAN", tags=(), family="lint") == "other"


def test_classify_issue_type_iwxxm_family() -> None:
    assert classify_issue_type(code="XML_SCHEMA", tags=("xsd",), family="iwxxm") == "iwxxm_schema"


def test_source_access_for_matrix() -> None:
    assert (
        source_access_for(
            source_url="https://store.icao.int/x",
            raw_status="ok",
        )
        == "paywall"
    )
    assert source_access_for(source_url=None, raw_status="paywall") == "paywall"
    assert (
        source_access_for(
            source_url="vendor:documentation/webpages/AHL.asciidoc",
            raw_status="ok",
        )
        == "semantic_only"
    )
    assert (
        source_access_for(
            source_url=None,
            raw_status=None,
            operator_status="semantic_only",
        )
        == "semantic_only"
    )
    assert source_access_for(source_url=None, raw_status="gap") == "semantic_only"
    assert source_access_for(source_url=None, raw_status="N/A") == "semantic_only"
    assert source_access_for(source_url="https://codes.wmo.int/", raw_status="ok") == "public"
    assert source_access_for(source_url=None, raw_status=None) is None


def test_source_locator_for_variants() -> None:
    assert source_locator_for(None) is None
    assert source_locator_for("   ") is None
    assert source_locator_for("App 5 / Table A5-1") == "App 5 / Table A5-1"
    assert (
        source_locator_for("EUR Doc 014 public; Annex 3 paywall companion")
        == "EUR Doc 014 public; Annex 3 paywall companion"
    )


def test_human_source_cite_variants() -> None:
    assert human_source_cite("App 5") == "Source: App 5."
    assert human_source_cite("App 5", paywall=True) == "Source: App 5. Full normative text may require purchase."
    assert human_source_cite(None, paywall=True) == "Source section unavailable (normative text may require purchase)."
    assert human_source_cite(None) == "Source section unavailable."


def test_attribution_amd_present_source_locator_and_access() -> None:
    row = ca.attribution_for("AMD_PRESENT")
    assert row["source_locator"] == "ICAO Annex 3 App 5 / Table A5-1"
    assert row["source_access"] == "paywall"
    assert row["source_id"] == "icao-annex-3"


def test_attribution_tc_cyclone_public_access() -> None:
    row = ca.attribution_for("TC_CYCLONE_IDENTITY")
    assert row["source_access"] == "public"
    assert row["source_locator"] == "EUR Doc 014 public; Annex 3 paywall companion"


def test_attribution_semantic_vendor_and_codes_registry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "codes": {
            "VENDOR_CODE": {
                "source_id": "opmet-guidelines-5th",
                "source_url": "vendor:documentation/webpages/AHL.asciidoc",
                "status": "ok",
                "note": "WMO AHL heading",
            },
            "CODES_GUIDE": {
                "source_id": "codes-wmo-int",
                "source_url": ("https://codes.wmo.int/ui/resources/WMO-Codes-Registry_user-guide-v1.0.pdf"),
                "status": "ok",
                "note": "Cloud amount register landing",
            },
            "STORE_WITH_EUR_NOTE": {
                "source_id": "icao-annex-3",
                "source_url": (
                    "https://store.icao.int/en/annex-3-meteorological-service-for-international-air-navigation-1"
                ),
                "status": "paywall",
                "note": "EUR Doc 014 public companion for SIGMET",
            },
            "GAP_ROW": {
                "source_id": "unknown",
                "source_url": None,
                "status": "gap",
                "note": "",
            },
            "INTERNAL_NOTE": {
                "source_id": "icao-annex-3",
                "source_url": "https://example.invalid/landing",
                "status": "ok",
                "note": "See [Corpus: product] and EV-062",
            },
        },
    }
    data_path = tmp_path / "catalog_attribution.json"
    data_path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(ca, "_DATA", data_path)
    ca._load.cache_clear()

    vendor = ca.attribution_for("VENDOR_CODE")
    assert vendor["source_access"] == "semantic_only"
    assert vendor["status"] == "semantic_only"
    assert vendor["source_locator"] == "WMO AHL heading"

    codes = ca.attribution_for("CODES_GUIDE")
    assert codes["source_access"] == "public"
    assert codes["semantic_identifier"] == "https://codes.wmo.int/"
    assert codes["source_type"] == "tier3"

    swapped = ca.attribution_for("STORE_WITH_EUR_NOTE")
    assert swapped["source_access"] == "public"
    assert swapped["replacement_url"]
    assert "store.icao.int" in swapped["replacement_url"]
    assert swapped["source_url"]
    assert "icao.int/sites" in swapped["source_url"]

    gap = ca.attribution_for("GAP_ROW")
    assert gap["source_access"] == "semantic_only"
    assert gap["status"] == "semantic_only"
    assert gap["source_locator"] is None

    scrubbed = ca.attribution_for("INTERNAL_NOTE")
    assert scrubbed["source_attribution"] is not None
    assert "Corpus" not in scrubbed["source_attribution"]
    assert scrubbed["source_type"] == "tier2"

    missing = ca.attribution_for("DOES_NOT_EXIST")
    assert missing["source_url"] is None
    assert missing["source_access"] is None
