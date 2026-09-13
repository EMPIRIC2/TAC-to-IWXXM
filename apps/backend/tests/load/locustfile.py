"""Locust entrypoint for METAR-to-IWXXM backend load testing."""

from __future__ import annotations

from locust import events

# Side-effect imports: register Prometheus hooks and expose HttpUser classes to Locust.
from tests.load import metrics as _load_metrics
from tests.load.config import load_profile
from tests.load.scenarios import (
    ConversionApiUser,
    EvaluationApiUser,
    PublicApiUser,
    ValidationApiUser,
)

# Keep imported symbols referenced so Ruff does not treat them as unused.
_ = (_load_metrics, ConversionApiUser, EvaluationApiUser, PublicApiUser, ValidationApiUser)


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
