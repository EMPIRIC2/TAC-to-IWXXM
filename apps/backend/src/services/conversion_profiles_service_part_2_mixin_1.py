"""Mixin extracted from ``conversion_profiles_service_part_2.py``::ConversionProfilesService."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import delete, insert, or_, select, update
from sqlalchemy.exc import SQLAlchemyError

from ..schemas.conversion_profiles import (
    ConversionTemplateOut,
    ConversionTemplateSlot,
    OverlayCreate,
    OverlayOut,
    OverlayUpdate,
    RulePackCreate,
    RulePackOut,
    RulePackUpdate,
)
from .conversion_profiles_service_part_1 import (
    OVERLAYS_TABLE,
    RULE_PACKS_TABLE,
    _get_engine,
    _handle_db_error,
    _reject_secrets,
    _row_to_out,
    _table,
)
from .conversion_profiles_service_part_2_mixin_1_mixin_1 import (
    __ConversionProfilesServiceMethodsMixinMethodsMixin,
)
from .profile_overlay import sign_overlay, verify_overlay_signature


class _ConversionProfilesServiceMethodsMixin(__ConversionProfilesServiceMethodsMixinMethodsMixin):
    """Methods mixin for ``ConversionProfilesService``."""

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
