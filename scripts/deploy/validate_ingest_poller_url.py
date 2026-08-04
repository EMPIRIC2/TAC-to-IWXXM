#!/usr/bin/env python3
"""CLI: validate INGEST_POLLER_URL (EV-033 / F8). Exit 0 OK, 2 invalid.

Usage:
  python scripts/deploy/validate_ingest_poller_url.py 'https://…'
  INGEST_POLLER_URL=https://… python scripts/deploy/validate_ingest_poller_url.py
  python scripts/deploy/validate_ingest_poller_url.py --probe   # GET after validate
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps/worker/src"))

from metar_worker.poller_url import (  # noqa: E402
    DEFAULT_FIXTURE_INGEST_POLLER_URL,
    validate_ingest_poller_url,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "url",
        nargs="?",
        default=os.environ.get("INGEST_POLLER_URL", ""),
        help="Poller URL (default: $INGEST_POLLER_URL)",
    )
    parser.add_argument(
        "--probe",
        action="store_true",
        help="After validate, GET the URL and require JSON items/list",
    )
    parser.add_argument(
        "--print-fixture",
        action="store_true",
        help="Print the documented non-prod fixture URL and exit 0",
    )
    args = parser.parse_args()
    if args.print_fixture:
        print(DEFAULT_FIXTURE_INGEST_POLLER_URL)
        return 0

    try:
        url = validate_ingest_poller_url(args.url)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.probe:
        req = Request(url, headers={"User-Agent": "validate-ingest-poller-url/1"})
        try:
            with urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"ERROR: probe failed for {url}: {exc}", file=sys.stderr)
            return 2
        if isinstance(payload, dict) and "items" in payload:
            n = len(payload["items"]) if isinstance(payload["items"], list) else "?"
        elif isinstance(payload, list):
            n = len(payload)
        else:
            print("ERROR: feed must be JSON list or {items: [...]}", file=sys.stderr)
            return 2
        print(f"OK: {url} (probe items={n})")
        return 0

    print(f"OK: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
