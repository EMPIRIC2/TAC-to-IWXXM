"""HandleStore failure / isolation paths (EV-stage coverage expansion).

[Corpus: tests] — memory-only handle expiry, user mismatch, and purge branches.
"""

from __future__ import annotations

from dissemination.handles import HandleStore, default_handle_store


def test_handle_store_missing_token_returns_none() -> None:
    store = HandleStore(ttl_seconds=30)
    assert store.get("no-such-token", user_id="u1") is None
    assert store.pop("no-such-token", user_id="u1") is None


def test_handle_store_user_mismatch_blocks_get_and_pop() -> None:
    store = HandleStore(ttl_seconds=60)
    token = store.create(
        user_id="owner",
        sink_type="postgres",
        uri="postgresql://db.example.test/wx",
        params={"ddl": True},
        now=1_000.0,
    )
    assert store.get(token, user_id="intruder", now=1_001.0) is None
    assert store.pop(token, user_id="intruder") is None
    rec = store.get(token, user_id="owner", now=1_001.0)
    assert rec is not None
    assert rec.params == {"ddl": True}


def test_handle_store_expired_get_removes_record() -> None:
    store = HandleStore(ttl_seconds=10)
    token = store.create(
        user_id="u1",
        sink_type="sqlite",
        uri="sqlite:///:memory:",
        now=100.0,
    )
    assert store.get(token, user_id="u1", now=109.0) is not None
    assert store.get(token, user_id="u1", now=111.0) is None
    assert store.pop(token, user_id="u1") is None


def test_handle_store_create_purges_expired_siblings() -> None:
    store = HandleStore(ttl_seconds=5)
    stale = store.create(
        user_id="u1",
        sink_type="wis2",
        uri="https://broker.example.test/ds",
        now=50.0,
    )
    fresh = store.create(
        user_id="u1",
        sink_type="edis",
        uri=None,
        params=None,
        now=60.0,
    )
    assert store.get(stale, user_id="u1", now=60.0) is None
    assert store.get(fresh, user_id="u1", now=60.0) is not None


def test_default_handle_store_clear_is_isolated() -> None:
    default_handle_store.clear()
    token = default_handle_store.create(
        user_id="default-user",
        sink_type="amhs",
        uri=None,
    )
    assert default_handle_store.get(token, user_id="default-user") is not None
    default_handle_store.clear()
    assert default_handle_store.get(token, user_id="default-user") is None
