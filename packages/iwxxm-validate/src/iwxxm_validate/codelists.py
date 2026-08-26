"""Offline WMO codelist reference validation against bundled RDF files."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import lxml.etree as _lxml_etree

from iwxxm_validate.models import Issue

# lxml ships without complete type stubs; bind as Any for strict basedpyright.
etree: Any = _lxml_etree

logger = logging.getLogger(__name__)

_LAYER = "codelists"

_RDF_NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
}

_XLINK_NS = {"xlink": "http://www.w3.org/1999/xlink"}


def _issue(
    *,
    severity: str,
    code: str,
    message: str,
    location: str | None = None,
) -> Issue:
    return Issue(
        severity=severity,
        code=code,
        message=message,
        layer=_LAYER,
        location=location,
    )


def _load_codelist_cache(codelists_dir: Path) -> dict[str, set[str]]:
    cache: dict[str, set[str]] = {}
    if not codelists_dir.is_dir():
        return cache
    for rdf_file in codelists_dir.glob("*.rdf"):
        codelist_name = rdf_file.stem.split("-")[-1] if "-" in rdf_file.stem else rdf_file.stem
        codes: set[str] = set()
        try:
            root = ET.parse(rdf_file).getroot()
            for concept in root.findall(".//skos:Concept", _RDF_NS):
                about = concept.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about")
                if about:
                    codes.add(about.split("/")[-1])
                for label in concept.findall("skos:prefLabel", _RDF_NS):
                    if label.text:
                        codes.add(label.text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to parse codelist RDF %s: %s", rdf_file.name, exc)
            continue
        if codes:
            cache[codelist_name] = codes
    return cache


def validate_codelist_references(
    xml_content: str,
    *,
    codelists_dir: Path,
) -> list[Issue]:
    """
    Validate ``xlink:href`` references to WMO code lists (offline RDF only).

    Parameters
    ----------
    xml_content :
        IWXXM XML document.
    codelists_dir :
        Directory containing bundled ``codes.wmo.int-*.rdf`` files.

    Returns
    -------
    list[Issue]
        Findings for unresolved or invalid codelist references.
    """
    issues: list[Issue] = []
    cache = _load_codelist_cache(codelists_dir)

    try:
        xml_tree = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError as exc:
        return [
            _issue(
                severity="error",
                code="XML_SYNTAX_ERROR",
                message=f"XML parsing failed: {exc}",
            )
        ]

    for elem in xml_tree.xpath("//*[@xlink:href]", namespaces=_XLINK_NS):
        href = elem.get("{http://www.w3.org/1999/xlink}href")
        if not href or "codes.wmo.int" not in href:
            continue
        xpath = xml_tree.getroottree().getpath(elem)
        url_parts = href.rstrip("/").split("/")
        if len(url_parts) >= 6:
            codelist_name = url_parts[-2]
            potential_code = url_parts[-1]
        else:
            codelist_name = url_parts[-1]
            potential_code = url_parts[-1]
        if codelist_name not in cache:
            issues.append(
                _issue(
                    severity="warning",
                    code="CODELIST_NOT_FOUND",
                    message=(f"Code list '{codelist_name}' not found in loaded RDF files (offline validation only)"),
                    location=xpath,
                )
            )
            continue
        if potential_code not in cache[codelist_name]:
            sample = ", ".join(sorted(cache[codelist_name])[:20])
            issues.append(
                _issue(
                    severity="error",
                    code="INVALID_CODELIST_VALUE",
                    message=(
                        f"Invalid code '{potential_code}' for codelist '{codelist_name}'. Valid codes include: {sample}"
                    ),
                    location=xpath,
                )
            )

    return issues


__all__ = ["validate_codelist_references"]
