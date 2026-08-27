"""GML reference validation (internal xlink:href and bundled RDF codelists)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import lxml.etree as _lxml_etree

from iwxxm_validate.models import Issue

# lxml ships without complete type stubs; bind as Any for strict basedpyright.
etree: Any = _lxml_etree

logger = logging.getLogger(__name__)

_GML_NS = "http://www.opengis.net/gml/3.2"

_NAMESPACES = {
    "gml": _GML_NS,
    "xlink": "http://www.w3.org/1999/xlink",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
}

_LAYER = "gml"


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


def _load_rdf_elements(rdf_path: Path, cache: dict[str, set[str]]) -> set[str]:
    key = str(rdf_path)
    if key in cache:
        return cache[key]
    if not rdf_path.is_file():
        return set()
    try:
        rdf_root = etree.parse(str(rdf_path)).getroot()
        elements: set[str] = set()
        for desc in rdf_root.xpath("//rdf:Description", namespaces=_NAMESPACES):
            about = desc.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about")
            if about:
                elements.add(about.split("#", 1)[1] if "#" in about else about)
        cache[key] = elements
        return elements
    except Exception as exc:
        logger.warning("Failed to parse RDF %s: %s", rdf_path, exc)
        return set()


def validate_gml_references(
    xml_content: str,
    *,
    codelists_dir: Path | None = None,
) -> list[Issue]:
    """
    Validate GML internal ``#id`` references and external RDF codelist hrefs.

    Parameters
    ----------
    xml_content :
        IWXXM XML document.
    codelists_dir :
        Directory containing bundled ``codes.wmo.int-*.rdf`` files.

    Returns
    -------
    list[Issue]
        Empty when all references resolve.
    """
    issues: list[Issue] = []
    rdf_cache: dict[str, set[str]] = {}

    try:
        xml_tree = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError as exc:
        return [
            _issue(
                severity="error",
                code="XML_SYNTAX_ERROR",
                message=f"XML is not well-formed: {exc}",
            )
        ]

    id_registry: dict[str, list[str]] = {}
    for elem in xml_tree.xpath("//*[@gml:id]", namespaces=_NAMESPACES):
        gml_id = elem.get(f"{{{_GML_NS}}}id")
        if not gml_id:
            continue
        xpath = xml_tree.getroottree().getpath(elem)
        id_registry.setdefault(gml_id, []).append(xpath)

    for gml_id, locations in id_registry.items():
        if len(locations) > 1:
            issues.append(
                _issue(
                    severity="error",
                    code="DUPLICATE_GML_ID",
                    message=(
                        f"Duplicate gml:id '{gml_id}' found at {len(locations)} locations: {', '.join(locations)}"
                    ),
                )
            )

    references: list[tuple[str, str, str]] = []
    for elem in xml_tree.xpath("//*[@xlink:href]", namespaces=_NAMESPACES):
        href = elem.get("{http://www.w3.org/1999/xlink}href")
        if href and href.startswith("#"):
            references.append((href, href[1:], xml_tree.getroottree().getpath(elem)))

    for href, target_id, xpath in references:
        if target_id not in id_registry:
            issues.append(
                _issue(
                    severity="error",
                    code="BROKEN_INTERNAL_REFERENCE",
                    message=(
                        f"Broken internal reference: xlink:href='{href}' points to non-existent gml:id '{target_id}'"
                    ),
                    location=xpath,
                )
            )

    if codelists_dir is not None:
        for elem in xml_tree.xpath("//*[@xlink:href]", namespaces=_NAMESPACES):
            href = elem.get("{http://www.w3.org/1999/xlink}href")
            if not href or href.startswith("#") or "#" not in href:
                continue
            xpath = xml_tree.getroottree().getpath(elem)
            rdf_file, element_id = href.split("#", 1)
            rdf_path = codelists_dir / rdf_file
            elements = _load_rdf_elements(rdf_path, rdf_cache)
            if not elements:
                issues.append(
                    _issue(
                        severity="warning",
                        code="UNRESOLVABLE_EXTERNAL_REFERENCE",
                        message=f"Could not resolve external reference: xlink:href='{href}'",
                        location=xpath,
                    )
                )
            elif element_id not in elements:
                issues.append(
                    _issue(
                        severity="error",
                        code="BROKEN_EXTERNAL_REFERENCE",
                        message=(
                            f"Broken external reference: xlink:href='{href}' - "
                            f"element '{element_id}' not found in {rdf_file}"
                        ),
                        location=xpath,
                    )
                )

    return issues


__all__ = ["validate_gml_references"]
