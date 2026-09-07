"""EV-080 coverage fills for scripts/vendor/sync_iwxxm.py."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import pytest
import scripts.vendor.sync_iwxxm as sync_mod
from scripts.vendor.sync_iwxxm import (
    main,
    sync_bundle,
    sync_from_manifest,
)


@dataclass
class _Integrity:
    ok: bool
    errors: list[str]


def test_fetch_github_tree_removes_existing(tmp_path: Path) -> None:
    dest = tmp_path / "dest"
    dest.mkdir()
    (dest / "old.txt").write_text("old", encoding="utf-8")
    with patch.object(sync_mod.subprocess, "run") as run:
        sync_mod._fetch_github_tree("wmo-im/iwxxm", "a" * 40, dest)
    assert run.called
    assert dest.is_dir()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    (src / "a.xsd").write_text("<x/>", encoding="utf-8")
    (src / ".git").mkdir()
    sync_mod._copy_tree(src, dst)
    assert (dst / "a.xsd").is_file()
    assert not (dst / ".git").exists()

    sync_mod._copy_tree(src, dst)  # replaces existing

    dest = tmp_path / "fetch"
    with patch.object(sync_mod.subprocess, "run") as run:
        sync_mod._fetch_github_tree("wmo-im/iwxxm", "a" * 40, dest)
    assert run.call_args.kwargs["check"] is True
    assert dest.is_dir()


def test_sync_bundle_legacy_and_fetch(tmp_path: Path) -> None:
    legacy = tmp_path / "schemas/iwxxm"
    legacy.mkdir(parents=True)
    (legacy / "x.xsd").write_text("x", encoding="utf-8")
    entry = {
        "local_path": "vendor/schemas/iwxxm",
        "upstream_repo": "wmo-im/iwxxm",
        "commit_sha": "b" * 40,
    }
    with patch.object(sync_mod, "_copy_tree") as copy:
        sync_bundle(tmp_path, "iwxxm", entry, prefer_legacy=True)
    copy.assert_called_once()

    with patch.object(sync_mod, "_fetch_github_tree") as fetch:
        sync_bundle(tmp_path, "iwxxm", entry, prefer_legacy=False)
    fetch.assert_called_once()


def test_sync_from_manifest_branches(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"bundles": "bad"}), encoding="utf-8")
    with pytest.raises(ValueError, match="bundles must be an object"):
        sync_from_manifest(tmp_path, manifest_path)

    manifest_path.write_text(json.dumps({"bundles": {}}), encoding="utf-8")
    with (
        patch.object(sync_mod, "GITHUB_BUNDLE_NAMES", ("iwxxm",)),
        pytest.raises(ValueError, match="missing bundle entry"),
    ):
        sync_from_manifest(tmp_path, manifest_path)

    entry = {
        "local_path": "vendor/schemas/iwxxm",
        "upstream_repo": "wmo-im/iwxxm",
        "commit_sha": "c" * 40,
        "tree_sha256": "deadbeef" * 8,
    }
    manifest_path.write_text(
        json.dumps({"bundles": {"iwxxm": entry}}), encoding="utf-8"
    )
    dest = tmp_path / entry["local_path"]
    dest.mkdir(parents=True)
    (dest / "f.xsd").write_text("f", encoding="utf-8")

    with (
        patch.object(sync_mod, "GITHUB_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(sync_mod, "sync_bundle"),
        patch.object(sync_mod, "compute_tree_sha256", return_value="other"),
        pytest.raises(ValueError, match="checksum mismatch"),
    ):
        sync_from_manifest(tmp_path, manifest_path)

    with (
        patch.object(sync_mod, "GITHUB_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(sync_mod, "sync_bundle"),
        patch.object(
            sync_mod, "compute_tree_sha256", return_value=entry["tree_sha256"]
        ),
        patch.object(
            sync_mod,
            "verify_manifest_integrity",
            return_value=_Integrity(ok=False, errors=["bad"]),
        ),
        pytest.raises(ValueError, match="manifest integrity failed"),
    ):
        sync_from_manifest(tmp_path, manifest_path)

    with (
        patch.object(sync_mod, "GITHUB_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(sync_mod, "sync_bundle"),
        patch.object(
            sync_mod, "compute_tree_sha256", return_value=entry["tree_sha256"]
        ),
        patch.object(
            sync_mod,
            "verify_manifest_integrity",
            return_value=_Integrity(ok=True, errors=[]),
        ),
    ):
        sync_from_manifest(tmp_path, manifest_path, verify=True)

    no_hash = {
        "local_path": "vendor/schemas/iwxxm",
        "upstream_repo": "wmo-im/iwxxm",
        "commit_sha": "c" * 40,
    }
    manifest_path.write_text(
        json.dumps({"bundles": {"iwxxm": no_hash}}), encoding="utf-8"
    )
    with (
        patch.object(sync_mod, "GITHUB_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(sync_mod, "sync_bundle"),
        patch.object(
            sync_mod,
            "verify_manifest_integrity",
            return_value=_Integrity(ok=True, errors=[]),
        ),
    ):
        sync_from_manifest(tmp_path, manifest_path, verify=True)

    with (
        patch.object(sync_mod, "GITHUB_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(sync_mod, "sync_bundle"),
        patch.object(
            sync_mod, "compute_tree_sha256", return_value=entry["tree_sha256"]
        ),
        patch.object(sync_mod, "verify_manifest_integrity") as verify,
    ):
        sync_from_manifest(tmp_path, manifest_path, verify=False)
    verify.assert_not_called()


def test_main(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import sys

    manifest = tmp_path / "vendor/manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"bundles": {}}), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["sync", "--no-legacy", "--no-verify", "--manifest", str(manifest)],
    )
    with patch.object(sync_mod, "sync_from_manifest") as sync:
        main()
    sync.assert_called_once_with(
        tmp_path,
        manifest,
        prefer_legacy=False,
        verify=False,
    )
