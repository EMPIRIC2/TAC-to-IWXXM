"""EV-080 coverage fills for scripts/vendor/check_upstream.py."""
# ruff: noqa: SIM117

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
import scripts.vendor.check_upstream as check_mod
from scripts.vendor.check_upstream import (
    check_upstream,
    latest_release_tag,
    main,
    refresh_tree_hashes,
    resolve_ref_sha,
)


def test_resolve_ref_sha_validates() -> None:
    client = MagicMock()
    client.get.return_value.json.return_value = {"sha": "a" * 40}
    assert resolve_ref_sha(client, "wmo-im/iwxxm", "v1") == "a" * 40
    client.get.return_value.json.return_value = {"sha": "short"}
    with pytest.raises(ValueError, match="could not resolve"):
        resolve_ref_sha(client, "wmo-im/iwxxm", "v1")


def test_latest_release_tag_branches() -> None:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {"tag_name": "v1"}
    client.get.return_value = response
    with patch.object(check_mod, "resolve_ref_sha", return_value="b" * 40):
        assert latest_release_tag(client, "wmo-im/iwxxm") == ("v1", "b" * 40)

    err = httpx.HTTPStatusError(
        "404", request=MagicMock(), response=MagicMock(status_code=404)
    )
    client.get.side_effect = err
    assert latest_release_tag(client, "wmo-im/iwxxm") is None

    err500 = httpx.HTTPStatusError(
        "500", request=MagicMock(), response=MagicMock(status_code=500)
    )
    client.get.side_effect = err500
    with pytest.raises(httpx.HTTPStatusError):
        latest_release_tag(client, "wmo-im/iwxxm")

    client.get.side_effect = None
    response.json.return_value = {"tag_name": "  "}
    assert latest_release_tag(client, "wmo-im/iwxxm") is None


def test_check_upstream_dry_run_and_update(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "bundles": {
                    "iwxxm": {
                        "upstream_repo": "wmo-im/iwxxm",
                        "tag": "old",
                        "commit_sha": "0" * 40,
                    },
                    "skip": "not-a-dict",
                    "no_repo": {},
                }
            }
        ),
        encoding="utf-8",
    )
    with (
        patch.object(check_mod, "VENDOR_BUNDLE_NAMES", ("iwxxm", "skip", "no_repo")),
        patch.object(check_mod.httpx, "Client") as client_cls,
        patch.object(check_mod, "latest_release_tag", return_value=("v2", "1" * 40)),
    ):
        client_cls.return_value.__enter__.return_value = MagicMock()
        changed = check_upstream(manifest_path, update=False)
    assert changed is True
    assert "upstream update available" in capsys.readouterr().out

    manifest_path.write_text(
        json.dumps(
            {
                "bundles": {
                    "iwxxm": {
                        "upstream_repo": "wmo-im/iwxxm",
                        "tag": "v2",
                        "commit_sha": "0" * 40,
                        "tree_sha256": "a" * 64,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    with (
        patch.object(check_mod, "VENDOR_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(check_mod.httpx, "Client") as client_cls,
        patch.object(check_mod, "latest_release_tag", return_value=("v2", "1" * 40)),
    ):
        client_cls.return_value.__enter__.return_value = MagicMock()
        assert check_upstream(manifest_path, update=True) is False
    assert "keeping pin" in capsys.readouterr().out

    with (
        patch.object(check_mod, "VENDOR_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(check_mod.httpx, "Client") as client_cls,
        patch.object(check_mod, "latest_release_tag", return_value=("v3", "2" * 40)),
    ):
        client_cls.return_value.__enter__.return_value = MagicMock()
        assert check_upstream(manifest_path, update=True) is True
    updated = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert updated["bundles"]["iwxxm"]["tag"] == "v3"
    assert "tree_sha256" not in updated["bundles"]["iwxxm"]

    with (
        patch.object(check_mod, "VENDOR_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(check_mod.httpx, "Client") as client_cls,
        patch.object(check_mod, "latest_release_tag", return_value=None),
    ):
        client_cls.return_value.__enter__.return_value = MagicMock()
        assert check_upstream(manifest_path, update=False) is False


def test_check_upstream_matching_pins_unchanged(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    sha = "a" * 40
    manifest_path.write_text(
        json.dumps(
            {
                "bundles": {
                    "iwxxm": {
                        "upstream_repo": "wmo-im/iwxxm",
                        "tag": "v1",
                        "commit_sha": sha,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    with (
        patch.object(check_mod, "VENDOR_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(check_mod.httpx, "Client") as client_cls,
        patch.object(check_mod, "latest_release_tag", return_value=("v1", sha)),
    ):
        client_cls.return_value.__enter__.return_value = MagicMock()
        assert check_upstream(manifest_path, update=False) is False


def test_check_upstream_same_tag_non_string_pin(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "bundles": {
                    "iwxxm": {
                        "upstream_repo": "wmo-im/iwxxm",
                        "tag": "v2",
                        "commit_sha": 123,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    with (
        patch.object(check_mod, "VENDOR_BUNDLE_NAMES", ("iwxxm",)),
        patch.object(check_mod.httpx, "Client") as client_cls,
        patch.object(check_mod, "latest_release_tag", return_value=("v2", "1" * 40)),
    ):
        client_cls.return_value.__enter__.return_value = MagicMock()
        assert check_upstream(manifest_path, update=True) is False


def test_refresh_tree_hashes_skips_bad_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "bundles": {
                    "iwxxm": {"local_path": 123},
                    "other": {"local_path": "vendor/missing"},
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(check_mod, "VENDOR_BUNDLE_NAMES", ("iwxxm", "other"))
    refresh_tree_hashes(tmp_path, manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "tree_sha256" not in data["bundles"]["iwxxm"]
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"bundles": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="bundles must be an object"):
        check_upstream(manifest_path, update=False)


def test_refresh_tree_hashes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = tmp_path / "repo"
    tree = repo_root / "vendor/schemas/iwxxm"
    tree.mkdir(parents=True)
    (tree / "a.xsd").write_text("<x/>", encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps({"bundles": {"iwxxm": {"local_path": "vendor/schemas/iwxxm"}}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(check_mod, "VENDOR_BUNDLE_NAMES", ("iwxxm", "missing"))
    monkeypatch.setattr(check_mod, "compute_tree_sha256", lambda p: "hash-" + p.name)
    refresh_tree_hashes(repo_root, manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["bundles"]["iwxxm"]["tree_sha256"] == "hash-iwxxm"

    manifest_path.write_text(json.dumps({"bundles": "bad"}), encoding="utf-8")
    refresh_tree_hashes(repo_root, manifest_path)  # no-op


def test_main_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest = tmp_path / "vendor/manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"bundles": {}}), encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        sys, "argv", ["check", "--refresh-tree-hashes", "--manifest", str(manifest)]
    )
    with patch.object(check_mod, "refresh_tree_hashes") as refresh:
        main()
    refresh.assert_called_once()

    monkeypatch.setattr(sys, "argv", ["check", "--update", "--manifest", str(manifest)])
    with patch.object(check_mod, "check_upstream", return_value=False):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0
    assert "already match" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["check", "--update"])
    with patch.object(check_mod, "check_upstream", return_value=True):
        with pytest.raises(SystemExit) as exc2:
            main()
    assert exc2.value.code == 0
