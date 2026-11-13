#!/usr/bin/env python3
"""Parameterized national ops-corpus harvest entrypoint (#1036 / playbook type J).

Reusable CLI for public-feed nationals. CA_ECCC is the reference implementation;
other profiles fail closed until a second corpus lands.

Examples
--------
    uv run python scripts/iwxxm/harvest_ops_corpus.py --profile CA_ECCC --product TAF
    uv run python scripts/iwxxm/harvest_ops_corpus.py --profile CA_ECCC --skip-network

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests]
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import types
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SUPPORTED = frozenset({"CA_ECCC"})


def _load_ca_harvest() -> types.ModuleType:
    """Load ``harvest_ca_eccc_ops`` by path (avoids package install for scripts)."""
    path = _REPO / "scripts" / "iwxxm" / "harvest_ca_eccc_ops.py"
    spec = importlib.util.spec_from_file_location("harvest_ca_eccc_ops", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load harvest module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    """CLI entry: dispatch ``--profile`` / ``--product`` to the CA harvest module."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        default="CA_ECCC",
        help="Semantic profile id (only CA_ECCC implemented; playbook type J)",
    )
    parser.add_argument(
        "--product",
        default="ALL",
        help="Product filter: ALL or METAR/SPECI/TAF/AIRMET/SIGMET",
    )
    parser.add_argument("--pin-date", default=None, help="Pin date (YYYY-MM-DD)")
    parser.add_argument("--datamart-base", default=None, help="HTTPS datamart base")
    parser.add_argument(
        "--fixtures-root",
        type=Path,
        default=None,
        help="Profile fixture root (defaults from profile id)",
    )
    parser.add_argument("--rate-limit", type=float, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Offline: encoder-reference + committed datamart fixtures only",
    )
    args = parser.parse_args(argv)

    profile = args.profile.strip().upper()
    if profile not in _SUPPORTED:
        print(
            f"unsupported profile {profile!r}: supported={sorted(_SUPPORTED)} "
            "(generalize when a second public ops corpus lands)",
            file=sys.stderr,
        )
        return 2

    ca = _load_ca_harvest()
    fixtures_root = args.fixtures_root or ca.ops_fixture_root(_REPO, profile=profile)
    manifest = ca.harvest(
        fixtures_root=fixtures_root,
        pin_date=args.pin_date or ca.DEFAULT_PIN_DATE,
        datamart_base=args.datamart_base or ca.DEFAULT_BASE,
        rate_limit=args.rate_limit
        if args.rate_limit is not None
        else ca.DEFAULT_RATE_LIMIT,
        dry_run=args.dry_run,
        skip_network=args.skip_network,
        product_filter=args.product,
    )
    rel = fixtures_root / "ops_manifest.json"
    try:
        shown = rel.relative_to(_REPO)
    except ValueError:
        shown = rel
    print(f"{'would write' if args.dry_run else 'wrote'} {shown}")
    print(
        f"profile={profile} product={args.product} "
        f"cases={len(manifest['cases'])} checksum={manifest['manifest_sha256'][:12]}…"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
