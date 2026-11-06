"""BUG-2026-09-30 — vendor sync must match the pinned full tree.

GitHub archive tarballs drop ``export-ignore`` paths, and replacing
``vendor/schemas/iwxxm`` deletes the nested ``3.0.0`` profile-line snapshot.
Weekly sync then raises ``post-sync checksum mismatch`` even when the pin
did not change.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from unittest.mock import patch

from scripts.vendor.sync_iwxxm import sync_from_manifest

from metar_shared.vendor_manifest import compute_tree_sha256


def test_bug_2026_09_30_sync_keeps_full_tree_hash(tmp_path: Path) -> None:
    parent = tmp_path / "vendor/schemas/iwxxm"
    nested = parent / "3.0.0"
    nested.mkdir(parents=True)
    (nested / "core.xsd").write_text("core", encoding="utf-8")

    def fake_fetch(_repo: str, _sha: str, destination: Path) -> None:
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        external = destination / "externalSchema"
        external.mkdir()
        (external / "aixm.xsd").write_text("aixm", encoding="utf-8")

    expected = tmp_path / "expected"
    (expected / "externalSchema").mkdir(parents=True)
    (expected / "externalSchema" / "aixm.xsd").write_text("aixm", encoding="utf-8")
    (expected / "3.0.0").mkdir()
    (expected / "3.0.0" / "core.xsd").write_text("core", encoding="utf-8")

    manifest_path = tmp_path / "vendor/manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "bundles": {
                    "iwxxm": {
                        "upstream_repo": "wmo-im/iwxxm",
                        "tag": "v2025-2",
                        "commit_sha": "35180cbe3bec0bc536a78714dd78d2e7ba60931f",
                        "local_path": "vendor/schemas/iwxxm",
                        "tree_sha256": compute_tree_sha256(expected),
                    },
                    "iwxxm-3.0.0": {
                        "local_path": "vendor/schemas/iwxxm/3.0.0",
                        "version_line": "3.0.0",
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    with (
        patch("scripts.vendor.sync_iwxxm.GITHUB_BUNDLE_NAMES", ("iwxxm",)),
        patch("scripts.vendor.sync_iwxxm._fetch_github_tree", side_effect=fake_fetch),
        patch("scripts.vendor.sync_iwxxm.verify_manifest_integrity") as verify,
    ):
        sync_from_manifest(tmp_path, manifest_path, prefer_legacy=False, verify=False)

    verify.assert_not_called()
    assert (parent / "externalSchema" / "aixm.xsd").is_file()
    assert (nested / "core.xsd").read_text(encoding="utf-8") == "core"
    assert compute_tree_sha256(parent) == compute_tree_sha256(expected)
