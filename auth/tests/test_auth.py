"""Auth service tests: register, login, API key, password reset.

Uses in-memory SQLite DB by setting AUTH_DB_URL before importing modules.
"""
from __future__ import annotations

import os
import importlib
import sys
import pathlib

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure src layout path precedence for imports
ROOT = pathlib.Path(__file__).resolve().parents[2]
AUTH_SRC = ROOT / "auth" / "src"
if str(AUTH_SRC) not in sys.path:
    sys.path.insert(0, str(AUTH_SRC))
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


@pytest.fixture(scope="session")
def app_client():
    # Use file-based SQLite to persist schema across connections; ensure clean start
    os.environ["AUTH_DB_URL"] = "sqlite:///./test_auth.db"
    test_db_path = pathlib.Path("test_auth.db")
    if test_db_path.exists():
        test_db_path.unlink()
    import auth.database as database
    import auth.models as models
    import auth.api as api
    importlib.reload(database)
    importlib.reload(models)
    importlib.reload(api)
    database.init_db()
    app = FastAPI()
    app.include_router(api.router)
    return TestClient(app)


def test_register_and_login(app_client):
    client = app_client
    reg_payload = {
        "name": "Test User",
        "email": "test@example.com",
        "address": "123 Test Ave",
        "username": "testuser",
        "password": "StrongPass123!",
    }
    r = client.post("/auth/register", json=reg_payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["username"] == "testuser"
    r_dup = client.post("/auth/register", json=reg_payload)
    assert r_dup.status_code == 400
    r_login = client.post(
        "/auth/login", json={"username": "testuser", "password": "StrongPass123!"})
    assert r_login.status_code == 200, r_login.text
    token = r_login.json()["access_token"]
    bad_login = client.post(
        "/auth/login", json={"username": "testuser", "password": "Wrong"})
    assert bad_login.status_code == 400
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "testuser"


def test_apikey_flow(app_client):
    client = app_client
    client.post("/auth/register", json={
        "name": "API User",
        "email": "api@example.com",
        "address": "1 Key Way",
        "username": "apiuser",
        "password": "StrongPass123!",
    })
    login = client.post(
        "/auth/login", json={"username": "apiuser", "password": "StrongPass123!"})
    token = login.json()["access_token"]
    create = client.post(
        "/auth/apikeys", headers={"Authorization": f"Bearer {token}"})
    assert create.status_code == 200, create.text
    key_id = create.json()["id"]
    list_keys = client.get(
        "/auth/apikeys", headers={"Authorization": f"Bearer {token}"})
    keys = list_keys.json()
    assert any(k["id"] == key_id for k in keys)
    revoke = client.delete(
        f"/auth/apikeys/{key_id}", headers={"Authorization": f"Bearer {token}"})
    assert revoke.status_code == 200
    list_after = client.get(
        "/auth/apikeys", headers={"Authorization": f"Bearer {token}"})
    after_keys = list_after.json()
    assert any(k["id"] == key_id and k["revoked"] for k in after_keys)


def test_password_reset_flow(app_client, monkeypatch):
    client = app_client
    captured = {"token": None}
    import auth.api as api_mod

    def fake_send(email: str, token: str):
        captured["token"] = token

    monkeypatch.setattr(api_mod, "send_reset_email", fake_send)
    client.post("/auth/register", json={
        "name": "Reset User",
        "email": "reset@example.com",
        "address": "99 Reset Rd",
        "username": "resetuser",
        "password": "OriginalPass1!",
    })
    req = client.post("/auth/password-reset/request",
                      json={"email": "reset@example.com"})
    assert req.status_code == 200
    assert captured["token"] is not None
    reset_token = captured["token"]
    conf = client.post("/auth/password-reset/confirm",
                       json={"token": reset_token, "new_password": "NewPass456!"})
    assert conf.status_code == 200, conf.text
    login_new = client.post(
        "/auth/login", json={"username": "resetuser", "password": "NewPass456!"})
    assert login_new.status_code == 200
    login_old = client.post(
        "/auth/login", json={"username": "resetuser", "password": "OriginalPass1!"})
    assert login_old.status_code == 400
