"""Fail-closed profile-binding overlay check for embedders / CLI (#1227)."""

from __future__ import annotations

import os
from pathlib import Path

from tac2iwxxm.profile_resolve import ENV_PROFILE_DIR, resolve_validation_policies


def check_profile_overlay_dir(directory: Path | str, *, profile: str = "annex3") -> None:
    """
    Resolve validation policies with ``TAC2IWXXM_PROFILE_DIR`` set to ``directory``.

    Parameters
    ----------
    directory :
        Directory of profile → policy binding YAML overlays.
    profile :
        Conversion profile id to resolve (default ``annex3``).

    Raises
    ------
    tac2iwxxm.profile_resolve.ProfileResolveError
        When overlays fail closed (bad ``extends``, headers, etc.).
    """
    path = Path(directory).expanduser().resolve()
    if not path.is_dir():
        msg = f"profile overlay directory is not a folder: {path}"
        raise FileNotFoundError(msg)
    previous = os.environ.get(ENV_PROFILE_DIR)
    os.environ[ENV_PROFILE_DIR] = str(path)
    try:
        resolve_validation_policies(profile)
    finally:
        if previous is None:
            os.environ.pop(ENV_PROFILE_DIR, None)
        else:
            os.environ[ENV_PROFILE_DIR] = previous
