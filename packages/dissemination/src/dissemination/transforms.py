"""Ordered Dissemination library transforms (EV-bridge AC8 / TC-EVBRIDGE-008).

Apply only on Disseminate / Convert & Send paths — never on Convert-only.
Transforms carry no destination secrets (ADR-021 / ADR-029).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from dissemination.collect_namespaces import is_collect_bulletin
from dissemination.packaging import wrap_global_afs_collect

_BULLETIN_ID_RE = re.compile(
    r"(<collect:bulletinIdentifier>)(.*?)(</collect:bulletinIdentifier>)",
    re.IGNORECASE | re.DOTALL,
)
_CHECKSUM_COMMENT_RE = re.compile(
    r"<!--\s*dissemination-checksum:[a-f0-9]{64}\s*-->\s*",
    re.IGNORECASE,
)

KNOWN_TRANSFORM_TYPES = frozenset({"envelope", "topic_filename", "checksum", "bulletin_rewrap"})


@dataclass(frozen=True, slots=True)
class TransformStep:
    """One ordered transform from a Dissemination library body."""

    id: str
    type: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TransformResult:
    """Outcome of applying an ordered transform pipeline."""

    xml: str
    applied: tuple[str, ...]
    annotations: tuple[str, ...] = ()


def normalize_transform_steps(raw: object) -> list[TransformStep]:
    """
    Normalize library ``transforms`` JSON into ordered steps.

    Accepts ``list[str]`` (type ids) or ``list[dict]`` with ``type`` / ``id``.
    Unknown shapes are skipped. Empty / None → empty list.
    """
    if raw is None:
        return []
    if not isinstance(raw, list):
        return []
    steps: list[TransformStep] = []
    for index, item in enumerate(raw):
        if isinstance(item, str):
            token = item.strip()
            if not token:
                continue
            steps.append(TransformStep(id=token, type=token))
            continue
        if not isinstance(item, dict):
            continue
        type_token = str(item.get("type") or item.get("id") or "").strip()
        if not type_token:
            continue
        step_id = str(item.get("id") or type_token or f"step-{index}").strip()
        params_raw = item.get("params") if isinstance(item.get("params"), dict) else {}
        steps.append(
            TransformStep(
                id=step_id,
                type=type_token,
                params=dict(params_raw),
            )
        )
    return steps


def apply_dissemination_transforms(
    xml: str,
    transforms: object,
    *,
    bulletin_identifier: str | None = None,
    topic: str | None = None,
) -> TransformResult:
    """
    Apply Dissemination library transforms in order.

    Parameters
    ----------
    xml :
        IWXXM (or already-COLLECT) document.
    transforms :
        Library body ``transforms`` list (dicts or type strings).
    bulletin_identifier :
        Optional COLLECT bulletin id / topic filename.
    topic :
        Alias for bulletin_identifier when the latter is omitted.

    Returns
    -------
    TransformResult
        Transformed XML plus applied step ids.

    Raises
    ------
    ValueError
        When a step type is unknown (fail closed).
    """
    steps = normalize_transform_steps(transforms)
    if not steps:
        return TransformResult(xml=xml, applied=())

    bid = (bulletin_identifier or topic or "").strip() or None
    current = xml
    applied: list[str] = []
    annotations: list[str] = []

    for step in steps:
        kind = step.type.strip().lower()
        if kind not in KNOWN_TRANSFORM_TYPES:
            raise ValueError(f"Unknown dissemination transform type: {step.type!r}")
        if kind == "envelope":
            current = wrap_global_afs_collect(current, bulletin_identifier=bid)
        elif kind == "topic_filename":
            name = str(step.params.get("filename") or bid or "A_UNKNOWN.xml")
            current = _ensure_collect_then_set_bulletin_id(current, name)
            annotations.append(f"topic_filename={name}")
        elif kind == "checksum":
            current, digest = _apply_checksum_comment(current)
            annotations.append(f"checksum={digest}")
        elif kind == "bulletin_rewrap":
            current = _bulletin_rewrap(current, bulletin_identifier=bid)
        applied.append(step.id)

    return TransformResult(
        xml=current,
        applied=tuple(applied),
        annotations=tuple(annotations),
    )


def _ensure_collect_then_set_bulletin_id(xml: str, bulletin_id: str) -> str:
    wrapped = wrap_global_afs_collect(xml, bulletin_identifier=bulletin_id)
    if _BULLETIN_ID_RE.search(wrapped):
        return _BULLETIN_ID_RE.sub(
            rf"\g<1>{bulletin_id}\g<3>",
            wrapped,
            count=1,
        )
    return wrapped


def _apply_checksum_comment(xml: str) -> tuple[str, str]:
    stripped = _CHECKSUM_COMMENT_RE.sub("", xml)
    digest = hashlib.sha256(stripped.encode("utf-8")).hexdigest()
    comment = f"<!-- dissemination-checksum:{digest} -->\n"
    if stripped.lstrip().startswith("<?xml"):
        # Insert after XML declaration
        decl_end = stripped.find("?>")
        if decl_end != -1:
            insert_at = decl_end + 2
            out = stripped[:insert_at] + "\n" + comment + stripped[insert_at:].lstrip("\n")
            return out, digest
    return comment + stripped, digest


def _bulletin_rewrap(xml: str, *, bulletin_identifier: str | None) -> str:
    if not is_collect_bulletin(xml):
        return wrap_global_afs_collect(xml, bulletin_identifier=bulletin_identifier)
    # Unwrap member for a fresh COLLECT shell
    start = xml.find("<collect:meteorologicalInformation>")
    end = xml.find("</collect:meteorologicalInformation>")
    if start == -1 or end == -1:
        return wrap_global_afs_collect(xml, bulletin_identifier=bulletin_identifier)
    inner_start = start + len("<collect:meteorologicalInformation>")
    member = xml[inner_start:end].strip()
    return wrap_global_afs_collect(member, bulletin_identifier=bulletin_identifier)


__all__ = [
    "KNOWN_TRANSFORM_TYPES",
    "TransformResult",
    "TransformStep",
    "apply_dissemination_transforms",
    "normalize_transform_steps",
]
