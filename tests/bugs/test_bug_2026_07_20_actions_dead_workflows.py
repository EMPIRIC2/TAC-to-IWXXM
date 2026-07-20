"""BUG-2026-07-20 — drop always-red Actions + fix Vendor Sync checksum order.

P0+P1: remove dead smoke/legacy workflows; disable E2E cron / Performance
Benchmarks (legacy ``backend/``).

Vendor Sync: pin updates must clear stale ``tree_sha256`` and the workflow
must sync with ``--no-verify`` before ``--refresh-tree-hashes``.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
CHECK_UPSTREAM = ROOT / "scripts" / "vendor" / "check_upstream.py"
SYNC_IWXXM = ROOT / "scripts" / "vendor" / "sync_iwxxm.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_bug_2026_07_20_dead_workflows_removed() -> None:
    assert not (WORKFLOWS / "smoke-tests-deploy.yml").exists()
    assert not (WORKFLOWS / "test-coverage-95.yml").exists()


def test_bug_2026_07_20_e2e_no_schedule_or_legacy_benchmarks() -> None:
    path = WORKFLOWS / "e2e-tests.yml"
    assert path.is_file()
    raw = path.read_text(encoding="utf-8")
    # PyYAML may parse the key `on` as boolean True
    doc = yaml.safe_load(raw)
    assert isinstance(doc, dict)

    triggers = doc.get("on")
    if triggers is None:
        triggers = doc.get(True)
    assert isinstance(triggers, dict), "e2e-tests.yml must have an `on:` trigger map"
    assert "schedule" not in triggers, "E2E cron disabled until monorepo rewrite"

    jobs = doc.get("jobs") or {}
    assert "performance-benchmarks" not in jobs
    assert "cd backend" not in raw
    assert "\n    name: Performance Benchmarks\n" not in raw


def test_bug_2026_07_20_vendor_sync_workflow_verifies_after_hash_refresh() -> None:
    raw = (WORKFLOWS / "vendor-sync.yml").read_text(encoding="utf-8")
    sync_idx = raw.index("sync_iwxxm.py")
    refresh_idx = raw.index("--refresh-tree-hashes")
    assert sync_idx < refresh_idx
    assert "--no-verify" in raw[sync_idx:refresh_idx]


def test_bug_2026_07_20_pin_update_clears_stale_tree_sha256(tmp_path: Path) -> None:
    """Repro: updating commit_sha while keeping old tree_sha256 broke weekly sync."""
    check = _load_module(CHECK_UPSTREAM, "check_upstream_bug_2026_07_20")
    manifest_path = tmp_path / "manifest.json"
    stale_hash = "a" * 64
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "bundles": {
                    "iwxxm": {
                        "upstream_repo": "wmo-im/iwxxm",
                        "tag": "v2025-2",
                        "commit_sha": "0" * 40,
                        "local_path": "vendor/schemas/iwxxm",
                        "tree_sha256": stale_hash,
                    }
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    new_sha = "1" * 40
    with (
        patch.object(check, "latest_release_tag", return_value=("v2025-2", new_sha)),
        patch.object(check, "VENDOR_BUNDLE_NAMES", ("iwxxm",)),
    ):
        changed = check.check_upstream(manifest_path, update=True)

    assert changed is True
    updated = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry = updated["bundles"]["iwxxm"]
    assert entry["commit_sha"] == new_sha
    assert "tree_sha256" not in entry


def test_bug_2026_07_20_sync_rejects_stale_hash_without_no_verify(
    tmp_path: Path,
) -> None:
    """Document the failure mode sync_iwxxm had before workflow --no-verify."""
    sync = _load_module(SYNC_IWXXM, "sync_iwxxm_bug_2026_07_20")
    repo = tmp_path / "repo"
    fixture = tmp_path / "fixture_tree"
    fixture.mkdir()
    (fixture / "dummy.txt").write_text("content", encoding="utf-8")

    from metar_shared.vendor_manifest import compute_tree_sha256

    actual = compute_tree_sha256(fixture)
    stale = "b" * 64
    assert actual != stale

    for name in (
        "iwxxm",
        "iwxxm-codelists",
        "iwxxm-modelling",
        "iwxxm-translation",
        "iwxxm-us",
    ):
        shutil.copytree(fixture, repo / "vendor" / "schemas" / name)

    good = compute_tree_sha256(fixture)
    manifest_path = repo / "vendor" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "bundles": {
                    "iwxxm": {
                        "upstream_repo": "wmo-im/iwxxm",
                        "tag": "v2025-2",
                        "commit_sha": "c" * 40,
                        "local_path": "vendor/schemas/iwxxm",
                        "tree_sha256": stale,
                    },
                    "iwxxm-codelists": {
                        "upstream_repo": "wmo-im/iwxxm-codelists",
                        "tag": "49-2",
                        "commit_sha": "d" * 40,
                        "local_path": "vendor/schemas/iwxxm-codelists",
                        "tree_sha256": good,
                    },
                    "iwxxm-modelling": {
                        "upstream_repo": "wmo-im/iwxxm-modelling",
                        "tag": "v2025-2",
                        "commit_sha": "e" * 40,
                        "local_path": "vendor/schemas/iwxxm-modelling",
                        "tree_sha256": good,
                    },
                    "iwxxm-translation": {
                        "upstream_repo": "wmo-im/iwxxm-translation",
                        "tag": "master",
                        "commit_sha": "f" * 40,
                        "local_path": "vendor/schemas/iwxxm-translation",
                        "tree_sha256": good,
                    },
                    "iwxxm-us": {
                        "source_url": "https://example.invalid/iwxxm-us.tgz",
                        "tag": "3.0",
                        "local_path": "vendor/schemas/iwxxm-us",
                        "tree_sha256": good,
                        "archive_sha256": "0" * 64,
                    },
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    def _fake_fetch(_upstream: str, _commit_sha: str, destination: Path) -> None:
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(fixture, destination)

    with (
        patch.object(sync, "_fetch_github_tree", side_effect=_fake_fetch),
        patch.object(sync, "GITHUB_BUNDLE_NAMES", ("iwxxm",)),
    ):
        try:
            sync.sync_from_manifest(
                repo,
                manifest_path,
                prefer_legacy=False,
                verify=True,
            )
            raised = False
        except ValueError as exc:
            raised = True
            assert "post-sync checksum mismatch" in str(exc)

    assert raised, "stale tree_sha256 must fail sync when verify=True"

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["bundles"]["iwxxm"].pop("tree_sha256", None)
    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    with (
        patch.object(sync, "_fetch_github_tree", side_effect=_fake_fetch),
        patch.object(sync, "GITHUB_BUNDLE_NAMES", ("iwxxm",)),
    ):
        sync.sync_from_manifest(
            repo,
            manifest_path,
            prefer_legacy=False,
            verify=False,
        )
