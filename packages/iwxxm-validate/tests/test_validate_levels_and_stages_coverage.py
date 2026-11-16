"""Coverage for validate_levels helpers and ca_eccc_stages.run_rust_stage."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from iwxxm_validate.ca_eccc_layers import STAGE_CA_XSD
from iwxxm_validate.ca_eccc_stages import run_rust_stage
from iwxxm_validate.models import Issue
from iwxxm_validate.validate_levels import append_extended_levels


def test_append_extended_levels_empty_selection_is_noop() -> None:
    """Mutation: empty selected levels leaves the issue list unchanged."""
    seed = [
        Issue(
            severity="error",
            code="SEED",
            message="keep",
            layer="xsd",
        )
    ]
    out = append_extended_levels(
        seed,
        "<root/>",
        iwxxm_version="2023-1",
        selected=(),
    )
    assert out == seed


def test_append_extended_levels_codelist_dir_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failure: missing codelist dir yields CODELIST_DIR_NOT_FOUND warning."""

    def _missing(_version: str) -> Path:
        raise FileNotFoundError("missing")

    monkeypatch.setattr(
        "iwxxm_validate.validate_levels.codelists_dir",
        _missing,
    )
    out = append_extended_levels(
        [],
        "<root/>",
        iwxxm_version="2023-1",
        selected=("codelists",),
    )
    assert any(i.code == "CODELIST_DIR_NOT_FOUND" for i in out)


def test_append_extended_levels_gml_and_codelists_with_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Success: gml + codelists levels run when the resolver returns a dir."""
    monkeypatch.setattr(
        "iwxxm_validate.validate_levels.codelists_dir",
        lambda _version: tmp_path,
    )
    monkeypatch.setattr(
        "iwxxm_validate.validate_levels.validate_gml_references",
        lambda _xml, *, codelists_dir: [
            Issue(
                severity="warning",
                code="GML_PROBE",
                message=str(codelists_dir),
                layer="gml",
            )
        ],
    )
    monkeypatch.setattr(
        "iwxxm_validate.validate_levels.validate_codelist_references",
        lambda _xml, *, codelists_dir: [
            Issue(
                severity="warning",
                code="CL_PROBE",
                message=str(codelists_dir),
                layer="codelists",
            )
        ],
    )
    out = append_extended_levels(
        [],
        "<root/>",
        iwxxm_version="2023-1",
        selected=("gml", "codelists"),
    )
    assert {i.code for i in out} == {"GML_PROBE", "CL_PROBE"}


def test_run_rust_stage_invokes_native_and_maps_layer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Success: run_rust_stage maps native findings onto the caller stage."""
    rust = MagicMock()
    rust.validate_document.return_value = [
        {
            "layer": "xsd",
            "severity": "error",
            "code": "NATIVE_XSD",
            "message": "rust fail",
        }
    ]
    monkeypatch.setattr("iwxxm_validate.ca_eccc_stages.rust_module", lambda: rust)
    issues = run_rust_stage(
        "<root/>",
        xsd_path="/tmp/x.xsd",
        sch_path="/tmp/x.sch",
        catalog_roots=["/tmp/cat"],
        levels=["xsd"],
        stage_id=STAGE_CA_XSD,
    )
    rust.validate_document.assert_called_once()
    assert issues[0].code == "NATIVE_XSD"
    assert issues[0].layer == STAGE_CA_XSD
