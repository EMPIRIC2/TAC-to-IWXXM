#!/usr/bin/env python3
"""Fetch official WMO IWXXM XSD + Schematron pins into the schema cache.

[Corpus: fr] FR-077  [Corpus: nfr] NFR-016  [Corpus: decisions] D-019

Acquisition SoT is ``config/schemas/iwxxm-official-pins.json``. Vendored trees
under ``vendor/schemas/`` are optional materialization only — not SoT.

Usage
-----
From repo root::

    make fetch-iwxxm-schemas
    uv run python scripts/schemas/fetch_official_iwxxm_pins.py --write-hashes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = REPO_ROOT / "config" / "schemas" / "iwxxm-official-pins.json"
_SKIP_DIR_NAMES = frozenset(
    {"html", "examples", "XMI", "documentation", ".git", "__pycache__"}
)


def load_catalog(path: Path) -> dict[str, Any]:
    """Load the official pin catalog JSON object."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = "pin catalog root must be a JSON object"
        raise ValueError(msg)
    return data


def default_cache_root(catalog: dict[str, Any]) -> Path:
    """Return schema cache root from env or catalog default."""
    env = os.environ.get("IWXXM_SCHEMA_CACHE")
    if env:
        return Path(env).expanduser().resolve()
    rel = catalog.get("default_cache_rel", ".cache/iwxxm-schemas")
    return (REPO_ROOT / str(rel)).resolve()


def compute_runtime_subset_sha256(pin_root: Path) -> str:
    """
    Deterministic SHA-256 over ``IWXXM/*.xsd`` and ``IWXXM/rule/**`` files.

    Parameters
    ----------
    pin_root :
        Cache directory for one pin (contains ``IWXXM/``).
    """
    iwxxm = pin_root / "IWXXM"
    if not iwxxm.is_dir():
        msg = f"IWXXM runtime tree missing under {pin_root}"
        raise FileNotFoundError(msg)

    files: list[Path] = sorted(iwxxm.glob("*.xsd"))
    rule = iwxxm / "rule"
    if rule.is_dir():
        files.extend(sorted(path for path in rule.rglob("*") if path.is_file()))
    if not files:
        msg = f"no runtime XSD/SCH files under {iwxxm}"
        raise FileNotFoundError(msg)

    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(pin_root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _should_skip(path: Path, *, relative_to: Path) -> bool:
    try:
        parts = path.relative_to(relative_to).parts
    except ValueError:
        parts = path.parts
    return any(part in _SKIP_DIR_NAMES for part in parts)


def _copy_tree(src: Path, dest: Path) -> int:
    """Copy files from ``src`` to ``dest``, skipping excluded directory names."""
    if not src.is_dir():
        raise FileNotFoundError(f"source missing: {src}")
    count = 0
    for path in src.rglob("*"):
        if not path.is_file() or _should_skip(path, relative_to=src):
            continue
        rel = path.relative_to(src)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        count += 1
    return count


def _fetch_github_commit(repo: str, commit_sha: str, destination: Path) -> None:
    """Shallow-checkout ``commit_sha`` from GitHub into ``destination``."""
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
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


def _materialize_pin(
    *,
    repo: str,
    commit_sha: str,
    cache_dirname: str,
    cache_root: Path,
    checkout_root: Path,
) -> Path:
    """Fetch one pin and copy the runtime IWXXM subset into the cache."""
    work = checkout_root / cache_dirname
    _fetch_github_commit(repo, commit_sha, work)
    src_iwxxm = work / "IWXXM"
    if not src_iwxxm.is_dir():
        msg = f"IWXXM/ missing in checkout for {cache_dirname} @ {commit_sha}"
        raise FileNotFoundError(msg)

    pin_dest = cache_root / cache_dirname
    if pin_dest.exists():
        shutil.rmtree(pin_dest)
    dest_iwxxm = pin_dest / "IWXXM"
    dest_iwxxm.mkdir(parents=True)

    for xsd in sorted(src_iwxxm.glob("*.xsd")):
        shutil.copy2(xsd, dest_iwxxm / xsd.name)
    rule_src = src_iwxxm / "rule"
    if not rule_src.is_dir():
        msg = f"Schematron rule/ missing for {cache_dirname}"
        raise FileNotFoundError(msg)
    _copy_tree(rule_src, dest_iwxxm / "rule")

    ext_src = work / "externalSchema"
    if ext_src.is_dir():
        ext_dest = cache_root / "externalSchema"
        if ext_dest.exists():
            shutil.rmtree(ext_dest)
        _copy_tree(ext_src, ext_dest)

    return pin_dest


def fetch_pins(
    *,
    catalog_path: Path,
    cache_root: Path | None = None,
    pins: list[str] | None = None,
    write_hashes: bool = False,
    verify: bool = True,
) -> dict[str, Any]:
    """
    Fetch selected official pins into the schema cache.

    Returns
    -------
    dict
        Summary with per-pin paths and hashes.
    """
    catalog = load_catalog(catalog_path)
    repo = str(catalog["upstream_repo"])
    pin_table = catalog["pins"]
    if not isinstance(pin_table, dict):
        msg = "catalog.pins must be an object"
        raise ValueError(msg)

    selected = list(pins) if pins else list(pin_table.keys())
    root = cache_root or default_cache_root(catalog)
    root.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {"cache_root": str(root), "pins": {}}
    with tempfile.TemporaryDirectory(prefix="iwxxm-official-fetch-") as tmp:
        checkout_root = Path(tmp)
        for pin_id in selected:
            entry = pin_table.get(pin_id)
            if not isinstance(entry, dict):
                msg = f"unknown official pin: {pin_id!r}"
                raise KeyError(msg)
            commit = str(entry["commit_sha"])
            dirname = str(entry.get("cache_dirname", pin_id))
            pin_dest = _materialize_pin(
                repo=repo,
                commit_sha=commit,
                cache_dirname=dirname,
                cache_root=root,
                checkout_root=checkout_root,
            )
            actual = compute_runtime_subset_sha256(pin_dest)
            expected = str(entry.get("runtime_subset_sha256") or "").strip()
            if verify and expected and actual.lower() != expected.lower():
                msg = (
                    f"hash mismatch for pin {pin_id}: expected {expected}, got {actual}"
                )
                raise ValueError(msg)
            if write_hashes:
                entry["runtime_subset_sha256"] = actual
            results["pins"][pin_id] = {
                "path": str(pin_dest),
                "runtime_subset_sha256": actual,
                "tag": entry.get("tag"),
                "commit_sha": commit,
            }

    if write_hashes:
        catalog_path.write_text(
            json.dumps(catalog, indent=2) + "\n",
            encoding="utf-8",
        )

    stamp = root / "LAST_FETCH.json"
    stamp.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results


def verify_existing_pins(
    *,
    catalog_path: Path,
    pins: list[str] | None = None,
) -> dict[str, Any]:
    """
    Fail-closed hash check against resolvable pin trees (no network).

    Uses ``iwxxm_validate.paths.version_dir`` so packaged, cache, and vendor
    materialization all count.
    """
    # Import lazily so the script still runs before the package is installed.
    from iwxxm_validate.paths import clear_path_caches, version_dir

    catalog = load_catalog(catalog_path)
    pin_table = catalog["pins"]
    if not isinstance(pin_table, dict):
        msg = "catalog.pins must be an object"
        raise ValueError(msg)
    selected = list(pins) if pins else list(pin_table.keys())
    clear_path_caches()
    results: dict[str, Any] = {"pins": {}}
    for pin_id in selected:
        entry = pin_table.get(pin_id)
        if not isinstance(entry, dict):
            msg = f"unknown official pin: {pin_id!r}"
            raise KeyError(msg)
        try:
            pin_root = version_dir(pin_id)
        except FileNotFoundError as exc:
            msg = (
                f"official pin cache missing for {pin_id!r}: {exc}. "
                "Run `make fetch-iwxxm-schemas`."
            )
            raise FileNotFoundError(msg) from exc
        actual = compute_runtime_subset_sha256(pin_root)
        expected = str(entry.get("runtime_subset_sha256") or "").strip()
        if expected and actual.lower() != expected.lower():
            msg = f"hash mismatch for pin {pin_id}: expected {expected}, got {actual}"
            raise ValueError(msg)
        if not expected:
            msg = f"catalog missing runtime_subset_sha256 for pin {pin_id}"
            raise ValueError(msg)
        results["pins"][pin_id] = {
            "path": str(pin_root),
            "runtime_subset_sha256": actual,
        }
    return results


def main(argv: list[str] | None = None) -> int:
    """CLI entry for official pin fetch."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG,
        help="Path to iwxxm-official-pins.json",
    )
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=None,
        help="Override IWXXM_SCHEMA_CACHE / catalog default",
    )
    parser.add_argument(
        "--pin",
        action="append",
        dest="pins",
        default=None,
        help="Fetch only this pin id (repeatable)",
    )
    parser.add_argument(
        "--write-hashes",
        action="store_true",
        help="Write computed runtime_subset_sha256 back into the catalog",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip hash verify when catalog already has hashes",
    )
    parser.add_argument(
        "--verify-existing",
        action="store_true",
        help="Hash-check resolvable pin trees only (no network fetch)",
    )
    args = parser.parse_args(argv)
    try:
        if args.verify_existing:
            summary = verify_existing_pins(
                catalog_path=args.catalog,
                pins=args.pins,
            )
            print(f"verified {len(summary['pins'])} official pin(s)")
            for pin_id, info in summary["pins"].items():
                print(f"  {pin_id}: ok ({info['path']})")
            return 0
        summary = fetch_pins(
            catalog_path=args.catalog,
            cache_root=args.cache_root.resolve() if args.cache_root else None,
            pins=args.pins,
            write_hashes=args.write_hashes,
            verify=not args.no_verify,
        )
    except (
        FileNotFoundError,
        KeyError,
        ValueError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"fetched {len(summary['pins'])} pin(s) -> {summary['cache_root']}")
    for pin_id, info in summary["pins"].items():
        print(f"  {pin_id}: {info['runtime_subset_sha256'][:12]}… ({info['tag']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
