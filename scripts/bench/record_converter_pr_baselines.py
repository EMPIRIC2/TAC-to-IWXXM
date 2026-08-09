#!/usr/bin/env python3
"""Record converter PR baselines to tests/perf/baselines/converter_pr.yaml.

Usage:
  uv run python scripts/bench/record_converter_pr_baselines.py --host ubuntu-latest --status ci_recorded
  make perf-converter-baseline
"""

from __future__ import annotations

import argparse
import platform
from datetime import date
from pathlib import Path

import yaml

from scripts.bench.converter_pr_baselines import (
    DEFAULT_BASELINES,
    load_converter_pr_baselines,
    record_baselines_dict,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        default=platform.platform(),
        help="recorded_host label (use ubuntu-latest on CI)",
    )
    parser.add_argument(
        "--status",
        default="ci_recorded",
        choices=("laptop_seed", "ci_recorded"),
        help="baseline authority status",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_BASELINES,
        help="output YAML path",
    )
    args = parser.parse_args()
    baselines = load_converter_pr_baselines()
    data = record_baselines_dict(
        baselines, status=args.status, recorded_host=args.host
    )
    data["recorded"] = date.today().isoformat()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        yaml.safe_dump(data, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    print(f"Wrote {args.out} status={args.status} host={args.host}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
