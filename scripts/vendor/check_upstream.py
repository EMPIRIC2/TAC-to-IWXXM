"""Check wmo-im upstream tags and refresh vendor/manifest.json pins (M6, UJ-DEV-002)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import httpx

from metar_shared.vendor_manifest import (
    MANIFEST_RELATIVE_PATH,
    VENDOR_BUNDLE_NAMES,
    compute_tree_sha256,
    load_manifest,
)

GITHUB_API = "https://api.github.com"


def _github_get(client: httpx.Client, path: str) -> Any:
    response = client.get(
        f"{GITHUB_API}{path}", headers={"Accept": "application/vnd.github+json"}
    )
    response.raise_for_status()
    return response.json()


def resolve_ref_sha(client: httpx.Client, repo: str, ref: str) -> str:
    data = _github_get(client, f"/repos/{repo}/commits/{ref}")
    sha = data.get("sha")
    if not isinstance(sha, str) or len(sha) != 40:
        msg = f"could not resolve commit for {repo}@{ref}"
        raise ValueError(msg)
    return sha


def latest_release_tag(client: httpx.Client, repo: str) -> tuple[str, str] | None:
    try:
        data = _github_get(client, f"/repos/{repo}/releases/latest")
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return None
        raise
    tag_name = data.get("tag_name")
    if not isinstance(tag_name, str) or not tag_name.strip():
        return None
    commit_sha = resolve_ref_sha(client, repo, tag_name)
    return tag_name, commit_sha


def check_upstream(manifest_path: Path, *, update: bool) -> bool:
    """Return True when manifest pins were changed."""
    manifest = load_manifest(manifest_path)
    bundles = manifest.get("bundles")
    if not isinstance(bundles, dict):
        msg = "manifest bundles must be an object"
        raise ValueError(msg)

    changed = False
    with httpx.Client(timeout=60.0) as client:
        for name in VENDOR_BUNDLE_NAMES:
            entry = bundles.get(name)
            if not isinstance(entry, dict):
                continue
            upstream = entry.get("upstream_repo")
            if not isinstance(upstream, str):
                continue

            latest = latest_release_tag(client, upstream)
            if latest is None:
                continue

            tag_name, commit_sha = latest
            if entry.get("tag") == tag_name and entry.get("commit_sha") == commit_sha:
                continue

            # Release tag unchanged but tip commit moved — keep intentional pin
            # (wmo-im may republish the same tag with a different tree layout).
            if entry.get("tag") == tag_name:
                pinned_sha = entry.get("commit_sha")
                if isinstance(pinned_sha, str) and pinned_sha != commit_sha:
                    print(
                        f"{name}: release tag {tag_name} tip is {commit_sha[:7]}; "
                        f"keeping pin {pinned_sha[:7]}"
                    )
                continue

            if not update:
                print(
                    f"{name}: upstream update available ({tag_name} @ {commit_sha[:7]})"
                )
                changed = True
                continue

            entry["tag"] = tag_name
            entry["commit_sha"] = commit_sha
            # Stale tree_sha256 would fail sync_iwxxm mid-check before
            # --refresh-tree-hashes runs (BUG-2026-07-20 Vendor Sync).
            entry.pop("tree_sha256", None)
            changed = True
            print(f"{name}: pinned to {tag_name} @ {commit_sha}")

    if update and changed:
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
    return changed


def refresh_tree_hashes(repo_root: Path, manifest_path: Path) -> None:
    manifest = load_manifest(manifest_path)
    bundles = manifest.get("bundles")
    if not isinstance(bundles, dict):
        return
    for name in VENDOR_BUNDLE_NAMES:
        entry = bundles.get(name)
        if not isinstance(entry, dict):
            continue
        local_path = entry.get("local_path")
        if not isinstance(local_path, str):
            continue
        tree_root = repo_root / local_path
        if tree_root.is_dir():
            entry["tree_sha256"] = compute_tree_sha256(tree_root)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(MANIFEST_RELATIVE_PATH),
        help="Path to vendor/manifest.json",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Write manifest when upstream releases differ from pins",
    )
    parser.add_argument(
        "--refresh-tree-hashes",
        action="store_true",
        help="Recompute tree_sha256 fields after vendor sync",
    )
    args = parser.parse_args()

    repo_root = Path.cwd()
    manifest_path = (
        args.manifest if args.manifest.is_absolute() else repo_root / args.manifest
    )

    if args.refresh_tree_hashes:
        refresh_tree_hashes(repo_root, manifest_path)
        return

    changed = check_upstream(manifest_path, update=args.update)
    if args.update and not changed:
        print("vendor pins already match upstream latest releases")
    sys.exit(0)


if __name__ == "__main__":
    main()
