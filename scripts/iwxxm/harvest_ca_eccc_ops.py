#!/usr/bin/env python3
"""Harvest CA_ECCC MSC datamart ops IWXXM fixtures (EV-072 M2 / #1036).

Fetches TAF/AIRMET (and METAR/SPECI when published) from the MSC datamart tree for a
pin date, writes offline fixtures + ``ops_manifest.json``. CI uses committed fixtures
only — no live network in tests.

Respect MSC open-data terms: conservative rate limit, pin-date reproducibility.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV072]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "packages" / "tac2iwxxm" / "src"))

from tac2iwxxm.ca_ops_corpus import (  # noqa: E402
    manifest_checksum,
    msc_filename_from_url,
    ops_fixture_root,
)

DEFAULT_PIN_DATE = "2026-08-24"
DEFAULT_BASE = "https://dd.weather.gc.ca"
DEFAULT_RATE_LIMIT = 1.0

# Pin-date harvest plan — datamart URLs verified 2026-08-24.
# METAR/SPECI IWXXM paths return 404 on MSC datamart at pin_date; bootstrap uses encoder reference.
_PINNED_FETCHES: list[dict[str, str]] = [
    {
        "id": "taf_cwao_12_001",
        "product": "TAF",
        "rel_path": "TAF/ops/taf_cwao_12_001.xml",
        "url": f"{DEFAULT_BASE}/today/aviation/iwxxm/taf/cwao/12/A_LTCN22CWAO241200_C_CWAO_20260824120000.xml",
    },
    {
        "id": "taf_cwao_12_002",
        "product": "TAF",
        "rel_path": "TAF/ops/taf_cwao_12_002.xml",
        "url": f"{DEFAULT_BASE}/today/aviation/iwxxm/taf/cwao/12/A_LTCN31CWAO241200_C_CWAO_20260824120000.xml",
    },
    {
        "id": "airmet_czul_05_001",
        "product": "AIRMET",
        "rel_path": "AIRMET/ops/airmet_czul_05_001.xml",
        "url": f"{DEFAULT_BASE}/today/aviation/iwxxm/airmet/czul/05/A_LWCN25CWAO240529_C_CWAO_20260824052916.xml",
    },
    {
        "id": "airmet_czvr_13_001",
        "product": "AIRMET",
        "rel_path": "AIRMET/ops/airmet_czvr_13_001.xml",
        "url": f"{DEFAULT_BASE}/today/aviation/iwxxm/airmet/czvr/13/A_LWCN21CWAO241302_C_CWAO_20260824130238.xml",
    },
    {
        "id": "sigmet_czeg_15_001",
        "product": "SIGMET",
        "rel_path": "SIGMET/ops/sigmet_czeg_15_001.xml",
        "url": f"{DEFAULT_BASE}/today/aviation/iwxxm/sigmet/czeg/15/A_LSCN22CWAO241540_C_CWAO_20260824154038.xml",
        "sigmet_kind": "weather",
    },
    {
        "id": "sigmet_czqm_08_001",
        "product": "SIGMET",
        "rel_path": "SIGMET/ops/sigmet_czqm_08_001.xml",
        "url": f"{DEFAULT_BASE}/today/aviation/iwxxm/sigmet/czqm/08/A_LSCN26CWAO240835_C_CWAO_20260824083546.xml",
        "sigmet_kind": "weather",
    },
]

# VAA: no MSC aviation/iwxxm VAA tree on 2026-08-24 (D-EV074-vaa-follow).

_ENCODER_REFERENCE: list[dict[str, str]] = [
    {
        "id": "metar_basic_ops",
        "product": "METAR",
        "rel_path": "METAR/ops/metar_basic_ops.xml",
        "golden_tac": "METAR/valid/metar_basic.tac",
    },
    {
        "id": "metar_auto_ops",
        "product": "METAR",
        "rel_path": "METAR/ops/metar_auto_ops.xml",
        "golden_tac": "METAR/valid/metar_auto.tac",
    },
    {
        "id": "metar_lwis_ops",
        "product": "METAR",
        "rel_path": "METAR/ops/metar_lwis_ops.xml",
        "golden_tac": "METAR/valid/metar_lwis.tac",
    },
    {
        "id": "metar_sawr_ops",
        "product": "METAR",
        "rel_path": "METAR/ops/metar_sawr_ops.xml",
        "golden_tac": "METAR/valid/metar_sawr.tac",
    },
    {
        "id": "metar_vis_sm_ops",
        "product": "METAR",
        "rel_path": "METAR/ops/metar_vis_sm_ops.xml",
        "golden_tac": "METAR/valid/metar_vis_sm.tac",
    },
    {
        "id": "speci_basic_ops",
        "product": "SPECI",
        "rel_path": "SPECI/ops/speci_basic_ops.xml",
        "tac_inline": "SPECI CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012=",
    },
    {
        "id": "speci_auto_ops",
        "product": "SPECI",
        "rel_path": "SPECI/ops/speci_auto_ops.xml",
        "tac_inline": "SPECI CYUL 231800Z AUTO 24010KT 9999 FEW240 22/12 A3012=",
    },
]

_METAR_SPECI_WAIVER = (
    "METAR/SPECI IWXXM not published on MSC datamart at pin_date; "
    "encoder reference for layer-6 packaging checks only"
)
_DATAMART_WAIVER = (
    "MSC operational COLLECT members omit translationCentre* attrs; "
    "filename + reportStatus checks only"
)


def _fetch_url(url: str, *, timeout: float = 30.0) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "TAC-to-IWXXM-ops-harvest/1.0"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _bootstrap_encoder_reference(
    fixtures_root: Path, *, dry_run: bool
) -> list[dict[str, Any]]:
    from tac2iwxxm import convert

    cases: list[dict[str, Any]] = []
    for row in _ENCODER_REFERENCE:
        dest = fixtures_root / row["rel_path"]
        tac = row.get("tac_inline")
        if tac is None:
            tac_path = fixtures_root / row["golden_tac"]
            tac = tac_path.read_text(encoding="utf-8").strip()
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            result = convert(
                tac, product=row["product"], profile="ca_eccc", iwxxm_version="3.0.0"
            )
            if not result.ok or result.xml is None:
                raise RuntimeError(
                    f"encoder reference failed for {row['id']}: {result.issues}"
                )
            dest.write_text(result.xml, encoding="utf-8")
        cases.append(
            {
                "id": row["id"],
                "product": row["product"],
                "tier": "wmoReference",
                "ops_xml": row["rel_path"],
                "source": "encoder_reference",
                "packaging_waiver": _METAR_SPECI_WAIVER,
            }
        )
    return cases


def harvest(
    *,
    fixtures_root: Path,
    pin_date: str,
    datamart_base: str,
    rate_limit: float,
    dry_run: bool,
    skip_network: bool,
) -> dict[str, Any]:
    """
    Harvest datamart ops fixtures and write ``ops_manifest.json``.

    Parameters
    ----------
    fixtures_root :
        CA_ECCC profile fixture directory.
    pin_date :
        Pin date recorded in the manifest (YYYY-MM-DD).
    datamart_base :
        MSC datamart HTTPS base URL.
    rate_limit :
        Seconds to sleep between network fetches.
    dry_run :
        When ``True``, do not write files.
    skip_network :
        When ``True``, skip datamart fetches (manifest + encoder reference only).

    Returns
    -------
    dict[str, Any]
        Ops manifest payload (without checksum field).
    """
    cases: list[dict[str, Any]] = []

    if not skip_network:
        for row in _PINNED_FETCHES:
            url = row["url"].replace(DEFAULT_BASE, datamart_base.rstrip("/"))
            dest = fixtures_root / row["rel_path"]
            if not dry_run:
                try:
                    payload = _fetch_url(url)
                except urllib.error.HTTPError as exc:
                    raise RuntimeError(f"fetch failed {url}: HTTP {exc.code}") from exc
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(payload)
                time.sleep(rate_limit)
            source_filename = msc_filename_from_url(url)
            entry: dict[str, Any] = {
                "id": row["id"],
                "product": row["product"],
                "tier": "wmoReference",
                "ops_xml": row["rel_path"],
                "source_url": url,
                "source_filename": source_filename,
                "packaging_waiver": _DATAMART_WAIVER,
            }
            if "sigmet_kind" in row:
                entry["sigmet_kind"] = row["sigmet_kind"]
            cases.append(entry)

    cases.extend(_bootstrap_encoder_reference(fixtures_root, dry_run=dry_run))

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "description": "EV-072 M2 — CA_ECCC MSC datamart ops conformance corpus",
        "profile": "CA_ECCC",
        "pin_date": pin_date,
        "datamart_base": datamart_base.rstrip("/"),
        "rate_limit_seconds": rate_limit,
        "cases": cases,
        "vaa_harvest": "deferred_no_datamart_tree",
    }
    manifest["manifest_sha256"] = manifest_checksum(manifest)
    if not dry_run:
        manifest_path = fixtures_root / "ops_manifest.json"
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
        "--datamart-base",
        default=DEFAULT_BASE,
        help="MSC datamart HTTPS base (default: dd.weather.gc.ca)",
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
        help="Regenerate encoder-reference fixtures + manifest only",
    )
    args = parser.parse_args()

    manifest = harvest(
        fixtures_root=args.fixtures_root,
        pin_date=args.pin_date,
        datamart_base=args.datamart_base,
        rate_limit=args.rate_limit,
        dry_run=args.dry_run,
        skip_network=args.skip_network,
    )
    rel = args.fixtures_root / "ops_manifest.json"
    print(f"{'would write' if args.dry_run else 'wrote'} {rel.relative_to(_REPO)}")
    print(
        f"cases={len(manifest['cases'])} checksum={manifest['manifest_sha256'][:12]}…"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
