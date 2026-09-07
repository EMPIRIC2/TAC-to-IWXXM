#!/usr/bin/env python3
"""Scaffold a national semantic profile from docs/domain/profiles/_template/.

Copies stub files and prints the remaining hand-edit checklist (registry, convert,
OpenAPI, FE). Does **not** auto-edit profile_registry.py or frontend enums.

[Corpus: domain-profiles] [Corpus: product §F36] [Corpus: tests §TC-EV088]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_TEMPLATE = _REPO / "docs" / "domain" / "profiles" / "_template"
_PROFILES = _REPO / "docs" / "domain" / "profiles"
_MINING = _REPO / "docs" / "domain" / "mining"
_FIXTURES = _REPO / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "profiles"

_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+$")


def _slug(profile_id: str) -> str:
    """Return filesystem slug for mining note filenames."""
    return profile_id.lower().replace("_", "-")


def validate_profile_id(profile_id: str) -> None:
    """
    Validate canonical semantic profile id shape.

    Parameters
    ----------
    profile_id :
        e.g. ``UK_METOFFICE``, ``BR_DECEA``.

    Raises
    ------
    ValueError
        If ``profile_id`` is empty or malformed.
    """
    if not profile_id or not _ID_RE.match(profile_id):
        raise ValueError(
            f"invalid profile id {profile_id!r}; expected e.g. UK_METOFFICE "
            "(SEGMENT_SEGMENT, uppercase A-Z / digits / underscores)"
        )


def planned_paths(profile_id: str) -> dict[str, Path]:
    """
    Map logical artifact names to destination paths.

    Parameters
    ----------
    profile_id :
        Canonical profile id.

    Returns
    -------
    dict[str, Path]
        Destination paths keyed by artifact role.
    """
    slug = _slug(profile_id)
    return {
        "semantic_stub": _PROFILES / "semantic" / f"{profile_id}.md",
        "tac_mining": _MINING / f"{slug}-tac-mining-notes.md",
        "iwxxm_mining": _MINING / f"{slug}-iwxxm-mining-notes.md",
        "fixture_dir": _FIXTURES / profile_id,
        "manifest": _FIXTURES / profile_id / "manifest.json",
        "catalog_snippet": _PROFILES
        / "_scaffold_out"
        / f"{profile_id}-catalog-row.yaml",
    }


def checklist(profile_id: str) -> list[str]:
    """Return post-scaffold hand-edit checklist lines."""
    return [
        f"1. Merge catalog row from docs/domain/profiles/_scaffold_out/{profile_id}-catalog-row.yaml into catalog.yaml",
        f"2. Fill docs/domain/profiles/semantic/{profile_id}.md",
        "3. Fill mining notes under docs/domain/mining/; index mining/README.md",
        f"4. Add TAC fixtures under packages/tac2iwxxm/tests/fixtures/profiles/{profile_id}/",
        "5. Edit packages/tac2iwxxm/src/tac2iwxxm/profile_registry.py (canonical <-> emit maps)",
        "6. Edit packages/tac2iwxxm/src/tac2iwxxm/convert.py product allowlist / emit branch",
        "7. OpenAPI / Form profile enum + regenerate contract if required",
        "8. FE wire types / picker options if operator-visible",
        "9. Tests + docs/test-plan.md TC rows as needed",
        "10. Promote durable URLs → RULE_SOURCE_URLS / COVERAGE_MATRIX",
        "See docs/domain/profiles/NATIONAL_PROFILE_PLAYBOOK.md",
    ]


def _replace_placeholders(text: str, profile_id: str) -> str:
    slug = _slug(profile_id)
    return (
        text.replace("PLACEHOLDER_ID", profile_id)
        .replace("PLACEHOLDER_ORG", f"{profile_id} issuing body (fill)")
        .replace("PLACEHOLDER_SLUG", slug)
        .replace("PLACEHOLDER", profile_id)
    )


def scaffold(
    profile_id: str, *, dry_run: bool = False, force: bool = False
) -> list[str]:
    """
    Copy templates into place for ``profile_id``.

    Parameters
    ----------
    profile_id :
        Canonical semantic profile id.
    dry_run :
        If True, only report planned writes.
    force :
        If True, overwrite existing destination files.

    Returns
    -------
    list[str]
        Human-readable action lines.
    """
    validate_profile_id(profile_id)
    if not _TEMPLATE.is_dir():
        raise FileNotFoundError(f"missing templates dir: {_TEMPLATE}")

    paths = planned_paths(profile_id)
    actions: list[str] = []

    copies: list[tuple[Path, Path]] = [
        (_TEMPLATE / "semantic-profile.md", paths["semantic_stub"]),
        (_TEMPLATE / "tac-mining-notes.md", paths["tac_mining"]),
        (_TEMPLATE / "iwxxm-mining-notes.md", paths["iwxxm_mining"]),
        (_TEMPLATE / "catalog-row.yaml", paths["catalog_snippet"]),
        (_TEMPLATE / "manifest.json.example", paths["manifest"]),
    ]

    for src, dest in copies:
        if not src.is_file():
            raise FileNotFoundError(f"missing template: {src}")
        if dest.exists() and not force:
            actions.append(f"skip (exists): {dest.relative_to(_REPO)}")
            continue
        actions.append(
            f"{'would write' if dry_run else 'write'}: {dest.relative_to(_REPO)}"
        )
        if dry_run:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = _replace_placeholders(src.read_text(encoding="utf-8"), profile_id)
        dest.write_text(text, encoding="utf-8")

    fixture_dir = paths["fixture_dir"]
    metar_valid = fixture_dir / "METAR" / "valid"
    if not dry_run:
        metar_valid.mkdir(parents=True, exist_ok=True)
        placeholder_tac = metar_valid / "example_valid.tac"
        if force or not placeholder_tac.exists():
            placeholder_tac.write_text(
                f"METAR PLACEHOLDER {profile_id} — replace with real TAC\n",
                encoding="utf-8",
            )
            actions.append(f"write: {placeholder_tac.relative_to(_REPO)}")
        else:
            actions.append(f"skip (exists): {placeholder_tac.relative_to(_REPO)}")
    else:
        actions.append(f"would mkdir: {metar_valid.relative_to(_REPO)}")

    return actions


def main(argv: list[str] | None = None) -> int:
    """CLI entry — return process exit code."""
    parser = argparse.ArgumentParser(
        description="Scaffold national semantic profile stubs from _template/"
    )
    parser.add_argument(
        "--id",
        required=True,
        help="Canonical profile id (e.g. UK_METOFFICE)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned writes without creating files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing destination files",
    )
    args = parser.parse_args(argv)

    try:
        actions = scaffold(args.id, dry_run=args.dry_run, force=args.force)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"scaffold profile {args.id}" + (" (dry-run)" if args.dry_run else ""))
    for line in actions:
        print(f"  {line}")
    print("\nHand-edit checklist:")
    for line in checklist(args.id):
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
