"""Vendor schema presence tests - test-plan.md §Vendor, M2 exit gate."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VENDOR_SCHEMAS = ROOT / "vendor" / "schemas"

REQUIRED_VENDOR_PATHS = (
    "iwxxm/2025-2/IWXXM/iwxxm.xsd",
    "iwxxm/2025-2/IWXXM/rule/iwxxm.sch",
    "iwxxm/2023-1/IWXXM/iwxxm.xsd",
    "iwxxm-codelists/49-2",
    "iwxxm-modelling/EA",
    "iwxxm-translation/README.md",
)


@pytest.mark.migration
class TestVendorSchemaPresence:
    """Each vendored wmo-im bundle exposes expected schema artifacts."""

    @pytest.mark.parametrize("relative_path", REQUIRED_VENDOR_PATHS)
    def test_required_vendor_path_exists(self, relative_path: str) -> None:
        path = VENDOR_SCHEMAS / relative_path
        assert path.exists(), f"missing vendored schema path: {relative_path}"

    def test_vendor_schemas_root_is_populated(self) -> None:
        for bundle in (
            "iwxxm",
            "iwxxm-codelists",
            "iwxxm-modelling",
            "iwxxm-translation",
        ):
            bundle_root = VENDOR_SCHEMAS / bundle
            assert bundle_root.is_dir(), f"missing bundle directory: {bundle}"
            assert any(bundle_root.rglob("*")), f"empty bundle directory: {bundle}"
