"""Part 2 of ``conversion_profiles_service.py`` (line-cap split)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import delete, insert, or_, select, update
from sqlalchemy.exc import SQLAlchemyError

from ..schemas.conversion_profiles import (
    DisseminationTemplateCreate,
    DisseminationTemplateOut,
    DisseminationTemplateUpdate,
    PresetCreate,
    PresetOut,
    PresetUpdate,
    RulePackOut,
)
from .conversion_profiles_service_part_1 import (
    PRESETS_TABLE,
    RULE_PACKS_TABLE,
    TEMPLATES_TABLE,
    _get_engine,
    _handle_db_error,
    _preset_row_to_out,
    _reject_secrets,
    _reject_template_values,
    _row_to_out,
    _table,
    _template_row_to_out,
)
from .conversion_profiles_service_part_2_mixin_1 import _ConversionProfilesServiceMethodsMixin


class ConversionProfilesService(_ConversionProfilesServiceMethodsMixin):
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
