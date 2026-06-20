"""TC-M002: Vendor Manifest Integrity — test-plan.md §TC-M002, UJ-DEV-002.

Verifies ``vendor/manifest.json`` pins match checked-in schema tree checksums.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from metar_shared.vendor_manifest import (
    MANIFEST_SCHEMA_VERSION,
    VENDOR_BUNDLE_NAMES,
    compute_tree_sha256,
    load_manifest,
    validate_manifest_schema,
    verify_manifest_integrity,
)

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "vendor" / "manifest.json"


@pytest.mark.migration
class TestTcM002ManifestIntegrity:
    """Manifest pins must match vendored wmo-im schema trees."""

    def test_manifest_integrity_passes(self) -> None:
        """Step 1-2: manifest validation reports no drift."""
        result = verify_manifest_integrity(ROOT)
        assert result.ok, "manifest integrity failed:\n" + "\n".join(result.errors)

    def test_manifest_declares_all_required_bundles(self) -> None:
        """Each wmo-im bundle from dependency-inventory.md is pinned."""
        assert MANIFEST_PATH.is_file(), "vendor/manifest.json must exist (T2.2)"
        manifest = load_manifest(MANIFEST_PATH)
        bundles = manifest["bundles"]
        for name in VENDOR_BUNDLE_NAMES:
            assert name in bundles, f"missing bundle pin: {name}"

    def test_manifest_schema_version(self) -> None:
        """Manifest uses the supported schema version."""
        assert MANIFEST_PATH.is_file()
        manifest = load_manifest(MANIFEST_PATH)
        assert manifest.get("schema_version") == MANIFEST_SCHEMA_VERSION

    def test_manifest_schema_has_no_structural_errors(self) -> None:
        """Required fields present before checksum verification."""
        assert MANIFEST_PATH.is_file()
        manifest = load_manifest(MANIFEST_PATH)
        errors = validate_manifest_schema(manifest)
        assert not errors, "manifest schema errors:\n" + "\n".join(errors)


@pytest.mark.unit
class TestVendorManifestHelpers:
    """Unit coverage for shared manifest utilities."""

    def test_compute_tree_sha256_is_deterministic(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
        nested = tmp_path / "nested"
        nested.mkdir()
        (nested / "b.txt").write_text("beta", encoding="utf-8")

        first = compute_tree_sha256(tmp_path)
        second = compute_tree_sha256(tmp_path)
        assert first == second
        assert len(first) == 64

    def test_compute_tree_sha256_changes_when_content_changes(
        self, tmp_path: Path
    ) -> None:
        target = tmp_path / "file.txt"
        target.write_text("v1", encoding="utf-8")
        before = compute_tree_sha256(tmp_path)
        target.write_text("v2", encoding="utf-8")
        after = compute_tree_sha256(tmp_path)
        assert before != after

    def test_validate_manifest_schema_reports_missing_bundle(self) -> None:
        errors = validate_manifest_schema(
            {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": {}}
        )
        assert any("missing required bundle" in err for err in errors)
