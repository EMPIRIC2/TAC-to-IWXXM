#!/usr/bin/env python3
"""
Summarize XSD / Schematron / example-stem deltas between two IWXXM vendor trees.

Use on sync PRs to speed RELEASE_LINE_ADOPTABILITY adopt triage (#852 / TC-EV038-005).
Never hand-edits ``vendor/schemas/*`` — read-only compare of pinned trees.

Examples::

  make tip-diff-iwxxm
  uv run python scripts/vendor/tip_diff_iwxxm.py --from 2023-1 --to 2025-2
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_IWXXM_ROOT = _REPO_ROOT / "vendor" / "schemas" / "iwxxm"


def _iwxxm_product_dir(version: str, root: Path) -> Path:
    """Resolve ``vendor/schemas/iwxxm/{version}/IWXXM`` (or flat layout)."""
    versioned = root / version / "IWXXM"
    if versioned.is_dir():
        return versioned
    flat = root / "IWXXM"
    if flat.is_dir() and version in ("", "flat"):
        return flat
    raise SystemExit(f"No IWXXM tree for version {version!r} under {root}")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _collect(tree: Path) -> dict[str, dict[str, str]]:
    """
    Map relative path → sha256, grouped by kind: xsd | sch | example | other.

    Example stems use ``examples/<stem>`` (suffix-stripped) as the logical key for
    add/remove reporting; content hash still uses the full relative path.
    """
    by_kind: dict[str, dict[str, str]] = defaultdict(dict)
    if not tree.is_dir():
        return by_kind
    for path in sorted(tree.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(tree).as_posix()
        digest = _file_sha256(path)
        lower = rel.lower()
        if lower.endswith(".xsd"):
            kind = "xsd"
            key = rel
        elif "/rule/" in f"/{lower}" and (lower.endswith(".sch") or lower.endswith(".rdf")):
            kind = "sch"
            key = rel
        elif lower.startswith("examples/") or "/examples/" in f"/{lower}":
            kind = "example"
            # stem without extension for triage lists
            key = Path(rel).with_suffix("").as_posix()
            # keep first-seen hash if multiple suffixes share a stem
            if key in by_kind[kind]:
                continue
        else:
            kind = "other"
            key = rel
        by_kind[kind][key] = digest
    return by_kind


def _diff_maps(
    old: dict[str, str], new: dict[str, str]
) -> tuple[list[str], list[str], list[str]]:
    old_keys, new_keys = set(old), set(new)
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = sorted(k for k in old_keys & new_keys if old[k] != new[k])
    return added, removed, changed


def summarize(from_ver: str, to_ver: str, *, root: Path) -> str:
    """Build a human-readable tip-diff report."""
    old_tree = _iwxxm_product_dir(from_ver, root)
    new_tree = _iwxxm_product_dir(to_ver, root)
    old_maps = _collect(old_tree)
    new_maps = _collect(new_tree)

    def _rel(path: Path) -> str:
        resolved = path.resolve()
        try:
            return resolved.relative_to(_REPO_ROOT.resolve()).as_posix()
        except ValueError:
            return str(path)

    lines = [
        f"# IWXXM tip-diff: {from_ver} → {to_ver}",
        "",
        f"- old: `{_rel(old_tree)}`",
        f"- new: `{_rel(new_tree)}`",
        "",
        "Read-only vendor compare — do **not** hand-edit under `vendor/schemas/*`.",
        "",
    ]
    for kind, title in (
        ("xsd", "XSD"),
        ("sch", "Schematron / RDF (rule/)"),
        ("example", "Example stems"),
    ):
        added, removed, changed = _diff_maps(old_maps.get(kind, {}), new_maps.get(kind, {}))
        lines.append(f"## {title}")
        lines.append(f"- added ({len(added)}):")
        lines.extend(f"  - `{item}`" for item in added[:80] or ["*(none)*"])
        if len(added) > 80:
            lines.append(f"  - … +{len(added) - 80} more")
        lines.append(f"- removed ({len(removed)}):")
        lines.extend(f"  - `{item}`" for item in removed[:80] or ["*(none)*"])
        if len(removed) > 80:
            lines.append(f"  - … +{len(removed) - 80} more")
        lines.append(f"- content-changed ({len(changed)}):")
        lines.extend(f"  - `{item}`" for item in changed[:80] or ["*(none)*"])
        if len(changed) > 80:
            lines.append(f"  - … +{len(changed) - 80} more")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    """CLI entry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="from_ver", default="2023-1", help="Previous pin / line")
    parser.add_argument("--to", dest="to_ver", default="2025-2", help="New pin / line")
    parser.add_argument(
        "--root",
        type=Path,
        default=_DEFAULT_IWXXM_ROOT,
        help="Vendor iwxxm root (default: vendor/schemas/iwxxm)",
    )
    args = parser.parse_args(argv)
    sys.stdout.write(summarize(args.from_ver, args.to_ver, root=args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
