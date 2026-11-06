"""EV-080 coverage fills for scripts/vendor/sync_iwxxm.py."""

from __future__ import annotations

import json
import shutil
import subprocess
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

from metar_shared.vendor_manifest import compute_tree_sha256


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


def test_fetch_github_tree_checks_out_export_ignore_paths(tmp_path: Path) -> None:
    """GitHub archives drop export-ignore paths; checkout must keep them."""
    dest = tmp_path / "tree"
    commands: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        commands.append(cmd)
        cwd = Path(str(kwargs["cwd"]))
        if cmd[1] == "init":
            (cwd / ".git").mkdir()
        if "checkout" in cmd:
            external = cwd / "externalSchema"
            external.mkdir()
            (external / "a.xsd").write_text("schema", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0)

    with patch.object(sync_mod.subprocess, "run", side_effect=fake_run):
        sync_mod._fetch_github_tree("wmo-im/iwxxm", "a" * 40, dest)

    joined = " ".join(" ".join(cmd) for cmd in commands)
    assert "curl" not in joined
    assert "git fetch --depth 1 origin " + ("a" * 40) in joined
    assert "https://github.com/wmo-im/iwxxm.git" in joined
    assert (dest / "externalSchema" / "a.xsd").read_text(encoding="utf-8") == "schema"
    assert not (dest / ".git").exists()


def test_sync_preserves_nested_profile_line(tmp_path: Path) -> None:
    """Parent replace must keep iwxxm/3.0.0 and still match tree_sha256."""
    parent = tmp_path / "vendor/schemas/iwxxm"
    nested = parent / "3.0.0"
    nested.mkdir(parents=True)
    (nested / "core.xsd").write_text("core", encoding="utf-8")
    extra = parent / "extra"
    extra.mkdir()
    (extra / "keep.txt").write_text("keep", encoding="utf-8")

    def fake_fetch(_repo: str, _sha: str, destination: Path) -> None:
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        (destination / "IWXXM").mkdir()
        (destination / "IWXXM" / "iwxxm.xsd").write_text("pin", encoding="utf-8")
        # Fetch also writes the nested path; the pinned overlay must win.
        (destination / "3.0.0").mkdir()
        (destination / "3.0.0" / "upstream.txt").write_text("nope", encoding="utf-8")

    expected = tmp_path / "expected"
    (expected / "IWXXM").mkdir(parents=True)
    (expected / "IWXXM" / "iwxxm.xsd").write_text("pin", encoding="utf-8")
    (expected / "3.0.0").mkdir()
    (expected / "3.0.0" / "core.xsd").write_text("core", encoding="utf-8")
    (expected / "extra").mkdir()
    (expected / "extra" / "keep.txt").write_text("keep", encoding="utf-8")
    pinned = compute_tree_sha256(expected)

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "bundles": {
                    "iwxxm": {
                        "local_path": "vendor/schemas/iwxxm",
                        "upstream_repo": "wmo-im/iwxxm",
                        "commit_sha": "c" * 40,
                        "tree_sha256": pinned,
                    },
                    "noise": "skip-me",
                    "badpath": {"local_path": 1},
                    "sibling": {"local_path": "vendor/schemas/iwxxm-codelists"},
                    "missing-nested": {
                        "local_path": "vendor/schemas/iwxxm/not-vendored"
                    },
                    "iwxxm-3.0.0": {"local_path": "vendor/schemas/iwxxm/3.0.0"},
                    "extra-line": {"local_path": "vendor/schemas/iwxxm/extra"},
                }
            }
        ),
        encoding="utf-8",
    )

    with (
        patch.object(sync_mod, "GITHUB_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(sync_mod, "_fetch_github_tree", side_effect=fake_fetch),
        patch.object(
            sync_mod,
            "verify_manifest_integrity",
            return_value=_Integrity(ok=True, errors=[]),
        ),
    ):
        sync_from_manifest(tmp_path, manifest_path, prefer_legacy=False, verify=True)

    assert (parent / "IWXXM" / "iwxxm.xsd").read_text(encoding="utf-8") == "pin"
    assert (nested / "core.xsd").read_text(encoding="utf-8") == "core"
    assert not (nested / "upstream.txt").exists()
    assert (extra / "keep.txt").read_text(encoding="utf-8") == "keep"


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
