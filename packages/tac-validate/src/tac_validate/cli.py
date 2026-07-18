"""Command-line interface for ``tac-validate`` (F12)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from tac_validate.api import lint
from tac_validate.codec import json_encoder
from tac_validate.products import PRODUCTS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tac-validate",
        description="Lint TAC text for F6 products (parse-gate + checklist/template gates).",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to a TAC text file",
    )
    parser.add_argument(
        "--product",
        required=True,
        choices=list(PRODUCTS),
        help="F6 product id",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit LintReport as JSON on stdout",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run ``tac-validate`` CLI.

    Parameters
    ----------
    argv :
        Argument vector (defaults to ``sys.argv[1:]``).

    Returns
    -------
    int
        ``0`` when ``report.ok``; ``1`` on lint errors or I/O failure.
    """
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    path: Path = args.path
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 1

    report = lint(text, product=args.product)
    if args.json:
        sys.stdout.write(json_encoder.encode(report).decode("utf-8"))
        sys.stdout.write("\n")
    else:
        status = "ok" if report.ok else "fail"
        print(f"{status} product={report.product} issues={len(report.issues)}")
        for issue in report.issues:
            span = ""
            if issue.start is not None and issue.end is not None:
                span = f" [{issue.start}:{issue.end}]"
            print(f"  {issue.severity}:{issue.code}{span} {issue.message}")

    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
