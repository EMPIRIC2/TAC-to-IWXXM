"""TC-EVPVD-002..003 — AU_BOM / NZ_CAA_MET catalog implemented + convert goldens.

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests §TC-EVPVD]
[Corpus: decisions] D-EVPVD-02 / #1221
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from tac2iwxxm import convert

REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG = REPO_ROOT / "docs" / "domain" / "profiles" / "catalog.yaml"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles"


def _catalog_status(profile_id: str) -> str:
    data = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    for row in data.get("profiles", []):
        if row.get("id") == profile_id:
            return str(row.get("status", ""))
    raise AssertionError(f"profile {profile_id} missing from catalog.yaml")


def _active_cases(profile_id: str) -> list[dict[str, str]]:
    root = FIXTURES / profile_id
    data = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    cases = data.get("cases")
    assert isinstance(cases, list)
    return [c for c in cases if c.get("status") == "active"]


@pytest.mark.parametrize("profile_id", ["AU_BOM", "NZ_CAA_MET"])
def test_tc_evpvd_002_003_catalog_status_implemented(profile_id: str) -> None:
    assert _catalog_status(profile_id) == "implemented"


@pytest.mark.parametrize("profile_id", ["AU_BOM", "NZ_CAA_MET"])
def test_tc_evpvd_002_003_metar_speci_taf_convert_goldens(profile_id: str) -> None:
    cases = _active_cases(profile_id)
    products = {c["product"] for c in cases}
    assert {"METAR", "SPECI", "TAF"} <= products

    root = FIXTURES / profile_id
    for case in cases:
        if case["product"] not in {"METAR", "SPECI", "TAF"}:
            continue
        tac = (root / case["tac"]).read_text(encoding="utf-8")
        result = convert(tac, product=case["product"], profile=profile_id)
        assert result.xml.strip(), f"{profile_id}/{case['id']} empty xml"
        assert "iwxxm" in result.xml.lower()
