"""TC-EV1222 — regional exchange packaging deepen (#1222).

[Corpus: product §F36] [Corpus: adr/ADR-036] [Corpus: tests]
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml
from dissemination.packaging import (
    APAC_ROBEX_DEFAULT_BULLETIN_IDENTIFIER,
    apply_exchange_packaging,
)

_MEMBER = """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" xmlns:gml="http://www.opengis.net/gml/3.2" gml:id="metar.1"/>
"""

_BID_RE = re.compile(
    r"<collect:bulletinIdentifier>([^<]+)</collect:bulletinIdentifier>",
)


def _bulletin_id(xml: str) -> str:
    match = _BID_RE.search(xml)
    assert match is not None, xml
    return match.group(1)


def test_tc_ev1222_001_apac_robex_default_bulletin_differs_from_global_afs() -> None:
    """TC-EV1222-001 — APAC_ROBEX default bulletinIdentifier ≠ GLOBAL_AFS."""
    global_xml = apply_exchange_packaging(_MEMBER, exchange_profile="GLOBAL_AFS")
    apac_xml = apply_exchange_packaging(_MEMBER, exchange_profile="APAC_ROBEX")
    assert _bulletin_id(global_xml) == "A_UNKNOWN.xml"
    assert _bulletin_id(apac_xml) == APAC_ROBEX_DEFAULT_BULLETIN_IDENTIFIER
    assert _bulletin_id(apac_xml) != _bulletin_id(global_xml)
    assert "SACI31" in APAC_ROBEX_DEFAULT_BULLETIN_IDENTIFIER


def test_tc_ev1222_001_apac_robex_respects_explicit_bulletin_identifier() -> None:
    """Caller-supplied bulletinIdentifier wins over the ROBEX default."""
    xml = apply_exchange_packaging(
        _MEMBER,
        exchange_profile="APAC_ROBEX",
        bulletin_identifier="A_CUSTOM.xml",
    )
    assert _bulletin_id(xml) == "A_CUSTOM.xml"


def test_tc_ev1222_002_remaining_overlays_catalog_honesty() -> None:
    """TC-EV1222-002 — EUR/AFI/CAR_SAM stay stub with explicit gaps."""
    catalog = Path("docs/domain/profiles/catalog.yaml")
    data = yaml.safe_load(catalog.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in data["profiles"] if row.get("kind") == "exchange"}
    for wire_id in ("EUR_RODEX", "AFI", "CAR_SAM"):
        row = by_id[wire_id]
        assert row["status"] == "stub", wire_id
        gaps = row.get("gaps") or []
        assert gaps, f"{wire_id} must retain explicit gaps"
    apac = by_id["APAC_ROBEX"]
    assert apac["status"] in {"in_progress", "implemented"}
    assert any("robex-hb-19th" in str(p) for p in (apac.get("mining_notes") or []))


def test_tc_ev1222_003_unknown_exchange_still_fail_closed() -> None:
    """TC-EV1222-003 — unknown id still raises."""
    with pytest.raises(ValueError, match="unknown exchange profile"):
        apply_exchange_packaging(_MEMBER, exchange_profile="NOT_A_REAL_EXCHANGE")


def test_tc_ev1222_004_global_afs_default_unchanged() -> None:
    """TC-EV1222-004 — GLOBAL_AFS still defaults to A_UNKNOWN.xml."""
    xml = apply_exchange_packaging(_MEMBER, exchange_profile="GLOBAL_AFS")
    assert _bulletin_id(xml) == "A_UNKNOWN.xml"
