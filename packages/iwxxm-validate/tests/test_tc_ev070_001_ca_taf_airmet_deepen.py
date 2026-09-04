"""TC-EV070-005: CA_ECCC TAF + AIRMET convert → validate round-trip (#1041).

Spec: docs/test-plan.md TC-EV070-005; full ca_eccc stack layers 1-6.
Corpus: [Corpus: product §F2] [Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from iwxxm_validate import rust_available, validate_iwxxm
from iwxxm_validate.ca_eccc_bundle import CA_ECCC_IWXXM_VERSION

REPO_ROOT = Path(__file__).resolve().parents[3]
CA_FIXTURES = REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "profiles" / "CA_ECCC"
PROFILE = "ca_eccc"

EV070_CASE_IDS = (
    "taf_ic_weather",
    "taf_amd",
    "airmet_gfa_sfc_vis",
)


@pytest.fixture(scope="module")
def golden_manifest() -> dict:
    return json.loads((CA_FIXTURES / "manifest.json").read_text(encoding="utf-8"))


@pytest.mark.unit
@pytest.mark.parametrize("case_id", EV070_CASE_IDS)
def test_tc_ev070_005_convert_validate_full_ca_stack(case_id: str, golden_manifest: dict) -> None:
    """Convert EV-070 goldens then pass full ca_eccc validation stack."""
    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (CA_FIXTURES / case["tac"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=CA_ECCC_IWXXM_VERSION,
    )
    assert result.ok
    assert result.xml

    report = validate_iwxxm(
        result.xml,
        iwxxm_version=CA_ECCC_IWXXM_VERSION,
        profile="ca_eccc",
        product=case["product"],
        levels=("xsd", "schematron"),
    )
    stage_ids = [stage.stage for stage in report.stages]
    assert stage_ids == [
        "wellformed",
        "wmo_xsd",
        "wmo_schematron",
        "ca_xsd",
        "code_ca",
        "exchange",
    ]
    assert all(stage.ok for stage in report.stages), [
        (stage.stage, [(i.code, i.message) for i in stage.issues]) for stage in report.stages if not stage.ok
    ]
    assert report.ok is True, f"{case_id}: {[(i.code, i.message) for i in report.issues]}"
