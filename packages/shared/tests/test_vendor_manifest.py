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


def _sample_http_bundle(
    local_path: str, *, tree_sha256: str = "a" * 64
) -> dict[str, str]:
    return {
        "source_url": "https://nws.weather.gov/schemas/iwxxm-us/3.0/iwxxm-us-3.0-schemas.tgz",
        "tag": "3.0",
        "local_path": local_path,
        "tree_sha256": tree_sha256,
        "archive_sha256": "c" * 64,
    }


def _sample_profile_line_bundle(
    local_path: str, *, tree_sha256: str = "a" * 64
) -> dict[str, str]:
    return {
        "parent_bundle": "iwxxm",
        "version_line": "3.0.0",
        "local_path": local_path,
        "tree_sha256": tree_sha256,
    }


def _sample_for_bundle(
    name: str, local_path: str, *, tree_sha256: str = "a" * 64
) -> dict[str, str]:
    """Pick GitHub vs HTTP vs profile-line sample factory from bundle name."""
    if name in ("iwxxm-us", "iwxxm-ca"):
        return _sample_http_bundle(local_path, tree_sha256=tree_sha256)
    if name == "iwxxm-3.0.0":
        return _sample_profile_line_bundle(local_path, tree_sha256=tree_sha256)
    return _sample_bundle(local_path, tree_sha256=tree_sha256)


def _bundle_local_path(name: str) -> str:
    if name == "iwxxm-3.0.0":
        return "vendor/schemas/iwxxm/3.0.0"
    return f"vendor/schemas/{name}"


def _bundle_tree_root(tmp_path: Path, name: str) -> Path:
    if name == "iwxxm-3.0.0":
        return tmp_path / "vendor" / "schemas" / "iwxxm" / "3.0.0"
    return tmp_path / "vendor" / "schemas" / name


def _required_bundles(
    *,
    tree_sha256: str = "a" * 64,
) -> dict[str, dict[str, str]]:
    bundles: dict[str, dict[str, str]] = {}
    for name in (
        "iwxxm",
        "iwxxm-codelists",
        "iwxxm-modelling",
        "iwxxm-translation",
        "iwxxm-us",
        "iwxxm-ca",
    ):
        bundles[name] = _sample_for_bundle(
            name, f"vendor/schemas/{name}", tree_sha256=tree_sha256
        )
    bundles["iwxxm-3.0.0"] = _sample_profile_line_bundle(
        "vendor/schemas/iwxxm/3.0.0", tree_sha256=tree_sha256
    )
    return bundles


def test_load_manifest_rejects_non_object_root(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps([]), encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        load_manifest(path)


def test_validate_manifest_schema_accepts_minimal_valid_manifest() -> None:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "bundles": _required_bundles(),
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
    bundles = _required_bundles()
    bundles["iwxxm"] = _sample_bundle("vendor/schemas/iwxxm", tree_sha256="0" * 64)
    manifest_path.write_text(
        json.dumps({"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}),
        encoding="utf-8",
    )

    for name in (
        "iwxxm-codelists",
        "iwxxm-modelling",
        "iwxxm-translation",
        "iwxxm-us",
        "iwxxm-ca",
        "iwxxm-3.0.0",
    ):
        path = _bundle_tree_root(tmp_path, name)
        path.mkdir(parents=True)
        bundle = _sample_for_bundle(
            name,
            _bundle_local_path(name),
            tree_sha256=compute_tree_sha256(path),
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


def test_validate_manifest_schema_reports_missing_required_bundle() -> None:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "bundles": {
            "iwxxm": _sample_bundle("vendor/schemas/iwxxm"),
        },
    }
    errors = validate_manifest_schema(manifest)
    assert any("missing required bundle 'iwxxm-codelists'" in err for err in errors)
    assert any("missing required bundle 'iwxxm-us'" in err for err in errors)
    assert any("missing required bundle 'iwxxm-ca'" in err for err in errors)
    assert any("missing required bundle 'iwxxm-3.0.0'" in err for err in errors)


def test_validate_profile_line_bundle_reports_field_errors() -> None:
    bundles = _required_bundles()
    bundles["iwxxm-3.0.0"] = {
        "parent_bundle": "unknown",
        "version_line": "",
        "local_path": "schemas/iwxxm/3.0.0",
        "tree_sha256": "short",
    }
    errors = validate_manifest_schema(
        {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}
    )
    assert any("parent_bundle must be a GitHub bundle name" in err for err in errors)
    assert any("missing or empty 'version_line'" in err for err in errors)
    assert any("local_path must start with 'vendor/schemas/'" in err for err in errors)
    assert any("tree_sha256 must be 64" in err for err in errors)


def test_validate_manifest_schema_reports_bundle_field_errors() -> None:
    bundles = _required_bundles()
    bundles["iwxxm"] = {
        "upstream_repo": "other/iwxxm",
        "tag": "",
        "commit_sha": "short",
        "local_path": "schemas/iwxxm",
        "tree_sha256": "short",
    }
    errors = validate_manifest_schema(
        {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}
    )
    assert any("upstream_repo must start with 'wmo-im/'" in err for err in errors)
    assert any("commit_sha must be 40" in err for err in errors)
    assert any("tree_sha256 must be 64" in err for err in errors)
    assert any("local_path must start with 'vendor/schemas/'" in err for err in errors)
    assert any("missing or empty 'tag'" in err for err in errors)


def test_validate_manifest_schema_rejects_non_object_bundle() -> None:
    bundles: dict[str, object] = dict(_required_bundles())
    bundles["iwxxm"] = []
    errors = validate_manifest_schema(
        {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}
    )
    assert any("bundle 'iwxxm' must be an object" in err for err in errors)


def test_validate_http_bundle_requires_https_source_url() -> None:
    bundles = _required_bundles()
    bundles["iwxxm-us"] = {
        "source_url": "http://example.com/schemas.tgz",
        "tag": "3.0",
        "local_path": "vendor/schemas/iwxxm-us",
        "tree_sha256": "a" * 64,
    }
    errors = validate_manifest_schema(
        {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}
    )
    assert any("source_url must be https://" in err for err in errors)


def test_validate_http_bundle_reports_empty_fields_and_bad_archive_hash() -> None:
    bundles = _required_bundles()
    bundles["iwxxm-us"] = {
        "source_url": "https://nws.weather.gov/schemas/iwxxm-us/3.0/x.tgz",
        "tag": "   ",
        "local_path": "vendor/schemas/iwxxm-us",
        "tree_sha256": "a" * 64,
        "archive_sha256": "short",
    }
    errors = validate_manifest_schema(
        {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}
    )
    assert any("missing or empty 'tag'" in err for err in errors)
    assert any("archive_sha256 must be 64 hex chars" in err for err in errors)


def test_github_bundle_with_source_url_still_uses_github_rules() -> None:
    """Dispatch is by bundle name, not presence of source_url (Sourcery #700)."""
    bundles = _required_bundles()
    bundles["iwxxm"] = {
        **_sample_bundle("vendor/schemas/iwxxm"),
        "source_url": "https://example.com/extra",
    }
    assert (
        validate_manifest_schema(
            {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}
        )
        == []
    )


def test_archive_sha256_rejects_non_hex() -> None:
    bundles = _required_bundles()
    bundles["iwxxm-us"]["archive_sha256"] = "g" * 64
    errors = validate_manifest_schema(
        {"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}
    )
    assert any("archive_sha256 must be 64 hex chars" in err for err in errors)


def test_verify_manifest_integrity_reports_non_object_bundles(tmp_path: Path) -> None:
    """``bundles`` as a non-object skips tree checks (EV-080 M2a branch 252→277)."""
    manifest_path = tmp_path / "vendor" / "manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "bundles": [],
            }
        ),
        encoding="utf-8",
    )
    result = verify_manifest_integrity(tmp_path, manifest_path=manifest_path)
    assert not result.ok
    assert any("bundles must be an object" in err for err in result.errors)


def test_verify_manifest_integrity_reports_oserror_from_load(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """OSError from ``load_manifest`` maps to invalid-manifest result (EV-080 M2a)."""
    manifest_path = tmp_path / "vendor" / "manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text("{}", encoding="utf-8")

    def _boom(_path: Path) -> dict[str, object]:
        raise OSError("permission denied")

    monkeypatch.setattr(
        "metar_shared.vendor_manifest.load_manifest",
        _boom,
    )
    result = verify_manifest_integrity(tmp_path, manifest_path=manifest_path)
    assert not result.ok
    assert result.errors[0].startswith("invalid manifest:")


def test_verify_manifest_integrity_skips_non_object_or_incomplete_bundle_entries(
    tmp_path: Path,
) -> None:
    bundles: dict[str, object] = {
        "iwxxm": "not-an-object",
        "iwxxm-codelists": {"local_path": 123, "tree_sha256": "a" * 64},
    }
    for name in (
        "iwxxm-modelling",
        "iwxxm-translation",
        "iwxxm-us",
        "iwxxm-ca",
        "iwxxm-3.0.0",
    ):
        root = _bundle_tree_root(tmp_path, name)
        root.mkdir(parents=True)
        (root / "README.md").write_text(name, encoding="utf-8")
        bundles[name] = _sample_for_bundle(
            name,
            _bundle_local_path(name),
            tree_sha256=compute_tree_sha256(root),
        )

    manifest_path = tmp_path / "vendor" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "bundles": bundles,
            }
        ),
        encoding="utf-8",
    )
    result = verify_manifest_integrity(tmp_path, manifest_path=manifest_path)
    assert not result.ok
    assert not any("tree missing" in err for err in result.errors)


def test_verify_manifest_integrity_reports_missing_bundle_tree(tmp_path: Path) -> None:
    manifest_path = tmp_path / "vendor" / "manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "bundles": _required_bundles(),
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
        "iwxxm-us",
        "iwxxm-ca",
    ):
        root = _bundle_tree_root(tmp_path, name)
        root.mkdir(parents=True)
        (root / "README.md").write_text(name, encoding="utf-8")
        bundles[name] = _sample_for_bundle(
            name,
            _bundle_local_path(name),
            tree_sha256=compute_tree_sha256(root),
        )

    profile_root = _bundle_tree_root(tmp_path, "iwxxm-3.0.0")
    profile_root.mkdir(parents=True)
    (profile_root / "README.md").write_text("iwxxm-3.0.0", encoding="utf-8")
    bundles["iwxxm-3.0.0"] = _sample_profile_line_bundle(
        _bundle_local_path("iwxxm-3.0.0"),
        tree_sha256=compute_tree_sha256(profile_root),
    )
    # Profile line is nested under iwxxm - re-hash parent after subtree materialises.
    iwxxm_root = _bundle_tree_root(tmp_path, "iwxxm")
    bundles["iwxxm"] = _sample_for_bundle(
        "iwxxm",
        _bundle_local_path("iwxxm"),
        tree_sha256=compute_tree_sha256(iwxxm_root),
    )

    manifest_path = tmp_path / "vendor" / "manifest.json"
    manifest_path.write_text(
        json.dumps({"schema_version": MANIFEST_SCHEMA_VERSION, "bundles": bundles}),
        encoding="utf-8",
    )
    result = verify_manifest_integrity(tmp_path, manifest_path=manifest_path)
    assert result.ok
    assert result.errors == ()
