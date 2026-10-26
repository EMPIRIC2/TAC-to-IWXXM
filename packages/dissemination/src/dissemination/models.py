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
    """
    One schema difference returned from dissemination preflight.

    Attributes
    ----------
    kind : str
        Difference kind.
    table : str
        Table name.
    detail : str
        Detail text.
    column : str or None, optional
        Column name.
    """

    kind: str
    table: str
    detail: str
    column: str | None = None


class PreflightRequest(msgspec.Struct, frozen=True):
    """
    Preflight a destination sink before operator send.

    Attributes
    ----------
    dissemination_template_id : str or None, optional
        Dissemination template ID.
    sink_type : SinkType or None, optional
        Sink type id.
    uri : str or None, optional
        Destination URI.
    ddl : bool or None, optional
        DDL.
    product : str or None, optional
        Product id.
    iwxxm_version : str or None, optional
        IWXXM release line.
    params : dict[str, Any], optional
        Extra sink parameters. By default an empty dict.
    """

    dissemination_template_id: str | None = None
    sink_type: SinkType | None = None
    uri: str | None = None
    ddl: bool | None = None
    product: str | None = None
    iwxxm_version: str | None = None
    params: dict[str, Any] = msgspec.field(default_factory=dict)


class PreflightResponse(msgspec.Struct, frozen=True):
    """
    Preflight outcome with connectivity, schema diffs, and optional handle.

    Attributes
    ----------
    ok : bool
        True when the result succeeded.
    connectivity_ok : bool
        True when connectivity succeeded.
    diffs : list[SchemaDiffItem]
        Schema differences.
    handle : str or None, optional
        Preflight handle.
    detail : str or None, optional
        Detail text.
    """

    ok: bool
    connectivity_ok: bool
    diffs: list[SchemaDiffItem]
    handle: str | None = None
    detail: str | None = None


class SendRequest(msgspec.Struct, frozen=True):
    """
    Send IWXXM (and optional TAC) to a preflighted or one-shot destination.

    Attributes
    ----------
    dissemination_template_id : str or None, optional
        Dissemination template ID.
    dissemination_library_id : str or None, optional
        Dissemination library ID.
    handle : str or None, optional
        Preflight handle.
    sink_type : SinkType or None, optional
        Sink type id.
    uri : str or None, optional
        Destination URI.
    iwxxm_xml : str or None, optional
        IWXXM XML text.
    tac_text : str or None, optional
        TAC text.
    product : str or None, optional
        Product id.
    iwxxm_version : str or None, optional
        IWXXM release line.
    params : dict[str, Any], optional
        Extra sink parameters. By default an empty dict.
    """

    dissemination_template_id: str | None = None
    dissemination_library_id: str | None = None
    handle: str | None = None
    sink_type: SinkType | None = None
    uri: str | None = None
    iwxxm_xml: str | None = None
    tac_text: str | None = None
    product: str | None = None
    iwxxm_version: str | None = None
    params: dict[str, Any] = msgspec.field(default_factory=dict)


class SendResponse(msgspec.Struct, frozen=True):
    """
    Send outcome with optional object-store upload key metadata.

    Attributes
    ----------
    ok : bool
        True when the result succeeded.
    kv_upload_key : str or None, optional
        Key-value upload key.
    detail : str or None, optional
        Detail text.
    """

    ok: bool
    kv_upload_key: str | None = None
    detail: str | None = None
