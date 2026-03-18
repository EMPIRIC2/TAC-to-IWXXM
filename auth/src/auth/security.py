"""Compatibility wrapper for auth.security imports."""

import importlib

import security as _security

# Reload to ensure env-driven constants are refreshed when this module is reloaded in tests.
_security = importlib.reload(_security)

_public = {name: getattr(_security, name) for name in dir(_security) if not name.startswith("_")}
globals().update(_public)

__all__ = list(getattr(_security, "__all__", []))
