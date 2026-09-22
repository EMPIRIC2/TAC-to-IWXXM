"""TC-EVBRIDGE — library assets API (router + service CRUD / preview)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from src.api import app
from src.routers import conversion_profiles as profiles_router
from src.schemas.conversion_profiles import (
    LibraryAssetCreate,
    LibraryAssetOut,
    LibraryAssetUpdate,
)
from src.services import conversion_profiles_service as svc
from src.services.conversion_profiles_service import ConversionProfilesService
from src.utilities.security import verify_supabase_token
from tac2iwxxm.library_assets import list_first_party_library_assets

USER_ID = uuid4()
ASSET_ID = uuid4()
NOW = datetime(2026, 9, 15, tzinfo=UTC)


def _svc() -> ConversionProfilesService:
    return ConversionProfilesService(user_id=str(uuid4()))


def _fp_out() -> LibraryAssetOut:
    return LibraryAssetOut(
        id="LIB.CONVERSION.ICAO_2025",
        kind="conversion",
        name="ICAO Conversion",
        access="first_party",
        engine_profile_id="ICAO_2025",
        attached_national_line="ICAO",
        body={"rules": []},
        shared=True,
    )


def _custom_out(**overrides: Any) -> LibraryAssetOut:
    base = LibraryAssetOut(
        id=str(ASSET_ID),
        kind="conversion",
        name="My conversion",
        access="custom",
        engine_profile_id="ICAO_2025",
        attached_national_line="ICAO",
        body={"rules": []},
        fork_of="LIB.CONVERSION.ICAO_2025",
        user_id=USER_ID,
        slug="my-conversion",
        shared=False,
        created_at=NOW,
        updated_at=NOW,
    )
    return base.model_copy(update=overrides)


class _FakeLibrarySvc:
    def __init__(self) -> None:
        self.custom = _custom_out()

    def list_library_assets(self, *, kind: str | None = None) -> list[LibraryAssetOut]:
        items = [_fp_out(), self.custom]
        if kind is not None:
            items = [i for i in items if i.kind == kind]
        return items

    def get_library_asset(self, asset_id: str, *, require_owner: bool = False) -> LibraryAssetOut:
        if asset_id == "LIB.CONVERSION.ICAO_2025":
            if require_owner:
                raise HTTPException(status_code=403, detail="First-party library assets are read-only")
            return _fp_out()
        if asset_id == str(ASSET_ID):
            return self.custom
        raise HTTPException(status_code=404, detail="Library asset not found")

    def create_library_asset(self, payload: LibraryAssetCreate) -> LibraryAssetOut:
        self.custom = self.custom.model_copy(
            update={
                "slug": payload.slug,
                "name": payload.name,
                "kind": payload.kind,
                "body": payload.body,
                "fork_of": payload.fork_of,
            }
        )
        return self.custom

    def update_library_asset(self, asset_id: str, payload: LibraryAssetUpdate) -> LibraryAssetOut:
        if asset_id == "LIB.CONVERSION.ICAO_2025":
            return self.create_library_asset(
                LibraryAssetCreate(
                    slug=payload.slug or "forked",
                    name=payload.name or "Fork",
                    kind="conversion",
                    engineProfileId="ICAO_2025",
                    attachedNationalLine="ICAO",
                    body=payload.body or {},
                    forkOf="LIB.CONVERSION.ICAO_2025",
                )
            )
        data = payload.model_dump(exclude_unset=True, by_alias=False)
        self.custom = self.custom.model_copy(update=data)
        return self.custom

    def delete_library_asset(self, asset_id: str) -> None:
        if asset_id == "LIB.DECODING.US_FAA_NWS":
            raise HTTPException(status_code=403, detail="First-party library defaults cannot be deleted")
        if asset_id != str(ASSET_ID):
            raise HTTPException(status_code=404, detail="Library asset not found")

    def preview_library_rule(self, library_id: str, focus_group: str) -> tuple[str, str]:
        if library_id != "LIB.CONVERSION.ICAO_2025":
            raise HTTPException(status_code=400, detail="Rule preview requires a conversion library")
        if focus_group == "NOTAGROUPXYZ":
            raise HTTPException(status_code=400, detail="unmatched")
        return "CV.WIND", "Wind group"

    def validate_library_yaml_document(
        self,
        yaml_body: str,
        *,
        kind: str,
        lifecycle: str = "draft",
    ) -> dict[str, Any]:
        from tac2iwxxm.library_yaml import LibraryKind, LibraryLifecycle, validate_library_yaml

        return validate_library_yaml(
            yaml_body,
            expected_kind=cast(LibraryKind, kind),
            lifecycle=cast(LibraryLifecycle, lifecycle),
        ).to_dict()


@pytest.fixture
def client() -> Any:
    fake = _FakeLibrarySvc()

    async def override_verify() -> dict[str, str]:
        return {"sub": str(USER_ID)}

    def override_service() -> _FakeLibrarySvc:
        return fake

    app.dependency_overrides[verify_supabase_token] = override_verify
    app.dependency_overrides[profiles_router.profiles_service] = override_service
    yield TestClient(app), fake
    app.dependency_overrides.clear()


def test_list_first_party_library_assets_projection() -> None:
    """First-party catalog projects to LibraryAssetOut."""
    service = _svc()
    items = []
    for asset in list_first_party_library_assets():
        out = service._first_party_library_out(asset.id)
        assert out is not None
        items.append(out)
    assert len(items) >= 5 * 2
    kinds = {i.kind for i in items}
    assert kinds == {
        "conversion",
        "tac_validation",
        "iwxxm_validation",
        "dissemination",
        "decoding",
    }


def test_preview_library_rule_wind_match() -> None:
    """AC11 preview resolves CV.WIND for a wind group."""
    service = _svc()
    rule_id, rule_name = service.preview_library_rule(
        "LIB.CONVERSION.ICAO_2025",
        "18012G20KT",
    )
    assert rule_id == "CV.WIND"
    assert rule_name


def test_preview_library_rule_unmatched_fail_closed() -> None:
    """AC11 unmatched group fails closed."""
    service = _svc()
    with pytest.raises(HTTPException) as exc:
        service.preview_library_rule("LIB.CONVERSION.ICAO_2025", "NOTAGROUPXYZ")
    assert exc.value.status_code == 400


def test_preview_library_rule_non_conversion_rejected() -> None:
    """Rule preview requires a conversion library."""
    service = _svc()
    with pytest.raises(HTTPException) as exc:
        service.preview_library_rule("LIB.DISSEMINATION.ICAO_2025", "18012G20KT")
    assert exc.value.status_code == 400


def test_delete_first_party_library_forbidden() -> None:
    """AC4: cannot delete first-party defaults."""
    service = _svc()
    with pytest.raises(HTTPException) as exc:
        service.delete_library_asset("LIB.DECODING.US_FAA_NWS")
    assert exc.value.status_code == 403


def test_router_library_assets_crud_and_preview(client: Any) -> None:
    """HTTP surface: list/get remain; mutate routes return 410 (authoring retired)."""
    http, _fake = client
    listed = http.get("/api/v1/profiles/library-assets")
    assert listed.status_code == 200
    assert len(listed.json()["items"]) >= 2

    filtered = http.get("/api/v1/profiles/library-assets", params={"kind": "conversion"})
    assert filtered.status_code == 200
    assert all(i["kind"] == "conversion" for i in filtered.json()["items"])

    created = http.post(
        "/api/v1/profiles/library-assets",
        json={
            "slug": "forked-conv",
            "name": "Forked",
            "kind": "conversion",
            "engineProfileId": "ICAO_2025",
            "attachedNationalLine": "ICAO",
            "body": {"rules": []},
            "forkOf": "LIB.CONVERSION.ICAO_2025",
        },
    )
    assert created.status_code == 410
    assert created.json()["detail"]["code"] == "library_authoring_retired"

    got = http.get(f"/api/v1/profiles/library-assets/{ASSET_ID}")
    assert got.status_code == 200
    assert got.json()["id"] == str(ASSET_ID)

    patched = http.patch(
        f"/api/v1/profiles/library-assets/{ASSET_ID}",
        json={"name": "Renamed"},
    )
    assert patched.status_code == 410

    preview = http.post(
        "/api/v1/profiles/library-assets/preview-rule",
        json={"libraryId": "LIB.CONVERSION.ICAO_2025", "focusGroup": "18012G20KT"},
    )
    assert preview.status_code == 410

    validated = http.post(
        "/api/v1/profiles/library-assets/validate-yaml",
        json={
            "kind": "tac_validation",
            "yamlBody": "kind: tac_validation\nname: Wind\nrules:\n  - pattern: '(?P<wind>\\\\d{5})KT'\n",
            "lifecycle": "draft",
        },
    )
    assert validated.status_code == 410

    deleted = http.delete(f"/api/v1/profiles/library-assets/{ASSET_ID}")
    assert deleted.status_code == 410


class _Result:
    def __init__(self, row: dict[str, Any] | None = None, rows: list[dict[str, Any]] | None = None) -> None:
        self._row = row
        self._rows = rows if rows is not None else ([] if row is None else [row])

    def mappings(self) -> _Result:
        return self

    def first(self) -> dict[str, Any] | None:
        return self._row

    def all(self) -> list[dict[str, Any]]:
        return self._rows


def _stmt_chain() -> MagicMock:
    stmt = MagicMock()
    stmt.where.return_value = stmt
    stmt.order_by.return_value = stmt
    return stmt


def _library_row(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": ASSET_ID,
        "user_id": USER_ID,
        "slug": "my-conversion",
        "name": "My conversion",
        "kind": "conversion",
        "engine_profile_id": "ICAO_2025",
        "attached_national_line": "ICAO",
        "body": {"rules": []},
        "fork_of": "LIB.CONVERSION.ICAO_2025",
        "shared": False,
        "created_at": NOW,
        "updated_at": NOW,
    }
    base.update(overrides)
    return base


@pytest.fixture
def service() -> ConversionProfilesService:
    return ConversionProfilesService(str(USER_ID))


def test_library_asset_service_crud_mocked(service: ConversionProfilesService) -> None:
    """Cover list/get/create/update/delete library asset DB paths."""
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    begin_conn.execute.return_value.rowcount = 1
    custom = _library_row()
    updated = {**custom, "name": "Renamed"}
    read_conn.execute.side_effect = [
        _Result(rows=[custom]),
        _Result(row=custom),
        _Result(row=custom),
        _Result(row=updated),
        _Result(row=updated),
    ]
    ins = MagicMock()
    ins.values.return_value = "insert-stmt"
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    dele = MagicMock()
    dele.where.return_value = "d"

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=ins),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "delete", return_value=dele),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "or_", return_value="owner-or-shared"),
    ):
        items = service.list_library_assets()
        assert any(i.id == "LIB.CONVERSION.ICAO_2025" for i in items)
        assert any(i.slug == "my-conversion" for i in items)

        filtered = service.list_library_assets(kind="conversion")
        assert all(i.kind == "conversion" for i in filtered)

        fp = service.get_library_asset("LIB.CONVERSION.ICAO_2025")
        assert fp.access == "first_party"
        with pytest.raises(HTTPException) as own_exc:
            service.get_library_asset("LIB.CONVERSION.ICAO_2025", require_owner=True)
        assert own_exc.value.status_code == 403

        created = service.create_library_asset(
            LibraryAssetCreate(
                slug="forked",
                name="Forked",
                kind="conversion",
                engineProfileId="ICAO_2025",
                attachedNationalLine="ICAO",
                body={"rules": []},
                forkOf="LIB.CONVERSION.ICAO_2025",
            )
        )
        assert created.slug == "my-conversion"

        patched = service.update_library_asset(
            str(ASSET_ID),
            LibraryAssetUpdate(name="Renamed"),
        )
        assert patched.name == "Renamed"

        forked = service.update_library_asset(
            "LIB.CONVERSION.ICAO_2025",
            LibraryAssetUpdate(name="Fork edit", body={"rules": [{"id": "x"}]}),
        )
        assert forked.fork_of == "LIB.CONVERSION.ICAO_2025" or forked.access == "custom"

        service.delete_library_asset(str(ASSET_ID))


def test_list_library_assets_skips_null_first_party_projection(
    service: ConversionProfilesService,
) -> None:
    """When first-party projection returns None, list continues (branch 912->908)."""
    engine = MagicMock()
    read_conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = read_conn
    read_conn.execute.return_value = _Result(rows=[])
    with (
        patch.object(svc.ConversionProfilesService, "_first_party_library_out", return_value=None),
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "or_", return_value="x"),
    ):
        assert service.list_library_assets(kind="decoding") == []


def test_library_asset_service_error_paths(service: ConversionProfilesService) -> None:
    """Fail-closed paths for library assets."""
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    other = _library_row(user_id=uuid4(), shared=False)
    shared = _library_row(shared=True, user_id=uuid4())
    read_conn.execute.side_effect = [
        _Result(row=None),
        _Result(row=other),
        _Result(row=other),
        _Result(row=shared),
        SQLAlchemyError("list boom"),
        SQLAlchemyError("get boom"),
        _Result(row=_library_row(body="not-a-dict")),
    ]

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as bad_id,
    ):
        service.get_library_asset("not-a-uuid")
    assert bad_id.value.status_code == 400

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as missing,
    ):
        service.get_library_asset(str(ASSET_ID))
    assert missing.value.status_code == 404

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as forbidden,
    ):
        service.get_library_asset(str(ASSET_ID))
    assert forbidden.value.status_code == 403

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        pytest.raises(HTTPException) as owner_req,
    ):
        service.get_library_asset(str(ASSET_ID), require_owner=True)
    assert owner_req.value.status_code == 403

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        got = service.get_library_asset(str(ASSET_ID))
        assert got.shared is True

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "or_", return_value="x"),
        patch.object(svc, "_handle_db_error", side_effect=HTTPException(status_code=503, detail="db")),
        pytest.raises(HTTPException),
    ):
        service.list_library_assets()

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "_handle_db_error", side_effect=HTTPException(status_code=503, detail="db")),
        pytest.raises(HTTPException),
    ):
        service.get_library_asset(str(ASSET_ID))

    with (
        patch.object(svc.ConversionProfilesService, "_first_party_library_out", return_value=None),
        pytest.raises(HTTPException) as bad_upd,
    ):
        service.update_library_asset("not-uuid", LibraryAssetUpdate(name="x"))
    assert bad_upd.value.status_code == 400

    with (
        patch.object(svc.ConversionProfilesService, "_first_party_library_out", return_value=None),
        pytest.raises(HTTPException) as bad_del,
    ):
        service.delete_library_asset("not-uuid")
    assert bad_del.value.status_code == 400

    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        out = service._library_row_to_out(_library_row(body="not-a-dict"))
        assert out.body == {}

    ins = MagicMock()
    ins.values.return_value = "i"
    begin_conn.execute.side_effect = SQLAlchemyError("create boom")
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "insert", return_value=ins),
        patch.object(svc, "_handle_db_error", side_effect=HTTPException(status_code=503, detail="db")),
        pytest.raises(HTTPException),
    ):
        service.create_library_asset(
            LibraryAssetCreate(
                slug="x",
                name="x",
                kind="conversion",
                engineProfileId="ICAO_2025",
                attachedNationalLine="ICAO",
                body={},
            )
        )

    with pytest.raises(HTTPException) as uri_exc:
        service.create_library_asset(
            LibraryAssetCreate(
                slug="uri-bad",
                name="uri-bad",
                kind="dissemination",
                engineProfileId="ICAO_2025",
                attachedNationalLine="ICAO",
                body={"endpoint": "postgresql://user:pass@host/db"},
            )
        )
    assert uri_exc.value.status_code == 422

    begin_conn.execute.side_effect = None
    begin_conn.execute.return_value.rowcount = 0
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    with (
        patch.object(svc.ConversionProfilesService, "_first_party_library_out", return_value=None),
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "update", return_value=upd),
        pytest.raises(HTTPException) as miss_upd,
    ):
        service.update_library_asset(str(ASSET_ID), LibraryAssetUpdate(name="gone"))
    assert miss_upd.value.status_code == 404

    begin_conn.execute.side_effect = SQLAlchemyError("upd boom")
    with (
        patch.object(svc.ConversionProfilesService, "_first_party_library_out", return_value=None),
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "update", return_value=upd),
        patch.object(svc, "_handle_db_error", side_effect=HTTPException(status_code=503, detail="db")),
        pytest.raises(HTTPException),
    ):
        service.update_library_asset(str(ASSET_ID), LibraryAssetUpdate(name="x"))

    begin_conn.execute.side_effect = None
    begin_conn.execute.return_value.rowcount = 0
    dele = MagicMock()
    dele.where.return_value = "d"
    with (
        patch.object(svc.ConversionProfilesService, "_first_party_library_out", return_value=None),
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "delete", return_value=dele),
        pytest.raises(HTTPException) as miss_del,
    ):
        service.delete_library_asset(str(ASSET_ID))
    assert miss_del.value.status_code == 404

    begin_conn.execute.side_effect = SQLAlchemyError("del boom")
    with (
        patch.object(svc.ConversionProfilesService, "_first_party_library_out", return_value=None),
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "delete", return_value=dele),
        patch.object(svc, "_handle_db_error", side_effect=HTTPException(status_code=503, detail="db")),
        pytest.raises(HTTPException),
    ):
        service.delete_library_asset(str(ASSET_ID))

    with pytest.raises(HTTPException) as secret_exc:
        service.update_library_asset(
            "LIB.CONVERSION.ICAO_2025",
            LibraryAssetUpdate(body={"password": "secret"}),
        )
    assert secret_exc.value.status_code == 422

    with (
        patch.object(svc.ConversionProfilesService, "_first_party_library_out", return_value=None),
        pytest.raises(HTTPException) as custom_secret,
    ):
        service.update_library_asset(
            str(ASSET_ID),
            LibraryAssetUpdate(body={"api_key": "sekrit"}),
        )
    assert custom_secret.value.status_code == 422

    begin_conn.execute.side_effect = None
    begin_conn.execute.return_value.rowcount = 1
    read_conn.execute.side_effect = [_Result(row=_library_row(body={"rules": [{"id": "a"}]}))]
    upd2 = MagicMock()
    upd2.where.return_value = upd2
    upd2.values.return_value = "u2"
    with (
        patch.object(svc.ConversionProfilesService, "_first_party_library_out", return_value=None),
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "update", return_value=upd2),
        patch.object(svc, "select", return_value=_stmt_chain()),
    ):
        body_upd = service.update_library_asset(
            str(ASSET_ID),
            LibraryAssetUpdate(body={"rules": [{"id": "a"}]}),
        )
        assert body_upd.body == {"rules": [{"id": "a"}]}


def test_first_party_library_import_fallback(service: ConversionProfilesService) -> None:
    """ImportError branches for first-party projection / list / preview."""
    real_import = __import__

    def _fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "tac2iwxxm.library_assets" or (
            name == "tac2iwxxm"
            and isinstance(kwargs.get("fromlist"), (list, tuple))
            and "library_assets" in kwargs["fromlist"]
        ):
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=_fake_import):
        assert service._first_party_library_out("LIB.CONVERSION.ICAO_2025") is None

    engine = MagicMock()
    read_conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = read_conn
    read_conn.execute.return_value = _Result(rows=[])
    with (
        patch("builtins.__import__", side_effect=_fake_import),
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "or_", return_value="x"),
    ):
        assert service.list_library_assets() == []

    with (
        patch.object(
            svc.ConversionProfilesService,
            "get_library_asset",
            return_value=_fp_out(),
        ),
        patch("builtins.__import__", side_effect=_fake_import),
        pytest.raises(HTTPException) as exc,
    ):
        service.preview_library_rule("LIB.CONVERSION.ICAO_2025", "18012G20KT")
    assert exc.value.status_code == 503


def test_validate_library_yaml_and_activate_gate(service: ConversionProfilesService) -> None:
    """TC-EVPYL-ACTIVATE — Draft may Fail; Activate requires zero Fail."""
    ok = service.validate_library_yaml_document(
        "kind: conversion\nname: Wind\nrules: []\n",
        kind="conversion",
    )
    assert ok["can_activate"] is True
    extra = service._enforce_yaml_lifecycle(
        yaml_body="kind: conversion\nname: Wind\nrules: []\n",
        kind="conversion",
        lifecycle_status="activated",
    )
    assert extra["status"] == "activated"
    assert extra["name"] == "Wind"

    draft_fail = service._enforce_yaml_lifecycle(
        yaml_body="kind: tac_validation\nname: Broken\nrules:\n  - pattern: '(unclosed'\n",
        kind="tac_validation",
        lifecycle_status="draft",
    )
    assert draft_fail["status"] == "draft"

    with pytest.raises(HTTPException) as exc:
        service._enforce_yaml_lifecycle(
            yaml_body="kind: tac_validation\nname: Broken\nrules:\n  - pattern: '(unclosed'\n",
            kind="tac_validation",
            lifecycle_status="activated",
        )
    assert exc.value.status_code == 422

    with pytest.raises(HTTPException) as missing:
        service._enforce_yaml_lifecycle(yaml_body=None, kind="conversion", lifecycle_status="activated")
    assert missing.value.status_code == 422

    draft_none = service._enforce_yaml_lifecycle(
        yaml_body=None,
        kind="conversion",
        lifecycle_status="draft",
    )
    assert draft_none["status"] == "draft"

    invalid = service._enforce_yaml_lifecycle(
        yaml_body="kind: conversion\n  bad indent",
        kind="conversion",
        lifecycle_status="draft",
    )
    assert "body" not in invalid

    with patch.object(
        ConversionProfilesService,
        "validate_library_yaml_document",
        return_value={"valid_yaml": True, "can_activate": True, "data": ["nope"], "name": "  "},
    ):
        odd = service._enforce_yaml_lifecycle(
            yaml_body="kind: conversion\nname: x\n",
            kind="conversion",
            lifecycle_status="draft",
        )
    assert "body" not in odd
    assert "name" not in odd


def test_update_library_asset_yaml_and_schema_version(service: ConversionProfilesService) -> None:
    """Persist yaml_body, status, and schema_version on PATCH."""
    engine = MagicMock()
    begin_conn = MagicMock()
    read_conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = begin_conn
    engine.connect.return_value.__enter__.return_value = read_conn
    begin_conn.execute.return_value.rowcount = 1
    row = _library_row(yaml_body="kind: conversion\nname: x\n", status="draft")
    activated = {**row, "status": "activated", "schema_version": 2}
    read_conn.execute.side_effect = [
        _Result(row=row),
        _Result(row=activated),
    ]
    upd = MagicMock()
    upd.where.return_value = upd
    upd.values.return_value = "u"
    with (
        patch.object(svc, "_get_engine", return_value=engine),
        patch.object(svc, "_table", return_value=MagicMock()),
        patch.object(svc, "select", return_value=_stmt_chain()),
        patch.object(svc, "update", return_value=upd),
    ):
        out = service.update_library_asset(
            str(ASSET_ID),
            LibraryAssetUpdate(
                yamlBody="kind: conversion\nname: Wind\nrules: []\n",
                status="activated",
                schemaVersion=2,
            ),
        )
    assert out.status == "activated"
    assert out.schema_version == 2


def test_library_row_maps_yaml_lifecycle_columns() -> None:
    """Custom rows expose yaml_body / status / schema_version."""
    service = _svc()
    out = service._library_row_to_out(
        _library_row(yaml_body="kind: conversion\nname: x\n", status="activated", schema_version=2)
    )
    assert out.status == "activated"
    assert out.schema_version == 2
    assert out.yaml_body is not None
    draft = service._library_row_to_out(_library_row())
    assert draft.status == "draft"
    assert draft.schema_version == 1


def test_validate_library_yaml_unavailable(service: ConversionProfilesService) -> None:
    """Fail closed when tac2iwxxm.library_yaml cannot be imported."""
    real_import = __import__

    def _fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "tac2iwxxm.library_yaml" or (
            name == "tac2iwxxm" and kwargs.get("fromlist") and "library_yaml" in kwargs["fromlist"]
        ):
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=_fake_import), pytest.raises(HTTPException) as exc:
        service.validate_library_yaml_document("kind: conversion\nname: x\n", kind="conversion")
    assert exc.value.status_code == 503
