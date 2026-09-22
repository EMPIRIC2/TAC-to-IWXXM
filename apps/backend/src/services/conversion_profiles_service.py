"""Owner-scoped CRUD for ConversionProfile rule packs (EV-933 / F7.w)."""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime
from typing import Any, Literal, NoReturn, cast
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import MetaData, Table, create_engine, delete, insert, or_, select, update
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..schemas.conversion_profiles import (
    ConversionTemplateCreate,
    ConversionTemplateOut,
    ConversionTemplateSlot,
    ConversionTemplateUpdate,
    DisseminationTemplateCreate,
    DisseminationTemplateOut,
    DisseminationTemplateUpdate,
    LibraryAssetCreate,
    LibraryAssetOut,
    LibraryAssetUpdate,
    OverlayCreate,
    OverlayOut,
    OverlayUpdate,
    PresetCreate,
    PresetOut,
    PresetUpdate,
    RulePackCreate,
    RulePackOut,
    RulePackUpdate,
)
from .profile_overlay import sign_overlay, verify_overlay_signature

logger = logging.getLogger(__name__)

RULE_PACKS_TABLE = "tac_profile_rule_packs"
OVERLAYS_TABLE = "tac_profile_overlays"
PRESETS_TABLE = "tac_profile_presets"
TEMPLATES_TABLE = "tac_dissemination_templates"
CONVERSION_TEMPLATES_TABLE = "tac_conversion_templates"
LIBRARY_ASSETS_TABLE = "tac_library_assets"
_SECRET_KEY = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|uri|connection_string|dsn)")
_URI_VALUE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)

_engine: Engine | None = None
_metadata = MetaData()
_tables: dict[str, Table] = {}


def _sync_database_url() -> str:
    """
    Internal helper ``_sync_database_url``.

    Returns
    -------
    object
        Return value.
    """
    raw = (os.environ.get("DATABASE_URL") or "").strip()
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile rule packs unavailable - missing DATABASE_URL",
        )
    if raw.startswith("postgresql+asyncpg://"):
        url = "postgresql+psycopg://" + raw.removeprefix("postgresql+asyncpg://")
    elif raw.startswith("postgresql+psycopg2://"):
        url = "postgresql+psycopg://" + raw.removeprefix("postgresql+psycopg2://")
    elif raw.startswith("postgresql://"):
        url = "postgresql+psycopg://" + raw.removeprefix("postgresql://")
    else:
        url = raw
    if "ssl=require" in url and "sslmode=" not in url:
        url = url.replace("ssl=require", "sslmode=require")
    return url


def _get_engine() -> Engine:
    """
    Internal helper ``_get_engine``.

    Returns
    -------
    object
        Return value.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(_sync_database_url(), pool_pre_ping=True)
    return _engine


def _table(name: str) -> Table:
    """
    Internal helper ``_table``.

    Parameters
    ----------
    name : object
        Argument ``name``.

    Returns
    -------
    object
        Return value.
    """
    if name not in _tables:
        _tables[name] = Table(name, _metadata, autoload_with=_get_engine())
    return _tables[name]


def _reject_secrets(payload: dict[str, Any], *, path: str = "") -> None:
    """
    Internal helper ``_reject_secrets``.

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    path : object
        Argument ``path``.
    """
    for key, value in payload.items():
        full = f"{path}.{key}" if path else key
        if _SECRET_KEY.search(key):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Field not allowed in profile persistence: {full}",
            )
        if isinstance(value, dict):
            nested = cast(dict[str, Any], value)
            _reject_secrets(nested, path=full)


def _handle_db_error(exc: Exception) -> NoReturn:
    """
    Internal helper ``_handle_db_error``.

    Parameters
    ----------
    exc : object
        Argument ``exc``.

    Returns
    -------
    object
        Return value.
    """
    logger.exception("conversion profiles db error: %s", exc)
    if isinstance(exc, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict saving profile row",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Profile storage unavailable",
    ) from exc


def _row_to_out(row: dict[str, Any]) -> RulePackOut:
    """
    Internal helper ``_row_to_out``.

    Parameters
    ----------
    row : object
        Argument ``row``.

    Returns
    -------
    object
        Return value.
    """
    return RulePackOut(
        id=row["id"],
        user_id=row["user_id"],
        slug=row["slug"],
        profile=row["profile"],
        product=row["product"],
        stage=row["stage"],
        severity=row["severity"],
        when_expr=str(row.get("when_expr") or ""),
        message=str(row.get("message") or ""),
        standard_reference=str(row.get("standard_reference") or ""),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _preset_row_to_out(row: dict[str, Any]) -> PresetOut:
    """
    Internal helper ``_preset_row_to_out``.

    Parameters
    ----------
    row : object
        Argument ``row``.

    Returns
    -------
    object
        Return value.
    """
    raw_extensions = row.get("extensions")
    extensions = [str(item) for item in cast(list[object], raw_extensions)] if isinstance(raw_extensions, list) else []
    return PresetOut(
        id=row["id"],
        user_id=row["user_id"],
        slug=row["slug"],
        name=row["name"],
        semantic_profile=str(row["semantic_profile"]),
        iwxxm_version=str(row["iwxxm_version"]),
        extensions=extensions,
        report_variant=str(row["report_variant"]) if row.get("report_variant") else None,
        overlay_id=row.get("overlay_id"),
        shared=bool(row.get("shared")),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _template_row_to_out(row: dict[str, Any]) -> DisseminationTemplateOut:
    """
    Internal helper ``_template_row_to_out``.

    Parameters
    ----------
    row : object
        Argument ``row``.

    Returns
    -------
    object
        Return value.
    """
    raw_params = row.get("params")
    params: dict[str, Any] = cast(dict[str, Any], raw_params) if isinstance(raw_params, dict) else {}
    return DisseminationTemplateOut(
        id=row["id"],
        user_id=row["user_id"],
        slug=row["slug"],
        name=row["name"],
        sink_type=str(row["sink_type"]),
        product=str(row["product"]) if row.get("product") else None,
        ddl=bool(row.get("ddl")),
        params=params,
        shared=bool(row.get("shared")),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _reject_template_values(value: object, *, path: str) -> None:
    """
    Internal helper ``_reject_template_values``.

    Parameters
    ----------
    value : object
        Argument ``value``.
    path : object
        Argument ``path``.
    """
    if isinstance(value, dict):
        _reject_secrets(cast(dict[str, Any], value), path=path)
        for key, nested in cast(dict[str, Any], value).items():
            nested_path = f"{path}.{key}" if path else str(key)
            _reject_template_values(nested, path=nested_path)
        return
    if isinstance(value, list):
        for index, nested in enumerate(cast(list[object], value)):
            _reject_template_values(nested, path=f"{path}[{index}]")
        return
    if isinstance(value, str) and _URI_VALUE.match(value.strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Field not allowed in template persistence: {path}",
        )


class ConversionProfilesService:
    """
    JWT-owner scoped rule pack persistence.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self, user_id: str) -> None:
        """
        Parameters
        ----------
        user_id :
            JWT ``sub`` (UUID string).
        """
        try:
            self.user_id = UUID(user_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user identity",
            ) from exc

    def list_rule_packs(self) -> list[RulePackOut]:
        """
        List rule packs owned by the caller.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_rule_packs)
        2

        Returns
        -------
        object
            Return value.
        """
        t = _table(RULE_PACKS_TABLE)
        try:
            with _get_engine().connect() as conn:
                rows = conn.execute(select(t).where(t.c.user_id == self.user_id).order_by(t.c.slug)).mappings().all()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return [_row_to_out(dict(r)) for r in rows]

    def list_presets(self) -> list[PresetOut]:
        """
        List semantic presets owned by the caller (plus shared rows).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_presets)
        2

        Returns
        -------
        object
            Return value.
        """
        t = _table(PRESETS_TABLE)
        try:
            with _get_engine().connect() as conn:
                rows = (
                    conn.execute(
                        select(t).where(or_(t.c.user_id == self.user_id, t.c.shared.is_(True))).order_by(t.c.slug)
                    )
                    .mappings()
                    .all()
                )
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return [_preset_row_to_out(dict(r)) for r in rows]

    def get_preset(self, preset_id: UUID, *, require_owner: bool = False) -> PresetOut:
        """
        Fetch one semantic preset by id (owner or shared).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_preset)
        2

        Parameters
        ----------
        preset_id : object
            Argument ``preset_id``.
        require_owner : object
            Argument ``require_owner``.

        Returns
        -------
        object
            Return value.
        """
        t = _table(PRESETS_TABLE)
        try:
            with _get_engine().connect() as conn:
                row = conn.execute(select(t).where(t.c.id == preset_id)).mappings().first()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        if row is None:
            raise HTTPException(status_code=404, detail="Preset not found")
        owner = row["user_id"]
        shared = bool(row.get("shared"))
        if require_owner and owner != self.user_id:
            raise HTTPException(status_code=403, detail="Preset ownership required")
        if owner != self.user_id and not shared:
            raise HTTPException(status_code=403, detail="Preset ownership required")
        return _preset_row_to_out(dict(row))

    def create_preset(self, payload: PresetCreate) -> PresetOut:
        """
        Insert a new semantic preset.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (create_preset)
        2

        Parameters
        ----------
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        data = payload.model_dump(by_alias=False)
        _reject_secrets(data)
        now = datetime.now(tz=UTC)
        preset_id = uuid4()
        t = _table(PRESETS_TABLE)
        values = {
            "id": preset_id,
            "user_id": self.user_id,
            "slug": payload.slug,
            "name": payload.name,
            "semantic_profile": payload.semantic_profile,
            "iwxxm_version": payload.iwxxm_version,
            "extensions": payload.extensions,
            "report_variant": payload.report_variant,
            "overlay_id": payload.overlay_id,
            "shared": payload.shared,
            "created_at": now,
            "updated_at": now,
        }
        try:
            with _get_engine().begin() as conn:
                conn.execute(insert(t).values(**values))
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_preset(preset_id, require_owner=True)

    def update_preset(self, preset_id: UUID, payload: PresetUpdate) -> PresetOut:
        """
        Patch an owned semantic preset.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (update_preset)
        2

        Parameters
        ----------
        preset_id : object
            Argument ``preset_id``.
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        existing = self.get_preset(preset_id, require_owner=True)
        data = payload.model_dump(exclude_unset=True, by_alias=False)
        _reject_secrets(data)
        if not data:
            return existing
        values = {
            "slug": str(data.get("slug") or existing.slug),
            "name": str(data.get("name") or existing.name),
            "semantic_profile": str(data.get("semantic_profile") or existing.semantic_profile),
            "iwxxm_version": str(data.get("iwxxm_version") or existing.iwxxm_version),
            "extensions": data.get("extensions") if "extensions" in data else existing.extensions,
            "report_variant": data.get("report_variant") if "report_variant" in data else existing.report_variant,
            "overlay_id": data.get("overlay_id") if "overlay_id" in data else existing.overlay_id,
            "shared": bool(data["shared"]) if "shared" in data else existing.shared,
            "updated_at": datetime.now(tz=UTC),
        }
        t = _table(PRESETS_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(
                    update(t).where(t.c.id == preset_id, t.c.user_id == self.user_id).values(**values)
                )
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Preset not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_preset(preset_id, require_owner=True)

    def delete_preset(self, preset_id: UUID) -> None:
        """
        Delete a semantic preset owned by the caller.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (delete_preset)
        2

        Parameters
        ----------
        preset_id : object
            Argument ``preset_id``.
        """
        t = _table(PRESETS_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(delete(t).where(t.c.id == preset_id, t.c.user_id == self.user_id))
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Preset not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)

    def list_templates(self) -> list[DisseminationTemplateOut]:
        """
        List dissemination templates owned by the caller (plus shared rows).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_templates)
        2

        Returns
        -------
        object
            Return value.
        """
        t = _table(TEMPLATES_TABLE)
        try:
            with _get_engine().connect() as conn:
                rows = (
                    conn.execute(
                        select(t).where(or_(t.c.user_id == self.user_id, t.c.shared.is_(True))).order_by(t.c.slug)
                    )
                    .mappings()
                    .all()
                )
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return [_template_row_to_out(dict(r)) for r in rows]

    def get_template(self, template_id: UUID, *, require_owner: bool = False) -> DisseminationTemplateOut:
        """
        Fetch one dissemination template by id (owner or shared).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_template)
        2

        Parameters
        ----------
        template_id : object
            Argument ``template_id``.
        require_owner : object
            Argument ``require_owner``.

        Returns
        -------
        object
            Return value.
        """
        t = _table(TEMPLATES_TABLE)
        try:
            with _get_engine().connect() as conn:
                row = conn.execute(select(t).where(t.c.id == template_id)).mappings().first()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        if row is None:
            raise HTTPException(status_code=404, detail="Dissemination template not found")
        owner = row["user_id"]
        shared = bool(row.get("shared"))
        if require_owner and owner != self.user_id:
            raise HTTPException(status_code=403, detail="Dissemination template ownership required")
        if owner != self.user_id and not shared:
            raise HTTPException(status_code=403, detail="Dissemination template ownership required")
        return _template_row_to_out(dict(row))

    def create_template(self, payload: DisseminationTemplateCreate) -> DisseminationTemplateOut:
        """
        Insert a new dissemination template.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (create_template)
        2

        Parameters
        ----------
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        data = payload.model_dump(by_alias=False)
        _reject_secrets(data)
        _reject_template_values(payload.params, path="params")
        now = datetime.now(tz=UTC)
        template_id = uuid4()
        t = _table(TEMPLATES_TABLE)
        values = {
            "id": template_id,
            "user_id": self.user_id,
            "slug": payload.slug,
            "name": payload.name,
            "sink_type": payload.sink_type,
            "product": payload.product,
            "ddl": payload.ddl,
            "params": payload.params,
            "shared": payload.shared,
            "created_at": now,
            "updated_at": now,
        }
        try:
            with _get_engine().begin() as conn:
                conn.execute(insert(t).values(**values))
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_template(template_id, require_owner=True)

    def update_template(self, template_id: UUID, payload: DisseminationTemplateUpdate) -> DisseminationTemplateOut:
        """
        Patch an owned dissemination template.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (update_template)
        2

        Parameters
        ----------
        template_id : object
            Argument ``template_id``.
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        existing = self.get_template(template_id, require_owner=True)
        data = payload.model_dump(exclude_unset=True, by_alias=False)
        _reject_secrets(data)
        if "params" in data and data["params"] is not None:
            _reject_template_values(cast(dict[str, Any], data["params"]), path="params")
        if not data:
            return existing
        values = {
            "slug": str(data.get("slug") or existing.slug),
            "name": str(data.get("name") or existing.name),
            "sink_type": str(data.get("sink_type") or existing.sink_type),
            "product": str(data["product"]) if data.get("product") else None,
            "ddl": bool(data["ddl"]) if "ddl" in data else existing.ddl,
            "params": data.get("params") if "params" in data else existing.params,
            "shared": bool(data["shared"]) if "shared" in data else existing.shared,
            "updated_at": datetime.now(tz=UTC),
        }
        t = _table(TEMPLATES_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(
                    update(t).where(t.c.id == template_id, t.c.user_id == self.user_id).values(**values)
                )
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Dissemination template not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_template(template_id, require_owner=True)

    def delete_template(self, template_id: UUID) -> None:
        """
        Delete a dissemination template owned by the caller.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (delete_template)
        2

        Parameters
        ----------
        template_id : object
            Argument ``template_id``.
        """
        t = _table(TEMPLATES_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(delete(t).where(t.c.id == template_id, t.c.user_id == self.user_id))
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Dissemination template not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)

    def get_rule_pack(self, pack_id: UUID) -> RulePackOut:
        """
        Fetch one rule pack by id (owner-scoped).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_rule_pack)
        2

        Parameters
        ----------
        pack_id : object
            Argument ``pack_id``.

        Returns
        -------
        object
            Return value.
        """
        t = _table(RULE_PACKS_TABLE)
        try:
            with _get_engine().connect() as conn:
                row = conn.execute(select(t).where(t.c.id == pack_id, t.c.user_id == self.user_id)).mappings().first()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        if row is None:
            raise HTTPException(status_code=404, detail="Rule pack not found")
        return _row_to_out(dict(row))

    def create_rule_pack(self, payload: RulePackCreate) -> RulePackOut:
        """
        Insert a new rule pack.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (create_rule_pack)
        2

        Parameters
        ----------
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        data = payload.model_dump(by_alias=False)
        _reject_secrets(data)
        now = datetime.now(tz=UTC)
        pack_id = uuid4()
        t = _table(RULE_PACKS_TABLE)
        values = {
            "id": pack_id,
            "user_id": self.user_id,
            "slug": payload.slug,
            "profile": payload.profile,
            "product": payload.product,
            "stage": payload.stage,
            "severity": payload.severity,
            "when_expr": payload.when_expr,
            "message": payload.message,
            "standard_reference": payload.standard_reference,
            "created_at": now,
            "updated_at": now,
        }
        try:
            with _get_engine().begin() as conn:
                conn.execute(insert(t).values(**values))
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_rule_pack(pack_id)

    def update_rule_pack(self, pack_id: UUID, payload: RulePackUpdate) -> RulePackOut:
        """
        Patch an existing rule pack.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (update_rule_pack)
        2

        Parameters
        ----------
        pack_id : object
            Argument ``pack_id``.
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        data = payload.model_dump(exclude_unset=True, by_alias=False)
        _reject_secrets(data)
        if not data:
            return self.get_rule_pack(pack_id)
        data["updated_at"] = datetime.now(tz=UTC)
        t = _table(RULE_PACKS_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(update(t).where(t.c.id == pack_id, t.c.user_id == self.user_id).values(**data))
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Rule pack not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_rule_pack(pack_id)

    def delete_rule_pack(self, pack_id: UUID) -> None:
        """
        Delete a rule pack owned by the caller.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (delete_rule_pack)
        2

        Parameters
        ----------
        pack_id : object
            Argument ``pack_id``.
        """
        t = _table(RULE_PACKS_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(delete(t).where(t.c.id == pack_id, t.c.user_id == self.user_id))
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Rule pack not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)

    def _overlay_to_out(self, row: dict[str, Any]) -> OverlayOut:
        """
        Internal helper ``_overlay_to_out``.

        Parameters
        ----------
        row : object
            Argument ``row``.

        Returns
        -------
        object
            Return value.
        """
        raw_body = row.get("body")
        body_dict: dict[str, Any] = cast(dict[str, Any], raw_body) if isinstance(raw_body, dict) else {}
        verify_overlay_signature(
            user_id=row["user_id"],
            base_profile_id=str(row["base_profile_id"]),
            body=body_dict,
            signature=str(row.get("signature") or ""),
        )
        return OverlayOut(
            id=row["id"],
            user_id=row["user_id"],
            slug=row["slug"],
            base_profile_id=str(row["base_profile_id"]),
            body=body_dict,
            signature=str(row["signature"]),
            shared=bool(row.get("shared")),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_overlays(self) -> list[OverlayOut]:
        """
        List overlays owned by the caller (plus shared rows).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_overlays)
        2

        Returns
        -------
        object
            Return value.
        """
        t = _table(OVERLAYS_TABLE)
        try:
            with _get_engine().connect() as conn:
                rows = (
                    conn.execute(
                        select(t).where(or_(t.c.user_id == self.user_id, t.c.shared.is_(True))).order_by(t.c.slug)
                    )
                    .mappings()
                    .all()
                )
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return [self._overlay_to_out(dict(r)) for r in rows]

    def get_overlay(self, overlay_id: UUID, *, require_owner: bool = False) -> OverlayOut:
        """
        Fetch one overlay by id (owner or shared).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_overlay)
        2

        Parameters
        ----------
        overlay_id : object
            Argument ``overlay_id``.
        require_owner : object
            Argument ``require_owner``.

        Returns
        -------
        object
            Return value.
        """
        t = _table(OVERLAYS_TABLE)
        try:
            with _get_engine().connect() as conn:
                row = conn.execute(select(t).where(t.c.id == overlay_id)).mappings().first()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        if row is None:
            raise HTTPException(status_code=404, detail="Overlay not found")
        owner = row["user_id"]
        shared = bool(row.get("shared"))
        if require_owner and owner != self.user_id:
            raise HTTPException(status_code=403, detail="Overlay ownership required")
        if owner != self.user_id and not shared:
            raise HTTPException(status_code=403, detail="Overlay ownership required")
        return self._overlay_to_out(dict(row))

    def create_overlay(self, payload: OverlayCreate) -> OverlayOut:
        """
        Insert a new server-signed overlay.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (create_overlay)
        2

        Parameters
        ----------
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        data = payload.model_dump(by_alias=False)
        _reject_secrets(data)
        _reject_secrets(payload.body)
        now = datetime.now(tz=UTC)
        overlay_id = uuid4()
        signature = sign_overlay(
            user_id=self.user_id,
            base_profile_id=payload.base_profile_id,
            body=payload.body,
        )
        values = {
            "id": overlay_id,
            "user_id": self.user_id,
            "slug": payload.slug,
            "base_profile_id": payload.base_profile_id,
            "body": payload.body,
            "signature": signature,
            "shared": payload.shared,
            "created_at": now,
            "updated_at": now,
        }
        t = _table(OVERLAYS_TABLE)
        try:
            with _get_engine().begin() as conn:
                conn.execute(insert(t).values(**values))
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_overlay(overlay_id, require_owner=True)

    def update_overlay(self, overlay_id: UUID, payload: OverlayUpdate) -> OverlayOut:
        """
        Patch an owned overlay and re-sign.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (update_overlay)
        2

        Parameters
        ----------
        overlay_id : object
            Argument ``overlay_id``.
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        existing = self.get_overlay(overlay_id, require_owner=True)
        data = payload.model_dump(exclude_unset=True, by_alias=False)
        _reject_secrets(data)
        if "body" in data and data["body"] is not None:
            _reject_secrets(cast(dict[str, Any], data["body"]))
        if not data:
            return existing
        base_profile_id = str(data.get("base_profile_id") or existing.base_profile_id)
        body = cast(dict[str, Any], data.get("body") if "body" in data else existing.body)
        shared = bool(data["shared"]) if "shared" in data else existing.shared
        signature = sign_overlay(
            user_id=self.user_id,
            base_profile_id=base_profile_id,
            body=body,
        )
        values = {
            "slug": str(data.get("slug") or existing.slug),
            "base_profile_id": base_profile_id,
            "body": body,
            "shared": shared,
            "signature": signature,
            "updated_at": datetime.now(tz=UTC),
        }
        t = _table(OVERLAYS_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(
                    update(t).where(t.c.id == overlay_id, t.c.user_id == self.user_id).values(**values)
                )
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Overlay not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_overlay(overlay_id, require_owner=True)

    def delete_overlay(self, overlay_id: UUID) -> None:
        """
        Delete an overlay owned by the caller.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (delete_overlay)
        2

        Parameters
        ----------
        overlay_id : object
            Argument ``overlay_id``.
        """
        t = _table(OVERLAYS_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(delete(t).where(t.c.id == overlay_id, t.c.user_id == self.user_id))
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Overlay not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)

    @staticmethod
    def _first_party_template_out(template_id: str) -> ConversionTemplateOut | None:
        """
        Internal helper ``_first_party_template_out``.

        Parameters
        ----------
        template_id : object
            Argument ``template_id``.

        Returns
        -------
        object
            Return value.
        """
        try:
            from tac2iwxxm.conversion_templates import get_first_party_template
        except ImportError:
            return None
        tmpl = get_first_party_template(template_id)
        if tmpl is None:
            return None
        slots = [
            ConversionTemplateSlot.model_validate(
                {
                    "id": s.id,
                    "label": s.label,
                    "type": s.type,
                    "optional": s.optional,
                    "digits": s.digits,
                    "enumValues": s.enum_values,
                    "literal": s.literal,
                    "iwxxmField": s.iwxxm_field,
                }
            )
            for s in tmpl.slots
        ]
        return ConversionTemplateOut(
            id=tmpl.id,
            user_id=None,
            slug=tmpl.id,
            name=tmpl.name,
            access="first_party",
            iwxxm_block=tmpl.iwxxm_block,
            slots=slots,
            sample=tmpl.sample,
            comments=tmpl.comments or None,
            fork_of=None,
            shared=True,
            profiles=list(tmpl.profiles),
            created_at=None,
            updated_at=None,
        )

    def _conversion_template_row_to_out(self, row: dict[str, Any]) -> ConversionTemplateOut:
        """
        Internal helper ``_conversion_template_row_to_out``.

        Parameters
        ----------
        row : object
            Argument ``row``.

        Returns
        -------
        object
            Return value.
        """
        raw_slots_any: Any = row.get("slots") or []
        slot_items: list[Any] = cast(list[Any], raw_slots_any) if isinstance(raw_slots_any, list) else []
        slots: list[ConversionTemplateSlot] = [
            ConversionTemplateSlot.model_validate(cast(dict[str, Any], item))
            for item in slot_items
            if isinstance(item, dict)
        ]
        return ConversionTemplateOut(
            id=str(row["id"]),
            user_id=row["user_id"],
            slug=str(row["slug"]),
            name=str(row["name"]),
            access="custom",
            iwxxm_block=str(row["iwxxm_block"]),
            slots=slots,
            sample=str(row.get("sample") or ""),
            comments=row.get("comments"),
            fork_of=row.get("fork_of"),
            shared=bool(row.get("shared")),
            profiles=[],
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def list_conversion_templates(self) -> list[ConversionTemplateOut]:
        """
        List first-party builtins plus custom templates visible to the caller.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_conversion_templates)
        2

        Returns
        -------
        object
            Return value.
        """
        items: list[ConversionTemplateOut] = []
        try:
            from tac2iwxxm.conversion_templates import list_first_party_templates
        except ImportError:
            list_first_party_templates = None  # type: ignore[assignment]
        if list_first_party_templates is not None:
            for tmpl in list_first_party_templates():
                out = self._first_party_template_out(tmpl.id)
                if out is not None:
                    items.append(out)
        t = _table(CONVERSION_TEMPLATES_TABLE)
        try:
            with _get_engine().connect() as conn:
                rows = (
                    conn.execute(
                        select(t).where(or_(t.c.user_id == self.user_id, t.c.shared.is_(True))).order_by(t.c.slug)
                    )
                    .mappings()
                    .all()
                )
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        items.extend(self._conversion_template_row_to_out(dict(r)) for r in rows)
        return items

    def get_conversion_template(self, template_id: str, *, require_owner: bool = False) -> ConversionTemplateOut:
        """
        Fetch a first-party or custom conversion template; fail-closed on unknown.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_conversion_template)
        2

        Parameters
        ----------
        template_id : object
            Argument ``template_id``.
        require_owner : object
            Argument ``require_owner``.

        Returns
        -------
        object
            Return value.
        """
        first = self._first_party_template_out(template_id)
        if first is not None:
            if require_owner:
                raise HTTPException(status_code=403, detail="First-party templates are read-only")
            return first
        try:
            template_uuid = UUID(template_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown conversion template id") from exc
        t = _table(CONVERSION_TEMPLATES_TABLE)
        try:
            with _get_engine().connect() as conn:
                row = conn.execute(select(t).where(t.c.id == template_uuid)).mappings().first()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        if row is None:
            raise HTTPException(status_code=404, detail="Conversion template not found")
        owner = row["user_id"]
        shared = bool(row.get("shared"))
        if require_owner and owner != self.user_id:
            raise HTTPException(status_code=403, detail="Conversion template ownership required")
        if owner != self.user_id and not shared:
            raise HTTPException(status_code=403, detail="Conversion template ownership required")
        return self._conversion_template_row_to_out(dict(row))

    def create_conversion_template(self, payload: ConversionTemplateCreate) -> ConversionTemplateOut:
        """
        Insert a custom conversion template (fork or new).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (create_conversion_template)
        2

        Parameters
        ----------
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        data = payload.model_dump(by_alias=False)
        _reject_secrets(data)
        for slot in payload.slots:
            _reject_secrets(slot.model_dump(by_alias=False))
        now = datetime.now(tz=UTC)
        template_id = uuid4()
        slots_json = [s.model_dump(by_alias=True) for s in payload.slots]
        values = {
            "id": template_id,
            "user_id": self.user_id,
            "slug": payload.slug,
            "name": payload.name,
            "iwxxm_block": payload.iwxxm_block,
            "slots": slots_json,
            "sample": payload.sample,
            "comments": payload.comments,
            "fork_of": payload.fork_of,
            "shared": payload.shared,
            "created_at": now,
            "updated_at": now,
        }
        t = _table(CONVERSION_TEMPLATES_TABLE)
        try:
            with _get_engine().begin() as conn:
                conn.execute(insert(t).values(**values))
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_conversion_template(str(template_id), require_owner=True)

    def update_conversion_template(self, template_id: str, payload: ConversionTemplateUpdate) -> ConversionTemplateOut:
        """
        Patch an owned custom conversion template; reject first-party ids.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (update_conversion_template)
        2

        Parameters
        ----------
        template_id : object
            Argument ``template_id``.
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        if self._first_party_template_out(template_id) is not None:
            raise HTTPException(status_code=403, detail="First-party templates cannot be modified")
        existing = self.get_conversion_template(template_id, require_owner=True)
        data = payload.model_dump(exclude_unset=True, by_alias=False)
        _reject_secrets(data)
        if "slots" in data and data["slots"] is not None:
            for slot in cast(list[Any], data["slots"]):
                if isinstance(slot, dict):
                    _reject_secrets(cast(dict[str, Any], slot))
        if not data:
            return existing
        try:
            template_uuid = UUID(template_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown conversion template id") from exc
        slots_value: Any = [s.model_dump(by_alias=True) for s in existing.slots]
        if "slots" in data and data["slots"] is not None:
            slots_value = [
                s.model_dump(by_alias=True) if hasattr(s, "model_dump") else s for s in cast(list[Any], data["slots"])
            ]
        values = {
            "slug": str(data.get("slug") or existing.slug),
            "name": str(data.get("name") or existing.name),
            "iwxxm_block": str(data.get("iwxxm_block") or existing.iwxxm_block),
            "slots": slots_value,
            "sample": str(data["sample"]) if "sample" in data else existing.sample,
            "comments": data.get("comments", existing.comments),
            "shared": bool(data["shared"]) if "shared" in data else existing.shared,
            "updated_at": datetime.now(tz=UTC),
        }
        t = _table(CONVERSION_TEMPLATES_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(
                    update(t).where(t.c.id == template_uuid, t.c.user_id == self.user_id).values(**values)
                )
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Conversion template not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_conversion_template(template_id, require_owner=True)

    def delete_conversion_template(self, template_id: str) -> None:
        """
        Delete an owned custom conversion template; reject first-party.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (delete_conversion_template)
        2

        Parameters
        ----------
        template_id : object
            Argument ``template_id``.
        """
        if self._first_party_template_out(template_id) is not None:
            raise HTTPException(status_code=403, detail="First-party templates cannot be deleted")
        try:
            template_uuid = UUID(template_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown conversion template id") from exc
        t = _table(CONVERSION_TEMPLATES_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(delete(t).where(t.c.id == template_uuid, t.c.user_id == self.user_id))
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Conversion template not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)

    def _first_party_library_out(self, asset_id: str) -> LibraryAssetOut | None:
        """
        Internal helper ``_first_party_library_out``.

        Parameters
        ----------
        asset_id : object
            Argument ``asset_id``.

        Returns
        -------
        object
            Return value.
        """
        try:
            from tac2iwxxm.library_assets import get_first_party_library_asset
        except ImportError:
            return None
        asset = get_first_party_library_asset(asset_id)
        if asset is None:
            return None
        return LibraryAssetOut(
            id=asset.id,
            kind=asset.kind,
            name=asset.name,
            access="first_party",
            engine_profile_id=asset.engine_profile_id,
            attached_national_line=asset.attached_national_line,
            body=dict(asset.body),
            fork_of=asset.fork_of,
            shared=True,
            status="activated",
            schema_version=1,
        )

    def _library_row_to_out(self, row: dict[str, Any]) -> LibraryAssetOut:
        """
        Internal helper ``_library_row_to_out``.

        Parameters
        ----------
        row : object
            Argument ``row``.

        Returns
        -------
        object
            Return value.
        """
        body_candidate: Any = row.get("body")
        body: dict[str, Any] = cast(dict[str, Any], body_candidate) if isinstance(body_candidate, dict) else {}
        status_raw = str(row.get("status") or "draft")
        status: Literal["draft", "activated"] = "activated" if status_raw == "activated" else "draft"
        schema_raw = row.get("schema_version")
        schema_version = int(schema_raw) if isinstance(schema_raw, int) else 1
        yaml_raw = row.get("yaml_body")
        yaml_body = str(yaml_raw) if isinstance(yaml_raw, str) else None
        return LibraryAssetOut(
            id=str(row["id"]),
            kind=str(row["kind"]),  # type: ignore[arg-type]
            name=str(row["name"]),
            access="custom",
            engine_profile_id=str(row["engine_profile_id"]),
            attached_national_line=str(row["attached_national_line"]),
            body=body,
            fork_of=row.get("fork_of"),
            user_id=row["user_id"],
            slug=str(row["slug"]),
            shared=bool(row.get("shared")),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
            yaml_body=yaml_body,
            status=status,
            schema_version=schema_version,
        )

    def list_library_assets(self, *, kind: str | None = None) -> list[LibraryAssetOut]:
        """
        List first-party defaults plus custom assets visible to the caller.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_library_assets)
        2

        Parameters
        ----------
        kind : object
            Argument ``kind``.

        Returns
        -------
        object
            Return value.
        """
        items: list[LibraryAssetOut] = []
        try:
            from tac2iwxxm.library_assets import list_first_party_library_assets
        except ImportError:
            list_first_party_library_assets = None  # type: ignore[assignment]
        if list_first_party_library_assets is not None:
            for asset in list_first_party_library_assets():
                if kind is not None and asset.kind != kind:
                    continue
                out = self._first_party_library_out(asset.id)
                if out is not None:
                    items.append(out)
        t = _table(LIBRARY_ASSETS_TABLE)
        try:
            with _get_engine().connect() as conn:
                stmt = select(t).where(or_(t.c.user_id == self.user_id, t.c.shared.is_(True)))
                if kind is not None:
                    stmt = stmt.where(t.c.kind == kind)
                rows = conn.execute(stmt.order_by(t.c.slug)).mappings().all()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        items.extend(self._library_row_to_out(dict(r)) for r in rows)
        return items

    def get_library_asset(self, asset_id: str, *, require_owner: bool = False) -> LibraryAssetOut:
        """
        Fetch a first-party or custom library asset; fail-closed on unknown.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_library_asset)
        2

        Parameters
        ----------
        asset_id : object
            Argument ``asset_id``.
        require_owner : object
            Argument ``require_owner``.

        Returns
        -------
        object
            Return value.
        """
        first = self._first_party_library_out(asset_id)
        if first is not None:
            if require_owner:
                raise HTTPException(status_code=403, detail="First-party library assets are read-only")
            return first
        try:
            asset_uuid = UUID(asset_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown library asset id") from exc
        t = _table(LIBRARY_ASSETS_TABLE)
        try:
            with _get_engine().connect() as conn:
                row = conn.execute(select(t).where(t.c.id == asset_uuid)).mappings().first()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        if row is None:
            raise HTTPException(status_code=404, detail="Library asset not found")
        owner = row["user_id"]
        shared = bool(row.get("shared"))
        if require_owner and owner != self.user_id:
            raise HTTPException(status_code=403, detail="Library asset ownership required")
        if owner != self.user_id and not shared:
            raise HTTPException(status_code=403, detail="Library asset ownership required")
        return self._library_row_to_out(dict(row))

    def validate_library_yaml_document(
        self,
        yaml_body: str,
        *,
        kind: str,
        lifecycle: str = "draft",
    ) -> dict[str, Any]:
        """
        Parse YAML and collect regex diagnostics without persisting.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (validate_library_yaml_document)
        2

        Parameters
        ----------
        yaml_body : object
            Argument ``yaml_body``.
        kind : object
            Argument ``kind``.
        lifecycle : object
            Argument ``lifecycle``.

        Returns
        -------
        object
            Return value.
        """
        try:
            from tac2iwxxm.library_yaml import LibraryKind, LibraryLifecycle, validate_library_yaml
        except ImportError as exc:
            raise HTTPException(status_code=503, detail="Library YAML validator unavailable") from exc
        report = validate_library_yaml(
            yaml_body,
            expected_kind=cast(LibraryKind, kind),
            lifecycle=cast(LibraryLifecycle, lifecycle),
        )
        return report.to_dict()

    def _enforce_yaml_lifecycle(
        self,
        *,
        yaml_body: str | None,
        kind: str,
        lifecycle_status: str,
    ) -> dict[str, Any]:
        """
        Internal helper ``_enforce_yaml_lifecycle``.

        Parameters
        ----------
        yaml_body : object
            Argument ``yaml_body``.
        kind : object
            Argument ``kind``.
        lifecycle_status : object
            Argument ``lifecycle_status``.

        Returns
        -------
        object
            Return value.
        """
        extra: dict[str, Any] = {}
        if yaml_body is None:
            if lifecycle_status == "activated":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Activate requires a YAML document with zero Fail diagnostics",
                )
            extra["status"] = lifecycle_status
            return extra
        extra["yaml_body"] = yaml_body
        extra["status"] = lifecycle_status
        report = self.validate_library_yaml_document(
            yaml_body,
            kind=kind,
            lifecycle=lifecycle_status,
        )
        if lifecycle_status == "activated" and not bool(report.get("can_activate")):
            detail = str(report.get("yaml_error") or "Activate requires zero Fail diagnostics")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=detail,
            )
        if bool(report.get("valid_yaml")):
            parsed_body = report.get("data")
            if isinstance(parsed_body, dict):
                extra["body"] = parsed_body
            parsed_name = report.get("name")
            if isinstance(parsed_name, str) and parsed_name.strip():
                extra["name"] = parsed_name.strip()
        return extra

    def create_library_asset(self, payload: LibraryAssetCreate) -> LibraryAssetOut:
        """
        Insert a custom library asset (fork or new).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (create_library_asset)
        2

        Parameters
        ----------
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        data = payload.model_dump(by_alias=False)
        _reject_secrets(data)
        _reject_secrets(payload.body)
        _reject_template_values(payload.body, path="body")
        now = datetime.now(tz=UTC)
        asset_id = uuid4()
        yaml_extra = self._enforce_yaml_lifecycle(
            yaml_body=payload.yaml_body,
            kind=payload.kind,
            lifecycle_status=payload.status,
        )
        values = {
            "id": asset_id,
            "user_id": self.user_id,
            "slug": payload.slug,
            "name": yaml_extra.get("name") or payload.name,
            "kind": payload.kind,
            "engine_profile_id": payload.engine_profile_id,
            "attached_national_line": payload.attached_national_line,
            "body": yaml_extra.get("body") if "body" in yaml_extra else payload.body,
            "fork_of": payload.fork_of,
            "shared": payload.shared,
            "created_at": now,
            "updated_at": now,
            "yaml_body": yaml_extra.get("yaml_body"),
            "status": yaml_extra.get("status") or payload.status,
            "schema_version": payload.schema_version,
        }
        t = _table(LIBRARY_ASSETS_TABLE)
        try:
            with _get_engine().begin() as conn:
                conn.execute(insert(t).values(**values))
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_library_asset(str(asset_id), require_owner=True)

    def update_library_asset(self, asset_id: str, payload: LibraryAssetUpdate) -> LibraryAssetOut:
        """
        Update owned custom asset, or auto-fork first-party on edit (AC3).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (update_library_asset)
        2

        Parameters
        ----------
        asset_id : object
            Argument ``asset_id``.
        payload : object
            Argument ``payload``.

        Returns
        -------
        object
            Return value.
        """
        first = self._first_party_library_out(asset_id)
        if first is not None:
            body = payload.body if payload.body is not None else dict(first.body)
            _reject_secrets(body)
            _reject_template_values(body, path="body")
            create = LibraryAssetCreate.model_validate(
                {
                    "slug": payload.slug or f"fork-{uuid4().hex[:8]}",
                    "name": payload.name or f"{first.name} (fork)",
                    "kind": first.kind,
                    "engineProfileId": first.engine_profile_id,
                    "attachedNationalLine": first.attached_national_line,
                    "body": body,
                    "forkOf": first.id,
                    "shared": bool(payload.shared) if payload.shared is not None else False,
                    "yamlBody": payload.yaml_body,
                    "status": payload.status or "draft",
                    "schemaVersion": payload.schema_version or 1,
                }
            )
            return self.create_library_asset(create)
        try:
            asset_uuid = UUID(asset_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown library asset id") from exc
        data = payload.model_dump(by_alias=False, exclude_unset=True)
        _reject_secrets(data)
        if "body" in data and isinstance(data["body"], dict):
            _reject_template_values(cast(dict[str, Any], data["body"]), path="body")
        values: dict[str, Any] = {"updated_at": datetime.now(tz=UTC)}
        for key in ("slug", "name", "body", "shared"):
            if key in data:
                values[key] = data[key]
        if "yaml_body" in data or "status" in data:
            existing = self.get_library_asset(asset_id, require_owner=True)
            yaml_body = data.get("yaml_body", existing.yaml_body)
            lifecycle_status = data.get("status", existing.status)
            yaml_extra = self._enforce_yaml_lifecycle(
                yaml_body=yaml_body if isinstance(yaml_body, str) else None,
                kind=existing.kind,
                lifecycle_status=str(lifecycle_status),
            )
            values.update(yaml_extra)
        if "schema_version" in data and data["schema_version"] is not None:
            values["schema_version"] = data["schema_version"]
        t = _table(LIBRARY_ASSETS_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(
                    update(t).where(t.c.id == asset_uuid, t.c.user_id == self.user_id).values(**values)
                )
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Library asset not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_library_asset(asset_id, require_owner=True)

    def delete_library_asset(self, asset_id: str) -> None:
        """
        Delete an owned custom library asset; reject first-party (AC4).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (delete_library_asset)
        2

        Parameters
        ----------
        asset_id : object
            Argument ``asset_id``.
        """
        if self._first_party_library_out(asset_id) is not None:
            raise HTTPException(status_code=403, detail="First-party library defaults cannot be deleted")
        try:
            asset_uuid = UUID(asset_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown library asset id") from exc
        t = _table(LIBRARY_ASSETS_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(delete(t).where(t.c.id == asset_uuid, t.c.user_id == self.user_id))
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Library asset not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)

    def preview_library_rule(self, library_id: str, focus_group: str) -> tuple[str, str]:
        """
        Resolve AC11 rule association; return ``(rule_id, rule_name)``.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (preview_library_rule)
        2

        Parameters
        ----------
        library_id : object
            Argument ``library_id``.
        focus_group : object
            Argument ``focus_group``.

        Returns
        -------
        object
            Return value.
        """
        asset_out = self.get_library_asset(library_id)
        if asset_out.kind != "conversion":
            raise HTTPException(status_code=400, detail="Rule preview requires a conversion library")
        try:
            from tac2iwxxm.library_assets import LibraryAsset, require_rule_for_group
        except ImportError as exc:
            raise HTTPException(status_code=503, detail="Library assets unavailable") from exc
        domain = LibraryAsset(
            id=asset_out.id,
            kind=asset_out.kind,
            name=asset_out.name,
            access=asset_out.access,
            engine_profile_id=asset_out.engine_profile_id,
            attached_national_line=asset_out.attached_national_line,
            body=dict(asset_out.body),
            fork_of=asset_out.fork_of,
        )
        try:
            rule = require_rule_for_group(domain, focus_group=focus_group)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return rule.id, rule.name
