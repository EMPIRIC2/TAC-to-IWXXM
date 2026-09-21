"""TC-EV-YEH-002 — Schematron issue code is the pattern id when the engine has one."""

from __future__ import annotations

from pathlib import Path

import pytest
from iwxxm_validate.models import Issue, StageResult, ValidationReport
from iwxxm_validate.native import rust_available, rust_module
from iwxxm_validate.policy import apply_output_policy_to_report

_NAMED = """<schema xmlns="http://purl.oclc.org/dml/schematron">
  <pattern id="P1">
    <rule context="/*"><assert test="false()">fail one</assert></rule>
  </pattern>
  <pattern id="P2">
    <rule context="/*"><assert test="true()">ok</assert></rule>
  </pattern>
</schema>
"""

_UNNAMED = """<schema xmlns="http://purl.oclc.org/dml/schematron">
  <pattern>
    <rule context="/*"><assert test="false()">fail</assert></rule>
  </pattern>
</schema>
"""


def _rows(sch: Path, xml: str = "<root/>") -> list[dict[str, str]]:
    rust = rust_module()
    assert rust is not None
    raw = rust.validate_document(
        xml,
        xsd_path="",
        sch_path=str(sch),
        catalog_roots=[],
        levels=["schematron"],
    )
    return list(raw)


@pytest.mark.skipif(not rust_available(), reason="iwxxm_validate._rust not built")
def test_native_code_is_pattern_id_and_unnamed_stays_generic(tmp_path: Path) -> None:
    named = tmp_path / "named.sch"
    named.write_text(_NAMED, encoding="utf-8")
    errors = [row for row in _rows(named) if row["severity"] == "error"]
    assert [row["code"] for row in errors] == ["P1"]

    unnamed = tmp_path / "unnamed.sch"
    unnamed.write_text(_UNNAMED, encoding="utf-8")
    generic = [row for row in _rows(unnamed) if row["severity"] == "error"]
    assert [row["code"] for row in generic] == ["SCHEMATRON_ASSERT"]


def test_empty_select_keeps_pattern_id_and_generic_code_is_not_dropped() -> None:
    report = ValidationReport(
        ok=False,
        iwxxm_version="2025-2",
        profile="annex3",
        issues=[
            Issue(severity="error", code="AIRMET.AIRMET-1", message="named", layer="schematron"),
            Issue(severity="error", code="SCHEMATRON_ASSERT", message="unnamed", layer="schematron"),
            Issue(severity="error", code="XSD_VALIDATION_ERROR", message="xsd", layer="xsd"),
        ],
        stages=[
            StageResult(
                stage="schematron",
                label="Schematron",
                ok=False,
                issues=[
                    Issue(severity="error", code="AIRMET.AIRMET-1", message="named", layer="schematron"),
                    Issue(severity="error", code="SCHEMATRON_ASSERT", message="unnamed", layer="schematron"),
                ],
            )
        ],
    )
    kept = apply_output_policy_to_report(report, "annex3-iwxxm-output", profile="annex3")
    assert [issue.code for issue in kept.issues] == [
        "AIRMET.AIRMET-1",
        "SCHEMATRON_ASSERT",
        "XSD_VALIDATION_ERROR",
    ]


def test_nonempty_select_drops_omitted_pattern_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overlay = tmp_path / "ov"
    overlay.mkdir()
    (overlay / "narrow.yaml").write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: narrow",
                "lifecycle: activated",
                "pin: '2025-2'",
                "extends: [annex3-iwxxm-output]",
                "profiles: [annex3]",
                "select: [AIRMET.AIRMET-2]",
                "ignore: []",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("IWXXM_VALIDATE_POLICY_DIR", str(overlay))
    report = ValidationReport(
        ok=False,
        iwxxm_version="2025-2",
        profile="annex3",
        issues=[
            Issue(severity="error", code="AIRMET.AIRMET-1", message="named", layer="schematron"),
            Issue(severity="error", code="SCHEMATRON_ASSERT", message="unnamed", layer="schematron"),
        ],
        stages=[],
    )
    narrowed = apply_output_policy_to_report(report, "annex3-iwxxm-output", profile="annex3")
    assert [issue.code for issue in narrowed.issues] == ["SCHEMATRON_ASSERT"]
