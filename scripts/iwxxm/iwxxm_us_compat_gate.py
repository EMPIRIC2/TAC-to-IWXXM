#!/usr/bin/env python3
"""
iwxxm-us compatibility gate for WMO default moves (#853 / TC-EV038-006).

Prints SoT default + iwxxm-us pin, reminds of lag policy (D-S046-853), and optionally
runs convert+validate smoke for annex3 default and iwxxm_us against that default.

Examples::

  make iwxxm-us-compat-smoke
  uv run python scripts/iwxxm/iwxxm_us_compat_gate.py --smoke
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
LAG_POLICY_ID = "D-S046-853"
LAG_POLICY_SUMMARY = (
    "Ship WMO-only first — bump annex3 DEFAULT_VERSION when WMO adopt is ready; "
    "if iwxxm_us smoke fails, record lag in the sync PR, keep US on last-known-good "
    "WMO base until NWS pin catches up, and open a child issue if needed. "
    "Do not block ICAO/Annex 3 adopt on US lag."
)


def load_manifest_us_pin(manifest_path: Path) -> dict[str, Any]:
    """
    Load the ``iwxxm-us`` bundle pin from ``vendor/manifest.json``.

    Parameters
    ----------
    manifest_path : Path
        Path to the vendor manifest JSON.

    Returns
    -------
    dict[str, Any]
        Bundle entry (tag, local_path, source_url, …).

    Raises
    ------
    SystemExit
        If the file or ``iwxxm-us`` bundle is missing.
    """
    if not manifest_path.is_file():
        raise SystemExit(f"missing vendor manifest: {manifest_path}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    bundles = data.get("bundles") or {}
    us = bundles.get("iwxxm-us")
    if not isinstance(us, dict):
        raise SystemExit("vendor/manifest.json missing bundles.iwxxm-us")
    return us


def build_gate_report(
    *,
    default_version: str,
    manifest_path: Path,
) -> str:
    """
    Build a human-readable gate summary for sync PRs.

    Parameters
    ----------
    default_version : str
        Python SoT ``DEFAULT_VERSION``.
    manifest_path : Path
        Vendor manifest path.

    Returns
    -------
    str
        Multi-line report including lag policy id and disposition guidance.
    """
    us = load_manifest_us_pin(manifest_path)
    tag = str(us.get("tag", "?"))
    local = str(us.get("local_path", "?"))
    source = str(us.get("source_url", ""))
    lines = [
        "iwxxm-us compatibility gate (#853 / TC-EV038-006)",
        f"IWXXM default (SoT): {default_version}",
        f"iwxxm-us pin: {tag} ({local})",
    ]
    if source:
        lines.append(f"iwxxm-us source: {source}")
    lines.extend(
        [
            f"Lag policy ({LAG_POLICY_ID}): Ship WMO-only first",
            LAG_POLICY_SUMMARY,
            "Checklist: confirm NWS still targets this WMO base; run smoke; "
            "on US fail → document lag in sync PR (do not block WMO default).",
        ]
    )
    return "\n".join(lines) + "\n"


def _default_version_from_sot() -> str:
    sys.path.insert(0, str(_REPO_ROOT / "apps" / "backend" / "src"))
    from config import iwxxm_versions as versions  # type: ignore[import-not-found]

    return str(versions.DEFAULT_VERSION)


def _run_smoke() -> int:
    """Run annex3 + iwxxm_us convert/validate smokes against SoT default fixtures."""
    print(
        "==> iwxxm_us convert+validate smoke (TC-F6-003 METAR/SPECI subset)",
        flush=True,
    )
    us_rc = subprocess.call(
        [
            "uv",
            "run",
            "pytest",
            "packages/tac2iwxxm/tests/test_tc_f6_003_metar_speci_iwxxm_us.py"
            "::test_tc_f6_003_m_parse_xsd_sch_iwxxm_us",
            "-k",
            "metar_us_ao2_slp or speci_us_ao2",
            "--no-cov",
            "-q",
            "--tb=short",
        ],
        cwd=_REPO_ROOT,
    )
    if us_rc != 0:
        return us_rc

    annex_path = "packages/tac2iwxxm/tests/test_tc_f6_020_021_metar_speci_annex3.py"
    if not (_REPO_ROOT / annex_path).is_file():
        print("==> annex3 smoke: module missing; US smoke only", flush=True)
        return 0

    print("==> annex3 default convert+validate smoke (METAR subset)", flush=True)
    return subprocess.call(
        [
            "uv",
            "run",
            "pytest",
            f"{annex_path}::test_tc_f6_020_m_parse_xsd_sch_annex3",
            "-k",
            "metar",
            "--no-cov",
            "-q",
            "--tb=short",
            "--maxfail=3",
        ],
        cwd=_REPO_ROOT,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry: print gate report; optionally run smoke tests."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run annex3 + iwxxm_us convert/validate smoke after the report",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=_REPO_ROOT / "vendor" / "manifest.json",
        help="Path to vendor/manifest.json",
    )
    args = parser.parse_args(argv)

    default_version = _default_version_from_sot()
    report = build_gate_report(
        default_version=default_version,
        manifest_path=args.manifest,
    )
    sys.stdout.write(report)
    sys.stdout.flush()
    if not args.smoke:
        return 0
    return _run_smoke()


if __name__ == "__main__":
    raise SystemExit(main())
