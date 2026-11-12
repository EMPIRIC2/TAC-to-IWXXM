"""Vendor manifest FAILURE paths — invalid JSON, missing fields, bad types."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metar_shared.vendor_manifest import (
    MANIFEST_SCHEMA_VERSION,
    load_manifest,
    validate_manifest_schema,
    verify_manifest_integrity,
)


def _required_minimal_bundles() -> dict[str, dict[str, object]]:
    return {
        "iwxxm": {
            "upstream_repo": "wmo-im/iwxxm",
            "tag": "2025-2",
            "commit_sha": "b" * 40,
            "local_path": "vendor/schemas/iwxxm",
            "tree_sha256": "a" * 64,
        },
        "iwxxm-codelists": {
            "upstream_repo": "wmo-im/iwxxm-codelists",
            "tag": "2025-2",
            "commit_sha": "b" * 40,
            "local_path": "vendor/schemas/iwxxm-codelists",
            "tree_sha256": "a" * 64,
        },
        "iwxxm-modelling": {
            "upstream_repo": "wmo-im/iwxxm-modelling",
            "tag": "2025-2",
            "commit_sha": "b" * 40,
            "local_path": "vendor/schemas/iwxxm-modelling",
            "tree_sha256": "a" * 64,
        },
        "iwxxm-translation": {
            "upstream_repo": "wmo-im/iwxxm-translation",
            "tag": "2025-2",
            "commit_sha": "b" * 40,
            "local_path": "vendor/schemas/iwxxm-translation",
            "tree_sha256": "a" * 64,
        },
        "iwxxm-us": {
            "source_url": "https://nws.weather.gov/schemas/iwxxm-us/3.0/x.tgz",
            "tag": "3.0",
            "local_path": "vendor/schemas/iwxxm-us",
            "tree_sha256": "a" * 64,
        },
        "iwxxm-ca": {
            "source_url": "https://example.com/iwxxm-ca.tgz",
            "tag": "1.0",
            "local_path": "vendor/schemas/iwxxm-ca",
            "tree_sha256": "a" * 64,
        },
        "iwxxm-3.0.0": {
            "parent_bundle": "iwxxm",
            "version_line": "3.0.0",
            "local_path": "vendor/schemas/iwxxm/3.0.0",
            "tree_sha256": "a" * 64,
        },
    }


def test_load_manifest_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_manifest(path)


def test_verify_manifest_integrity_maps_json_decode_error(tmp_path: Path) -> None:
    manifest_path = tmp_path / "vendor" / "manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text("{broken", encoding="utf-8")
    result = verify_manifest_integrity(tmp_path, manifest_path=manifest_path)
    assert result.ok is False
    assert result.errors[0].startswith("invalid manifest:")


def test_validate_github_bundle_missing_required_fields() -> None:
    bundles = _required_minimal_bundles()
    bundles["iwxxm"] = {
        "upstream_repo": "   ",
        "tag": "",
        "commit_sha": None,
        "local_path": "vendor/schemas/iwxxm",
        "tree_sha256": "a" * 64,
    }
    errors = validate_manifest_schema(
        {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}
    )
    assert any("missing or empty 'upstream_repo'" in err for err in errors)
    assert any("missing or empty 'tag'" in err for err in errors)
    assert any("missing or empty 'commit_sha'" in err for err in errors)


def test_validate_http_bundle_rejects_non_string_archive_sha() -> None:
    bundles = _required_minimal_bundles()
    bundles["iwxxm-us"]["archive_sha256"] = 12345  # type: ignore[assignment]
    errors = validate_manifest_schema(
        {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}
    )
    assert any("archive_sha256 must be 64 hex chars when present" in err for err in errors)


def test_validate_profile_line_missing_parent_bundle_field() -> None:
    bundles = _required_minimal_bundles()
    bundles["iwxxm-3.0.0"] = {
        "version_line": "3.0.0",
        "local_path": "vendor/schemas/iwxxm/3.0.0",
        "tree_sha256": "a" * 64,
    }
    errors = validate_manifest_schema(
        {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}
    )
    assert any("missing or empty 'parent_bundle'" in err for err in errors)
