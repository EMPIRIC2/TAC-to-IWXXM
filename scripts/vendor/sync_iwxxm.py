"""Populate vendor/schemas/* from manifest pins (migration bootstrap + future wmo-im fetch)."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
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
    """Checkout ``commit_sha`` including paths marked ``export-ignore``.

    GitHub archive tarballs omit those paths (for iwxxm: ``externalSchema/``,
    docs, and dotfiles). Vendor snapshots are full checkouts, so the tarball
    hash does not match ``tree_sha256``.
    """
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()
    remote = f"https://github.com/{repo}.git"
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=destination, check=True, env=env)

    git("init")
    git("remote", "add", "origin", remote)
    git("fetch", "--depth", "1", "origin", commit_sha)
    git("-c", "advice.detachedHead=false", "checkout", "FETCH_HEAD")
    git_dir = destination / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)


def _nested_preserve_rels(parent_local: str, bundles: dict[str, Any]) -> list[str]:
    """Bundle paths that live inside ``parent_local`` and must survive a replace."""
    parent = Path(parent_local)
    rels: list[str] = []
    for entry in bundles.values():
        if not isinstance(entry, dict):
            continue
        local = entry.get("local_path")
        if not isinstance(local, str):
            continue
        child = Path(local)
        if child != parent and parent in child.parents:
            rels.append(local)
    return rels


def _stash_nested(repo_root: Path, rels: list[str]) -> list[tuple[Path, Path]]:
    """Move nested bundle dirs aside so a parent replace does not delete them."""
    stashed: list[tuple[Path, Path]] = []
    for rel in rels:
        src = repo_root / rel
        if not src.is_dir():
            continue
        holder = Path(tempfile.mkdtemp(prefix="vendor-nested-"))
        parked = holder / src.name
        shutil.move(str(src), str(parked))
        stashed.append((src, parked))
    return stashed


def _restore_nested(stashed: list[tuple[Path, Path]]) -> None:
    """Put stashed nested bundle dirs back, replacing anything the fetch wrote."""
    for target, parked in stashed:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(parked), str(target))
        parked.parent.rmdir()


def sync_bundle(
    repo_root: Path,
    name: str,
    entry: dict[str, Any],
    *,
    prefer_legacy: bool,
    preserve_rels: list[str] | None = None,
) -> None:
    local_path = entry["local_path"]
    destination = repo_root / local_path
    upstream = entry["upstream_repo"]
    commit_sha = entry["commit_sha"]
    stashed = _stash_nested(repo_root, preserve_rels or [])

    try:
        legacy_source = repo_root / LEGACY_SOURCE_PATHS.get(name, "")
        if prefer_legacy and legacy_source.is_dir():
            _copy_tree(legacy_source, destination)
            return

        _fetch_github_tree(upstream, commit_sha, destination)
    finally:
        _restore_nested(stashed)


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
        preserve = _nested_preserve_rels(str(entry["local_path"]), bundles)
        sync_bundle(
            repo_root,
            name,
            entry,
            prefer_legacy=prefer_legacy,
            preserve_rels=preserve,
        )

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
