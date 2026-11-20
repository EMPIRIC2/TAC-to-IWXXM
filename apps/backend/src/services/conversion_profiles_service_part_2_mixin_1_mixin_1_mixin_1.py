"""Mixin extracted from ``conversion_profiles_service_part_2_mixin_1_mixin_1.py``::__ConversionProfilesServiceMethodsMixinMethodsMixin."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from ..schemas.conversion_profiles import (
    LibraryAssetCreate,
    LibraryAssetOut,
    LibraryAssetUpdate,
)
from .conversion_profiles_service_part_1 import (
    LIBRARY_ASSETS_TABLE,
    _get_engine,
    _handle_db_error,
    _reject_secrets,
    _reject_template_values,
    _table,
)


class ___ConversionProfilesServiceMethodsMixinMethodsMixinMethodsMixin:
    """Methods mixin for ``__ConversionProfilesServiceMethodsMixinMethodsMixin``."""

    def get_library_asset(self, asset_id: str, *, require_owner: bool = False) -> LibraryAssetOut:
        """
        Fetch a first-party or custom library asset; fail-closed on unknown.


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
