"""Mixin extracted from ``conversion_profiles_service_part_2_mixin_1.py``::_ConversionProfilesServiceMethodsMixin."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal, cast
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import delete, insert, or_, select, update
from sqlalchemy.exc import SQLAlchemyError

from ..schemas.conversion_profiles import (
    ConversionTemplateCreate,
    ConversionTemplateOut,
    ConversionTemplateSlot,
    ConversionTemplateUpdate,
    LibraryAssetOut,
)
from .conversion_profiles_service_part_1 import (
    CONVERSION_TEMPLATES_TABLE,
    LIBRARY_ASSETS_TABLE,
    _get_engine,
    _handle_db_error,
    _reject_secrets,
    _table,
)
from .conversion_profiles_service_part_2_mixin_1_mixin_1_mixin_1 import (
    ___ConversionProfilesServiceMethodsMixinMethodsMixinMethodsMixin,
)


class __ConversionProfilesServiceMethodsMixinMethodsMixin(
    ___ConversionProfilesServiceMethodsMixinMethodsMixinMethodsMixin
):
    """Methods mixin for ``_ConversionProfilesServiceMethodsMixin``."""

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
