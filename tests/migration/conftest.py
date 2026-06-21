"""Migration test collection hooks."""

from __future__ import annotations


def pytest_collection_modifyitems(items: list) -> None:
    """Run heavy TC-M001 ``make test-unit`` subprocess last to avoid resource contention."""

    def sort_key(item):
        if item.nodeid.endswith("test_make_test_unit_succeeds"):
            return (1, item.nodeid)
        return (0, item.nodeid)

    items.sort(key=sort_key)
