#!/usr/bin/env python3
"""Collect quality/golden outcome stats for EV-052 sticky PR comment.

Emits ``quality-summary.json`` files under ``--out`` for:

* annex3 + iwxxm_us golden manifests (live convert + canonicalize compare)
* quality-matrix RuleCase inventory (ready / needs-fixture / oos)

Outcome buckets: match | soft_diff | fail | skip (by product x profile).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DEFAULT = Path(__file__).resolve().parents[2]


def _bump(
    agg: dict[tuple[str, str], list[int]],
    product: str,
    profile: str,
    bucket: str,
) -> None:
    idx = {"match": 0, "soft_diff": 1, "fail": 2, "skip": 3}[bucket]
    key = (product.upper(), profile)
    if key not in agg:
        agg[key] = [0, 0, 0, 0]
    agg[key][idx] += 1


def _rows_from_agg(agg: dict[tuple[str, str], list[int]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for product, profile in sorted(agg.keys()):
        m, s, f, sk = agg[(product, profile)]
        rows.append(
            {
                "product": product,
                "profile": profile,
                "match": m,
                "soft_diff": s,
                "fail": f,
                "skip": sk,
            }
        )
    return rows


def _write_summary(
    path: Path, source: str, agg: dict[tuple[str, str], list[int]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source": source,
                "rows": _rows_from_agg(agg),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def collect_golden_pack(
    manifest_path: Path,
    *,
    default_profile: str,
) -> dict[tuple[str, str], list[int]]:
    """
    Live-compare golden pack cases under a manifest.

    Parameters
    ----------
    manifest_path : Path
        Path to ``manifest.json``.
    default_profile : str
        Profile when case/manifest omit it.

    Returns
    -------
    dict[tuple[str, str], list[int]]
        Aggregated outcome counts.
    """
    from metar_shared.xml_canonical import canonicalize_xml
    from tac2iwxxm import convert

    agg: dict[tuple[str, str], list[int]] = {}
    if not manifest_path.is_file():
        return agg

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    pack_profile = str(data.get("profile") or default_profile)
    fixtures = manifest_path.parent
    iwxxm_version = str(data.get("iwxxm_version") or "2025-2")

    for case in data.get("cases") or []:
        if not isinstance(case, dict):
            continue
        product = str(case.get("product") or "?").upper()
        profile = str(case.get("profile") or pack_profile)
        soft = case.get("soft_compare") is True
        tac_name = case.get("tac")
        golden_name = case.get("golden")

        if not tac_name:
            _bump(agg, product, profile, "skip")
            continue
        tac_path = fixtures / str(tac_name)
        if not tac_path.is_file():
            _bump(agg, product, profile, "skip")
            continue

        if soft:
            # Soft-compare fixtures are tracked as soft-diff (no strict golden).
            _bump(agg, product, profile, "soft_diff")
            continue

        if not golden_name:
            _bump(agg, product, profile, "skip")
            continue
        golden_path = fixtures / str(golden_name)
        if not golden_path.is_file():
            _bump(agg, product, profile, "skip")
            continue

        try:
            result = convert(
                tac_path.read_text(encoding="utf-8"),
                product=product,
                profile=profile,
                iwxxm_version=iwxxm_version,
            )
            if not result.ok or not result.xml:
                _bump(agg, product, profile, "fail")
                continue
            got = canonicalize_xml(result.xml)
            want = canonicalize_xml(golden_path.read_text(encoding="utf-8"))
            if got == want:
                _bump(agg, product, profile, "match")
            else:
                _bump(agg, product, profile, "fail")
        except Exception:
            _bump(agg, product, profile, "fail")

    return agg


def collect_quality_matrix_inventory(qm_root: Path) -> dict[tuple[str, str], list[int]]:
    """
    Inventory quality-matrix RuleCase YAML statuses (no engine execution).

    ready → match (pack slot ready), needs-fixture/oos → skip,
    other/unknown → soft_diff (explicit non-ready disposition).

    Parameters
    ----------
    qm_root : Path
        ``tests/quality_matrices`` root.

    Returns
    -------
    dict[tuple[str, str], list[int]]
        Aggregated inventory counts.
    """
    agg: dict[tuple[str, str], list[int]] = {}
    testdata = qm_root / "testdata"
    if not testdata.is_dir():
        return agg

    try:
        import yaml
    except ImportError:
        return agg

    for path in sorted(testdata.rglob("*.yml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        cases = data.get("cases")
        if not isinstance(cases, list):
            continue
        file_meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
        for case in cases:
            if not isinstance(case, dict):
                continue
            meta = case.get("meta") if isinstance(case.get("meta"), dict) else {}
            product = str(
                meta.get("product")
                or file_meta.get("product")
                or data.get("product")
                or path.parts[-2]
                or "?"
            ).upper()
            if product in {"METAR_SPECI", "METAR-SPECI"}:
                # Pilot pack scopes both; attribute under METAR for rollup clarity.
                product = "METAR"
            profile = str(
                meta.get("profile")
                or file_meta.get("profile")
                or data.get("profile")
                or "annex3"
            )
            status = str(case.get("status") or meta.get("status") or "ready").lower()
            if status in {"ready", "ok", "pass"}:
                # Inventory: ready slot (not a live engine outcome).
                _bump(agg, product, profile, "match")
            elif status in {"needs-fixture", "oos", "skip", "skipped"}:
                _bump(agg, product, profile, "skip")
            elif status in {"soft", "soft_diff", "soft-diff", "soft_compare"}:
                _bump(agg, product, profile, "soft_diff")
            elif status in {"fail", "failed", "error"}:
                _bump(agg, product, profile, "fail")
            else:
                _bump(agg, product, profile, "soft_diff")

    return agg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT_DEFAULT,
        help="Monorepo root (default: detected)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Directory for quality-summary.json artifacts",
    )
    args = parser.parse_args(argv)
    root: Path = args.repo_root
    out: Path = args.out

    annex3 = collect_golden_pack(
        root / "packages/tac2iwxxm/tests/fixtures/annex3_golden/manifest.json",
        default_profile="annex3",
    )
    _write_summary(
        out / "annex3-golden" / "quality-summary.json", "annex3-golden", annex3
    )

    iwxxm_us = collect_golden_pack(
        root / "packages/tac2iwxxm/tests/fixtures/iwxxm_us_golden/manifest.json",
        default_profile="iwxxm_us",
    )
    _write_summary(
        out / "iwxxm_us-golden" / "quality-summary.json",
        "iwxxm_us-golden",
        iwxxm_us,
    )

    qm = collect_quality_matrix_inventory(root / "tests/quality_matrices")
    _write_summary(
        out / "quality-matrix" / "quality-summary.json",
        "quality-matrix",
        qm,
    )

    total_rows = sum(len(_rows_from_agg(a)) for a in (annex3, iwxxm_us, qm))
    print(
        f"collect_quality_pr_stats: wrote summaries under {out} "
        f"({total_rows} product x profile rows)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
