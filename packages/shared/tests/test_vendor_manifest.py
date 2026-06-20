"""Unit tests for vendor manifest validation helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metar_shared.vendor_manifest import (
    MANIFEST_SCHEMA_VERSION,
    compute_tree_sha256,
    load_manifest,
    validate_manifest_schema,
    verify_manifest_integrity,
)


def _sample_bundle(local_path: str, *, tree_sha256: str = "a" * 64) -> dict[str, str]:
    return {
        "upstream_repo": "wmo-im/iwxxm",
        "tag": "2025-2",
        "commit_sha": "b" * 40,
        "local_path": local_path,
        "tree_sha256": tree_sha256,
    }


def test_load_manifest_rejects_non_object_root(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps([]), encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        load_manifest(path)


def test_validate_manifest_schema_accepts_minimal_valid_manifest() -> None:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "bundles": {
            "iwxxm": _sample_bundle("vendor/schemas/iwxxm"),
            "iwxxm-codelists": _sample_bundle("vendor/schemas/iwxxm-codelists"),
            "iwxxm-modelling": _sample_bundle("vendor/schemas/iwxxm-modelling"),
            "iwxxm-translation": _sample_bundle("vendor/schemas/iwxxm-translation"),
        },
    }
    assert validate_manifest_schema(manifest) == []


def test_verify_manifest_integrity_reports_missing_manifest(tmp_path: Path) -> None:
    result = verify_manifest_integrity(tmp_path)
    assert not result.ok
    assert result.errors[0].startswith("missing manifest:")


def test_verify_manifest_integrity_detects_checksum_drift(tmp_path: Path) -> None:
    bundle_root = tmp_path / "vendor" / "schemas" / "iwxxm"
    bundle_root.mkdir(parents=True)
    (bundle_root / "sample.txt").write_text("content", encoding="utf-8")
    actual_sha = compute_tree_sha256(bundle_root)

    manifest_path = tmp_path / "vendor" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "bundles": {
                    "iwxxm": _sample_bundle(
                        "vendor/schemas/iwxxm", tree_sha256="0" * 64
                    ),
                    "iwxxm-codelists": _sample_bundle("vendor/schemas/iwxxm-codelists"),
                    "iwxxm-modelling": _sample_bundle("vendor/schemas/iwxxm-modelling"),
                    "iwxxm-translation": _sample_bundle(
                        "vendor/schemas/iwxxm-translation"
                    ),
                },
            }
        ),
        encoding="utf-8",
    )

    # Create empty dirs for other bundles so checksum step runs only on iwxxm mismatch.
    for name in ("iwxxm-codelists", "iwxxm-modelling", "iwxxm-translation"):
        path = tmp_path / "vendor" / "schemas" / name
        path.mkdir(parents=True)
        bundle = _sample_bundle(
            f"vendor/schemas/{name}", tree_sha256=compute_tree_sha256(path)
        )
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["bundles"][name] = bundle
        manifest_path.write_text(json.dumps(data), encoding="utf-8")

    result = verify_manifest_integrity(tmp_path, manifest_path=manifest_path)
    assert not result.ok
    assert any("tree_sha256 mismatch" in err for err in result.errors)
    assert actual_sha != "0" * 64


def test_compute_tree_sha256_rejects_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not a directory"):
        compute_tree_sha256(tmp_path / "missing")


def test_validate_manifest_schema_reports_structural_errors() -> None:
    errors = validate_manifest_schema({"schema_version": 99, "bundles": "bad"})
    assert any("schema_version" in err for err in errors)
    assert any("bundles must be an object" in err for err in errors)


def test_validate_manifest_schema_reports_bundle_field_errors() -> None:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "bundles": {
            "iwxxm": {
                "upstream_repo": "other/iwxxm",
                "tag": "",
                "commit_sha": "short",
                "local_path": "schemas/iwxxm",
                "tree_sha256": "short",
            },
            "iwxxm-codelists": _sample_bundle("vendor/schemas/iwxxm-codelists"),
            "iwxxm-modelling": _sample_bundle("vendor/schemas/iwxxm-modelling"),
            "iwxxm-translation": _sample_bundle("vendor/schemas/iwxxm-translation"),
        },
    }
    errors = validate_manifest_schema(manifest)
    assert any("upstream_repo must start with 'wmo-im/'" in err for err in errors)
    assert any("commit_sha must be 40" in err for err in errors)
    assert any("tree_sha256 must be 64" in err for err in errors)
    assert any("local_path must live under vendor/schemas/" in err for err in errors)
    assert any("missing or empty 'tag'" in err for err in errors)


def test_validate_manifest_schema_rejects_non_object_bundle() -> None:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "bundles": {
            "iwxxm": [],
            "iwxxm-codelists": _sample_bundle("vendor/schemas/iwxxm-codelists"),
            "iwxxm-modelling": _sample_bundle("vendor/schemas/iwxxm-modelling"),
            "iwxxm-translation": _sample_bundle("vendor/schemas/iwxxm-translation"),
        },
    }
    errors = validate_manifest_schema(manifest)
    assert any("bundle 'iwxxm' must be an object" in err for err in errors)


def test_verify_manifest_integrity_reports_invalid_json(tmp_path: Path) -> None:
    manifest_path = tmp_path / "vendor" / "manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text("{not-json", encoding="utf-8")
    result = verify_manifest_integrity(tmp_path, manifest_path=manifest_path)
    assert not result.ok
    assert result.errors[0].startswith("invalid manifest:")


def test_verify_manifest_integrity_reports_missing_bundle_tree(tmp_path: Path) -> None:
    manifest_path = tmp_path / "vendor" / "manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "bundles": {
            "iwxxm": _sample_bundle("vendor/schemas/iwxxm"),
            "iwxxm-codelists": _sample_bundle("vendor/schemas/iwxxm-codelists"),
            "iwxxm-modelling": _sample_bundle("vendor/schemas/iwxxm-modelling"),
            "iwxxm-translation": _sample_bundle("vendor/schemas/iwxxm-translation"),
        },
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = verify_manifest_integrity(tmp_path, manifest_path=manifest_path)
    assert not result.ok
    assert any("tree missing" in err for err in result.errors)


def test_verify_manifest_integrity_passes_for_matching_tree(tmp_path: Path) -> None:
    bundles: dict[str, dict[str, str]] = {}
    for name in (
        "iwxxm",
        "iwxxm-codelists",
        "iwxxm-modelling",
        "iwxxm-translation",
    ):
        root = tmp_path / "vendor" / "schemas" / name
        root.mkdir(parents=True)
        (root / "README.md").write_text(name, encoding="utf-8")
        bundles[name] = _sample_bundle(
            f"vendor/schemas/{name}",
            tree_sha256=compute_tree_sha256(root),
        )

    manifest_path = tmp_path / "vendor" / "manifest.json"
    manifest_path.write_text(
        json.dumps({"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}),
        encoding="utf-8",
    )
    result = verify_manifest_integrity(tmp_path, manifest_path=manifest_path)
    assert result.ok
    assert result.errors == ()
