"""TC-EV068-003: EV-067 golden validate gate (EV-068 M6).

Spec: docs/test-plan.md TC-EV068-003; replaces XSD waive for EV-067 METAR/SPECI goldens.
Corpus: [Corpus: product §F2] [Corpus: product §F36] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from iwxxm_validate import rust_available, validate_iwxxm
from iwxxm_validate.ca_eccc_bundle import CA_ECCC_IWXXM_VERSION

REPO_ROOT = Path(__file__).resolve().parents[3]
CA_FIXTURES = REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "profiles" / "CA_ECCC"

EV067_CASES = (
    "metar_lwis",
    "metar_sawr",
    "metar_rmk_icing",
)

# Substitution-group roots skip WMO XSD/SCH; standard METAR root runs layers 2-4.
_EXPECTED_STAGES = {
    "metar_lwis": ("wellformed", "ca_xsd", "code_ca", "exchange"),
    "metar_sawr": ("wellformed", "ca_xsd", "code_ca", "exchange"),
    "metar_rmk_icing": ("wellformed", "wmo_xsd", "wmo_schematron", "ca_xsd", "code_ca", "exchange"),
}


@pytest.mark.parametrize("case_id", EV067_CASES)
def test_tc_ev068_003_ev067_golden_passes_ca_layers(case_id: str) -> None:
    """EV-067 goldens pass layered ca_eccc validation (layers 2-4 as applicable)."""
    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    golden_path = CA_FIXTURES / "METAR" / "valid" / f"{case_id}.golden.xml"
    assert golden_path.is_file(), f"missing golden fixture: {golden_path}"
    xml = golden_path.read_text(encoding="utf-8")

    report = validate_iwxxm(
        xml,
        iwxxm_version=CA_ECCC_IWXXM_VERSION,
        profile="ca_eccc",
        product="METAR",
        levels=("xsd", "schematron"),
    )
    assert report.profile == "ca_eccc"
    stage_ids = tuple(stage.stage for stage in report.stages)
    assert stage_ids == _EXPECTED_STAGES[case_id]
    assert all(stage.ok for stage in report.stages), [
        (stage.stage, stage.ok, [(i.code, i.message) for i in stage.issues]) for stage in report.stages
    ]
    assert report.ok is True
    assert not any(i.code == "CA_SCHEMA_NOT_FOUND" for i in report.issues)
    assert not any(i.code == "SCHEMA_IMPORT_WARNING" for i in report.issues)
