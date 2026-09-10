#!/usr/bin/env python3
"""Bump F12-F14 package versions to CalVer (YYYY.MM.DD[.N][.devN]).

Usage
-----
  python scripts/pypi/bump_calver.py --package tac-validate
  python scripts/pypi/bump_calver.py --all --dev 1
  python scripts/pypi/bump_calver.py --all --date 2026.09.10 --same-day-n 1

Traces to ADR-043 / EV-1150. Does not publish.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PACKAGES: dict[str, dict[str, Path]] = {
    "tac-validate": {
        "pyproject": REPO_ROOT / "packages" / "tac-validate" / "pyproject.toml",
        "init": REPO_ROOT
        / "packages"
        / "tac-validate"
        / "src"
        / "tac_validate"
        / "__init__.py",
    },
    "iwxxm-validate": {
        "pyproject": REPO_ROOT / "packages" / "iwxxm-validate" / "pyproject.toml",
        "init": REPO_ROOT
        / "packages"
        / "iwxxm-validate"
        / "src"
        / "iwxxm_validate"
        / "__init__.py",
        "cargo": REPO_ROOT / "packages" / "iwxxm-validate" / "rust" / "Cargo.toml",
    },
    "tac2iwxxm": {
        "pyproject": REPO_ROOT / "packages" / "tac2iwxxm" / "pyproject.toml",
        "init": REPO_ROOT
        / "packages"
        / "tac2iwxxm"
        / "src"
        / "tac2iwxxm"
        / "__init__.py",
        "cargo": REPO_ROOT / "packages" / "tac2iwxxm" / "rust" / "Cargo.toml",
    },
}

VERSION_RE = re.compile(
    r'^version\s*=\s*["\']([^"\']+)["\']',
    re.MULTILINE,
)
DUNDER_RE = re.compile(
    r'^__version__\s*=\s*["\']([^"\']+)["\']',
    re.MULTILINE,
)


def calver_string(
    *,
    day: date | None = None,
    same_day_n: int | None = None,
    dev: int | None = None,
) -> str:
    """
    Build a PEP 440 CalVer string.

    Parameters
    ----------
    day :
        Calendar day (default: today UTC-local date).
    same_day_n :
        Optional same-day rebuild suffix ``.N``.
    dev :
        Optional ``.devN`` for nightlies / TestPyPI.

    Returns
    -------
    str
        Version like ``2026.9.10``, ``2026.9.10.1``, or ``2026.9.10.dev7``.
    """
    d = day or date.today()
    base = f"{d.year}.{d.month}.{d.day}"
    if same_day_n is not None and same_day_n > 0:
        base = f"{base}.{same_day_n}"
    if dev is not None and dev > 0:
        base = f"{base}.dev{dev}"
    return base


def _replace_version(text: str, pattern: re.Pattern[str], new: str) -> str:
    if not pattern.search(text):
        raise ValueError(f"version field not found for pattern {pattern.pattern!r}")
    return pattern.sub(lambda m: m.group(0).replace(m.group(1), new), text, count=1)


def set_package_version(package: str, version: str) -> list[Path]:
    """Write ``version`` into known metadata files for ``package``."""
    if package not in PACKAGES:
        raise KeyError(package)
    changed: list[Path] = []
    paths = PACKAGES[package]
    py = paths["pyproject"]
    py.write_text(
        _replace_version(py.read_text(encoding="utf-8"), VERSION_RE, version),
        encoding="utf-8",
    )
    changed.append(py)
    init = paths["init"]
    init.write_text(
        _replace_version(init.read_text(encoding="utf-8"), DUNDER_RE, version),
        encoding="utf-8",
    )
    changed.append(init)
    cargo = paths.get("cargo")
    if cargo is not None and cargo.is_file():
        cargo.write_text(
            _replace_version(cargo.read_text(encoding="utf-8"), VERSION_RE, version),
            encoding="utf-8",
        )
        changed.append(cargo)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package",
        choices=sorted(PACKAGES),
        action="append",
        help="Package to bump (repeatable)",
    )
    parser.add_argument("--all", action="store_true", help="Bump all three packages")
    parser.add_argument(
        "--date",
        help="CalVer date as YYYY.M.D or YYYY.MM.DD (default: today)",
    )
    parser.add_argument(
        "--same-day-n",
        type=int,
        default=0,
        help="Same-day rebuild suffix N (0 = omit)",
    )
    parser.add_argument(
        "--dev",
        type=int,
        default=0,
        help="devN suffix for nightlies (0 = omit)",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print the version string and exit without writing",
    )
    args = parser.parse_args(argv)

    day: date | None = None
    if args.date:
        parts = [int(p) for p in args.date.replace("-", ".").split(".")]
        if len(parts) != 3:
            parser.error("--date must be YYYY.M.D")
        day = date(parts[0], parts[1], parts[2])

    version = calver_string(
        day=day,
        same_day_n=args.same_day_n or None,
        dev=args.dev or None,
    )
    if args.print_only:
        print(version)
        return 0

    packages = list(PACKAGES) if args.all else (args.package or [])
    if not packages:
        parser.error("pass --all or --package")

    for pkg in packages:
        changed = set_package_version(pkg, version)
        print(f"{pkg} -> {version}")
        for path in changed:
            print(f"  wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
