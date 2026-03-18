"""Unit tests for async database service helpers."""

from contextlib import asynccontextmanager

import pytest

from src.services import database as db


class _FakeAsyncSession:
    def __init__(self):
        self.closed = False
        self.executed = []

    async def close(self):
        self.closed = True

    async def execute(self, query):
        self.executed.append(query)
        return 1


class _FakeEngine:
    def __init__(self):
        self.disposed = False
        self.pool = self
        self.created_tables = False

    async def dispose(self):
        self.disposed = True

    def size(self):
        return 5

    def checkedout(self):
        return 2

    @asynccontextmanager
    async def begin(self):
        class _Conn:
            async def run_sync(self, fn):
                fn(type("Conn", (), {})())

        yield _Conn()


@pytest.mark.parametrize(
    "env_name,env_value,expected",
    [
        ("DATABASE_URL", "postgresql+psycopg2://u:p@h:5432/db", "postgresql+asyncpg://u:p@h:5432/db"),
        ("SUPABASE_DB_URL", "postgresql+psycopg2://a:b@x:5432/y", "postgresql+asyncpg://a:b@x:5432/y"),
    ],
)
def test_get_database_url_uses_direct_env(monkeypatch, env_name, env_value, expected) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    monkeypatch.setenv(env_name, env_value)

    assert db.get_database_url() == expected


def test_get_database_url_builds_from_components(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    monkeypatch.setenv("POSTGRES_HOST", "db.local")
    monkeypatch.setenv("POSTGRES_PORT", "6543")
    monkeypatch.setenv("POSTGRES_DB", "metar")
    monkeypatch.setenv("POSTGRES_USER", "svc")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")

    assert db.get_database_url() == "postgresql+asyncpg://svc:secret@db.local:6543/metar"


def test_get_database_url_warns_when_password_missing(monkeypatch, caplog) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    monkeypatch.setenv("POSTGRES_HOST", "db.local")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "metar")
    monkeypatch.setenv("POSTGRES_USER", "svc")
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)

    with caplog.at_level("WARNING"):
        url = db.get_database_url()

    assert url == "postgresql+asyncpg://svc:@db.local:5432/metar"
    assert "No PostgreSQL password configured" in caplog.text


@pytest.mark.asyncio
async def test_init_db_engine_returns_existing_instance() -> None:
    existing = _FakeEngine()
    db._engine = existing

    returned = await db.init_db_engine()

    assert returned is existing
    db._engine = None


@pytest.mark.asyncio
async def test_init_db_engine_initializes_engine_and_sessionmaker(monkeypatch) -> None:
    fake_engine = _FakeEngine()
    created = {"engine": 0, "maker": 0}

    def fake_create_async_engine(*args, **kwargs):
        created["engine"] += 1
        return fake_engine

    def fake_async_sessionmaker(*args, **kwargs):
        created["maker"] += 1

        @asynccontextmanager
        async def _maker():
            yield _FakeAsyncSession()

        return _maker

    monkeypatch.setattr(db, "get_database_url", lambda: "postgresql+asyncpg://u:p@h:5432/db")
    monkeypatch.setattr(db, "create_async_engine", fake_create_async_engine)
    monkeypatch.setattr(db, "async_sessionmaker", fake_async_sessionmaker)

    db._engine = None
    db._async_session_maker = None

    engine = await db.init_db_engine()

    assert engine is fake_engine
    assert db.get_db_engine() is fake_engine
    assert created == {"engine": 1, "maker": 1}


@pytest.mark.asyncio
async def test_init_db_engine_logs_and_raises_on_failure(monkeypatch) -> None:
    monkeypatch.setattr(db, "get_database_url", lambda: "postgresql+asyncpg://u:p@h:5432/db")
    monkeypatch.setattr(db, "create_async_engine", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    db._engine = None
    db._async_session_maker = None

    with pytest.raises(RuntimeError, match="boom"):
        await db.init_db_engine()


@pytest.mark.asyncio
async def test_close_db_engine_disposes_and_resets() -> None:
    fake_engine = _FakeEngine()
    db._engine = fake_engine
    db._async_session_maker = object()

    await db.close_db_engine()

    assert fake_engine.disposed is True
    assert db._engine is None
    assert db._async_session_maker is None


@pytest.mark.asyncio
async def test_close_db_engine_is_noop_when_not_initialized() -> None:
    db._engine = None
    db._async_session_maker = None

    await db.close_db_engine()

    assert db._engine is None
    assert db._async_session_maker is None


@pytest.mark.asyncio
async def test_get_db_session_requires_initialized_engine() -> None:
    db._async_session_maker = None
    with pytest.raises(RuntimeError, match="not initialized"):
        async with db.get_db_session():
            pass


@pytest.mark.asyncio
async def test_get_db_session_yields_and_closes_session() -> None:
    session = _FakeAsyncSession()

    @asynccontextmanager
    async def fake_maker():
        yield session

    db._async_session_maker = fake_maker

    async with db.get_db_session() as yielded:
        assert yielded is session

    assert session.closed is True


@pytest.mark.asyncio
async def test_test_db_connection_success_and_failure(monkeypatch) -> None:
    session = _FakeAsyncSession()

    @asynccontextmanager
    async def fake_good_session():
        yield session

    @asynccontextmanager
    async def fake_bad_session():
        raise RuntimeError("failed")
        yield

    monkeypatch.setattr(db, "get_db_session", fake_good_session)
    assert await db.test_db_connection() is True
    assert session.executed == ["SELECT 1"]

    monkeypatch.setattr(db, "get_db_session", fake_bad_session)
    assert await db.test_db_connection() is False


@pytest.mark.asyncio
async def test_get_db_stats_and_create_tables_paths(monkeypatch) -> None:
    db._engine = None
    assert await db.get_db_stats() == {"status": "not_initialized", "pool_size": 0}

    fake_engine = _FakeEngine()
    db._engine = fake_engine

    stats = await db.get_db_stats()
    assert stats["status"] == "active"
    assert stats["pool_size"] == 5
    assert stats["pool_checked_out"] == 2

    class _Meta:
        @staticmethod
        def create_all(_conn):
            return None

    class _Base:
        metadata = _Meta()

    monkeypatch.setattr("src.models.Base", _Base)
    await db.create_tables()


@pytest.mark.asyncio
async def test_create_tables_returns_early_when_engine_missing() -> None:
    db._engine = None

    await db.create_tables()


@pytest.mark.asyncio
async def test_create_tables_swallows_engine_errors() -> None:
    class _BrokenEngine:
        @asynccontextmanager
        async def begin(self):
            class _Conn:
                async def run_sync(self, fn):
                    _ = fn
                    raise RuntimeError("create_all failed")

            yield _Conn()

    db._engine = _BrokenEngine()

    await db.create_tables()


@pytest.mark.asyncio
async def test_database_lifespan_runs_startup_and_shutdown(monkeypatch) -> None:
    events = []

    async def fake_init_db_engine():
        events.append("init")

    async def fake_create_tables():
        events.append("create")

    async def fake_close_db_engine():
        events.append("close")

    monkeypatch.setattr(db, "init_db_engine", fake_init_db_engine)
    monkeypatch.setattr(db, "create_tables", fake_create_tables)
    monkeypatch.setattr(db, "close_db_engine", fake_close_db_engine)

    async with db.database_lifespan(app=object()):
        events.append("yield")

    assert events == ["init", "create", "yield", "close"]
