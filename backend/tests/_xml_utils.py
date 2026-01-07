import xml.etree.ElementTree as ET
from typing import Optional, Set


def _local(tag: str) -> str:
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def parse_xml(xml_text: str) -> ET.Element:
    return ET.fromstring(xml_text)


def strip_dynamic_attrs(elem: ET.Element, attrs_to_strip: Optional[Set[str]] = None) -> None:
    if attrs_to_strip is None:
        # Rely on local-name matching rather than fully qualified URIs
        attrs_to_strip = set()
    # Remove targeted attributes on this element
    for a in list(elem.attrib.keys()):
        # Consider both fully-qualified and plain names
        if a in attrs_to_strip or _local(a) in {"id", "schemaLocation"}:
            elem.attrib.pop(a, None)
    # Recurse
    for child in list(elem):
        strip_dynamic_attrs(child, attrs_to_strip)


def _norm_text(t: Optional[str]) -> str:
    if t is None:
        return ""
    # Collapse whitespace runs and strip
    return " ".join(t.split())


def elements_equal(a: ET.Element, b: ET.Element, ignore_attrs: Optional[Set[str]] = None) -> bool:
    """Structural XML equality ignoring attribute order and namespaces.

    - Compares tag local names (ignores namespace URIs)
    - Compares attributes after removing dynamic ones; compares by local name
    - Compares text/tail with normalized whitespace
    - Preserves child order
    """
    if ignore_attrs is None:
        ignore_attrs = set()

    if _local(a.tag) != _local(b.tag):
        return False

    # Compare attributes by local name (order-insensitive)
    def filt(attrs: dict) -> dict:
        out = {}
        for k, v in attrs.items():
            lk = _local(k)
            if lk in ignore_attrs:
                continue
            if lk in {"id", "schemaLocation"}:  # dynamic
                continue
            out[lk] = " ".join(str(v).split())
        return out

    if filt(a.attrib) != filt(b.attrib):
        return False

    # Normalize text and tail
    if _norm_text(a.text) != _norm_text(b.text):
        return False
    if _norm_text(a.tail) != _norm_text(b.tail):
        return False

    # Children count and per-index equality (order matters)
    ach = list(a)
    bch = list(b)
    if len(ach) != len(bch):
        return False
    for i in range(len(ach)):
        if not elements_equal(ach[i], bch[i], ignore_attrs=ignore_attrs):
            return False
    return True


def find_metar(root: ET.Element) -> Optional[ET.Element]:
    if _local(root.tag) == "METAR":
        return root
    for child in root.iter():
        if _local(child.tag) == "METAR":
            return child
    return None
