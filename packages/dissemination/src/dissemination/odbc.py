"""ODBC driver probes for SQL Server (aioodbc / E14-06).

CI and developer machines without an ODBC SQL Server driver skip live
engine tests; package code still normalizes URIs to ``mssql+aioodbc://``.
"""

from __future__ import annotations


def _is_sqlserver_odbc_driver(name: str) -> bool:
    lower = name.lower()
    if "freetds" in lower:
        return True
    if "sql server" in lower:
        return True
    # Microsoft "ODBC Driver 17/18 for SQL Server"
    return "odbc driver" in lower and "sql" in lower


def list_sqlserver_odbc_drivers() -> list[str]:
    """
    Return installed ODBC driver names usable with SQL Server.

    Returns
    -------
    list[str]
        Empty when ``pyodbc`` is missing or no SQL Server-capable driver is
        registered with the system ODBC manager.
    """
    try:
        import pyodbc
    except ImportError:
        return []
    return [d for d in pyodbc.drivers() if _is_sqlserver_odbc_driver(d)]


def odbc_sqlserver_available() -> bool:
    """Return True when at least one SQL Server ODBC driver is installed."""
    return bool(list_sqlserver_odbc_drivers())


def preferred_sqlserver_odbc_driver() -> str | None:
    """
    Prefer Microsoft ODBC Driver 18, then 17, then any SQL Server driver.

    Returns
    -------
    str | None
        Driver name for a SQLAlchemy ``driver=`` query parameter, or ``None``.
    """
    drivers = list_sqlserver_odbc_drivers()
    if not drivers:
        return None
    for needle in ("ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"):
        for d in drivers:
            if d == needle:
                return d
    return drivers[0]
