#!/usr/bin/env python3
"""Print the Hydra-composed national convert allowlist.

Examples
--------
uv run python scripts/tac2iwxxm/compose_convert_allowlist.py
uv run python scripts/tac2iwxxm/compose_convert_allowlist.py --override 'profiles.au_bom=[METAR,TAF]'
"""

from __future__ import annotations

import argparse

from tac2iwxxm.convert_allowlist import compose_allowlist, format_allowlist


def main(argv: list[str] | None = None) -> int:
    """
    Print the composed allowlist.

    Parameters
    ----------
    argv :
        CLI arguments. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        Process status. ``0`` when the allowlist printed.
    """
    parser = argparse.ArgumentParser(
        description="Compose the convert allowlist with Hydra."
    )
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="Hydra override, repeatable. Example: profiles.au_bom=[METAR,TAF]",
    )
    args = parser.parse_args(argv)
    print(format_allowlist(compose_allowlist(args.override)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
