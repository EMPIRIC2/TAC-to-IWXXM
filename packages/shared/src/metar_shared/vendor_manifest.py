"""Vendor manifest schema and integrity checks for wmo-im schema snapshots (TC-M002)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

MANIFEST_SCHEMA_VERSION = 1
MANIFEST_RELATIVE_PATH = Path("vendor/manifest.json")

VENDOR_BUNDLE_NAMES: tuple[str, ...] = (
    "iwxxm",
    "iwxxm-codelists",
    "iwxxm-modelling",
    "iwxxm-translation",
)

BUNDLE_REQUIRED_FIELDS: tuple[str, ...] = (
    "upstream_repo",
    "tag",
    "commit_sha",
    "local_path",
    "tree_sha256",
)


@dataclass(frozen=True)
class ManifestIntegrityResult:
    """Outcome of validating ``vendor/manifest.json`` against the checked-in tree."""

    ok: bool
    errors: tuple[str, ...] = field(default_factory=tuple)


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load and parse ``vendor/manifest.json``."""
    raw = manifest_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        msg = "manifest root must be a JSON object"
        raise ValueError(msg)
    return cast(dict[str, Any], data)


def compute_tree_sha256(root: Path) -> str:
    """Deterministic SHA-256 over sorted relative file paths and contents."""
    if not root.is_dir():
        msg = f"tree root is not a directory: {root}"
        raise ValueError(msg)

    digest = hashlib.sha256()
    files = sorted(
        path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts
    )
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _validate_bundle_entry(name: str, entry: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        errors.append(f"bundle {name!r} must be an object")
        return errors

    entry_dict = cast(dict[str, Any], entry)
    for field_name in BUNDLE_REQUIRED_FIELDS:
        value = entry_dict.get(field_name)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"bundle {name!r} missing or empty {field_name!r}")

    upstream = entry_dict.get("upstream_repo")
    if isinstance(upstream, str) and not upstream.startswith("wmo-im/"):
        errors.append(
            f"bundle {name!r} upstream_repo must start with 'wmo-im/', got {upstream!r}"
        )

    commit_sha = entry_dict.get("commit_sha")
    if isinstance(commit_sha, str) and len(commit_sha) != 40:
        errors.append(
            f"bundle {name!r} commit_sha must be 40 hex chars, got length {len(commit_sha)}"
        )

    tree_sha = entry_dict.get("tree_sha256")
    if isinstance(tree_sha, str) and len(tree_sha) != 64:
        errors.append(
            f"bundle {name!r} tree_sha256 must be 64 hex chars, got length {len(tree_sha)}"
        )

    local_path = entry_dict.get("local_path")
    if isinstance(local_path, str) and not local_path.startswith("vendor/schemas/"):
        errors.append(
            f"bundle {name!r} local_path must live under vendor/schemas/, got {local_path!r}"
        )

    return errors


def validate_manifest_schema(manifest: dict[str, Any]) -> list[str]:
    """Validate manifest structure without touching the vendor tree."""
    errors: list[str] = []

    schema_version = manifest.get("schema_version")
    if schema_version != MANIFEST_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {MANIFEST_SCHEMA_VERSION}, got {schema_version!r}"
        )

    bundles = manifest.get("bundles")
    if not isinstance(bundles, dict):
        errors.append("bundles must be an object")
        return errors

    bundle_map = cast(dict[str, Any], bundles)

    for name in VENDOR_BUNDLE_NAMES:
        if name not in bundle_map:
            errors.append(f"missing required bundle {name!r}")

    for name, entry in bundle_map.items():
        errors.extend(_validate_bundle_entry(name, entry))

    return errors


def verify_manifest_integrity(
    repo_root: Path,
    *,
    manifest_path: Path | None = None,
) -> ManifestIntegrityResult:
    """Ensure manifest pins match the checked-in vendor schema trees."""
    path = manifest_path or (repo_root / MANIFEST_RELATIVE_PATH)
    errors: list[str] = []

    if not path.is_file():
        return ManifestIntegrityResult(
            ok=False,
            errors=(f"missing manifest: {path.relative_to(repo_root).as_posix()}",),
        )

    try:
        manifest = load_manifest(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return ManifestIntegrityResult(ok=False, errors=(f"invalid manifest: {exc}",))

    errors.extend(validate_manifest_schema(manifest))

    bundles_raw = manifest.get("bundles")
    if isinstance(bundles_raw, dict):
        bundles = cast(dict[str, Any], bundles_raw)
        for name in VENDOR_BUNDLE_NAMES:
            entry = bundles.get(name)
            if not isinstance(entry, dict):
                continue

            entry_dict = cast(dict[str, Any], entry)
            local_path = entry_dict.get("local_path")
            pinned_sha = entry_dict.get("tree_sha256")
            if not isinstance(local_path, str) or not isinstance(pinned_sha, str):
                continue

            tree_root = repo_root / local_path
            if not tree_root.is_dir():
                errors.append(f"bundle {name!r} tree missing at {local_path}")
                continue

            actual_sha = compute_tree_sha256(tree_root)
            if actual_sha != pinned_sha:
                errors.append(
                    f"bundle {name!r} tree_sha256 mismatch at {local_path}: "
                    f"manifest={pinned_sha}, actual={actual_sha}"
                )

    if errors:
        return ManifestIntegrityResult(ok=False, errors=tuple(errors))
    return ManifestIntegrityResult(ok=True)
