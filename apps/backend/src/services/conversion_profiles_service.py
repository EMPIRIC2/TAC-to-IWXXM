"""Owner-scoped CRUD for ConversionProfile rule packs (EV-933 / F7.w)."""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime
from typing import Any, NoReturn, cast
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import MetaData, Table, create_engine, delete, insert, or_, select, update
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..schemas.conversion_profiles import (
    DisseminationTemplateCreate,
    DisseminationTemplateOut,
    DisseminationTemplateUpdate,
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
_SECRET_KEY = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|uri|connection_string|dsn)")
_URI_VALUE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)

_engine: Engine | None = None
_metadata = MetaData()
_tables: dict[str, Table] = {}


def _sync_database_url() -> str:
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
    global _engine
    if _engine is None:
        _engine = create_engine(_sync_database_url(), pool_pre_ping=True)
    return _engine


def _table(name: str) -> Table:
    if name not in _tables:
        _tables[name] = Table(name, _metadata, autoload_with=_get_engine())
    return _tables[name]


def _reject_secrets(payload: dict[str, Any], *, path: str = "") -> None:
    """Raise 422 if payload keys look like secrets or URIs."""
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
    """JWT-owner scoped rule pack persistence."""

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
        """List rule packs owned by the caller."""
        t = _table(RULE_PACKS_TABLE)
        try:
            with _get_engine().connect() as conn:
                rows = conn.execute(select(t).where(t.c.user_id == self.user_id).order_by(t.c.slug)).mappings().all()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return [_row_to_out(dict(r)) for r in rows]

    def list_presets(self) -> list[PresetOut]:
        """List semantic presets owned by the caller (plus shared rows)."""
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
        """Fetch one semantic preset by id (owner or shared)."""
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
        """Insert a new semantic preset."""
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
        """Patch an owned semantic preset."""
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
        """Delete a semantic preset owned by the caller."""
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
        """List dissemination templates owned by the caller (plus shared rows)."""
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
        """Fetch one dissemination template by id (owner or shared)."""
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
        """Insert a new dissemination template."""
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
        """Patch an owned dissemination template."""
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
        """Delete a dissemination template owned by the caller."""
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
        """Fetch one rule pack by id (owner-scoped)."""
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
        """Insert a new rule pack."""
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
        """Patch an existing rule pack."""
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
        """Delete a rule pack owned by the caller."""
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
        """List overlays owned by the caller (plus shared rows)."""
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
        """Fetch one overlay by id (owner or shared)."""
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
        """Insert a new server-signed overlay."""
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
        """Patch an owned overlay and re-sign."""
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
        """Delete an overlay owned by the caller."""
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
