#!/usr/bin/env python3
"""Generate precomputed official-corpus quality metrics for F7.q / EV-054.

Writes ``apps/backend/data/quality_metrics/corpus_metrics.json`` from the WMO
official TAC inventory, annex3 mirrors, vendor IWXXM examples, and engine
calls (convert / decode / lint / validate).

Usage (repo root)::

    uv run python scripts/ci/generate_quality_metrics.py
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURES = _REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures"
_VENDOR_EXAMPLES = (
    _REPO_ROOT / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples"
)
_OUT_DIR = _REPO_ROOT / "apps" / "backend" / "data" / "quality_metrics"
_OUT_PATH = _OUT_DIR / "corpus_metrics.json"
_IWXXM_PIN = "2025-2"
_PROFILE = "annex3"

# Prefer TAC catalog tier by stem (wmoPass over wmoReference when both exist).
_STEM_TIER: dict[str, str] = {
    "metar-A3-1": "wmoPass",
    "speci-A3-2": "wmoPass",
    "taf-A5-1": "wmoPass",
    "taf-A5-2": "wmoPass",
    "sigmet-A6-1a-TS": "wmoPass",
    "sigmet-A6-1b-CNL": "wmoPass",
    "sigmet-VA-EGGX": "wmoPass",
    "sigmet-multi-location-VA": "wmoPass",
    "sigmet-A6-2-TC": "wmoPass",
    "airmet-A6-1a-TS": "wmoPass",
    "va-advisory-A7-2": "wmoPass",
    "tc-advisory-A2-2": "wmoPass",
    "spacewx-A7-3": "wmoReference",
    "vona-A7-1": "wmoPass",
    "spacewx-A7-4": "wmoReference",
    "spacewx-A7-5": "wmoReference",
    "metar-NIL-collect": "wmoReference",
    "taf-NIL-collect": "wmoReference",
}

_STEM_PRODUCT_FALLBACK: dict[str, str] = {
    "spacewx-A7-4": "SWXA",
    "spacewx-A7-5": "SWXA",
    "metar-NIL-collect": "METAR",
    "taf-NIL-collect": "TAF",
}


def _ensure_imports() -> None:
    """Add fixture path so inventory module imports like package tests."""
    sys.path.insert(0, str(_FIXTURES))


def _product_key(product: str) -> str:
    return product.strip().lower()


def _serialize_lint_issues(issues: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for issue in issues:
        out.append(
            {
                "severity": issue.severity,
                "code": issue.code,
                "message": issue.message,
                "location": getattr(issue, "location", None),
                "start": getattr(issue, "start", None),
                "end": getattr(issue, "end", None),
            }
        )
    return out


def _serialize_validate_issues(issues: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for issue in issues:
        out.append(
            {
                "severity": issue.severity,
                "code": issue.code,
                "message": issue.message,
                "layer": getattr(issue, "layer", None),
            }
        )
    return out


def _error_count(issues: list[dict[str, Any]]) -> int:
    return sum(1 for i in issues if i.get("severity") == "error")


def _build_summaries(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "match_pass": 0,
            "match_fail": 0,
            "residual_nonempty": 0,
            "lint_fail": 0,
            "validate_fail": 0,
            "deferred_gaps": 0,
        }
    )
    for row in files:
        product = row["product"]
        b = buckets[product]
        if row["deferred"]:
            b["deferred_gaps"] += 1
            continue
        if row["match_status"] == "equal":
            b["match_pass"] += 1
        else:
            b["match_fail"] += 1
        if row["residual_count"] > 0:
            b["residual_nonempty"] += 1
        if row["lint_error_count"] > 0:
            b["lint_fail"] += 1
        if row["validate_error_count"] > 0:
            b["validate_fail"] += 1
    return [
        {"product": product, **counts}
        for product, counts in sorted(buckets.items(), key=lambda kv: kv[0])
    ]


def generate_corpus_metrics() -> dict[str, Any]:
    """
    Build the full corpus metrics document (list + per-stem details).

    Returns
    -------
    dict[str, Any]
        Artifact matching [Corpus: api] quality-metrics shape plus ``details``.
    """
    _ensure_imports()
    from iwxxm_validate import validate_for_quality_metrics
    from iwxxm_validate.c14n import c14n_equal
    from tac_validate import lint
    from wmo_official_tac_inventory import (
        OFFICIAL_TAC_PEERS,
        annex3_path,
    )

    from tac2iwxxm import convert, decode_tac

    details: dict[str, dict[str, Any]] = {}
    files: list[dict[str, Any]] = []

    for peer in OFFICIAL_TAC_PEERS:
        product_raw = peer.product or _STEM_PRODUCT_FALLBACK.get(peer.stem, "UNKNOWN")
        product = _product_key(product_raw)
        deferred = peer.disposition == "deferred"
        tier = "deferred" if deferred else _STEM_TIER.get(peer.stem, "unknown")

        if deferred:
            detail = {
                "stem": peer.stem,
                "product": product,
                "tier": tier,
                "deferred": True,
                "deferral_reason": peer.deferral_reason,
                "tac": "",
                "official_xml": "",
                "converted_xml": "",
                "match_status": "deferred",
                "residuals": [],
                "lint_issues": [],
                "validate_issues": [],
            }
            files.append(
                {
                    "stem": peer.stem,
                    "product": product,
                    "tier": tier,
                    "match_status": "deferred",
                    "residual_count": 0,
                    "lint_error_count": 0,
                    "validate_error_count": 0,
                    "deferred": True,
                }
            )
            details[peer.stem] = detail
            continue

        tac_path = annex3_path(peer)
        tac = tac_path.read_text(encoding="utf-8")
        official_path = _VENDOR_EXAMPLES / f"{peer.stem}.xml"
        if not official_path.is_file():
            # Fallback: annex3 golden XML when vendor example missing
            golden = _FIXTURES / "annex3_golden" / f"{peer.catalog_id}.golden.xml"
            if not golden.is_file():
                raise FileNotFoundError(
                    f"No official XML for {peer.stem}: tried {official_path} and {golden}"
                )
            official_xml = golden.read_text(encoding="utf-8")
        else:
            official_xml = official_path.read_text(encoding="utf-8")

        conv = convert(
            tac,
            product=product_raw,
            profile=_PROFILE,
            iwxxm_version=_IWXXM_PIN,
        )
        converted_xml = conv.xml or ""
        if not conv.ok or not converted_xml:
            match_status = "convert_fail"
        elif c14n_equal(converted_xml, official_xml):
            match_status = "equal"
        else:
            match_status = "unequal"

        decode = decode_tac(tac, product=product_raw)
        residuals = [
            {"start": r.start, "end": r.end, "text": r.text} for r in decode.residuals
        ]

        lint_report = lint(tac, product=product_raw, profile=_PROFILE)
        lint_issues = _serialize_lint_issues(lint_report.issues)

        if converted_xml:
            val_report = validate_for_quality_metrics(
                converted_xml,
                iwxxm_version=_IWXXM_PIN,
                profile=_PROFILE,
            )
            validate_issues = _serialize_validate_issues(val_report.issues)
        else:
            validate_issues = []

        detail = {
            "stem": peer.stem,
            "product": product,
            "tier": tier,
            "deferred": False,
            "tac": tac,
            "official_xml": official_xml,
            "converted_xml": converted_xml,
            "match_status": match_status,
            "residuals": residuals,
            "lint_issues": lint_issues,
            "validate_issues": validate_issues,
        }
        files.append(
            {
                "stem": peer.stem,
                "product": product,
                "tier": tier,
                "match_status": match_status,
                "residual_count": len(residuals),
                "lint_error_count": _error_count(lint_issues),
                "validate_error_count": _error_count(validate_issues),
                "deferred": False,
            }
        )
        details[peer.stem] = detail

    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "iwxxm_pin": _IWXXM_PIN,
        "summaries": _build_summaries(files),
        "files": files,
        "details": details,
    }


def main() -> int:
    """Write corpus_metrics.json and print a short summary."""
    doc = generate_corpus_metrics()
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    _OUT_PATH.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    n_files = len(doc["files"])
    n_deferred = sum(1 for f in doc["files"] if f["deferred"])
    print(
        f"Wrote {_OUT_PATH.relative_to(_REPO_ROOT)} ({n_files} stems, {n_deferred} deferred)"
    )
    for summary in doc["summaries"]:
        print(
            f"  {summary['product']}: match_pass={summary['match_pass']} "
            f"match_fail={summary['match_fail']} deferred={summary['deferred_gaps']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
