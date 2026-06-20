"""Unit tests for validation configuration settings."""

from src.config import validation as validation_config


def test_get_validation_settings_returns_singleton(monkeypatch) -> None:
    created = []

    class FakeSettings:
        def __init__(self):
            created.append(1)

    monkeypatch.setattr(validation_config, "ValidationSettings", FakeSettings)
    validation_config.reset_validation_settings()

    first = validation_config.get_validation_settings()
    second = validation_config.get_validation_settings()

    assert first is second
    assert len(created) == 1


def test_reset_validation_settings_creates_new_instance(monkeypatch) -> None:
    created = []

    class FakeSettings:
        def __init__(self):
            created.append(1)

    monkeypatch.setattr(validation_config, "ValidationSettings", FakeSettings)
    validation_config.reset_validation_settings()
    before = validation_config.get_validation_settings()

    validation_config.reset_validation_settings()
    after = validation_config.get_validation_settings()

    assert before is not after
    assert len(created) == 2


def test_settings_read_environment_overrides(monkeypatch) -> None:
    # Bypass .env loading to avoid unrelated extra keys in test environments.
    monkeypatch.setenv("WMO_ONLINE_VALIDATION", "false")
    monkeypatch.setenv("WMO_VALIDATION_TIMEOUT", "12")
    monkeypatch.setenv("SCHEMATRON_USE_DOCKER", "false")

    settings = validation_config.ValidationSettings(_env_file=None)

    assert settings.wmo_online_validation is False
    assert settings.wmo_validation_timeout == 12
    assert settings.schematron_use_docker is False
