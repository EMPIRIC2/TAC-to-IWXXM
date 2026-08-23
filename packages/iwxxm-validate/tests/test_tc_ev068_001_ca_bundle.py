"""TC-EV068-001: CA_ECCC profile-pinned 3.0.0 bundle resolution (EV-068 M1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from iwxxm_validate.ca_eccc_layers import (
    CA_IWXXM_VERSION,
    CA_PRODUCT_XSD,
    CA_VALIDATION_STAGES,
    IMPLEMENTED_CA_STAGES,
    ca_eccc_bundle_available,
    ca_iwxxm_core_xsd_path,
    ca_product_xsd_path,
    pending_ca_stages,
)
from iwxxm_validate.paths import ca_xsd_path

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.unit
class TestTcEv068001CaEcccBundle:
    """Profile-pinned IWXXM 3.0.0 + iwxxm-ca vendor trees resolve for ca_eccc."""

    def test_ca_eccc_bundle_available_when_vendored(self) -> None:
        assert ca_eccc_bundle_available()
        assert ca_xsd_path() is not None
        assert ca_iwxxm_core_xsd_path() is not None

    def test_ca_iwxxm_core_is_3_0_0_line(self) -> None:
        core = ca_iwxxm_core_xsd_path()
        assert core is not None
        assert core.as_posix().endswith("/3.0.0/IWXXM/iwxxm.xsd")

    def test_ca_product_xsd_map_resolves_metar(self) -> None:
        path = ca_product_xsd_path("METAR")
        assert path is not None
        assert path.name == CA_PRODUCT_XSD["METAR"]
        assert path.is_file()

    def test_ca_product_xsd_map_resolves_taf_and_airmet(self) -> None:
        taf = ca_product_xsd_path("TAF")
        airmet = ca_product_xsd_path("airmet")
        assert taf is not None and taf.name == "taf-ca.xsd"
        assert airmet is not None and airmet.name == "airmet-ca.xsd"

    def test_layered_stage_registry_matches_catalog(self) -> None:
        assert CA_IWXXM_VERSION == "3.0.0"
        assert CA_VALIDATION_STAGES[:3] == ("wellformed", "wmo_xsd", "wmo_schematron")
        assert IMPLEMENTED_CA_STAGES == frozenset(CA_VALIDATION_STAGES)
        assert pending_ca_stages() == ()

    def test_ca_eccc_bundle_unavailable_when_extension_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "iwxxm_validate.ca_eccc_bundle.ca_xsd_path",
            lambda **_: None,
        )
        assert not ca_eccc_bundle_available()
