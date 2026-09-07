"""Unit tests for SQL Server ODBC probes (T2.6 / E14-06)."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest

from dissemination import odbc as odbc_mod


def test_is_sqlserver_odbc_driver_names() -> None:
    assert odbc_mod._is_sqlserver_odbc_driver("ODBC Driver 18 for SQL Server")
    assert odbc_mod._is_sqlserver_odbc_driver("ODBC Driver 17 for SQL Server")
    assert odbc_mod._is_sqlserver_odbc_driver("FreeTDS")
    assert odbc_mod._is_sqlserver_odbc_driver("SQL Server")
    assert not odbc_mod._is_sqlserver_odbc_driver("PostgreSQL Unicode")
    assert not odbc_mod._is_sqlserver_odbc_driver("MySQL ODBC 8.0 Driver")


def test_list_drivers_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delitem(sys.modules, "pyodbc", raising=False)
    real_import = __import__

    def _no_pyodbc(name: str, globals=None, locals=None, fromlist=(), level=0):
        if name == "pyodbc" or name.startswith("pyodbc."):
            raise ImportError("no pyodbc")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _no_pyodbc)
    assert odbc_mod.list_sqlserver_odbc_drivers() == []
    assert odbc_mod.odbc_sqlserver_available() is False
    assert odbc_mod.preferred_sqlserver_odbc_driver() is None


def test_preferred_driver_order(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        odbc_mod,
        "list_sqlserver_odbc_drivers",
        lambda: [
            "FreeTDS",
            "ODBC Driver 17 for SQL Server",
            "ODBC Driver 18 for SQL Server",
        ],
    )
    assert odbc_mod.preferred_sqlserver_odbc_driver() == "ODBC Driver 18 for SQL Server"

    monkeypatch.setattr(
        odbc_mod,
        "list_sqlserver_odbc_drivers",
        lambda: ["FreeTDS", "ODBC Driver 17 for SQL Server"],
    )
    assert odbc_mod.preferred_sqlserver_odbc_driver() == "ODBC Driver 17 for SQL Server"

    monkeypatch.setattr(odbc_mod, "list_sqlserver_odbc_drivers", lambda: ["FreeTDS"])
    assert odbc_mod.preferred_sqlserver_odbc_driver() == "FreeTDS"
    assert odbc_mod.odbc_sqlserver_available() is True


def test_list_drivers_filters_pyodbc(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = ModuleType("pyodbc")
    fake.drivers = lambda: [  # type: ignore[attr-defined]
        "PostgreSQL Unicode",
        "ODBC Driver 18 for SQL Server",
        "MySQL ODBC 8.0 Driver",
        "FreeTDS",
    ]
    monkeypatch.setitem(sys.modules, "pyodbc", fake)
    assert odbc_mod.list_sqlserver_odbc_drivers() == [
        "ODBC Driver 18 for SQL Server",
        "FreeTDS",
    ]
