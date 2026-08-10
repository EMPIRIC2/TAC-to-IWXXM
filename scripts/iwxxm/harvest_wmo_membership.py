#!/usr/bin/env python3
"""Regenerate tac-validate WMO membership artifact (EV-050 / AC1).

Offline only — reads vendor/schemas/iwxxm-codelists CSV + pin RDF.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "packages" / "tac-validate" / "src"))

from tac_validate.membership import write_membership_artifact  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iwxxm-version",
        default="2025-2",
        help="IWXXM pin line for nil RDF (default: 2025-2)",
    )
    args = parser.parse_args()
    path = write_membership_artifact(root=_REPO, iwxxm_version=args.iwxxm_version)
    print(f"wrote {path.relative_to(_REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
