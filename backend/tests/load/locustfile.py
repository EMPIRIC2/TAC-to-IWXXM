"""Locust entrypoint for METAR-to-IWXXM backend load testing."""

from __future__ import annotations

from locust import events

from tests.load.config import load_profile
from tests.load.metrics import on_locust_init, on_locust_request  # noqa: F401


@events.test_start.add_listener
def announce_profile(environment, **kwargs):
    """Print selected profile details at test start."""
    del environment, kwargs
    profile = load_profile()
    print(
        "[locust] profile="
        f"{profile.name} host={profile.host} auth_mode={profile.auth_mode} "
        f"evaluation_enabled={profile.evaluation_enabled}"
    )
