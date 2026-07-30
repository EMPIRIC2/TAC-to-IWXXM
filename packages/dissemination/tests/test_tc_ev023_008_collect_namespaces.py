"""TC-EV023-008 — COLLECT / multi-version namespaces (S030 / EV-023 T6.3).

Hooks on the F16–F19 / bulletin path (S02.M2). Single-report convert SoT
must remain unchanged (no COLLECT root from ``tac2iwxxm.convert``).
"""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_VENDOR_COLLECT = (
    _REPO / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples" / "sigmet-translation-failed-collect.xml"
)

_MULTI_VERSION_COLLECT = """\
<?xml version="1.0" encoding="UTF-8"?>
<collect:MeteorologicalBulletin
    xmlns:collect="http://def.wmo.int/collect/2014"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    gml:id="uuid.multi-version-test">
  <collect:meteorologicalInformation>
    <iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2023-1" gml:id="uuid.m1"
      reportStatus="NORMAL" permissibleUsage="OPERATIONAL"/>
  </collect:meteorologicalInformation>
  <collect:meteorologicalInformation>
    <iwxxm:SIGMET xmlns:iwxxm="http://icao.int/iwxxm/2025-2" gml:id="uuid.m2"
      reportStatus="NORMAL" permissibleUsage="OPERATIONAL"/>
  </collect:meteorologicalInformation>
  <collect:bulletinIdentifier>A_TEST_MULTI.xml</collect:bulletinIdentifier>
</collect:MeteorologicalBulletin>
"""


def test_tc_ev023_008_afs_collect_mandate_constant() -> None:
    from dissemination.collect_namespaces import AFS_REQUIRES_COLLECT

    assert AFS_REQUIRES_COLLECT is True


def test_tc_ev023_008_iwxxm_namespace_uri() -> None:
    from dissemination.collect_namespaces import iwxxm_namespace_uri

    assert iwxxm_namespace_uri("2025-2") == "http://icao.int/iwxxm/2025-2"
    assert iwxxm_namespace_uri("2023-1") == "http://icao.int/iwxxm/2023-1"
    with pytest.raises(ValueError):
        iwxxm_namespace_uri("")
    with pytest.raises(ValueError):
        iwxxm_namespace_uri("2025/2")


def test_tc_ev023_008_vendor_failed_collect_member_ns() -> None:
    """Official failed-member COLLECT declares pin namespace on the member."""
    from dissemination.collect_namespaces import (
        collect_namespace_issues,
        is_collect_bulletin,
        member_iwxxm_namespace_uris,
    )

    xml = _VENDOR_COLLECT.read_text(encoding="utf-8")
    assert is_collect_bulletin(xml) is True
    assert member_iwxxm_namespace_uris(xml) == ["http://icao.int/iwxxm/2025-2"]
    assert collect_namespace_issues(xml) == []


def test_tc_ev023_008_multi_version_member_groups() -> None:
    """FAQ §14.7 — each group may declare its own http://icao.int/iwxxm/{version}."""
    from dissemination.collect_namespaces import (
        collect_namespace_issues,
        member_iwxxm_namespace_uris,
    )

    uris = member_iwxxm_namespace_uris(_MULTI_VERSION_COLLECT)
    assert uris == [
        "http://icao.int/iwxxm/2023-1",
        "http://icao.int/iwxxm/2025-2",
    ]
    assert collect_namespace_issues(_MULTI_VERSION_COLLECT) == []


def test_tc_ev023_008_single_report_convert_is_not_collect() -> None:
    """Convert SoT stays single-report — no MeteorologicalBulletin root."""
    from tac2iwxxm import convert

    from dissemination.collect_namespaces import is_collect_bulletin

    result = convert(
        "METAR KJFK 231751Z 18012KT 9999 FEW020 15/07 Q1013=",
        product="METAR",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok is True
    assert result.xml is not None
    assert is_collect_bulletin(result.xml) is False
    assert "MeteorologicalBulletin" not in result.xml


def test_tc_ev023_008_non_collect_reports_issue() -> None:
    from dissemination.collect_namespaces import collect_namespace_issues

    issues = collect_namespace_issues("<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>")
    assert issues
    assert "COLLECT" in issues[0] or "collect" in issues[0].lower()


def test_tc_ev023_008_collect_without_member_ns_and_dupes() -> None:
    from dissemination.collect_namespaces import (
        collect_namespace_issues,
        member_iwxxm_namespace_uris,
    )

    empty = """\
<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/2014"
  xmlns:gml="http://www.opengis.net/gml/3.2" gml:id="uuid.e">
  <collect:bulletinIdentifier>A_EMPTY.xml</collect:bulletinIdentifier>
</collect:MeteorologicalBulletin>
"""
    issues = collect_namespace_issues(empty)
    assert any("no http://icao.int/iwxxm" in i for i in issues)

    dup = """\
<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/2014"
  xmlns:gml="http://www.opengis.net/gml/3.2" gml:id="uuid.d">
  <collect:meteorologicalInformation>
    <iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2/extra" gml:id="uuid.m"/>
  </collect:meteorologicalInformation>
  <collect:meteorologicalInformation>
    <iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2/extra" gml:id="uuid.m2"/>
  </collect:meteorologicalInformation>
</collect:MeteorologicalBulletin>
"""
    assert member_iwxxm_namespace_uris(dup) == ["http://icao.int/iwxxm/2025-2/extra"]
    bad = collect_namespace_issues(dup)
    assert any("malformed" in i for i in bad)
