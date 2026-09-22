"""Fail-closed IWXXM output policy overlay check for embedders / CLI (#1227)."""

from __future__ import annotations

import os
from pathlib import Path

from iwxxm_validate.policy import load_output_policy_catalog

ENV_POLICY_DIR = "IWXXM_VALIDATE_POLICY_DIR"


def check_iwxxm_policy_overlay_dir(directory: Path | str, *, profile: str = "annex3") -> None:
    """
    Load IWXXM output policies with ``IWXXM_VALIDATE_POLICY_DIR`` set to ``directory``.

    Parameters
    ----------
    directory :
        Directory of output-policy YAML overlays.
    profile :
        Conversion profile id used when loading the catalog.

    Raises
    ------
    iwxxm_validate.policy.PolicyError
        When overlays fail closed (bad ``extends``, headers, etc.).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (check_iwxxm_policy_overlay_dir)
    2
    """
    path = Path(directory).expanduser().resolve()
    if not path.is_dir():
        msg = f"IWXXM policy overlay directory is not a folder: {path}"
        raise FileNotFoundError(msg)
    previous = os.environ.get(ENV_POLICY_DIR)
    os.environ[ENV_POLICY_DIR] = str(path)
    try:
        load_output_policy_catalog(profile=profile)
    finally:
        if previous is None:
            os.environ.pop(ENV_POLICY_DIR, None)
        else:
            os.environ[ENV_POLICY_DIR] = previous
