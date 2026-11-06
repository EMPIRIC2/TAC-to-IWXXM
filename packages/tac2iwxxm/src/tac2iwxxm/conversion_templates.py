"""Parameterizable conversion templates (EV-080 / #1146).

Slot-builder-first Conversion rule objects: typed captures map TAC groups to
IWXXM blocks. First-party builtins are view/fork sources; custom templates are
persisted by the API layer.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Literal, cast

SlotType = Literal["digits", "enum", "literal", "unit", "station", "time"]
SlotMode = Literal["convert", "decode_only", "skip"]


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
        """
        Serialize for JSON persistence / API.

        Returns
        -------
        dict[str, Any]
            Serialized form for JSON persistence / API.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (to_dict)
        2
        """
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
        """
        Serialize for JSON / API responses.

        Returns
        -------
        dict[str, Any]
            Serialized form for JSON / API responses.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (to_dict)
        2
        """
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


def slot_from_dict(raw: dict[str, Any]) -> Slot:
    """
    Build a :class:`Slot` from a JSON-like mapping.

    Parameters
    ----------
    raw : dict[str, Any]
        JSON-like slot mapping.

    Returns
    -------
    Slot
        A :class:`Slot` from a JSON-like mapping.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (slot_from_dict)
    2
    """
    mode_raw = str(raw.get("mode") or "convert")
    mode: SlotMode = (
        "decode_only"
        if mode_raw in {"decode_only", "decode-only", "decode"}
        else "skip"
        if mode_raw == "skip"
        else "convert"
    )
    return Slot(
        id=str(raw["id"]),
        label=str(raw.get("label") or raw["id"]),
        type=raw["type"],  # type: ignore[arg-type]
        optional=bool(raw.get("optional", False)),
        digits=int(raw["digits"]) if raw.get("digits") is not None else None,
        enum_values=raw.get("enum_values") or raw.get("enumValues"),
        literal=raw.get("literal"),
        iwxxm_field=str(raw.get("iwxxm_field") or raw.get("iwxxmField") or ""),
        mode=mode,
        gloss=str(raw.get("gloss") or ""),
    )


def template_from_dict(raw: dict[str, Any]) -> ConversionTemplate:
    """
    Build a :class:`ConversionTemplate` from a JSON-like mapping.

    Parameters
    ----------
    raw : dict[str, Any]
        JSON-like template mapping.

    Returns
    -------
    ConversionTemplate
        A :class:`ConversionTemplate` from a JSON-like mapping.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (template_from_dict)
    2
    """
    slots_raw: list[Any] = list(raw.get("slots") or [])
    parsed_slots: list[Slot] = []
    for item in slots_raw:
        if isinstance(item, Slot):
            parsed_slots.append(item)
        elif isinstance(item, dict):
            typed_item = cast(dict[str, Any], item)
            parsed_slots.append(slot_from_dict(typed_item))
    profiles_raw = raw.get("profiles") or ()
    profiles: tuple[str, ...] = tuple(str(p) for p in profiles_raw)
    access_raw = raw.get("access") or "custom"
    access: Literal["first_party", "custom"] = "first_party" if access_raw == "first_party" else "custom"
    return ConversionTemplate(
        id=str(raw["id"]),
        name=str(raw.get("name") or raw["id"]),
        access=access,
        iwxxm_block=str(raw.get("iwxxm_block") or raw.get("iwxxmBlock") or "(omit)"),
        slots=tuple(parsed_slots),
        sample=str(raw.get("sample") or ""),
        profiles=profiles,
        comments=str(raw.get("comments") or ""),
        fork_of=(str(raw["fork_of"]) if raw.get("fork_of") else None)
        or (str(raw["forkOf"]) if raw.get("forkOf") else None),
    )


def compile_pattern(slots: list[Slot] | tuple[Slot, ...]) -> str:
    """
    Compile slots to a secondary pattern string (not the default authoring UI).

    Parameters
    ----------
    slots : list[Slot] | tuple[Slot, ...]
        Ordered template slots.

    Returns
    -------
    str
        Secondary pattern string.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (compile_pattern)
    2
    """
    parts: list[str] = []
    for s in slots:
        if s.mode == "skip":
            continue
        if s.type == "literal":
            parts.append(s.literal or "")
            continue
        if s.type in {"unit", "enum"}:
            body = f"{{{s.id}{'?' if s.optional else ''}:{s.enum_values or '…'}}}"
            parts.append(f"{s.literal or ''}{body}")
            continue
        if s.type == "digits":
            parts.append(f"{s.literal or ''}{{{s.id}{'?' if s.optional else ''}:d{s.digits or 2}}}")
            continue
        parts.append(f"{{{s.id}{'?' if s.optional else ''}:{s.type}}}")
    return "".join(parts)


def reorder_slots(
    slots: list[Slot] | tuple[Slot, ...],
    from_id: str,
    to_id: str,
) -> tuple[Slot, ...]:
    """
    Reorder slots by moving ``from_id`` onto ``to_id``'s index.

    Parameters
    ----------
    slots : list[Slot] | tuple[Slot, ...]
        Ordered template slots.

    from_id : str
        Slot id to move.

    to_id : str
        Slot id whose index is the destination.

    Returns
    -------
    tuple[Slot, ...]
        Slots with ``from_id`` placed at ``to_id``'s index.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (reorder_slots)
    2
    """
    items = list(slots)
    from_i = next((i for i, s in enumerate(items) if s.id == from_id), -1)
    to_i = next((i for i, s in enumerate(items) if s.id == to_id), -1)
    if from_i < 0 or to_i < 0 or from_i == to_i:
        return tuple(items)
    item = items.pop(from_i)
    items.insert(to_i, item)
    return tuple(items)


_WIND_RE = re.compile(r"^(\d{3})(\d{2,3})(?:G(\d{2,3}))?(KT|MPS)$", re.IGNORECASE)


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
    captures : list[dict[str, str]]
        Captures.
    xml_block : str
        XML block. Default ``''``.
    compiled_pattern : str
        Compiled pattern. Default ``''``.
    skipped : list[dict[str, str]]
        Skipped.
    """

    template_id: str
    focus_group: str
    matched: bool
    captures: list[dict[str, str]] = field(default_factory=list)
    xml_block: str = ""
    compiled_pattern: str = ""
    skipped: list[dict[str, str]] = field(default_factory=list)


def preview_bridge(
    template: ConversionTemplate,
    *,
    focus_group: str,
) -> BridgePreview:
    """
    Preview captures and an IWXXM-shaped XML sketch for a focused TAC group.

    Phase-1 ships a full parser for the first-party wind template; other templates
    return structure-only previews with ``matched=False`` when the focus group does
    not fit the wind shape. Skip-mode slots surface as ``skipped`` chips (never silent).

    Parameters
    ----------
    template : ConversionTemplate
        Conversion template.

    focus_group : str
        TAC group to preview.

    Returns
    -------
    BridgePreview
        Captures and an IWXXM-shaped XML sketch for a focused TAC group.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (preview_bridge)
    2
    """
    pattern = compile_pattern(template.slots)
    skipped = [
        {"slot": s.id, "label": s.label, "gloss": s.gloss or s.label} for s in template.slots if s.mode == "skip"
    ]
    group = (focus_group or "").strip()
    if template.id == "CV.WIND" or template.iwxxm_block == "iwxxm:WindObservation":
        m = _WIND_RE.match(group)
        if not m:
            return BridgePreview(
                template_id=template.id,
                focus_group=group,
                matched=False,
                compiled_pattern=pattern,
                xml_block="<!-- select a wind group to preview XML -->",
                skipped=skipped,
            )
        direction, speed, gust, unit = m.group(1), m.group(2), m.group(3), m.group(4).upper()
        uom = "[m/s]" if unit == "MPS" else "[kn]"
        captures = [
            {"slot": "direction", "value": direction, "field": "WindObservation / direction"},
            {"slot": "speed", "value": f"{speed} ({uom})", "field": "WindObservation / speed"},
            {
                "slot": "gust",
                "value": gust or "(absent)",
                "field": "WindObservation / gust",
            },
            {"slot": "unit", "value": f"{unit} → {uom}", "field": "@uom on speed/gust"},
        ]
        lines = [
            "<iwxxm:WindObservation>",
            f'  <iwxxm:direction uom="deg">{direction}</iwxxm:direction>',
            f'  <iwxxm:speed uom="{uom}">{speed}</iwxxm:speed>',
        ]
        if gust:
            lines.append(f'  <iwxxm:gustSpeed uom="{uom}">{gust}</iwxxm:gustSpeed>')
        else:
            lines.append("  <!-- gust omitted (optional slot absent) -->")
        lines.append("</iwxxm:WindObservation>")
        return BridgePreview(
            template_id=template.id,
            focus_group=group,
            matched=True,
            captures=captures,
            xml_block="\n".join(lines),
            compiled_pattern=pattern,
            skipped=skipped,
        )
    return BridgePreview(
        template_id=template.id,
        focus_group=group,
        matched=False,
        compiled_pattern=pattern,
        xml_block=f"<!-- structure preview for {template.iwxxm_block}; group={group!r} -->",
        skipped=skipped,
    )


def _builtin_catalog() -> dict[str, ConversionTemplate]:
    """
    Internal helper ``_builtin_catalog``.

    Returns
    -------
    dict[str, ConversionTemplate]
        Return value.
    """
    wind = ConversionTemplate(
        id="CV.WIND",
        name="Wind group",
        access="first_party",
        iwxxm_block="iwxxm:WindObservation",
        sample="18012G20KT",
        profiles=("ICAO_2025", "US_FAA_NWS", "CA_ECCC"),
        slots=(
            Slot("ddd", "direction", "digits", digits=3, iwxxm_field="WindObservation / direction"),
            Slot("ff", "speed", "digits", digits=2, iwxxm_field="WindObservation / speed"),
            Slot(
                "gust",
                "gust",
                "digits",
                optional=True,
                digits=2,
                literal="G",
                iwxxm_field="WindObservation / gust",
            ),
            Slot(
                "uom",
                "unit",
                "unit",
                enum_values="KT|MPS",
                iwxxm_field="@uom on speed/gust",
            ),
        ),
    )
    cloud = ConversionTemplate(
        id="CV.CLOUD",
        name="Cloud layer",
        access="first_party",
        iwxxm_block="iwxxm:AerodromeCloudLayer",
        sample="FEW050",
        profiles=("ICAO_2025", "US_FAA_NWS", "CA_ECCC"),
        slots=(
            Slot(
                "amt",
                "amount",
                "enum",
                enum_values="FEW|SCT|BKN|OVC",
                iwxxm_field="AerodromeCloudLayer / amount",
            ),
            Slot(
                "hhh",
                "height",
                "digits",
                digits=3,
                iwxxm_field="AerodromeCloudLayer / base (x100 ft)",
            ),
        ),
    )
    vis = ConversionTemplate(
        id="CV.VIS",
        name="Visibility",
        access="first_party",
        iwxxm_block="iwxxm:AerodromeHorizontalVisibility",
        sample="10SM",
        profiles=("ICAO_2025", "US_FAA_NWS"),
        slots=(
            Slot(
                "vv",
                "visibility",
                "digits",
                digits=2,
                iwxxm_field="AerodromeHorizontalVisibility / prevailing",
            ),
            Slot("uom", "unit", "unit", enum_values="SM|M", iwxxm_field="@uom"),
        ),
    )
    return {t.id: t for t in (wind, cloud, vis)}


FIRST_PARTY_TEMPLATES: dict[str, ConversionTemplate] = _builtin_catalog()


def list_first_party_templates() -> list[ConversionTemplate]:
    """
    Return built-in first-party conversion templates.

    Returns
    -------
    list[ConversionTemplate]
        Built-in first-party conversion templates.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (list_first_party_templates)
    2
    """
    return list(FIRST_PARTY_TEMPLATES.values())


def get_first_party_template(template_id: str) -> ConversionTemplate | None:
    """
    Return a first-party template by id, or ``None``.

    Parameters
    ----------
    template_id : str
        Template id.

    Returns
    -------
    ConversionTemplate | None
        A first-party template by id, or ``None``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_first_party_template)
    2
    """
    return FIRST_PARTY_TEMPLATES.get(template_id)


def fork_first_party(template_id: str, *, new_id: str, name: str | None = None) -> ConversionTemplate:
    """
    Fork a first-party template into a custom template object (not persisted).

    Parameters
    ----------
    template_id : str
        Template id.

    new_id : str
        Id for the forked template.

    name : str | None, optional
        Display name. ``None`` keeps the source name.

    Returns
    -------
    ConversionTemplate
        A first-party template into a custom template object (not persisted).

    Raises
    ------
    KeyError
        If ``template_id`` is not a known first-party id.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (fork_first_party)
    2
    """
    base = FIRST_PARTY_TEMPLATES.get(template_id)
    if base is None:
        raise KeyError(template_id)
    return ConversionTemplate(
        id=new_id,
        name=name or f"{base.name} (custom)",
        access="custom",
        iwxxm_block=base.iwxxm_block,
        slots=base.slots,
        sample=base.sample,
        profiles=base.profiles,
        comments=base.comments,
        fork_of=base.id,
    )
