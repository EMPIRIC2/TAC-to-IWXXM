#!/usr/bin/env python3
"""Sync the E10-34 runtime schema subset into ``iwxxm_validate/schemas``.

Copies pinned files from monorepo ``vendor/schemas/*`` into the package tree so
hatch/maturin wheels can ship XSD + Schematron + catalogs without modelling /
translation bulk (E10-34 / E10-6).

Usage
-----
From repo root::

    make sync-iwxxm-validate-schemas
    # or:
    python packages/iwxxm-validate/scripts/sync_runtime_schemas.py
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
DEST_ROOT = PACKAGE_ROOT / "src" / "iwxxm_validate" / "schemas"
MANIFEST_PATH = DEST_ROOT / "MANIFEST.json"
VENDOR = REPO_ROOT / "vendor" / "schemas"

# Directory / file name fragments never copied into the wheel subset.
_SKIP_DIR_NAMES = frozenset(
    {
        "html",
        "examples",
        "XMI",
        "documentation",
        ".git",
        "__pycache__",
    }
)


def _load_manifest() -> dict:
    """Return the committed subset policy from ``MANIFEST.json``."""
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _should_skip(path: Path, *, relative_to: Path) -> bool:
    """Return True when ``path`` is under an excluded documentation/modelling tree."""
    try:
        parts = path.relative_to(relative_to).parts
    except ValueError:
        parts = path.parts
    return any(part in _SKIP_DIR_NAMES for part in parts)


def _copy_tree(src: Path, dest: Path) -> int:
    """
    Copy files from ``src`` to ``dest``, skipping excluded directory names.

    Returns
    -------
    int
        Number of files copied.
    """
    if not src.is_dir():
        raise FileNotFoundError(f"vendor source missing: {src}")
    count = 0
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        if _should_skip(path, relative_to=src):
            continue
        rel = path.relative_to(src)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        count += 1
    return count


def _copy_version_runtime(version: str) -> int:
    """Copy ``*.xsd`` and ``rule/**`` for one IWXXM release line."""
    src_iwxxm = VENDOR / "iwxxm" / version / "IWXXM"
    if not src_iwxxm.is_dir():
        raise FileNotFoundError(f"IWXXM version tree missing: {src_iwxxm}")
    dest_iwxxm = DEST_ROOT / "iwxxm" / version / "IWXXM"
    if dest_iwxxm.exists():
        shutil.rmtree(dest_iwxxm)
    dest_iwxxm.mkdir(parents=True)

    count = 0
    for xsd in sorted(src_iwxxm.glob("*.xsd")):
        shutil.copy2(xsd, dest_iwxxm / xsd.name)
        count += 1

    rule_src = src_iwxxm / "rule"
    if not rule_src.is_dir():
        raise FileNotFoundError(f"Schematron rule dir missing: {rule_src}")
    count += _copy_tree(rule_src, dest_iwxxm / "rule")
    return count


def sync(*, clean: bool = True) -> dict:
    """
    Materialize the runtime schema subset under ``iwxxm_validate/schemas``.

    Parameters
    ----------
    clean :
        When True, remove previous ``iwxxm`` / ``iwxxm-us`` trees before copy
        (keeps ``MANIFEST.json``).

    Returns
    -------
    dict
        Sync summary (versions, file counts, byte size).
    """
    if not VENDOR.is_dir():
        raise FileNotFoundError(f"vendor schemas root missing: {VENDOR}")

    policy = _load_manifest()
    versions: list[str] = list(policy["iwxxm_versions"])

    if clean:
        for name in ("iwxxm", "iwxxm-us"):
            target = DEST_ROOT / name
            if target.exists():
                shutil.rmtree(target)

    DEST_ROOT.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    for version in versions:
        counts[f"iwxxm/{version}"] = _copy_version_runtime(version)

    ext_src = VENDOR / "iwxxm" / "externalSchema"
    counts["iwxxm/externalSchema"] = _copy_tree(ext_src, DEST_ROOT / "iwxxm" / "externalSchema")

    us_src = VENDOR / "iwxxm-us"
    counts["iwxxm-us"] = _copy_tree(us_src, DEST_ROOT / "iwxxm-us")

    total_files = sum(counts.values())
    total_bytes = sum(p.stat().st_size for p in DEST_ROOT.rglob("*") if p.is_file() and p.name != "MANIFEST.json")

    summary = {
        "destination": str(DEST_ROOT.relative_to(REPO_ROOT)),
        "iwxxm_versions": versions,
        "file_counts": counts,
        "total_files": total_files,
        "total_bytes": total_bytes,
        "excluded": policy.get("exclude", []),
    }

    # Sync stamp is generated (gitignored); committed MANIFEST.json stays policy-only.
    stamp_path = DEST_ROOT / "LAST_SYNC.json"
    stamp_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    """CLI entry — sync schemas and print a one-line summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not wipe prior iwxxm/iwxxm-us trees before copying",
    )
    args = parser.parse_args(argv)
    try:
        summary = sync(clean=not args.no_clean)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    mb = summary["total_bytes"] / (1024 * 1024)
    print(
        f"synced {summary['total_files']} files ({mb:.1f} MiB) → {summary['destination']} "
        f"(versions={','.join(summary['iwxxm_versions'])})"
    )
    for key, count in summary["file_counts"].items():
        print(f"  {key}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
