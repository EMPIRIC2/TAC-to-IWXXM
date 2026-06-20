"""Integration test for frontend environment variable configuration.

Validates that the frontend has the correct VITE_AUTH_SERVICE_URL environment
variable configured, preventing the "Missing VITE_AUTH_SERVICE_URL" error that
causes the app to fail at startup.
"""

from pathlib import Path

import pytest


class TestFrontendEnvConfiguration:
    """Test frontend environment variable setup."""

    def test_frontend_env_has_vite_auth_service_url(self):
        """Frontend .env should have VITE_AUTH_SERVICE_URL, not VITE_AUTH_URL."""
        frontend_env_path = Path(__file__).parent.parent / "frontend" / ".env"

        assert frontend_env_path.exists(), (
            f"Frontend .env file not found at {frontend_env_path}"
        )

        with open(frontend_env_path) as f:
            env_content = f.read()

        # Should have VITE_AUTH_SERVICE_URL
        assert "VITE_AUTH_SERVICE_URL=" in env_content, (
            "Frontend .env missing VITE_AUTH_SERVICE_URL. "
            "Please add: VITE_AUTH_SERVICE_URL=http://localhost:8002"
        )

        # Should NOT have the old VITE_AUTH_URL (to prevent confusion)
        assert "VITE_AUTH_URL=" not in env_content, (
            "Frontend .env uses old VITE_AUTH_URL instead of VITE_AUTH_SERVICE_URL. "
            "Update .env to use VITE_AUTH_SERVICE_URL=http://localhost:8002"
        )

    def test_root_env_has_vite_auth_service_url(self):
        """Root .env should also have VITE_AUTH_SERVICE_URL for consistency."""
        root_env_path = Path(__file__).parent.parent / ".env"

        assert root_env_path.exists(), f"Root .env file not found at {root_env_path}"

        with open(root_env_path) as f:
            env_content = f.read()

        # Should have VITE_AUTH_SERVICE_URL
        assert "VITE_AUTH_SERVICE_URL=" in env_content, (
            "Root .env missing VITE_AUTH_SERVICE_URL. "
            "Please add: VITE_AUTH_SERVICE_URL=http://localhost:8002"
        )

        # Extract the value
        for line in env_content.split("\n"):
            if line.startswith("VITE_AUTH_SERVICE_URL="):
                value = line.split("=", 1)[1].strip()
                assert value == "http://localhost:8002", (
                    f"VITE_AUTH_SERVICE_URL should be http://localhost:8002, got {value}"
                )
                break

    def test_frontend_env_example_has_correct_variable_name(self):
        """Frontend .env.example should document VITE_AUTH_SERVICE_URL."""
        frontend_env_example = (
            Path(__file__).parent.parent / "frontend" / ".env.example"
        )

        if frontend_env_example.exists():
            with open(frontend_env_example) as f:
                content = f.read()

            assert "VITE_AUTH_SERVICE_URL=" in content, (
                "Frontend .env.example should include VITE_AUTH_SERVICE_URL"
            )

    def test_all_required_frontend_env_vars_exist(self):
        """Frontend .env should have all required VITE_* variables."""
        frontend_env_path = Path(__file__).parent.parent / "frontend" / ".env"

        assert frontend_env_path.exists(), (
            f"Frontend .env file not found at {frontend_env_path}"
        )

        with open(frontend_env_path) as f:
            env_content = f.read()

        required_vars = [
            "VITE_AUTH_SERVICE_URL",
            "VITE_APP_URL",
            "VITE_BACKEND_URL",
        ]

        for var in required_vars:
            assert f"{var}=" in env_content, (
                f"Frontend .env missing required variable {var}"
            )


class TestFrontendAuthServiceConnectivity:
    """Test that frontend can reach auth service."""

    def test_auth_service_port_configured(self):
        """Auth service should run on port 8002 as configured."""
        frontend_env_path = Path(__file__).parent.parent / "frontend" / ".env"

        with open(frontend_env_path) as f:
            env_content = f.read()

        for line in env_content.split("\n"):
            if line.startswith("VITE_AUTH_SERVICE_URL="):
                value = line.split("=", 1)[1].strip()
                # Port should be 8002 for consistency across services
                assert "8002" in value, (
                    f"Auth service should run on port 8002, configured as {value}"
                )
                break

    @pytest.mark.integration
    def test_auth_service_reachable_during_startup(self):
        """Auth service health endpoint should be reachable."""
        # This test validates that the auth service can be reached
        # It will be skipped if the auth service is not running
        try:
            import httpx

            # Try to reach the auth service
            try:
                response = httpx.get("http://localhost:8002/health", timeout=5)
                # Any response is acceptable (200, 404, etc.)
                # We just want to ensure it's reachable and not a connection error
                assert response.status_code < 500, (
                    f"Auth service returned error: {response.status_code}"
                )
            except (httpx.ConnectError, httpx.ReadTimeout):
                pytest.skip(
                    "Auth service not running on http://localhost:8002. "
                    "Start it with: cd auth && python -m uvicorn src.__main__:app --reload --port 8002"
                )
        except ImportError:
            pytest.skip("httpx not installed, skipping connectivity test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
