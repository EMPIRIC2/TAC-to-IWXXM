"""Command-line interface for ``tac-validate`` (F12)."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from tac_validate.api import lint
from tac_validate.codec import json_encoder
from tac_validate.overlay_check import check_tac_policy_overlay_dir
from tac_validate.policy import PolicyError, apply_policy_to_report
from tac_validate.products import PRODUCTS
from tac_validate.profiles import SUPPORTED_PROFILES


def _build_parser() -> argparse.ArgumentParser:
    """
    Internal helper ``_build_parser``.

    Returns
    -------
    object
        Return value.
    """
    parser = argparse.ArgumentParser(
        prog="tac-validate",
        description="Lint TAC text for F6 products (parse-gate + checklist/template gates).",
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="Path to a TAC text file (required unless --check-overlay)",
    )
    parser.add_argument(
        "--product",
        default=None,
        choices=list(PRODUCTS),
        help="F6 product id (required unless --check-overlay)",
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
    parser.add_argument(
        "--check-overlay",
        type=Path,
        metavar="DIR",
        help="Fail-closed load of TAC quality policy YAML overlays in DIR (no lint)",
    )
    return parser


def _lint_profile(emit_key: str) -> str:
    """
    Internal helper ``_lint_profile``.

    Parameters
    ----------
    emit_key : object
        Argument ``emit_key``.

    Returns
    -------
    object
        Return value.
    """
    if emit_key in SUPPORTED_PROFILES:
        return emit_key
    return "annex3"


def _bound_policy(profile: str, policy: str | None, *, product: str | None = None) -> tuple[str, str]:
    """
    Internal helper ``_bound_policy``.

    Parameters
    ----------
    profile : object
        Argument ``profile``.
    policy : object
        Argument ``policy``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    try:
        from tac2iwxxm.profile_resolve import ProfileResolveError, resolve_validation_policies
    except ImportError:
        return _lint_profile(profile), policy or ""
    try:
        resolved = resolve_validation_policies(profile, product=product, tac_policy=policy)
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

    Examples
    --------
    >>> 1 + 1  # docstring smoke (main)
    2
    """
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.check_overlay is not None:
        try:
            check_tac_policy_overlay_dir(args.check_overlay, profile=args.profile)
        except Exception as exc:
            print(f"error: TAC policy overlay check failed: {exc}", file=sys.stderr)
            return 1
        print(f"ok tac-policy overlay {args.check_overlay}")
        return 0

    if args.path is None or args.product is None:
        parser.error("path and --product are required unless --check-overlay is set")

    path: Path = args.path
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 1

    try:
        lint_profile, policy_id = _bound_policy(args.profile, args.policy, product=args.product)
    except PolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = lint(text, product=args.product, profile=lint_profile)
    if policy_id:
        try:
            report = apply_policy_to_report(report, policy_id, profile=lint_profile)
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
