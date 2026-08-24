"""CA_ECCC MSC datamart ops corpus helpers (EV-072 M2 / #1036).

Offline manifest loading and COLLECT envelope extraction for layer-6 packaging
checks on operational IWXXM fixtures.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC]
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import lxml.etree as _lxml_etree

etree: Any = _lxml_etree

_COLLECT_NS = "http://def.wmo.int/collect/2014"
_IWXXM_NS = "http://icao.int/iwxxm/3.0"
_CA_EXTENSION_NS = "https://dd.meteo.gc.ca/today/aviation/iwxxm/"
_OPS_IWXXM_ROOTS = frozenset({"METAR", "SPECI", "TAF", "AIRMET"})
_CA_SUBSTITUTION_ROOTS = frozenset({"LWIS", "SAWR"})
_MSC_FILENAME_RE = re.compile(r"^A_[A-Z]{2}[A-Z]{2}\d{2}[A-Z]{4}\d{6}(?:[A-Z0-9]{3})?_C_[A-Z]{4}_\d{14}\.xml$")


def extract_iwxxm_from_collect(xml_content: str) -> str | None:
    """
    Return inner IWXXM product XML from a COLLECT envelope, or the input unchanged.

    Parameters
    ----------
    xml_content :
        Full datamart file (COLLECT-wrapped or standalone IWXXM).

    Returns
    -------
    str | None
        Serialized inner product when found; ``None`` when XML is invalid.
    """
    try:
        root = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError:
        return None

    qname = etree.QName(root)
    if qname.localname == "MeteorologicalBulletin" and qname.namespace == _COLLECT_NS:
        for child in root:
            child_qname = etree.QName(child)
            if child_qname.localname != "meteorologicalInformation":
                continue
            for product in child:
                product_qname = etree.QName(product)
                if product_qname.namespace == _IWXXM_NS and product_qname.localname in _OPS_IWXXM_ROOTS:
                    return etree.tostring(product, encoding="unicode")
        return None

    if qname.namespace == _IWXXM_NS and qname.localname in _OPS_IWXXM_ROOTS:
        return xml_content
    if qname.namespace == _CA_EXTENSION_NS and qname.localname in _CA_SUBSTITUTION_ROOTS:
        return xml_content
    return None


def msc_filename_from_url(url: str) -> str | None:
    """
    Extract MSC datamart filename from a source URL path.

    Parameters
    ----------
    url :
        HTTPS URL ending with ``A_….xml``.

    Returns
    -------
    str | None
        Basename when it matches the MSC exchange pattern.
    """
    name = url.rstrip("/").rsplit("/", 1)[-1]
    if _MSC_FILENAME_RE.match(name):
        return name
    return None


def load_ops_manifest(path: Path) -> dict[str, Any]:
    """
    Load and validate the CA_ECCC ops manifest JSON.

    Parameters
    ----------
    path :
        Path to ``ops_manifest.json``.

    Returns
    -------
    dict[str, Any]
        Parsed manifest with ``cases`` list.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "cases" not in payload or not isinstance(payload["cases"], list):
        raise ValueError(f"invalid ops manifest (missing cases): {path}")
    return payload


def manifest_checksum(manifest: dict[str, Any]) -> str:
    """
    Stable SHA-256 of manifest content excluding the checksum field itself.

    Parameters
    ----------
    manifest :
        Ops manifest dict.

    Returns
    -------
    str
        Hex digest suitable for TC-EV072-007 pin-date reproducibility checks.
    """
    copy = dict(manifest)
    copy.pop("manifest_sha256", None)
    canonical = json.dumps(copy, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def ops_fixture_root(repo_root: Path | None = None) -> Path:
    """
    Return the CA_ECCC profile fixture root.

    Parameters
    ----------
    repo_root :
        Repository root; defaults to four parents above this module.

    Returns
    -------
    Path
        ``packages/tac2iwxxm/tests/fixtures/profiles/CA_ECCC``.
    """
    root = repo_root or Path(__file__).resolve().parents[4]
    return root / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "profiles" / "CA_ECCC"


__all__ = [
    "extract_iwxxm_from_collect",
    "load_ops_manifest",
    "manifest_checksum",
    "msc_filename_from_url",
    "ops_fixture_root",
]
