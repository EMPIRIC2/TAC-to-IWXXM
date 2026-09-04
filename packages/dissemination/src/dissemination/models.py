"""msgspec request/response models for dissemination preflight/send (F16-F19)."""

from __future__ import annotations

from typing import Any, Literal

import msgspec

SinkType = Literal[
    "postgres",
    "mysql",
    "sqlserver",
    "sqlite",
    "wis2",
    "edis",
    "amhs",
    "swim",
    "afs",
]

# Drawer chooser order - keep FE enums aligned (T5.2 / E14-05 / E14-10).
DRAWER_SINK_TYPES: tuple[SinkType, ...] = (
    "postgres",
    "mysql",
    "sqlserver",
    "sqlite",
    "wis2",
    "edis",
    "amhs",
    "swim",
    "afs",
)


class SchemaDiffItem(msgspec.Struct, frozen=True):
    """One schema difference returned from dissemination preflight."""

    kind: str
    table: str
    detail: str
    column: str | None = None


class PreflightRequest(msgspec.Struct, frozen=True):
    """Preflight a destination sink before operator send."""

    sink_type: SinkType
    uri: str | None = None
    ddl: bool = False
    product: str | None = None
    iwxxm_version: str | None = None
    params: dict[str, Any] = msgspec.field(default_factory=dict)


class PreflightResponse(msgspec.Struct, frozen=True):
    """Preflight outcome with connectivity, schema diffs, and optional handle."""

    ok: bool
    connectivity_ok: bool
    diffs: list[SchemaDiffItem]
    handle: str | None = None
    detail: str | None = None


class SendRequest(msgspec.Struct, frozen=True):
    """Send IWXXM (and optional TAC) to a preflighted or one-shot destination."""

    handle: str | None = None
    sink_type: SinkType | None = None
    uri: str | None = None
    iwxxm_xml: str | None = None
    tac_text: str | None = None
    product: str | None = None
    iwxxm_version: str | None = None
    params: dict[str, Any] = msgspec.field(default_factory=dict)


class SendResponse(msgspec.Struct, frozen=True):
    """Send outcome with optional object-store upload key metadata."""

    ok: bool
    kv_upload_key: str | None = None
    detail: str | None = None
