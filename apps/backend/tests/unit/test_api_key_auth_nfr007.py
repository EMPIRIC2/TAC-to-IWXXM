"""NFR-007 / FR-048 API key + rate-limit matrix (evolve-auto).

Covers success, failure, validation, and mutation permutations for
``X-API-Key`` enforcement and public key issue/revoke.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from src.services import api_key_store
from src.utilities.abuse_controls import (
    create_limiter,
    install_abuse_controls,
    rate_limit_key,
)
from src.utilities.api_key_auth import (
    ApiKeyAuthMiddleware,
    install_api_key_auth,
    path_is_api_key_exempt,
)


def _mini_app(monkeypatch: pytest.MonkeyPatch, *, required: bool = True) -> TestClient:
    monkeypatch.setenv("API_KEY_REQUIRED", "true" if required else "false")
    monkeypatch.setenv("DEMO_API_KEY", "demo-secret-key")
    monkeypatch.setenv("RATE_LIMIT_PUBLIC_PER_MIN", "3")
    # Reset limiter singleton between matrix cases.
    import src.utilities.abuse_controls as abuse

    abuse._limiter = None
    app = FastAPI()
    limiter = create_limiter()
    install_abuse_controls(app, limiter=limiter)
    install_api_key_auth(app)

    @app.get("/api/v1/ping")
    @limiter.limit("3/minute")
    async def ping(request: Request) -> dict[str, str]:
        return {"ok": "true"}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    return TestClient(app)


def test_exempt_paths() -> None:
    assert path_is_api_key_exempt("GET", "/health")
    assert path_is_api_key_exempt("POST", "/api/v1/api-keys")
    assert path_is_api_key_exempt("OPTIONS", "/api/v1/convert")
    assert path_is_api_key_exempt("GET", "/docs/oauth2-redirect")
    assert path_is_api_key_exempt("GET", "/docs/index.html")
    assert path_is_api_key_exempt("GET", "/api/v1/live-map/eval")
    assert path_is_api_key_exempt("GET", "/api/v1/station-health/eval-benchmark")
    assert path_is_api_key_exempt("GET", "/api/v1/station-health")
    assert not path_is_api_key_exempt("POST", "/api/v1/convert")


def test_non_api_paths_skip_key_check(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_KEY_REQUIRED", "true")
    monkeypatch.setenv("DEMO_API_KEY", "demo-secret-key")
    import src.utilities.abuse_controls as abuse

    abuse._limiter = None
    app = FastAPI()
    install_abuse_controls(app, limiter=create_limiter())
    install_api_key_auth(app)

    @app.get("/readyz")
    async def readyz() -> dict[str, str]:
        return {"ready": "true"}

    assert TestClient(app).get("/readyz").status_code == 200


def test_install_api_key_auth_skips_without_add_middleware() -> None:
    install_api_key_auth(object())


def test_read_happy_path_with_demo_key(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mini_app(monkeypatch, required=True)
    response = client.get(
        "/api/v1/ping",
        headers={"X-API-Key": "demo-secret-key"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": "true"}


def test_health_exempt_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mini_app(monkeypatch, required=True)
    assert client.get("/health").status_code == 200


def test_missing_key_hard_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mini_app(monkeypatch, required=True)
    response = client.get("/api/v1/ping")
    assert response.status_code == 401
    assert response.json()["detail"] == "API key required"


def test_invalid_key_hard_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mini_app(monkeypatch, required=True)
    response = client.get(
        "/api/v1/ping",
        headers={"X-API-Key": "not-a-real-key"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"


def test_empty_key_validation_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mini_app(monkeypatch, required=True)
    response = client.get("/api/v1/ping", headers={"X-API-Key": "   "})
    assert response.status_code == 401
    assert response.json()["detail"] == "API key required"


def test_enforcement_off_allows_anonymous(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mini_app(monkeypatch, required=False)
    assert client.get("/api/v1/ping").status_code == 200


def test_rate_limit_per_key_ip_returns_429(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _mini_app(monkeypatch, required=True)
    headers = {"X-API-Key": "demo-secret-key"}
    assert client.get("/api/v1/ping", headers=headers).status_code == 200
    assert client.get("/api/v1/ping", headers=headers).status_code == 200
    assert client.get("/api/v1/ping", headers=headers).status_code == 200
    limited = client.get("/api/v1/ping", headers=headers)
    assert limited.status_code == 429


def test_rate_limit_key_composites_key_and_ip() -> None:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/api/v1/ping",
        "raw_path": b"/api/v1/ping",
        "query_string": b"",
        "headers": [
            (b"x-api-key", b"abc"),
            (b"x-forwarded-for", b"203.0.113.9"),
        ],
        "client": ("127.0.0.1", 12345),
        "server": ("test", 80),
    }
    request = Request(scope)
    key = rate_limit_key(request)
    assert key.startswith("key:")
    assert key.endswith(":203.0.113.9") or ":127.0.0.1" in key


def test_hash_and_demo_verify(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEMO_API_KEY", "demo-only")
    monkeypatch.setenv("API_KEY_PEPPER", "pepper-value")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    api_key_store.reset_api_key_store_for_tests()
    assert api_key_store.verify_plaintext_key("demo-only") is not None
    assert api_key_store.verify_plaintext_key("other") is None
    assert api_key_store.verify_plaintext_key("   ") is None
    digest = api_key_store.hash_api_key("demo-only")
    assert len(digest) == 64
    monkeypatch.delenv("API_KEY_REQUIRED", raising=False)
    assert api_key_store.api_key_required_enabled() is False


def test_sync_database_url_normalizes_drivers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://u:p@h/db?ssl=require",
    )
    url = api_key_store._sync_database_url()
    assert url is not None
    assert url.startswith("postgresql+psycopg://")
    assert "sslmode=require" in url

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg2://u:p@h/db")
    assert api_key_store._sync_database_url() == "postgresql+psycopg://u:p@h/db"

    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    assert api_key_store._sync_database_url() == "postgresql+psycopg://u:p@h/db"

    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    assert api_key_store._sync_database_url() == "sqlite+pysqlite:///:memory:"


def test_table_requires_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    api_key_store.reset_api_key_store_for_tests()
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        api_key_store._table()


def test_issue_validation_label_too_long() -> None:
    with pytest.raises(ValueError, match="128"):
        api_key_store.issue_api_key(label="x" * 129)


def test_issue_requires_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    api_key_store.reset_api_key_store_for_tests()
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        api_key_store.issue_api_key(label="ops")


def test_revoke_without_key_or_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    api_key_store.reset_api_key_store_for_tests()
    assert api_key_store.revoke_api_key(key_id=uuid4(), plaintext="   ") is False
    assert api_key_store.revoke_api_key(key_id=uuid4(), plaintext="abc") is False


def _sqlite_api_keys_engine(monkeypatch: pytest.MonkeyPatch):
    """In-memory SQLite stand-in with client-side UUID defaults."""
    from sqlalchemy import Column, DateTime, MetaData, Table, Text, create_engine
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata = MetaData()
    keys = Table(
        "api_keys",
        metadata,
        Column("id", Text(), primary_key=True, default=lambda: str(uuid4())),
        Column("key_prefix", Text(), nullable=False),
        Column("key_hash", Text(), nullable=False, unique=True),
        Column("label", Text(), nullable=False, default=""),
        Column(
            "created_at",
            DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(UTC),
        ),
        Column("revoked_at", DateTime(timezone=True), nullable=True),
        Column("last_used_at", DateTime(timezone=True), nullable=True),
    )
    metadata.create_all(engine)
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    api_key_store.reset_api_key_store_for_tests()
    # Keep the in-memory Table (with Python defaults); avoid autoload that drops them.
    monkeypatch.setattr(api_key_store, "_engine", engine)
    monkeypatch.setattr(api_key_store, "_keys_table", keys)
    monkeypatch.setattr(api_key_store, "_metadata", metadata)
    return engine


def test_issue_and_revoke_with_sqlite_memory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mutation create/delete against an in-memory SQLite stand-in."""
    _sqlite_api_keys_engine(monkeypatch)

    issued = api_key_store.issue_api_key(label="ops")
    payload = api_key_store.issued_to_dict(issued)
    assert payload["label"] == "ops"
    assert payload["api_key"].startswith("t2i_")
    assert payload["created_at"].endswith("Z")

    verified = api_key_store.verify_plaintext_key(issued.api_key)
    assert verified is not None
    assert verified.source == "db"
    assert verified.id == str(issued.id)

    assert api_key_store.verify_plaintext_key("missing-key") is None

    assert api_key_store.revoke_api_key(key_id=issued.id, plaintext=issued.api_key) is True
    assert api_key_store.verify_plaintext_key(issued.api_key) is None
    assert api_key_store.revoke_api_key(key_id=issued.id, plaintext=issued.api_key) is True
    assert api_key_store.revoke_api_key(key_id=uuid4(), plaintext=issued.api_key) is False


def test_verify_fail_closed_on_db_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEMO_API_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    api_key_store.reset_api_key_store_for_tests()

    class _Boom:
        def begin(self):
            raise RuntimeError("db down")

    monkeypatch.setattr(api_key_store, "_engine", _Boom())
    monkeypatch.setattr(api_key_store, "_keys_table", object())
    assert api_key_store.verify_plaintext_key("anything") is None


def test_revoke_retries_string_id_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover UUID→str retry when the first id compare misses (line 337)."""
    engine = _sqlite_api_keys_engine(monkeypatch)
    table = api_key_store._keys_table
    assert table is not None

    key_uuid = uuid4()
    plaintext, prefix = api_key_store.generate_api_key_plaintext()
    digest = api_key_store.hash_api_key(plaintext)
    with engine.begin() as conn:
        conn.execute(
            table.insert().values(
                id=str(key_uuid),
                key_prefix=prefix,
                key_hash=digest,
                label="retry2",
                created_at=datetime.now(UTC),
            )
        )
    assert api_key_store.revoke_api_key(key_id=key_uuid, plaintext=plaintext) is True


def test_router_issue_validation_and_auth_matrix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """HTTP create validation fail + protected read success/failure."""
    monkeypatch.setenv("API_KEY_REQUIRED", "true")
    monkeypatch.setenv("DEMO_API_KEY", "demo-secret-key")
    engine = _sqlite_api_keys_engine(monkeypatch)

    import src.utilities.abuse_controls as abuse

    abuse._limiter = None
    from src.routers import api_keys as api_keys_router

    app = FastAPI()
    limiter = create_limiter()
    install_abuse_controls(app, limiter=limiter)
    app.include_router(api_keys_router.router)
    app.add_middleware(ApiKeyAuthMiddleware)

    @app.get("/api/v1/ping")
    async def ping() -> dict[str, str]:
        return {"ok": "true"}

    client = TestClient(app)

    bad = client.post("/api/v1/api-keys", json={"label": "y" * 200})
    assert bad.status_code == 422

    def _raise_label(*, label: str = "") -> None:
        _ = label
        msg = "label must be at most 128 characters"
        raise ValueError(msg)

    # Store-layer ValueError mapped to HTTP 422 (beyond Pydantic max_length).
    monkeypatch.setattr(api_keys_router, "issue_api_key", _raise_label)
    store_value = client.post("/api/v1/api-keys", json={"label": "ok"})
    assert store_value.status_code == 422
    monkeypatch.setattr(api_keys_router, "issue_api_key", api_key_store.issue_api_key)

    created = client.post("/api/v1/api-keys", json={"label": "ops"})
    assert created.status_code == 201
    body = created.json()
    assert "api_key" in body
    key_id = body["id"]
    plaintext = body["api_key"]

    ok = client.get("/api/v1/ping", headers={"X-API-Key": plaintext})
    assert ok.status_code == 200

    # Handler-level 401 (middleware would otherwise short-circuit).
    bare = FastAPI()
    install_abuse_controls(bare, limiter=create_limiter())
    bare.include_router(api_keys_router.router)
    bare_client = TestClient(bare)
    assert bare_client.delete(f"/api/v1/api-keys/{uuid4()}").status_code == 401
    assert (
        bare_client.delete(
            f"/api/v1/api-keys/{uuid4()}",
            headers={"X-API-Key": "   "},
        ).status_code
        == 401
    )

    missing = client.delete(
        f"/api/v1/api-keys/{uuid4()}",
        headers={"X-API-Key": plaintext},
    )
    assert missing.status_code == 404

    revoked = client.delete(
        f"/api/v1/api-keys/{key_id}",
        headers={"X-API-Key": plaintext},
    )
    assert revoked.status_code == 204

    # 503 when DB unavailable after reset.
    api_key_store.reset_api_key_store_for_tests()
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(api_key_store, "_engine", None)
    engine.dispose()
    missing_db = client.post("/api/v1/api-keys", json={"label": "ok"})
    assert missing_db.status_code == 503
