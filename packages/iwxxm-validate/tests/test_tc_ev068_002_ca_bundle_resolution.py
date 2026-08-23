"""TC-EV068-002: CA_ECCC bundle resolution + 3.0.0 GML/catalog spike (EV-068 M2).

Spec: docs/test-plan.md TC-EV068-002 (M2 slice); R-EV068-001; feasibility GML risk.
Corpus: [Corpus: product §F2] [Corpus: product §F13] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest

from iwxxm_validate.ca_eccc_bundle import (
    CA_ECCC_IWXXM_VERSION,
    ca_eccc_bundle_available,
    ca_eccc_catalog_roots,
    resolve_ca_eccc_bundle,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
VENDOR_METAR_3_0_0 = REPO_ROOT / "vendor" / "schemas" / "iwxxm" / "3.0.0" / "IWXXM" / "examples" / "metar-A3-1.xml"
CA_FIXTURES = REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "profiles" / "CA_ECCC"


@pytest.mark.unit
class TestTcEv068002CaBundleResolution:
    """``ca_eccc`` profile resolves profile-pinned 3.0.0 + iwxxm-ca for native XSD."""

    def test_resolve_ca_eccc_bundle_when_vendored(self) -> None:
        bundle = resolve_ca_eccc_bundle()
        assert bundle is not None
        assert bundle.iwxxm_version == CA_ECCC_IWXXM_VERSION
        assert bundle.core_xsd.name == "iwxxm.xsd"
        assert bundle.schematron.name == "iwxxm.sch"
        assert bundle.aggregate_ca_xsd is not None
        assert bundle.extension_root.name == "iwxxm-ca"

    def test_ca_eccc_catalog_roots_include_external_schema_and_ca_pin(self) -> None:
        roots = ca_eccc_catalog_roots()
        assert roots
        assert any("externalSchema" in entry for entry in roots)
        assert any("schemas.opengis.net" in entry for entry in roots)
        assert any("schemas.wmo.int" in entry for entry in roots)
        assert any("iwxxm-ca" in entry for entry in roots)
        assert any(entry.endswith("/3.0.0/IWXXM") or entry.endswith("/3.0.0") for entry in roots)

    def test_ca_eccc_bundle_unavailable_when_core_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "iwxxm_validate.ca_eccc_bundle.xsd_path",
            lambda _v: (_ for _ in ()).throw(FileNotFoundError("missing")),
        )
        assert not ca_eccc_bundle_available()

    def test_native_3_0_0_vendor_example_no_schema_import_warning(self) -> None:
        """Layer 2 spike: WMO 3.0.0 XSD compiles without GML/catalog import gaps."""
        from iwxxm_validate import rust_available, validate_iwxxm

        if not rust_available():
            pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

        assert VENDOR_METAR_3_0_0.is_file(), f"missing fixture {VENDOR_METAR_3_0_0}"
        xml = VENDOR_METAR_3_0_0.read_text(encoding="utf-8")
        report = validate_iwxxm(
            xml,
            iwxxm_version=CA_ECCC_IWXXM_VERSION,
            profile="ca_eccc",
            levels=("xsd",),
        )
        warned = [i for i in report.issues if i.code == "SCHEMA_IMPORT_WARNING"]
        assert warned == [], f"unexpected SCHEMA_IMPORT_WARNING: {warned}"
        assert report.ok is True

    def test_native_ca_golden_convert_passes_wmo_layers(self) -> None:
        """CA convert output validates on native path (layers 2–3) without catalog gaps."""
        from tac2iwxxm import convert

        from iwxxm_validate import rust_available, validate_iwxxm

        if not rust_available():
            pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

        tac = (CA_FIXTURES / "METAR" / "valid" / "metar_basic.tac").read_text(encoding="utf-8")
        converted = convert(
            tac,
            product="METAR",
            profile="ca_eccc",
            iwxxm_version=CA_ECCC_IWXXM_VERSION,
        )
        assert converted.ok and converted.xml

        report = validate_iwxxm(
            converted.xml,
            iwxxm_version=CA_ECCC_IWXXM_VERSION,
            profile="ca_eccc",
            levels=("xsd", "schematron"),
        )
        assert report.profile == "ca_eccc"
        assert not any(i.code == "SCHEMA_IMPORT_WARNING" for i in report.issues)
        assert not any(i.code == "CA_SCHEMA_NOT_FOUND" for i in report.issues)
        assert report.ok is True
        assert report.stages
        wmo_xsd = next(s for s in report.stages if s.stage == "wmo_xsd")
        assert wmo_xsd.ok is True

    def test_layered_stages_report_per_stage_results(self) -> None:
        """TC-EV068-002 M3: ca_eccc returns operator-readable per-stage breakdown."""
        from iwxxm_validate import rust_available, validate_iwxxm

        if not rust_available():
            pytest.skip("iwxxm_validate._rust not built")

        golden = (CA_FIXTURES / "METAR" / "valid" / "metar_rmk_icing.golden.xml").read_text(encoding="utf-8")
        report = validate_iwxxm(
            golden,
            iwxxm_version=CA_ECCC_IWXXM_VERSION,
            profile="ca_eccc",
            product="METAR",
            levels=("xsd", "schematron"),
        )
        stage_ids = [stage.stage for stage in report.stages]
        assert stage_ids == ["wellformed", "wmo_xsd", "wmo_schematron", "ca_xsd", "code_ca", "exchange"]
        assert all(stage.label for stage in report.stages)
        assert report.ok is True

    def test_ca_substitution_root_skips_wmo_layers(self) -> None:
        """LWIS/SAWR roots validate on Canadian product XSD without failing WMO core XSD."""
        from iwxxm_validate import rust_available, validate_iwxxm

        if not rust_available():
            pytest.skip("iwxxm_validate._rust not built")

        lwis = (CA_FIXTURES / "METAR" / "valid" / "metar_lwis.golden.xml").read_text(encoding="utf-8")
        report = validate_iwxxm(
            lwis,
            iwxxm_version=CA_ECCC_IWXXM_VERSION,
            profile="ca_eccc",
            product="METAR",
            levels=("xsd",),
        )
        stage_ids = [stage.stage for stage in report.stages]
        assert stage_ids == ["wellformed", "ca_xsd", "code_ca", "exchange"]
        assert report.ok is True

    def test_invalid_ca_extension_fails_at_ca_xsd_not_wmo_xsd(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-EV068-002: pipeline attributes CA-only XSD failures to layer 4."""
        from iwxxm_validate import validate_iwxxm
        from iwxxm_validate.ca_eccc_validate import STAGE_CA_XSD, STAGE_WMO_XSD

        golden = (CA_FIXTURES / "METAR" / "valid" / "metar_rmk_icing.golden.xml").read_text(encoding="utf-8")

        def fake_run_rust_stage(
            xml_content: str,
            *,
            xsd_path: str,
            sch_path: str,
            catalog_roots: list[str],
            levels: list[str],
            stage_id: str,
        ) -> list:
            from iwxxm_validate.models import Issue

            if stage_id == STAGE_WMO_XSD:
                return []
            if stage_id == STAGE_CA_XSD:
                return [
                    Issue(
                        severity="error",
                        code="XSD_VALIDATION_ERROR",
                        message="Canadian extension probe failure",
                        layer=STAGE_CA_XSD,
                    )
                ]
            return []

        monkeypatch.setattr(
            "iwxxm_validate.ca_eccc_validate._run_rust_stage",
            fake_run_rust_stage,
        )
        monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.rust_available", lambda: True)

        report = validate_iwxxm(
            golden,
            iwxxm_version=CA_ECCC_IWXXM_VERSION,
            profile="ca_eccc",
            product="METAR",
            levels=("xsd",),
        )
        wmo_stage = next(s for s in report.stages if s.stage == "wmo_xsd")
        ca_stage = next(s for s in report.stages if s.stage == "ca_xsd")
        assert wmo_stage.ok is True
        assert ca_stage.ok is False
        assert any(issue.layer == "ca_xsd" for issue in ca_stage.issues)
        assert report.ok is False
