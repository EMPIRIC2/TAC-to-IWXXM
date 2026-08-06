#!/usr/bin/env python3
"""
codes.wmo.int vs vendor codelist URI drift check (#859 / TC-EV038-008 / G6 residual).

Default (non-flake): compare Schematron RDF member concept URIs under the IWXXM pin
against ``iwxxm-codelists`` CSV entity rows for aviation registers that have both.

Optional ``--live``: fetch register RDF from codes.wmo.int with Linked-Data Accept
headers (not HTML browse). Network / 404 / HTML churn → soft-skip (exit 0) unless
``--strict-live``.

Drift lines always include stable ``http://codes.wmo.int/…`` URIs for #889 hand-off.

Examples::

  make codelist-uri-drift
  uv run python scripts/iwxxm/codelist_uri_drift.py
  uv run python scripts/iwxxm/codelist_uri_drift.py --live
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import urllib.error
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CONCEPT_ABOUT_RE = re.compile(
    r'<skos:Concept\s+rdf:about="(http://codes\.wmo\.int/[^"]+)"',
)
_HAND_OFF_889 = (
    "Hand-off [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889): "
    "when drift lists missing/changed notations used by TAC or encode, update "
    "RULE_SOURCE_URLS / fixtures / href policy from these stable URIs."
)

# SCH RDF ahead of iwxxm-codelists CSV on current pins (document; do not invent CSV).
# Clear entries when the next iwxxm-codelists sync includes these notations.
KNOWN_SCH_AHEAD_URIS: frozenset[str] = frozenset(
    {
        "http://codes.wmo.int/49-2/SpaceWxLocation/DAYSIDE",
        "http://codes.wmo.int/49-2/SpaceWxLocation/NIGHTSIDE",
    }
)


@dataclass(frozen=True)
class RegisterSpec:
    """One aviation register to compare SCH RDF ↔ vendor CSV (when present)."""

    register_uri: str
    sch_rdf_name: str
    csv_relpath: str | None  # None → SCH inventory only (no CSV in pin)


# Aviation-relevant SCH RDF ↔ CSV pairs on the current iwxxm-codelists pin.
# ``iwxxm/*`` SCH RDF has no CSV tree in this pin — inventory + optional live only.
REGISTER_SPECS: tuple[RegisterSpec, ...] = (
    RegisterSpec(
        "http://codes.wmo.int/common/nil",
        "codes.wmo.int-common-nil.rdf",
        "CSV/common/nil/nil_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather",
        "codes.wmo.int-49-2-AerodromePresentOrForecastWeather.rdf",
        "CSV/49-2/AerodromePresentOrForecastWeather/"
        "AerodromePresentOrForecastWeather_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/AerodromeRecentWeather",
        "codes.wmo.int-49-2-AerodromeRecentWeather.rdf",
        "CSV/49-2/AerodromeRecentWeather/AerodromeRecentWeather_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome",
        "codes.wmo.int-49-2-CloudAmountReportedAtAerodrome.rdf",
        "CSV/49-2/CloudAmountReportedAtAerodrome/"
        "CloudAmountReportedAtAerodrome_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/SigConvectiveCloudType",
        "codes.wmo.int-49-2-SigConvectiveCloudType.rdf",
        "CSV/49-2/SigConvectiveCloudType/SigConvectiveCloudType_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/SigWxPhenomena",
        "codes.wmo.int-49-2-SigWxPhenomena.rdf",
        "CSV/49-2/SigWxPhenomena/SigWxPhenomena_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/AirWxPhenomena",
        "codes.wmo.int-49-2-AirWxPhenomena.rdf",
        "CSV/49-2/AirWxPhenomena/AirWxPhenomena_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/WeatherCausingVisibilityReduction",
        "codes.wmo.int-49-2-WeatherCausingVisibilityReduction.rdf",
        "CSV/49-2/WeatherCausingVisibilityReduction/"
        "WeatherCausingVisibilityReduction_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/AviationColourCode",
        "codes.wmo.int-49-2-AviationColourCode.rdf",
        "CSV/49-2/AviationColourCode/AviationColourCode_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/MeteorologicalFeature",
        "codes.wmo.int-49-2-MeteorologicalFeature.rdf",
        "CSV/49-2/MeteorologicalFeature/MeteorologicalFeature_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/SpaceWxLocation",
        "codes.wmo.int-49-2-SpaceWxLocation.rdf",
        "CSV/49-2/SpaceWxLocation/SpaceWxLocation_entity.csv",
    ),
    RegisterSpec(
        "http://codes.wmo.int/49-2/SpaceWxPhenomena",
        "codes.wmo.int-49-2-SpaceWxPhenomena.rdf",
        "CSV/49-2/SpaceWxPhenomena/SpaceWxPhenomena_entity.csv",
    ),
    # SCH-only in this pin (no iwxxm/ CSV under iwxxm-codelists)
    RegisterSpec(
        "http://codes.wmo.int/iwxxm/nil",
        "codes.wmo.int-iwxxm-nil.rdf",
        None,
    ),
    RegisterSpec(
        "http://codes.wmo.int/iwxxm/AviationColourCode",
        "codes.wmo.int-iwxxm-AviationColourCode.rdf",
        None,
    ),
    RegisterSpec(
        "http://codes.wmo.int/iwxxm/MeteorologicalFeature",
        "codes.wmo.int-iwxxm-MeteorologicalFeature.rdf",
        None,
    ),
)


def load_sch_rdf_member_uris(path: Path) -> set[str]:
    """
    Extract ``skos:Concept`` ``rdf:about`` URIs from a Schematron RDF file.

    Parameters
    ----------
    path : Path
        Path to ``codes.wmo.int-*.rdf``.

    Returns
    -------
    set[str]
        Stable concept URIs.
    """
    text = path.read_text(encoding="utf-8")
    return set(_CONCEPT_ABOUT_RE.findall(text))


def load_csv_member_uris(path: Path) -> set[str]:
    """
    Load concept URIs from an ``*_entity.csv`` ``id`` column.

    Parameters
    ----------
    path : Path
        Codelist entity CSV path.

    Returns
    -------
    set[str]
        Stable concept URIs (non-empty ``id`` cells).
    """
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["id"].strip() for row in csv.DictReader(handle) if row.get("id", "").strip()}


def diff_uri_sets(left: Iterable[str], right: Iterable[str]) -> tuple[list[str], list[str]]:
    """
    Return sorted URIs only in left, only in right.

    Parameters
    ----------
    left, right : Iterable[str]
        URI sets to compare.

    Returns
    -------
    tuple[list[str], list[str]]
        ``(only_left, only_right)`` sorted.
    """
    left_s, right_s = set(left), set(right)
    return sorted(left_s - right_s), sorted(right_s - left_s)


def _sch_rdf_path(repo_root: Path, iwxxm_version: str, name: str) -> Path:
    return repo_root / "vendor" / "schemas" / "iwxxm" / iwxxm_version / "IWXXM" / "rule" / name


def _fetch_live_rdf(register_uri: str, timeout_s: float = 30.0) -> str | None:
    """Fetch register RDF; return body or None on soft failure."""
    # Prefer https browse host; concept URIs stay http://codes.wmo.int/…
    url = register_uri.replace("http://codes.wmo.int/", "https://codes.wmo.int/", 1)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/rdf+xml, application/xml;q=0.9, text/turtle;q=0.8, */*;q=0.1",
            "User-Agent": "TAC-to-IWXXM-codelist-uri-drift/1.0 (#859)",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            ctype = (resp.headers.get("Content-Type") or "").lower()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"  live soft-skip {register_uri}: {exc}", file=sys.stderr)
        return None
    if "html" in ctype and "rdf" not in ctype and "<skos:Concept" not in body:
        print(
            f"  live soft-skip {register_uri}: HTML/non-RDF response (avoid HTML churn)",
            file=sys.stderr,
        )
        return None
    return body


def summarize_drift(
    *,
    iwxxm_version: str,
    repo_root: Path,
    registers: tuple[RegisterSpec, ...] = REGISTER_SPECS,
    live: bool = False,
    strict_live: bool = False,
) -> tuple[str, bool]:
    """
    Build a human-readable drift report.

    Returns
    -------
    tuple[str, bool]
        Report text and whether the offline (and strict-live) checks passed.
    """
    lines: list[str] = [
        f"codes.wmo.int URI drift (#859 / TC-EV038-008) — IWXXM pin {iwxxm_version}",
        "Mode: SCH RDF ↔ iwxxm-codelists CSV (offline; non-flake)"
        + (" + optional live RDF" if live else ""),
        _HAND_OFF_889,
        "",
    ]
    ok = True
    codelists_root = repo_root / "vendor" / "schemas" / "iwxxm-codelists"

    for spec in registers:
        sch_path = _sch_rdf_path(repo_root, iwxxm_version, spec.sch_rdf_name)
        lines.append(f"## {spec.register_uri}")
        if not sch_path.is_file():
            lines.append(f"  ERROR missing SCH RDF: {sch_path.relative_to(repo_root)}")
            ok = False
            continue
        sch_uris = load_sch_rdf_member_uris(sch_path)
        lines.append(f"  SCH members: {len(sch_uris)} ({spec.sch_rdf_name})")

        if spec.csv_relpath is None:
            lines.append(
                "  CSV: none in iwxxm-codelists pin — SCH inventory only "
                "(prefer live RDF for `iwxxm/` registers)"
            )
            for uri in sorted(sch_uris)[:5]:
                lines.append(f"    sample: {uri}")
            if len(sch_uris) > 5:
                lines.append(f"    … +{len(sch_uris) - 5} more")
        else:
            csv_path = codelists_root / spec.csv_relpath
            if not csv_path.is_file():
                lines.append(f"  ERROR missing CSV: {csv_path.relative_to(repo_root)}")
                ok = False
                continue
            csv_uris = load_csv_member_uris(csv_path)
            only_sch, only_csv = diff_uri_sets(sch_uris, csv_uris)
            lines.append(f"  CSV members: {len(csv_uris)} ({spec.csv_relpath})")
            known_sch = [u for u in only_sch if u in KNOWN_SCH_AHEAD_URIS]
            new_sch = [u for u in only_sch if u not in KNOWN_SCH_AHEAD_URIS]
            if known_sch:
                lines.append("  KNOWN_LAG (SCH ahead of CSV pin; allowlisted):")
                for uri in known_sch:
                    lines.append(f"    only_in_SCH (known): {uri}")
            if new_sch or only_csv:
                ok = False
                lines.append("  DRIFT:")
                for uri in new_sch:
                    lines.append(f"    only_in_SCH: {uri}")
                for uri in only_csv:
                    lines.append(f"    only_in_CSV: {uri}")
            elif not known_sch:
                lines.append("  OK — SCH ↔ CSV URI sets match")
            else:
                lines.append("  OK — no new drift beyond known SCH-ahead allowlist")

        if live:
            body = _fetch_live_rdf(spec.register_uri)
            if body is None:
                if strict_live:
                    lines.append("  ERROR live fetch failed (--strict-live)")
                    ok = False
                else:
                    lines.append("  live: soft-skipped")
            else:
                # Reuse SCH regex on live RDF/XML (or Concept about= in turtle-ish)
                live_uris = set(_CONCEPT_ABOUT_RE.findall(body))
                if not live_uris:
                    live_uris = set(
                        re.findall(
                            r"(http://codes\.wmo\.int/[^\s\"'<>]+)",
                            body,
                        )
                    )
                    # keep only concept-depth URIs under this register
                    prefix = spec.register_uri.rstrip("/") + "/"
                    live_uris = {u.rstrip(".,;)") for u in live_uris if u.startswith(prefix)}
                only_sch_l, only_live = diff_uri_sets(sch_uris, live_uris)
                lines.append(f"  live members: {len(live_uris)}")
                if only_sch_l or only_live:
                    msg = "DRIFT vs live"
                    if strict_live:
                        ok = False
                        lines.append(f"  {msg}:")
                    else:
                        lines.append(f"  {msg} (advisory; not failing offline gate):")
                    for uri in only_sch_l[:20]:
                        lines.append(f"    only_in_SCH: {uri}")
                    for uri in only_live[:20]:
                        lines.append(f"    only_in_live: {uri}")
                else:
                    lines.append("  live OK — matches SCH URI set")
        lines.append("")

    lines.append("Disposition (D-S046-859): see RELEASE_LINE_ADOPTABILITY §codes.wmo.int drift")
    return "\n".join(lines) + "\n", ok


def main(argv: list[str] | None = None) -> int:
    """CLI entry for offline (+ optional live) codelist URI drift."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        default="2025-2",
        help="IWXXM vendor pin version directory (default: 2025-2)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Also compare against live codes.wmo.int RDF (soft-skip on HTML/network)",
    )
    parser.add_argument(
        "--strict-live",
        action="store_true",
        help="With --live, treat live fetch/drift failures as hard errors",
    )
    args = parser.parse_args(argv)
    report, ok = summarize_drift(
        iwxxm_version=args.version,
        repo_root=_REPO_ROOT,
        live=args.live or args.strict_live,
        strict_live=args.strict_live,
    )
    sys.stdout.write(report)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
