"""Optional thin CLI for ``iwxxm-validate`` (E10-39 / T3.9)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from iwxxm_validate.codec import json_encoder
from iwxxm_validate.validate_iwxxm import validate_iwxxm


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iwxxm-validate",
        description="Validate IWXXM XML (XSD + Schematron via validate_iwxxm SDK).",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to an IWXXM XML file",
    )
    parser.add_argument(
        "--version",
        dest="iwxxm_version",
        default="2023-1",
        help="IWXXM release line (default: 2023-1)",
    )
    parser.add_argument(
        "--profile",
        default="annex3",
        choices=("annex3", "iwxxm_us", "ca_eccc"),
        help="Schema profile (default: annex3)",
    )
    parser.add_argument(
        "--product",
        default=None,
        help="API product for Canadian extension XSD when --extensions includes IWXXM_CA",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=[],
        help="National extension tokens (e.g. IWXXM_CA enables full ca_eccc stack)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit ValidationReport as JSON on stdout",
    )
    return parser


def _cli_validate_product(profile: str, extensions: Sequence[str], product: str | None) -> str | None:
    if profile != "ca_eccc":
        return None
    normalized = {token.strip().upper().replace("-", "_") for token in extensions if token.strip()}
    if "IWXXM_CA" in normalized:
        return (product or "METAR").upper()
    return None


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run ``iwxxm-validate`` CLI.

    Parameters
    ----------
    argv :
        Argument vector (defaults to ``sys.argv[1:]``).

    Returns
    -------
    int
        ``0`` when ``report.ok``; ``1`` on validation errors or I/O failure.
    """
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    path: Path = args.path
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 1

    report = validate_iwxxm(
        text,
        iwxxm_version=args.iwxxm_version,
        profile=args.profile,
        product=_cli_validate_product(args.profile, args.extensions, args.product),
    )
    if args.json:
        sys.stdout.write(json_encoder.encode(report).decode("utf-8"))
        sys.stdout.write("\n")
    else:
        status = "ok" if report.ok else "fail"
        print(f"{status} version={report.iwxxm_version} profile={report.profile} issues={len(report.issues)}")
        for issue in report.issues:
            loc = f" @{issue.location}" if issue.location else ""
            print(f"  {issue.severity}:{issue.code}{loc} {issue.message}")

    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
