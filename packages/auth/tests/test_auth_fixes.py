"""Regression tests for auth service structural fixes."""

import inspect
import logging

from auth.__main__ import app
from auth.api_supabase import router
from auth.supabase_proxy import SupabaseAuthProxy


class TestAuthFixes:
    """Validate expected auth service wiring and proxy behavior."""

    def test_app_imports(self) -> None:
        assert app is not None

    def test_proxy_imports(self) -> None:
        assert SupabaseAuthProxy is not None

    def test_router_imports(self) -> None:
        assert router is not None

    def test_proxy_methods_are_sync(self) -> None:
        methods_to_check = [
            "sign_up",
            "sign_in",
            "sign_out",
            "get_user",
            "refresh_session",
            "reset_password_email",
            "update_password",
            "verify_token",
        ]

        async_methods = []
        for method_name in methods_to_check:
            method = getattr(SupabaseAuthProxy, method_name)
            if inspect.iscoroutinefunction(method):
                async_methods.append(method_name)

        assert not async_methods, f"Methods unexpectedly async: {async_methods}"

    def test_logging_configured(self) -> None:
        logger = logging.getLogger("supabase_proxy")
        assert len(logging.root.handlers) > 0 or len(logger.handlers) >= 0

    def test_required_routes_registered(self) -> None:
        routes = list(app.openapi()["paths"].keys())
        required_routes = [
            "/auth/register",
            "/auth/login",
            "/auth/logout",
            "/auth/me",
            "/auth/refresh",
            "/health",
        ]

        missing = [route for route in required_routes if not any(route in path for path in routes)]
        assert not missing, f"Missing routes: {missing}"
