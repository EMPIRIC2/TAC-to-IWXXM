"""CA_ECCC MSC COLLECT envelope packaging (EV-073 M1 / #1032).

Wrap single-report IWXXM 3.0.0 products in ``collect:MeteorologicalBulletin``
for MSC datamart exchange. Post-convert hook only — convert SoT stays inner product.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC]
"""

from __future__ import annotations

import re
import uuid
from typing import Any

import lxml.etree as _lxml_etree

etree: Any = _lxml_etree

_COLLECT_NS = "http://def.wmo.int/collect/2014"
_IWXXM_NS = "http://icao.int/iwxxm/3.0"
_IWXXM_CA_NS = "http://dd.meteo.gc.ca/iwxxm-ca/3.0.0"
_CA_COLLECT_SCHEMA_LOCATION = (
    "http://icao.int/iwxxm/3.0 http://schemas.wmo.int/iwxxm/3.0.0/iwxxm.xsd "
    "http://dd.meteo.gc.ca/iwxxm-ca/3.0.0 https://dd.meteo.gc.ca/today/aviation/iwxxm/schema/iwxxm-ca.xsd "
    "http://def.wmo.int/collect/2014 http://schemas.wmo.int/collect/1.2/collect.xsd"
)
_XML_DECL = re.compile(r"^\s*<\?xml[^?]*\?>\s*", re.IGNORECASE)


def is_ca_collect_bulletin(xml: str) -> bool:
    """
    Return whether ``xml`` is a WMO ``collect:MeteorologicalBulletin`` root.

    Parameters
    ----------
    xml :
        Document text.

    Returns
    -------
    bool
        True when the root element is a COLLECT bulletin.
    """
    try:
        root = etree.fromstring(xml.encode("utf-8"))
    except etree.XMLSyntaxError:
        return False
    qname = etree.QName(root)
    return qname.localname == "MeteorologicalBulletin" and qname.namespace == _COLLECT_NS


def wrap_ca_eccc_collect(
    xml: str,
    *,
    bulletin_identifier: str,
) -> str:
    """
    Wrap single-report CA IWXXM in an MSC COLLECT envelope.

    Parameters
    ----------
    xml :
        Inner IWXXM product XML (one root element).
    bulletin_identifier :
        MSC datamart filename for ``collect:bulletinIdentifier``.

    Returns
    -------
    str
        COLLECT bulletin XML; unchanged when input is already COLLECT.
    """
    if is_ca_collect_bulletin(xml):
        return xml

    member = _XML_DECL.sub("", xml.strip())
    bid = bulletin_identifier.strip()
    gid = f"uuid.{uuid.uuid4()}"
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<collect:MeteorologicalBulletin gml:id="{gid}"\n'
        f'    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"\n'
        f'    xmlns:collect="{_COLLECT_NS}"\n'
        f'    xmlns:gml="http://www.opengis.net/gml/3.2"\n'
        f'    xmlns:iwxxm="{_IWXXM_NS}"\n'
        f'    xmlns:iwxxm-ca="{_IWXXM_CA_NS}"\n'
        f'    xmlns:xlink="http://www.w3.org/1999/xlink"\n'
        f'    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        f'    xsi:schemaLocation="{_CA_COLLECT_SCHEMA_LOCATION}">\n'
        f"    <collect:meteorologicalInformation>\n"
        f"{member}\n"
        f"    </collect:meteorologicalInformation>\n"
        f"    <collect:bulletinIdentifier>{bid}</collect:bulletinIdentifier>\n"
        f"</collect:MeteorologicalBulletin>"
    )


__all__ = [
    "is_ca_collect_bulletin",
    "wrap_ca_eccc_collect",
]
