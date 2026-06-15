"""Auth package helper for M4 migration tests (TC-M005 prep).

Resolves ``packages/auth`` (monorepo target) with legacy ``auth/`` fallback.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGES_AUTH_ROOT = ROOT / "packages" / "auth"
LEGACY_AUTH_ROOT = ROOT / "auth"
AUTH_SRC_CANDIDATES = (
    PACKAGES_AUTH_ROOT / "src",
    PACKAGES_AUTH_ROOT,
    LEGACY_AUTH_ROOT / "src",
)


def resolve_auth_src_root() -> Path:
    """Prefer uv workspace install; fall back to packages/auth or legacy auth/src."""
    try:
        importlib.import_module("auth.security")
        import auth.security as security_mod

        security_path = Path(security_mod.__file__).resolve()
        return security_path.parent.parent
    except ImportError:
        pass

    for candidate in AUTH_SRC_CANDIDATES:
        security = candidate / "auth" / "security.py"
        if security.is_file():
            return candidate
    msg = (
        "Auth package not found under packages/auth or auth/ "
        "(required for M4 middleware tests)"
    )
    raise FileNotFoundError(msg)


def _load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_security_module():
    """Load JWT helpers without executing ``auth`` package ``__init__``."""
    auth_src = resolve_auth_src_root()
    for rel in (auth_src / "security.py", auth_src / "auth" / "security.py"):
        if rel.is_file():
            return _load_module_from_path("_auth_security", rel)
    raise FileNotFoundError("auth security module not found")


def load_api_supabase_module():
    """Load header/email helpers with stubbed Supabase proxy imports."""
    auth_src = resolve_auth_src_root()
    for rel in (auth_src / "api_supabase.py", auth_src / "auth" / "api_supabase.py"):
        if not rel.is_file():
            continue

        proxy_stub = types.ModuleType("auth.supabase_proxy")
        proxy_stub.SupabaseAuthProxy = object  # type: ignore[attr-defined]
        proxy_stub.get_supabase_proxy = lambda: None  # type: ignore[attr-defined]
        auth_pkg = types.ModuleType("auth")
        auth_pkg.supabase_proxy = proxy_stub  # type: ignore[attr-defined]

        saved: dict[str, object] = {}
        for key in ("auth", "auth.supabase_proxy"):
            if key in sys.modules:
                saved[key] = sys.modules[key]
        sys.modules["auth"] = auth_pkg
        sys.modules["auth.supabase_proxy"] = proxy_stub
        try:
            return _load_module_from_path("auth.api_supabase", rel)
        finally:
            for key in ("auth", "auth.supabase_proxy"):
                sys.modules.pop(key, None)
            sys.modules.update(saved)

    raise FileNotFoundError("auth api_supabase module not found")
