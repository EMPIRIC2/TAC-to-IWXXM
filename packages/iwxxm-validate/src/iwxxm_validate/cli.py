"""Optional thin CLI for ``iwxxm-validate`` (E10-39 / T3.9)."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from iwxxm_validate.codec import json_encoder
from iwxxm_validate.overlay_check import check_iwxxm_policy_overlay_dir
from iwxxm_validate.validate_iwxxm import validate_iwxxm


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iwxxm-validate",
        description="Validate IWXXM XML (XSD + Schematron via validate_iwxxm SDK).",
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="Path to an IWXXM XML file (required unless --check-overlay)",
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
        "--policy",
        default=None,
        help="IWXXM output policy id. Overrides the policy bound to --profile",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit ValidationReport as JSON on stdout",
    )
    parser.add_argument(
        "--check-overlay",
        type=Path,
        metavar="DIR",
        help="Fail-closed load of IWXXM output policy YAML overlays in DIR (no validate)",
    )
    return parser


def _cli_validate_product(profile: str, extensions: Sequence[str], product: str | None) -> str | None:
    if profile != "ca_eccc":
        return None
    normalized = {token.strip().upper().replace("-", "_") for token in extensions if token.strip()}
    if "IWXXM_CA" in normalized:
        return (product or "METAR").upper()
    return None


def _bind_output_policy(profile: str, policy: str | None) -> tuple[str | None, str | None]:
    """Return ``(policy_id, error)``. ``error`` is set when the policy cannot be activated."""
    try:
        from tac2iwxxm.profile_resolve import ProfileResolveError, resolve_validation_policies
    except ImportError:
        if not policy:
            return None, None
        policy_id = policy
    else:
        try:
            resolved = resolve_validation_policies(profile, iwxxm_policy=policy)
        except ProfileResolveError as exc:
            return None, str(exc)
        policy_id = resolved.iwxxm_output_policy_id
    from iwxxm_validate.policy import PolicyError, load_output_policy_catalog, resolve_output_policy

    catalog = load_output_policy_catalog()
    doc = catalog.get(policy_id)
    if doc is None:
        return None, f"unknown IWXXM output policy {policy_id!r}"
    try:
        resolve_output_policy(doc, policies=catalog)
    except PolicyError as exc:
        return None, str(exc)
    return policy_id, None


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

    if args.check_overlay is not None:
        try:
            check_iwxxm_policy_overlay_dir(args.check_overlay, profile=args.profile)
        except Exception as exc:
            print(f"error: IWXXM policy overlay check failed: {exc}", file=sys.stderr)
            return 1
        print(f"ok iwxxm-policy overlay {args.check_overlay}")
        return 0

    if args.path is None:
        parser.error("path is required unless --check-overlay is set")

    path: Path = args.path
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 1

    policy_id, policy_error = _bind_output_policy(args.profile, args.policy)
    if policy_error:
        print(f"error: {policy_error}", file=sys.stderr)
        return 2

    report = validate_iwxxm(
        text,
        iwxxm_version=args.iwxxm_version,
        profile=args.profile,
        product=_cli_validate_product(args.profile, args.extensions, args.product),
        output_policy_id=policy_id,
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
