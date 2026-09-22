"""Thin CLI for ``tac2iwxxm`` overlay DX (#1227 / #1229).

Conversion remains a library API (``tac2iwxxm.convert``). This entrypoint exists so
embedders can fail-closed-check profile binding or emit-map overlays without the
monorepo preflight script.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from tac2iwxxm.emit_map import check_emit_map_overlay_dir
from tac2iwxxm.overlay_check import check_profile_overlay_dir


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tac2iwxxm",
        description="tac2iwxxm DX helpers (overlay check). Use the Python API for convert.",
    )
    parser.add_argument(
        "--check-overlay",
        type=Path,
        metavar="DIR",
        required=True,
        help="Fail-closed load of overlay YAML in DIR",
    )
    parser.add_argument(
        "--overlay-kind",
        choices=("profile", "emit-map"),
        default="profile",
        help="profile→policy binding (default) or emit-map overlays",
    )
    parser.add_argument(
        "--profile",
        default="annex3",
        help="Conversion profile id to resolve for profile overlays (default: annex3)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run ``tac2iwxxm`` CLI.

    Parameters
    ----------
    argv :
        Argument vector (defaults to ``sys.argv[1:]``).

    Returns
    -------
    int
        ``0`` when the overlay loads; ``1`` on failure.
    """
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.overlay_kind == "emit-map":
            check_emit_map_overlay_dir(args.check_overlay)
        else:
            check_profile_overlay_dir(args.check_overlay, profile=args.profile)
    except Exception as exc:
        kind = args.overlay_kind
        print(f"error: {kind} overlay check failed: {exc}", file=sys.stderr)
        return 1
    print(f"ok {args.overlay_kind} overlay {args.check_overlay}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
