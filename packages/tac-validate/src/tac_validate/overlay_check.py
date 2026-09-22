"""Fail-closed TAC quality policy overlay check for embedders / CLI (#1227)."""

from __future__ import annotations

import os
from pathlib import Path

from tac_validate.policy import load_policy_catalog

ENV_POLICY_DIR = "TAC_VALIDATE_POLICY_DIR"


def check_tac_policy_overlay_dir(directory: Path | str, *, profile: str = "annex3") -> None:
    """
    Load TAC quality policies with ``TAC_VALIDATE_POLICY_DIR`` set to ``directory``.

    Parameters
    ----------
    directory :
        Directory of policy YAML overlays.
    profile :
        Conversion profile id used when loading the catalog.

    Raises
    ------
    tac_validate.policy.PolicyError
        When overlays fail closed (bad ``extends``, headers, etc.).
    """
    path = Path(directory).expanduser().resolve()
    if not path.is_dir():
        msg = f"TAC policy overlay directory is not a folder: {path}"
        raise FileNotFoundError(msg)
    previous = os.environ.get(ENV_POLICY_DIR)
    os.environ[ENV_POLICY_DIR] = str(path)
    try:
        load_policy_catalog(profile=profile)
    finally:
        if previous is None:
            os.environ.pop(ENV_POLICY_DIR, None)
        else:
            os.environ[ENV_POLICY_DIR] = previous
