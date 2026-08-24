#!/usr/bin/env python3
"""Harvest CA_ECCC Montreal VAAC TAC ops fixtures (D-EV074-vaa-waiver-tac).

Fetches Volcanic Ash Advisory TAC bulletins from weather.gc.ca/eer/vaac when
MSC datamart has no ``aviation/iwxxm/vaa`` tree. CI uses committed fixtures only.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV074]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "packages" / "tac2iwxxm" / "src"))

from tac2iwxxm.ca_ops_corpus import (  # noqa: E402
    load_ops_manifest,
    manifest_checksum,
    ops_fixture_root,
)

DEFAULT_PIN_DATE = "2026-08-24"
DEFAULT_RATE_LIMIT = 1.0
_VAAC_VIEW = "https://weather.gc.ca/eer/vaac/viewData_e.html"
_PRE_RE = re.compile(r"<pre[^>]*>(.*?)</pre>", re.IGNORECASE | re.DOTALL)

# Pin-date VAAC harvest plan — verified 2026-08-24 (31-day index had 1 FVCN bulletin).
_PINNED_VAAC: list[dict[str, str]] = [
    {
        "id": "vaa_edziza_20260818_001",
        "rel_path": "VAA/ops/vaa_edziza_20260818_001.tac",
        "data_param": "20260818-1859Z_FVCN01-0001_EDZIZA-320060.msg.sent.txt",
        "vaac_header": "FVCN01-0001",
        "volcano": "EDZIZA-320060",
    },
]

_VAA_TAC_WAIVER = (
    "VAA validate-first TAC from Montreal VAAC; no MSC datamart IWXXM "
    "(D-EV074-vaa-waiver-tac); exchange emit still deferred"
)


def _fetch_vaac_tac(data_param: str, *, timeout: float = 30.0) -> str:
    url = f"{_VAAC_VIEW}?product=FVCN&data={data_param}"
    request = urllib.request.Request(
        url, headers={"User-Agent": "TAC-to-IWXXM-vaac-harvest/1.0"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        html = response.read().decode("utf-8", errors="replace")
    match = _PRE_RE.search(html)
    if not match or "VA ADVISORY" not in match.group(1):
        raise RuntimeError(f"VAAC TAC not found in {url}")
    return match.group(1).strip()


def _merge_vaa_cases(
    manifest: dict[str, Any], new_cases: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_id = {c["id"]: c for c in manifest["cases"] if c.get("product") != "VAA"}
    for case in new_cases:
        by_id[case["id"]] = case
    return list(by_id.values())


def harvest_vaac_tac(
    *,
    fixtures_root: Path,
    pin_date: str,
    rate_limit: float,
    dry_run: bool,
    skip_network: bool,
) -> dict[str, Any]:
    """
    Harvest VAAC TAC fixtures and merge into ``ops_manifest.json``.

    Parameters
    ----------
    fixtures_root :
        CA_ECCC profile fixture directory.
    pin_date :
        Pin date recorded in manifest (YYYY-MM-DD).
    rate_limit :
        Seconds to sleep between network fetches.
    dry_run :
        When ``True``, do not write files.
    skip_network :
        When ``True``, update manifest metadata only (offline).

    Returns
    -------
    dict[str, Any]
        Updated ops manifest payload (without checksum field).
    """
    manifest_path = fixtures_root / "ops_manifest.json"
    manifest = load_ops_manifest(manifest_path)
    vaa_cases: list[dict[str, Any]] = []

    for row in _PINNED_VAAC:
        dest = fixtures_root / row["rel_path"]
        source_url = f"{_VAAC_VIEW}?product=FVCN&data={row['data_param']}"
        if not skip_network and not dry_run:
            try:
                tac = _fetch_vaac_tac(row["data_param"])
            except urllib.error.HTTPError as exc:
                raise RuntimeError(
                    f"VAAC fetch failed {source_url}: HTTP {exc.code}"
                ) from exc
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(tac + "\n", encoding="utf-8")
            time.sleep(rate_limit)

        vaa_cases.append(
            {
                "id": row["id"],
                "product": "VAA",
                "tier": "vaacTac",
                "ops_tac": row["rel_path"],
                "source": "vaac_tac",
                "source_url": source_url,
                "vaac_header": row["vaac_header"],
                "volcano": row["volcano"],
                "packaging_waiver": _VAA_TAC_WAIVER,
            }
        )

    manifest["cases"] = _merge_vaa_cases(manifest, vaa_cases)
    manifest["pin_date"] = pin_date
    manifest["vaa_harvest"] = "vaac_tac_waived"
    manifest["vaa_harvest_note"] = (
        "Datamart vaa/ tree absent; Montreal VAAC TAC via D-EV074-vaa-waiver-tac. "
        f"{len(vaa_cases)} bulletin(s) at pin {pin_date} (31-day index); ≥2 when published."
    )
    manifest["manifest_sha256"] = manifest_checksum(manifest)

    if not dry_run:
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pin-date", default=DEFAULT_PIN_DATE, help="Pin date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--fixtures-root",
        type=Path,
        default=ops_fixture_root(_REPO),
        help="CA_ECCC fixture root",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=DEFAULT_RATE_LIMIT,
        help="Seconds between HTTP fetches (default: 1.0)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Plan only; do not write files"
    )
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Update manifest VAA metadata only (offline)",
    )
    args = parser.parse_args()

    manifest = harvest_vaac_tac(
        fixtures_root=args.fixtures_root,
        pin_date=args.pin_date,
        rate_limit=args.rate_limit,
        dry_run=args.dry_run,
        skip_network=args.skip_network,
    )
    vaa_count = sum(1 for c in manifest["cases"] if c["product"] == "VAA")
    rel = args.fixtures_root / "ops_manifest.json"
    print(f"{'would write' if args.dry_run else 'wrote'} {rel.relative_to(_REPO)}")
    print(f"vaa_cases={vaa_count} vaa_harvest={manifest.get('vaa_harvest')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
