"""TC-1034: CA_ECCC code-list deviations from global WMO.

[Corpus: product §F36] [Corpus: tests] [Corpus: domain-profiles §CA_ECCC]
"""

from __future__ import annotations

from pathlib import Path

import yaml
from iwxxm_validate.ca_eccc_layers import STAGE_CODE_CA
from iwxxm_validate.code_ca_validate import validate_code_ca_membership
from iwxxm_validate.code_list_policy import load_code_list_policy

_REPO = Path(__file__).resolve().parents[3]
_MATRIX = _REPO / "config" / "profiles" / "semantic" / "CA_ECCC.code-list-deviations.yaml"
_IC_GOLDEN = (
    _REPO
    / "packages/tac2iwxxm/tests/fixtures/profiles/CA_ECCC/TAF/valid/taf_ic_weather.golden.xml"
)
_KINDS = frozenset({"replace", "override", "extend", "none"})
_CA_IC = "https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca/present_and_forecast_weather/IC"
_WMO_IC = "http://codes.wmo.int/306/4678/IC"


def test_tc_1034_001_deviation_matrix_has_ten_classified_entries() -> None:
    """Deviation matrix commits ≥10 classified entries with valid kinds."""
    assert _MATRIX.is_file(), f"missing matrix: {_MATRIX}"
    data = yaml.safe_load(_MATRIX.read_text(encoding="utf-8"))
    entries = data["entries"]
    assert len(entries) >= 10
    for entry in entries:
        assert entry["kind"] in _KINDS
        assert entry["id"]
        assert entry["area"]
    policy = data["code_list_policy"]
    assert policy["issue"] == "#1034"
    assert policy["status"] == "implemented"


def test_tc_1034_002_disallowed_global_ic_fails_closed() -> None:
    """WMO 4678/IC under CA_ECCC fails at code_ca with CODE_LIST_GLOBAL_DISALLOWED."""
    xml = _IC_GOLDEN.read_text(encoding="utf-8").replace(_CA_IC, _WMO_IC)
    assert _WMO_IC in xml
    issues = validate_code_ca_membership(xml, profile="CA_ECCC")
    assert issues
    assert all(issue.layer == STAGE_CODE_CA for issue in issues)
    assert any(issue.code == "CODE_LIST_GLOBAL_DISALLOWED" for issue in issues)


def test_tc_1034_003_policy_resolve_ic_and_gfa() -> None:
    """Policy resolve returns national URIs for replace tokens (no silent WMO)."""
    policy = load_code_list_policy("CA_ECCC")
    ic = policy.resolve_ca_uri(area="forecast_weather", token="IC")
    assert ic is not None
    assert "code-ca/present_and_forecast_weather/IC" in ic
    gfa = policy.resolve_ca_uri(area="airmet_phenomena", token="FRQ_TCU_ISOL_TS")
    assert gfa is not None
    assert "airmet_weather_phenomena/FRQ_TCU_ISOL_TS" in gfa
    disallowed = policy.disallowed_global_uris()
    assert "http://codes.wmo.int/306/4678/IC" in disallowed
