"""Success / failure / validation tests for WIS2 exchange-admin."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.services.exchange_admin import (
    clear_exchange_admin_state,
    user_has_exchange_admin,
)
from src.utilities.security import verify_supabase_token


@pytest.fixture
def admin_client(monkeypatch: pytest.MonkeyPatch):
    clear_exchange_admin_state()
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "wis2box,127.0.0.1")

    async def _admin():
        return {
            "sub": "admin-1",
            "app_metadata": {"roles": ["exchange-admin"]},
        }

    api_module.app.dependency_overrides[verify_supabase_token] = _admin
    with TestClient(api_module.app) as client:
        yield client
    api_module.app.dependency_overrides.clear()
    clear_exchange_admin_state()


@pytest.fixture
def plain_client():
    clear_exchange_admin_state()

    async def _user():
        return {"sub": "user-1", "app_metadata": {"roles": ["operator"]}}

    api_module.app.dependency_overrides[verify_supabase_token] = _user
    with TestClient(api_module.app) as client:
        yield client
    api_module.app.dependency_overrides.clear()
    clear_exchange_admin_state()


def test_role_detection_success() -> None:
    assert user_has_exchange_admin({"app_metadata": {"roles": ["exchange-admin"]}})


def test_role_detection_failure() -> None:
    assert user_has_exchange_admin({"app_metadata": {"roles": ["operator"]}}) is False


def test_role_detection_singular_role_and_tuple_bags() -> None:
    """Cover role / roles bag shapes used by Auth metadata."""
    assert user_has_exchange_admin({"app_metadata": {"role": "exchange-admin"}})
    assert user_has_exchange_admin(
        {"user_metadata": {"roles": ("exchange-admin",)}}
    )
    assert user_has_exchange_admin(
        {"app_metadata": {"roles": None, "role": "operator"}, "role": "exchange-admin"}
    )
    assert user_has_exchange_admin({"role": "exchange-admin"})
    # Non str/list/tuple roles values are ignored (fall through the isinstance chain).
    assert user_has_exchange_admin({"app_metadata": {"roles": 1}, "role": "exchange-admin"})


def test_allowlist_success_read_only(admin_client: TestClient) -> None:
    resp = admin_client.get("/api/v1/exchange-admin/allowlist")
    assert resp.status_code == 200
    body = resp.json()
    assert body["read_only"] is True
    assert body["admin_replay"] is False
    assert body["sink_scope"] == "wis2"
    assert "wis2box" in body["entries"]


def test_allowlist_failure_forbidden(plain_client: TestClient) -> None:
    resp = plain_client.get("/api/v1/exchange-admin/allowlist")
    assert resp.status_code == 403


def test_invitation_groups_and_select_success(plain_client: TestClient) -> None:
    groups = plain_client.get("/api/v1/exchange-admin/invitation-groups")
    assert groups.status_code == 200
    group_id = groups.json()["groups"][0]["id"]
    put = plain_client.put(
        "/api/v1/exchange-admin/invitation-group",
        json={"group_id": group_id},
    )
    assert put.status_code == 200
    assert put.json()["invitation_group_id"] == group_id


def test_invitation_group_validation_missing(plain_client: TestClient) -> None:
    resp = plain_client.put("/api/v1/exchange-admin/invitation-group", json={})
    assert resp.status_code == 422


def test_invitation_group_unknown_returns_400(plain_client: TestClient) -> None:
    resp = plain_client.put(
        "/api/v1/exchange-admin/invitation-group",
        json={"group_id": "group-does-not-exist"},
    )
    assert resp.status_code == 400
    assert "unknown" in resp.text.lower()


def test_template_validation_missing_fields(admin_client: TestClient) -> None:
    resp = admin_client.put(
        "/api/v1/exchange-admin/templates",
        json={"name": "Incomplete", "mqtt_host": "wis2box"},
    )
    assert resp.status_code == 400
    assert "required" in resp.text.lower()


def test_prefs_default_created_on_first_read(admin_client: TestClient) -> None:
    prefs = admin_client.get("/api/v1/exchange-admin/prefs")
    assert prefs.status_code == 200
    body = prefs.json()
    assert body["include_national_remarks"] is False
    assert body["invitation_group_id"] is None


def test_national_remarks_toggle_success(admin_client: TestClient) -> None:
    resp = admin_client.put(
        "/api/v1/exchange-admin/prefs/national-remarks",
        json={"include": True},
    )
    assert resp.status_code == 200
    assert resp.json()["include_national_remarks"] is True
    prefs = admin_client.get("/api/v1/exchange-admin/prefs")
    assert prefs.json()["include_national_remarks"] is True
    assert prefs.json()["admin_replay"] is False


def test_template_upsert_success_and_secret_rejected(admin_client: TestClient) -> None:
    ok = admin_client.put(
        "/api/v1/exchange-admin/templates",
        json={
            "name": "Demo WIS2",
            "mqtt_host": "wis2box",
            "mqtt_topic": "origin/a/wis2",
            "dataset_url": "http://127.0.0.1/ds",
        },
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["name"] == "Demo WIS2"
    listed = admin_client.get("/api/v1/exchange-admin/templates")
    assert listed.status_code == 200
    assert listed.json()["vault"] is False
    assert len(listed.json()["templates"]) == 1

    bad = admin_client.put(
        "/api/v1/exchange-admin/templates",
        json={
            "name": "Bad",
            "mqtt_host": "wis2box",
            "mqtt_topic": "t",
            "dataset_url": "http://127.0.0.1/ds",
            "mqtt_password": "secret",
        },
    )
    assert bad.status_code == 400
    assert "secret" in bad.text.lower()


@pytest.mark.parametrize(
    ("path", "payload", "expected"),
    [
        ("/api/v1/exchange-admin/invitation-group", {}, 422),
        ("/api/v1/exchange-admin/prefs/national-remarks", {}, 422),
        ("/api/v1/exchange-admin/templates", "not-json", 422),
    ],
    ids=["invitation-group", "national-remarks", "templates"],
)
def test_exchange_admin_put_validation(
    admin_client: TestClient,
    path: str,
    payload: object,
    expected: int,
) -> None:
    """Validation mode: malformed PUT bodies return 422."""
    if payload == "not-json":
        resp = admin_client.put(
            path,
            content=b"not-json",
            headers={"content-type": "application/json"},
        )
    else:
        resp = admin_client.put(path, json=payload)
    assert resp.status_code == expected

