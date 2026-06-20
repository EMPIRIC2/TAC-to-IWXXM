"""Validation configuration settings.

This module provides centralized configuration for all validation layers
including XSD, Schematron, and WMO Code List validation.
"""

from typing import Optional

from pydantic_settings import BaseSettings


class ValidationSettings(BaseSettings):
    """Validation configuration with environment variable support.

    All settings can be overridden via environment variables or .env file.
    """

    # WMO Code List Validation
    wmo_online_validation: bool = True  # DEFAULT ON - validate against live registry
    wmo_validation_timeout: int = 5  # Timeout for online validation (seconds)
    wmo_registry_cache_ttl: int = 3600  # Cache TTL for online validation (1 hour)
    wmo_registry_url: str = "https://codes.wmo.int"

    # Schematron Validation
    schematron_use_docker: bool = True  # Prefer Docker/Saxon for full XSLT2 support
    schematron_timeout: int = 30  # Timeout for Schematron validation (seconds)

    # XSD Validation
    xsd_cache_enabled: bool = True  # Cache compiled XSD schemas

    # Live API Testing
    enable_live_api_tests: bool = True  # Enable tests against live APIs

    class Config:
        """Pydantic configuration."""
        env_prefix = ""  # No prefix, use exact env var names
        case_sensitive = False  # Case-insensitive env var matching
        env_file = ".env"  # Load from .env file if present
        env_file_encoding = "utf-8"


# Global singleton instance
_settings_instance: Optional[ValidationSettings] = None


def get_validation_settings() -> ValidationSettings:
    """Get singleton instance of validation settings.

    Returns:
        ValidationSettings instance with current configuration
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = ValidationSettings()
    return _settings_instance


def reset_validation_settings():
    """Reset settings instance (useful for testing)."""
    global _settings_instance
    _settings_instance = None


__all__ = [
    "ValidationSettings",
    "get_validation_settings",
    "reset_validation_settings",
]
