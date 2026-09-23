"""Fail a unit test that opens a socket to the OurAirports host."""

from __future__ import annotations

import socket
from collections.abc import Callable
from typing import cast

_BLOCKED = frozenset({"ourairports.com", "www.ourairports.com", "davidmegginson.github.io"})
_original_create_connection: Callable[..., object] = socket.create_connection


def _guarded_create_connection(address: object, *args: object, **kwargs: object) -> object:
    """
    Reject sockets to the OurAirports host.

    Parameters
    ----------
    address :
        Socket address passed to ``create_connection``.
    args :
        Remaining positional arguments.
    kwargs :
        Keyword arguments.

    Returns
    -------
    object
        The original connection result for any other host.
    """
    host = ""
    if isinstance(address, tuple) and address:
        host = str(cast(object, address[0]))
    if host in _BLOCKED:
        message = f"unit test called {host}"
        raise RuntimeError(message)
    return _original_create_connection(address, *args, **kwargs)


def pytest_configure(config: object) -> None:
    """
    Install the socket guard for the test session.

    Parameters
    ----------
    config :
        Pytest config object. Unused.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (pytest_configure)
    2
    """
    del config
    socket.create_connection = _guarded_create_connection  # type: ignore[method-assign]
