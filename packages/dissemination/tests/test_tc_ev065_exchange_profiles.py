"""TC-EV065 — GLOBAL_AFS + APAC_ROBEX exchange profile closure (#921 / EV-065)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dissemination.collect_namespaces import is_collect_bulletin
from dissemination.packaging import apply_exchange_packaging

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "GLOBAL_AFS"


def _load_manifest() -> dict:
    return json.loads((_FIXTURES / "manifest.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "fixture_row",
    _load_manifest()["fixtures"],
    ids=[row["id"] for row in _load_manifest()["fixtures"]],
)
def test_tc_ev065_001_global_afs_fixture_collect_wrap(fixture_row: dict) -> None:
    """TC-EV065-001 — GLOBAL_AFS COLLECT golden from profile fixture."""
    member_path = _FIXTURES / fixture_row["path"]
    member_xml = member_path.read_text(encoding="utf-8")
    packaged = apply_exchange_packaging(
        member_xml,
        exchange_profile="GLOBAL_AFS",
        bulletin_identifier=fixture_row["bulletin_identifier"],
    )
    assert is_collect_bulletin(packaged)
    assert fixture_row["bulletin_identifier"] in packaged
    assert "iwxxm:METAR" in packaged


def test_tc_ev065_002_apac_robex_resolves_and_wraps() -> None:
    """TC-EV065-002 — APAC_ROBEX P0 stub produces COLLECT bulletin."""
    member_xml = (_FIXTURES / "METAR" / "valid" / "member_metar.xml").read_text(encoding="utf-8")
    packaged = apply_exchange_packaging(
        member_xml,
        exchange_profile="APAC_ROBEX",
        bulletin_identifier="A_APAC_SAMPLE.xml",
    )
    assert is_collect_bulletin(packaged)
    assert "A_APAC_SAMPLE.xml" in packaged
