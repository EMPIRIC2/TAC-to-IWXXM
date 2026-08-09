"""Offline WMO membership sets for tac-validate (S059 / EV-050 / AC1).

Harvests notations from ``vendor/schemas/iwxxm-codelists`` CSV entity files and
pin RDF for nil dual paths. Never fetches live ``codes.wmo.int`` HTML.
"""

from __future__ import annotations

import csv
import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, cast

_PACKAGE_DIR = Path(__file__).resolve().parent
_PACKAGE_ROOT = _PACKAGE_DIR.parents[1]
_DEFAULT_REPO_ROOT = _PACKAGE_ROOT.parents[1]
_ARTIFACT = _PACKAGE_DIR / "data" / "wmo_membership.json"

_CONCEPT_ABOUT = re.compile(r'<skos:Concept rdf:about="([^"]+)"')

# v1 families — D-S059-families=1a (+ SpaceWxPhenomena for AC4 fixtures).
FAMILY_CSV: Final[dict[str, str]] = {
    "weather_306_4678": "CSV/306/4678/4678_entity.csv",
    "present_or_forecast_weather": (
        "CSV/49-2/AerodromePresentOrForecastWeather/AerodromePresentOrForecastWeather_entity.csv"
    ),
    "recent_weather": "CSV/49-2/AerodromeRecentWeather/AerodromeRecentWeather_entity.csv",
    "cloud_amount": ("CSV/49-2/CloudAmountReportedAtAerodrome/CloudAmountReportedAtAerodrome_entity.csv"),
    "cloud_type": "CSV/49-2/SigConvectiveCloudType/SigConvectiveCloudType_entity.csv",
    "sigwx_phenomena": "CSV/49-2/SigWxPhenomena/SigWxPhenomena_entity.csv",
    "airwx_phenomena": "CSV/49-2/AirWxPhenomena/AirWxPhenomena_entity.csv",
    "spacewx_phenomena": "CSV/49-2/SpaceWxPhenomena/SpaceWxPhenomena_entity.csv",
    "nil_common": "CSV/common/nil/nil_entity.csv",
}

FAMILY_RDF: Final[dict[str, tuple[str, str]]] = {
    # family_key -> (rdf filename under IWXXM/rule/, register URI)
    "nil_common_rdf": (
        "codes.wmo.int-common-nil.rdf",
        "http://codes.wmo.int/common/nil",
    ),
    "nil_iwxxm_rdf": (
        "codes.wmo.int-iwxxm-nil.rdf",
        "http://codes.wmo.int/iwxxm/nil",
    ),
}

V1_FAMILY_KEYS: Final[tuple[str, ...]] = (
    "weather_306_4678",
    "present_or_forecast_weather",
    "recent_weather",
    "cloud_amount",
    "cloud_type",
    "sigwx_phenomena",
    "airwx_phenomena",
    "nil_common",
    "nil_common_rdf",
    "nil_iwxxm_rdf",
)


def repo_root() -> Path:
    """
    Return monorepo root containing ``vendor/schemas``.

    Honours ``TAC_VALIDATE_REPO_ROOT`` when set.
    """
    env = os.environ.get("TAC_VALIDATE_REPO_ROOT")
    if env:
        return Path(env).resolve()
    return _DEFAULT_REPO_ROOT


def membership_artifact_path() -> Path:
    """Path to the committed generated membership JSON artifact."""
    return _ARTIFACT


def _csv_notations(path: Path) -> frozenset[str]:
    if not path.is_file():
        raise FileNotFoundError(path)
    out: set[str] = set()
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or "notation" not in reader.fieldnames:
            raise ValueError(f"CSV missing notation column: {path}")
        for row in reader:
            notation = (row.get("notation") or "").strip()
            if notation:
                out.add(notation)
    if not out:
        raise ValueError(f"no notations in {path}")
    return frozenset(out)


def _rdf_notations(path: Path, *, register_uri: str) -> frozenset[str]:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    prefix = register_uri.rstrip("/") + "/"
    out: set[str] = set()
    for about in _CONCEPT_ABOUT.findall(text):
        if about.startswith(prefix):
            out.add(about[len(prefix) :])
    if not out:
        raise ValueError(f"no skos:Concept members under {register_uri} in {path}")
    return frozenset(out)


def harvest_membership(
    *,
    root: Path | None = None,
    iwxxm_version: str = "2025-2",
) -> dict[str, frozenset[str]]:
    """
    Harvest membership sets from offline vendor CSV (+ pin RDF for nil).

    Parameters
    ----------
    root : Path, optional
        Monorepo root; default :func:`repo_root`.
    iwxxm_version : str, optional
        IWXXM pin line for RDF under ``vendor/schemas/iwxxm/{version}/IWXXM/rule``.

    Returns
    -------
    dict[str, frozenset[str]]
        Family key → notations.
    """
    base = root if root is not None else repo_root()
    codelists = base / "vendor" / "schemas" / "iwxxm-codelists"
    rule_dir = base / "vendor" / "schemas" / "iwxxm" / iwxxm_version / "IWXXM" / "rule"
    result: dict[str, frozenset[str]] = {}
    for key, rel in FAMILY_CSV.items():
        result[key] = _csv_notations(codelists / rel)
    for key, (rdf_name, register_uri) in FAMILY_RDF.items():
        result[key] = _rdf_notations(rule_dir / rdf_name, register_uri=register_uri)
    return result


def write_membership_artifact(
    sets: dict[str, frozenset[str]] | None = None,
    *,
    root: Path | None = None,
    iwxxm_version: str = "2025-2",
    dest: Path | None = None,
) -> Path:
    """
    Write sorted JSON membership artifact for CI / runtime load.

    Returns
    -------
    Path
        Path written.
    """
    harvested = sets if sets is not None else harvest_membership(root=root, iwxxm_version=iwxxm_version)
    path = dest if dest is not None else membership_artifact_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "source": "vendor/schemas/iwxxm-codelists (+ pin RDF for nil)",
        "iwxxm_version": iwxxm_version,
        "offline_only": True,
        "families": {k: sorted(v) for k, v in sorted(harvested.items())},
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


@lru_cache(maxsize=1)
def load_membership_sets() -> dict[str, frozenset[str]]:
    """
    Load committed membership artifact (offline, no network).

    Returns
    -------
    dict[str, frozenset[str]]
        Family key → notations.

    Raises
    ------
    FileNotFoundError
        When the artifact is missing (run harvest / ``make membership-regen``).
    """
    path = membership_artifact_path()
    if not path.is_file():
        raise FileNotFoundError(path)
    payload = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    raw_families = payload.get("families")
    if not isinstance(raw_families, dict):
        raise ValueError(f"membership artifact missing families object: {path}")
    families = cast(dict[str, list[object]], raw_families)
    return {key: frozenset(str(item) for item in notations) for key, notations in families.items()}


def is_member(family: str, notation: str, *, sets: dict[str, frozenset[str]] | None = None) -> bool:
    """Return True if ``notation`` is in the named family set."""
    table = sets if sets is not None else load_membership_sets()
    members = table.get(family)
    if members is None:
        raise KeyError(f"unknown membership family: {family!r}")
    return notation in members


def normalize_register_notation(token: str) -> str:
    """
    Map TAC spaced phenomena to register underscore form.

    Parameters
    ----------
    token : str
        TAC fragment (e.g. ``ISOL TS`` or ``ISOL_TS``).

    Returns
    -------
    str
        Underscore-joined notation (e.g. ``ISOL_TS``).
    """
    return "_".join(token.strip().split())


def is_member_normalized(
    family: str,
    notation: str,
    *,
    sets: dict[str, frozenset[str]] | None = None,
) -> bool:
    """
    Return True if ``notation`` or its underscore-normalized form is in ``family``.

    Used for AIRMET/SIGMET phenomena where TAC may use spaces (``ISOL TS``) while
    ``codes.wmo.int`` / vendor CSV notations use underscores (``ISOL_TS``).
    """
    table = sets if sets is not None else load_membership_sets()
    if is_member(family, notation, sets=table):
        return True
    normalized = normalize_register_notation(notation)
    if normalized != notation and is_member(family, normalized, sets=table):
        return True
    return False
