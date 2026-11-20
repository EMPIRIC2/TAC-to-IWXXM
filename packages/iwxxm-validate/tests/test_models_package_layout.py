"""Models package layout, field validation, and nested-dict conversion."""

from __future__ import annotations

import msgspec
import pytest
from iwxxm_validate.models import (
    CodeListDeviation,
    CodeListPolicy,
    Issue,
    OutputPolicyCatalog,
    OutputPolicyDocument,
    PinSchBundle,
    ResolvedOutputPolicy,
    RustIssueDict,
    StageResult,
    ValidationReport,
    issue_from_rust_mapping,
    issues_from_rust,
)
from iwxxm_validate.models.ca_eccc import CaEcccSchemaBundle
from iwxxm_validate.models.code_list import CodeListEntryRaw
from iwxxm_validate.models.policy import OutputPolicyRaw


def test_issue_struct_rejects_missing_required_fields() -> None:
    """Validation failure: msgspec refuses Issue without required fields."""
    with pytest.raises(msgspec.ValidationError):
        msgspec.convert({"severity": "error"}, type=Issue)


def test_issue_struct_accepts_valid_fields() -> None:
    """Validation success: Issue accepts the public field set."""
    issue = msgspec.convert(
        {
            "severity": "error",
            "code": "XML_SYNTAX_ERROR",
            "message": "bad",
            "layer": "wellformed",
            "location": "line 1",
            "start": 0,
            "end": 3,
        },
        type=Issue,
    )
    assert issue.code == "XML_SYNTAX_ERROR"
    assert issue.start == 0


def test_validation_report_wire_keys_round_trip() -> None:
    """Success: ValidationReport encodes/decodes with stable JSON keys."""
    report = ValidationReport(
        ok=False,
        iwxxm_version="2023-1",
        profile="annex3",
        issues=[
            Issue(
                severity="error",
                code="XSD_ERROR",
                message="schema fail",
                layer="xsd",
            )
        ],
        stages=[
            StageResult(
                stage="wmo_xsd",
                label="WMO schema",
                ok=False,
                issues=[
                    Issue(
                        severity="error",
                        code="XSD_ERROR",
                        message="schema fail",
                        layer="wmo_xsd",
                    )
                ],
            )
        ],
    )
    raw = msgspec.json.decode(msgspec.json.encode(report))
    assert set(raw) >= {"ok", "iwxxm_version", "profile", "issues", "stages"}
    assert raw["issues"][0]["code"] == "XSD_ERROR"
    restored = msgspec.json.decode(msgspec.json.encode(report), type=ValidationReport)
    assert restored.ok is False
    assert restored.stages[0].stage == "wmo_xsd"


def test_rust_issue_dict_converts_to_issue() -> None:
    """Nested dict ownership: RustIssueDict maps to Issue with wire keys."""
    raw: RustIssueDict = {
        "severity": "warning",
        "code": "SCHEMATRON_ASSERT",
        "message": "rule",
        "layer": "schematron",
        "location": None,
    }
    issue = issue_from_rust_mapping(raw)
    assert issue.layer == "schematron"
    assert issue.code == "SCHEMATRON_ASSERT"


def test_issues_from_rust_layer_map_override() -> None:
    """Mutation-style remap: stage override wins when mapped layer differs."""
    raw = [{"severity": "error", "code": "X", "message": "m", "layer": "xsd"}]
    issues = issues_from_rust(raw, layer_map={"xsd": "wmo_xsd"}, stage_id="ca_xsd")
    assert issues[0].layer == "ca_xsd"


def test_output_policy_raw_builds_document() -> None:
    """Validation success: OutputPolicyRaw nested dict becomes OutputPolicyDocument."""
    raw: OutputPolicyRaw = {
        "schema_version": 1,
        "id": "demo",
        "lifecycle": "draft",
        "pin": "2023-1",
        "extends": [],
        "select": ["A"],
        "ignore": ["B"],
        "profiles": ["annex3"],
    }
    doc = OutputPolicyDocument(
        schema_version=raw["schema_version"],
        id=raw["id"],
        lifecycle="draft",
        pin=raw["pin"],
        extends=tuple(raw.get("extends") or ()),
        select=tuple(raw.get("select") or ()),
        ignore=tuple(raw.get("ignore") or ()),
        profiles=tuple(raw.get("profiles") or ()),
    )
    assert doc.id == "demo"
    assert doc.select == ("A",)


def test_output_policy_catalog_mutation_create_update_delete() -> None:
    """Mutation modes: create / update / delete entries on OutputPolicyCatalog."""
    doc = OutputPolicyDocument(
        schema_version=1,
        id="base",
        lifecycle="draft",
        pin="2023-1",
        extends=(),
        select=(),
        ignore=(),
    )
    by_id: dict[str, OutputPolicyDocument] = {}
    catalog = OutputPolicyCatalog(by_id=by_id)
    # Create
    by_id["base"] = doc
    assert catalog.get("base") is doc
    assert catalog.contains("base")
    # Update
    updated = OutputPolicyDocument(
        schema_version=1,
        id="base",
        lifecycle="activated",
        pin="2023-1",
        extends=(),
        select=("X",),
        ignore=(),
    )
    by_id["base"] = updated
    assert catalog.as_mapping()["base"].lifecycle == "activated"
    # Delete
    del by_id["base"]
    assert catalog.get("base") is None
    assert not catalog.contains("base")


def test_code_list_entry_raw_builds_deviation() -> None:
    """Validation success: CodeListEntryRaw nested dict becomes CodeListDeviation."""
    raw: CodeListEntryRaw = {
        "id": "d1",
        "area": "cloud",
        "token": "FEW",
        "kind": "extend",
        "ca_uri": "https://example.test/ca/few",
        "disallow_global": False,
        "products": ["METAR"],
    }
    entry = CodeListDeviation(
        id=raw["id"],
        area=raw["area"],
        token=raw["token"],
        kind=raw["kind"],
        global_uri=None,
        ca_uri=raw.get("ca_uri"),
        disallow_global=bool(raw.get("disallow_global")),
        products=tuple(raw.get("products") or ()),
    )
    policy = CodeListPolicy(profile="CA_ECCC", entries=(entry,))
    assert policy.resolve_ca_uri(area="cloud", token="FEW") == "https://example.test/ca/few"


def test_resolved_output_policy_and_bundles_are_models() -> None:
    """Model field presence for ResolvedOutputPolicy / PinSchBundle / CaEcccSchemaBundle."""
    from pathlib import Path

    resolved = ResolvedOutputPolicy(
        id="p",
        pin="2023-1",
        lifecycle="draft",
        enabled=frozenset({"A"}),
        warnings=(),
    )
    assert "A" in resolved.enabled
    pin = PinSchBundle(
        pin="2023-1",
        version_root=Path("/tmp"),
        xsd=Path("/tmp/x.xsd"),
        schematron=Path("/tmp/x.sch"),
        namespace_uri="http://icao.int/iwxxm/2023-1",
    )
    assert pin.pin == "2023-1"
    bundle = CaEcccSchemaBundle(
        iwxxm_version="3.0.0",
        core_xsd=Path("/tmp/core.xsd"),
        schematron=Path("/tmp/core.sch"),
        extension_root=Path("/tmp/ca"),
        aggregate_ca_xsd=None,
    )
    assert bundle.aggregate_ca_xsd is None
