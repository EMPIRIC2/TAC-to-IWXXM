"""Conversion template dataclasses."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal, TypedDict

SlotType = Literal["digits", "enum", "literal", "unit", "station", "time"]
SlotMode = Literal["convert", "decode_only", "skip"]


class BridgeCapture(TypedDict, total=False):
    """One capture chip in a bridge preview (wire keys preserved)."""

    id: str
    value: str
    label: str
    mode: str


class BridgeSkipped(TypedDict, total=False):
    """One skipped-slot chip in a bridge preview."""

    id: str
    reason: str
    label: str


@dataclass(frozen=True)
class Slot:
    """
    One ordered capture or literal in a conversion template.

    Attributes
    ----------
    id : str
        Slot id.
    label : str
        Slot label.
    type : SlotType
        Capture kind.
    optional : bool
        Whether the slot may be absent. Default ``False``.
    digits : int | None
        Digit width, or ``None``.
    enum_values : str | None
        Allowed values, or ``None``.
    literal : str | None
        Literal text, or ``None``.
    iwxxm_field : str
        IWXXM field name. Default ``''``.
    mode : SlotMode
        ``convert``, ``decode_only``, or ``skip``. Default ``'convert'``.
    gloss : str
        Gloss text. Default ``''``.
    """

    id: str
    label: str
    type: SlotType
    optional: bool = False
    digits: int | None = None
    enum_values: str | None = None
    literal: str | None = None
    iwxxm_field: str = ""
    mode: SlotMode = "convert"
    gloss: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON persistence / API."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None and v != ""}


@dataclass(frozen=True)
class ConversionTemplate:
    """
    Parameterizable conversion template (default Conversion rule object).

    Attributes
    ----------
    id : str
        ID.
    name : str
        Template name.
    access : Literal['first_party', 'custom']
        Access.
    iwxxm_block : str
        IWXXM block.
    slots : tuple[Slot, ...]
        Ordered template slots.
    sample : str
        Sample text. Default ``''``.
    profiles : tuple[str, ...]
        Profiles.
    comments : str
        Comments. Default ``''``.
    fork_of : str | None
        Fork of. Default ``None``.
    """

    id: str
    name: str
    access: Literal["first_party", "custom"]
    iwxxm_block: str
    slots: tuple[Slot, ...]
    sample: str = ""
    profiles: tuple[str, ...] = ()
    comments: str = ""
    fork_of: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON / API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "access": self.access,
            "iwxxm_block": self.iwxxm_block,
            "slots": [s.to_dict() for s in self.slots],
            "sample": self.sample,
            "profiles": list(self.profiles),
            "comments": self.comments,
            "fork_of": self.fork_of,
        }


@dataclass
class BridgePreview:
    """
    TAC → template → IWXXM bridge preview payload.

    Attributes
    ----------
    template_id : str
        Template id.
    focus_group : str
        TAC group to preview.
    matched : bool
        Matched.
    captures : list[BridgeCapture]
        Captures.
    xml_block : str
        XML block. Default ``''``.
    compiled_pattern : str
        Compiled pattern. Default ``''``.
    skipped : list[BridgeSkipped]
        Skipped.
    """

    template_id: str
    focus_group: str
    matched: bool
    captures: list[BridgeCapture] = field(default_factory=list)
    xml_block: str = ""
    compiled_pattern: str = ""
    skipped: list[BridgeSkipped] = field(default_factory=list)


__all__ = [
    "BridgeCapture",
    "BridgePreview",
    "BridgeSkipped",
    "ConversionTemplate",
    "Slot",
    "SlotMode",
    "SlotType",
]
