"""CA_ECCC document root and extension-block helpers."""

from __future__ import annotations

from typing import Any

import lxml.etree as _lxml_etree

CA_EXTENSION_NS = "https://dd.meteo.gc.ca/today/aviation/iwxxm/"
CA_SUBSTITUTION_ROOTS = frozenset({"LWIS", "SAWR"})
WMO_PRODUCT_ROOTS = frozenset({"METAR", "SPECI", "TAF", "AIRMET"})
_IWXXM_NS = "http://icao.int/iwxxm/3.0"

# lxml ships without complete type stubs; bind as Any for strict basedpyright.
etree: Any = _lxml_etree


def document_root_name(xml_content: str) -> tuple[str | None, str | None]:
    """
    Return ``(local_name, namespace)`` for the document root element.

    Parameters
    ----------
    xml_content : str
        IWXXM XML document.

    Returns
    -------
    tuple[str or None, str or None]
        Root local name and namespace URI, or ``(None, None)`` on syntax error.
    """
    try:
        root = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError:
        return None, None
    qname = etree.QName(root)
    return qname.localname, qname.namespace


def is_ca_substitution_root(local_name: str | None, namespace: str | None) -> bool:
    """
    Return whether the root is a Canadian LWIS/SAWR substitution group root.

    Parameters
    ----------
    local_name : str or None
        Root local name.
    namespace : str or None
        Root namespace URI.

    Returns
    -------
    bool
        ``True`` for CA extension substitution roots.
    """
    return namespace == CA_EXTENSION_NS and local_name in CA_SUBSTITUTION_ROOTS


def extract_ca_extension_blocks(xml_content: str) -> list[str]:
    """
    Serialize CA extension children under ``iwxxm:extension`` blocks.

    Parameters
    ----------
    xml_content : str
        IWXXM XML document.

    Returns
    -------
    list[str]
        Serialized CA extension element XML fragments.
    """
    try:
        root = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError:
        return []

    blocks: list[str] = []
    for extension in root.iter(f"{{{_IWXXM_NS}}}extension"):
        for child in extension:
            if etree.QName(child).namespace != CA_EXTENSION_NS:
                continue
            blocks.append(etree.tostring(child, encoding="unicode"))
    return blocks


def wrap_ca_lwis_extension_block(fragment_xml: str) -> str:
    """
    Wrap a CA extension fragment in a minimal LWIS probe document for XSD.

    Parameters
    ----------
    fragment_xml : str
        Serialized CA extension element.

    Returns
    -------
    str
        Well-formed LWIS probe XML.
    """
    designator = "CYXX"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm-ca:LWIS xmlns:iwxxm="http://icao.int/iwxxm/3.0"
    xmlns:iwxxm-ca="{CA_EXTENSION_NS}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    gml:id="ca.extension.probe"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL"
    automatedStation="true">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>2023-01-01T00:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.probe">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.probe">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>{designator}</aixm:designator>
          <aixm:locationIndicatorICAO>{designator}</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t.obs">
      <gml:timePosition>2023-01-01T00:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
  <iwxxm:observation>
    <iwxxm:MeteorologicalAerodromeObservation gml:id="obs.probe" cloudAndVisibilityOK="false">
      <iwxxm:extension>{fragment_xml}</iwxxm:extension>
    </iwxxm:MeteorologicalAerodromeObservation>
  </iwxxm:observation>
</iwxxm-ca:LWIS>"""


def ca_xsd_probe_document(fragment_xml: str, *, product: str) -> str:
    """
    Build a probe document for validating one CA extension fragment.

    Parameters
    ----------
    fragment_xml : str
        Serialized CA extension element.
    product : str
        Product id (``METAR``, ``TAF``, …).

    Returns
    -------
    str
        Probe XML suitable for product XSD validation.
    """
    product_u = product.upper()
    if product_u in {"TAF", "AIRMET"}:
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{fragment_xml}'
    return wrap_ca_lwis_extension_block(fragment_xml)


__all__ = [
    "CA_EXTENSION_NS",
    "CA_SUBSTITUTION_ROOTS",
    "WMO_PRODUCT_ROOTS",
    "ca_xsd_probe_document",
    "document_root_name",
    "etree",
    "extract_ca_extension_blocks",
    "is_ca_substitution_root",
    "wrap_ca_lwis_extension_block",
]
