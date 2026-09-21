"""Command-line interface for ``tac-validate`` (F12)."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from tac_validate.api import lint
from tac_validate.codec import json_encoder
from tac_validate.policy import PolicyError, apply_policy_to_report
from tac_validate.products import PRODUCTS
from tac_validate.profiles import SUPPORTED_PROFILES


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
        "--profile",
        default="annex3",
        help="Conversion profile id (for example annex3 or ICAO_2025). Default: annex3",
    )
    parser.add_argument(
        "--policy",
        default=None,
        help="TAC quality policy id. Overrides the policy bound to --profile",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit LintReport as JSON on stdout",
    )
    return parser


def _lint_profile(emit_key: str) -> str:
    if emit_key in SUPPORTED_PROFILES:
        return emit_key
    return "annex3"


def _bound_policy(profile: str, policy: str | None) -> tuple[str, str]:
    try:
        from tac2iwxxm.profile_resolve import ProfileResolveError, resolve_validation_policies
    except ImportError:
        return _lint_profile(profile), policy or ""
    try:
        resolved = resolve_validation_policies(profile, tac_policy=policy)
    except ProfileResolveError as exc:
        raise PolicyError(str(exc)) from exc
    return _lint_profile(resolved.emit_key), resolved.tac_quality_policy_id


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
        ``0`` when ``report.ok``; ``1`` on lint errors or I/O failure; ``2`` when the profile or policy id is unknown.
    """
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    path: Path = args.path
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 1

    try:
        lint_profile, policy_id = _bound_policy(args.profile, args.policy)
    except PolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = lint(text, product=args.product, profile=lint_profile)
    if policy_id:
        try:
            report = apply_policy_to_report(report, policy_id)
        except PolicyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
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
