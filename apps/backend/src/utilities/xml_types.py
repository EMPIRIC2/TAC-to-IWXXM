"""Type boundaries for untyped third-party XML tree libraries (lxml has no py.typed)."""

from __future__ import annotations

from typing import Protocol, cast

import lxml.etree as _lxml_etree


class XmlElement(Protocol):
    """Structural typing for lxml element nodes used in IWXXM XML handling."""

    tag: str

    def get(self, key: str) -> str | None:
        """Return attribute value for ``key``, if present."""
        ...

    def set(self, key: str, value: str) -> None:
        """Set attribute ``key`` to ``value``."""
        ...

    def xpath(self, path: str, *, namespaces: dict[str, str] | None = ...) -> list[XmlElement]:
        """Evaluate an XPath expression and return matching elements."""
        ...

    def getroottree(self) -> XmlRootTree:
        """Return the owning document tree."""
        ...

    def findall(self, path: str) -> list[XmlElement]:
        """Find all descendants matching ``path``."""
        ...


class XmlRootTree(Protocol):
    """Structural typing for lxml root trees that expose element XPath strings."""

    def getpath(self, element: XmlElement) -> str:
        """Return the absolute XPath for ``element``."""
        ...


class LxmlEtreeModule(Protocol):
    """Structural typing for the ``lxml.etree`` module surface used by the backend."""

    XMLSyntaxError: type[Exception]

    def Element(self, tag: str, nsmap: dict[str | None, str] | None = ...) -> XmlElement:
        """Create a new element with optional namespace map."""
        ...

    def SubElement(self, parent: XmlElement, tag: str) -> XmlElement:
        """Create a child element under ``parent``."""
        ...

    def ElementTree(self, element: XmlElement | None = ...) -> XmlTree:
        """Wrap ``element`` in an element tree."""
        ...

    def fromstring(self, text: str | bytes) -> XmlElement:
        """Parse XML text into an element."""
        ...

    def parse(self, source: str) -> XmlTree:
        """Parse an XML file path into an element tree."""
        ...


class XmlTree(Protocol):
    """Structural typing for lxml element trees supporting serialize and root access."""

    def write(
        self,
        file: object,
        *,
        encoding: str = ...,
        xml_declaration: bool = ...,
        pretty_print: bool = ...,
    ) -> None:
        """Serialize this tree to ``file``."""
        ...

    def getroot(self) -> XmlElement:
        """Return the root element."""
        ...


lxml_etree = cast(LxmlEtreeModule, _lxml_etree)

# Back-compat alias for element-typed parameters.
XmlNode = XmlElement
