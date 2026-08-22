"""BUG-2026-08-22 — Mutation pnpm conflict + Vendor Sync same-tag commit drift.

Mutation workflow: ``pnpm/action-setup`` with ``version: 9`` conflicts with
``packageManager: pnpm@9.15.4`` in package.json.

Vendor Sync: ``check_upstream --update`` moved pins when GitHub's latest release
tag matched but commit tip moved (wmo-im v2025-2 republish), breaking versioned
``2025-2/IWXXM/`` paths required by TC-M002.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
MUTATION_WORKFLOW = ROOT / ".github" / "workflows" / "mutation.yml"
CHECK_UPSTREAM = ROOT / "scripts" / "vendor" / "check_upstream.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_bug_2026_08_22_mutation_workflow_no_explicit_pnpm_version() -> None:
    raw = MUTATION_WORKFLOW.read_text(encoding="utf-8")
    assert "pnpm/action-setup@v4" in raw
    assert "version: 9" not in raw
    assert "actions/setup-node@v5" in raw


def test_bug_2026_08_22_same_release_tag_keeps_intentional_commit_pin(
    tmp_path: Path,
) -> None:
    check = _load_module(CHECK_UPSTREAM, "check_upstream_bug_2026_08_22")
    manifest_path = tmp_path / "manifest.json"
    pinned_sha = "0" * 40
    tip_sha = "1" * 40
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "bundles": {
                    "iwxxm": {
                        "upstream_repo": "wmo-im/iwxxm",
                        "tag": "v2025-2",
                        "commit_sha": pinned_sha,
                        "local_path": "vendor/schemas/iwxxm",
                        "tree_sha256": "a" * 64,
                    }
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    with (
        patch.object(check, "latest_release_tag", return_value=("v2025-2", tip_sha)),
        patch.object(check, "VENDOR_BUNDLE_NAMES", ("iwxxm",)),
    ):
        changed = check.check_upstream(manifest_path, update=True)

    assert changed is False
    entry = json.loads(manifest_path.read_text(encoding="utf-8"))["bundles"]["iwxxm"]
    assert entry["commit_sha"] == pinned_sha
    assert entry["tree_sha256"] == "a" * 64
