"""Type boundaries for untyped third-party XML tree libraries (lxml has no py.typed)."""

from __future__ import annotations

from typing import Protocol, cast

import lxml.etree as _lxml_etree


class XmlElement(Protocol):
    tag: str

    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str) -> None: ...

    def xpath(self, path: str, *, namespaces: dict[str, str] | None = ...) -> list[XmlElement]: ...

    def getroottree(self) -> XmlRootTree: ...

    def findall(self, path: str) -> list[XmlElement]: ...


class XmlRootTree(Protocol):
    def getpath(self, element: XmlElement) -> str: ...


class LxmlEtreeModule(Protocol):
    XMLSyntaxError: type[Exception]

    def Element(self, tag: str, nsmap: dict[str | None, str] | None = ...) -> XmlElement: ...

    def SubElement(self, parent: XmlElement, tag: str) -> XmlElement: ...

    def ElementTree(self, element: XmlElement | None = ...) -> XmlTree: ...

    def fromstring(self, text: str | bytes) -> XmlElement: ...

    def parse(self, source: str) -> XmlTree: ...


class XmlTree(Protocol):
    def write(
        self,
        file: object,
        *,
        encoding: str = ...,
        xml_declaration: bool = ...,
        pretty_print: bool = ...,
    ) -> None: ...

    def getroot(self) -> XmlElement: ...


lxml_etree = cast(LxmlEtreeModule, _lxml_etree)

# Back-compat alias for element-typed parameters.
XmlNode = XmlElement
