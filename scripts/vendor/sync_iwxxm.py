"""Populate vendor/schemas/* from manifest pins (migration bootstrap + future wmo-im fetch)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from typing import Any

from metar_shared.vendor_manifest import (
    GITHUB_BUNDLE_NAMES,
    MANIFEST_RELATIVE_PATH,
    compute_tree_sha256,
    load_manifest,
    verify_manifest_integrity,
)

# Legacy submodule paths used during monorepo migration (T2.4 bootstrap).
LEGACY_SOURCE_PATHS: dict[str, str] = {
    "iwxxm": "schemas/iwxxm",
    "iwxxm-codelists": "schemas/iwxxm-codelists",
    "iwxxm-modelling": "schemas/iwxxm-modelling",
    "iwxxm-translation": "data/iwxxm-translation",
}


def _copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )


def _fetch_github_tree(repo: str, commit_sha: str, destination: Path) -> None:
    archive_url = f"https://github.com/{repo}/archive/{commit_sha}.tar.gz"
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()
    subprocess.run(
        [
            "bash",
            "-c",
            (
                f"curl -fsSL '{archive_url}' | "
                "tar -xz --strip-components=1 -C "
                f"'{destination}'"
            ),
        ],
        check=True,
    )


def sync_bundle(
    repo_root: Path,
    name: str,
    entry: dict[str, Any],
    *,
    prefer_legacy: bool,
) -> None:
    local_path = entry["local_path"]
    destination = repo_root / local_path
    upstream = entry["upstream_repo"]
    commit_sha = entry["commit_sha"]

    legacy_source = repo_root / LEGACY_SOURCE_PATHS.get(name, "")
    if prefer_legacy and legacy_source.is_dir():
        _copy_tree(legacy_source, destination)
        return

    _fetch_github_tree(upstream, commit_sha, destination)


def sync_from_manifest(
    repo_root: Path,
    manifest_path: Path,
    *,
    prefer_legacy: bool = True,
    verify: bool = True,
) -> None:
    manifest = load_manifest(manifest_path)
    bundles = manifest.get("bundles")
    if not isinstance(bundles, dict):
        msg = "manifest bundles must be an object"
        raise ValueError(msg)

    for name in GITHUB_BUNDLE_NAMES:
        entry = bundles.get(name)
        if not isinstance(entry, dict):
            msg = f"missing bundle entry: {name}"
            raise ValueError(msg)
        sync_bundle(repo_root, name, entry, prefer_legacy=prefer_legacy)

        pinned = entry.get("tree_sha256")
        if isinstance(pinned, str):
            actual = compute_tree_sha256(repo_root / entry["local_path"])
            if actual != pinned:
                msg = (
                    f"post-sync checksum mismatch for {name}: "
                    f"manifest={pinned}, actual={actual}"
                )
                raise ValueError(msg)

    # HTTP archive bundles (e.g. iwxxm-us) are pinned offline; refresh via dedicated
    # sync helper / PR — not the wmo-im GitHub fetch path above.

    if verify:
        result = verify_manifest_integrity(repo_root, manifest_path=manifest_path)
        if not result.ok:
            msg = "manifest integrity failed after sync:\n" + "\n".join(result.errors)
            raise ValueError(msg)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(MANIFEST_RELATIVE_PATH),
        help="Path to vendor/manifest.json",
    )
    parser.add_argument(
        "--no-legacy",
        action="store_true",
        help="Fetch from wmo-im GitHub instead of legacy submodule paths",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip post-sync manifest integrity verification",
    )
    args = parser.parse_args()

    repo_root = Path.cwd()
    manifest_path = (
        args.manifest if args.manifest.is_absolute() else repo_root / args.manifest
    )
    sync_from_manifest(
        repo_root,
        manifest_path,
        prefer_legacy=not args.no_legacy,
        verify=not args.no_verify,
    )


if __name__ == "__main__":
    main()
