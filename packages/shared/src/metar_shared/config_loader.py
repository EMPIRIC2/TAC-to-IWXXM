"""Load committed non-secret configuration from ``config/{env}.json``."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[4]


def get_config_env() -> str:
    """Return active config profile (``local`` or ``prod``)."""
    return os.getenv("METAR_CONFIG_ENV", "local").strip() or "local"


def config_path(env: str | None = None) -> Path:
    """Path to ``config/{env}.json`` under the repository root."""
    profile = (env or get_config_env()).strip() or "local"
    return _REPO_ROOT / "config" / f"{profile}.json"


def load_config(env: str | None = None) -> dict[str, Any]:
    """
    Load and parse environment configuration JSON.

    Parameters
    ----------
    env
        Profile name; defaults to ``METAR_CONFIG_ENV`` or ``local``.

    Returns
    -------
    dict[str, Any]
        Parsed configuration object.

    Raises
    ------
    FileNotFoundError
        When the profile file is missing.
    json.JSONDecodeError
        When the file is not valid JSON.
    """
    path = config_path(env)
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_supabase_url_from_config(env: str | None = None) -> str:
    """Return ``supabase.url`` from config, or empty string when unset."""
    try:
        cfg = load_config(env)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return ""
    supabase = cfg.get("supabase")
    if not isinstance(supabase, dict):
        return ""
    url = supabase.get("url")
    return str(url).strip() if url else ""
