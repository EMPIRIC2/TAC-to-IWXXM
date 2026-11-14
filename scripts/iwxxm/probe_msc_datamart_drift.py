#!/usr/bin/env python3
"""Probe MSC aviation IWXXM datamart product/schema drift (#1036).

Offline mode (default, CI-safe): compare committed ``ops_datamart_probe.json``
expectations (expected product trees + schema filenames).

Live mode (``--live``): HTTP GET the datamart index and fail when expected live
products disappear or schema filenames change. METAR/SPECI remain documented
404 blockers until MSC publishes those trees.

No secrets. Rate-limited User-Agent only.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests]
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_PROBE = (
    _REPO
    / "packages"
    / "tac2iwxxm"
    / "tests"
    / "fixtures"
    / "profiles"
    / "CA_ECCC"
    / "ops_datamart_probe.json"
)
_DEFAULT_BASE = "https://dd.weather.gc.ca"
_UA = "TAC-to-IWXXM-ops-harvest/1.0"
_EXPECTED_LIVE_PRODUCTS = ("taf", "airmet", "sigmet")
_BLOCKED_PRODUCTS = ("metar", "speci", "vaa")
_EXPECTED_SCHEMA = frozenset(
    {
        "airmet-ca.xsd",
        "common-ca.xsd",
        "iwxxm-ca.xsd",
        "metar-speci-ca.xsd",
        "taf-ca.xsd",
    }
)


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if (
                key == "href"
                and value
                and not value.startswith("?")
                and not value.startswith("/")
            ):
                self.hrefs.append(value.rstrip("/"))


def _fetch_listing(url: str, *, timeout: float = 30.0) -> tuple[int, list[str]]:
    request = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", "replace")
            parser = _Links()
            parser.feed(body)
            return int(response.status), sorted(parser.hrefs)
    except urllib.error.HTTPError as exc:
        return int(exc.code), []


def _validate_committed(probe: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    products = probe.get("products") or {}
    for name in _EXPECTED_LIVE_PRODUCTS:
        row = products.get(name) or {}
        if row.get("http_status") != 200:
            errors.append(f"committed probe: {name} expected HTTP 200, got {row}")
        if not row.get("children"):
            errors.append(f"committed probe: {name} missing children issuers")
    for name in _BLOCKED_PRODUCTS:
        row = products.get(name) or {}
        if row.get("http_status") != 404:
            errors.append(
                f"committed probe: {name} expected documented HTTP 404 blocker, got {row}"
            )
    schema = (probe.get("schema") or {}).get("children") or []
    missing = _EXPECTED_SCHEMA - set(schema)
    if missing:
        errors.append(f"committed probe: schema missing {sorted(missing)}")
    if not (probe.get("blocker_note") or "").strip():
        errors.append("committed probe: missing blocker_note")
    return errors


def _validate_live(base: str) -> list[str]:
    errors: list[str] = []
    root_status, root_children = _fetch_listing(
        f"{base.rstrip('/')}/today/aviation/iwxxm/"
    )
    if root_status != 200:
        return [f"live datamart root HTTP {root_status}"]
    for name in _EXPECTED_LIVE_PRODUCTS:
        if name not in root_children:
            errors.append(
                f"live: expected product tree {name!r} missing from root {root_children}"
            )
        status, children = _fetch_listing(
            f"{base.rstrip('/')}/today/aviation/iwxxm/{name}/"
        )
        if status != 200:
            errors.append(f"live: {name}/ HTTP {status}")
        elif not children:
            errors.append(f"live: {name}/ empty issuer listing")
    for name in _BLOCKED_PRODUCTS:
        status, _children = _fetch_listing(
            f"{base.rstrip('/')}/today/aviation/iwxxm/{name}/"
        )
        if status == 200:
            errors.append(
                f"live: {name}/ now HTTP 200 — re-harvest ops fixtures "
                f"(previous METAR/SPECI/VAA datamart blocker lifted)"
            )
        elif status not in {404, 200}:
            errors.append(f"live: {name}/ unexpected HTTP {status}")
    schema_status, schema_children = _fetch_listing(
        f"{base.rstrip('/')}/today/aviation/iwxxm/schema/"
    )
    if schema_status != 200:
        errors.append(f"live: schema/ HTTP {schema_status}")
    else:
        missing = _EXPECTED_SCHEMA - set(schema_children)
        extra = set(schema_children) - _EXPECTED_SCHEMA
        if missing:
            errors.append(f"live: schema missing {sorted(missing)}")
        if extra:
            errors.append(f"live: schema unexpected files {sorted(extra)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    """CLI entry for offline (default) or ``--live`` MSC datamart drift checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--probe-json",
        type=Path,
        default=_DEFAULT_PROBE,
        help="Committed ops_datamart_probe.json path",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Fetch live MSC listings (scheduled workflow); default is offline",
    )
    parser.add_argument(
        "--datamart-base",
        default=_DEFAULT_BASE,
        help="MSC datamart HTTPS base",
    )
    args = parser.parse_args(argv)

    probe = json.loads(args.probe_json.read_text(encoding="utf-8"))
    errors = _validate_committed(probe)
    if args.live:
        errors.extend(_validate_live(args.datamart_base))

    if errors:
        print("MSC datamart drift FAIL:", file=sys.stderr)
        for item in errors:
            print(f"  - {item}", file=sys.stderr)
        return 1

    mode = "live" if args.live else "offline"
    print(f"MSC datamart drift OK ({mode})")
    print(
        f"probe={args.probe_json.relative_to(_REPO)} probed_at={probe.get('probed_at')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
