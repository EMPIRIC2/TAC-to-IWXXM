"""Fail-closed pack overlay check for embedders / CLI (#1227)."""

from __future__ import annotations

import os
from pathlib import Path

from tac_decoding.packs import clear_pack_cache, load_packs

ENV_PACK_DIR = "TAC_DECODING_PACK_DIR"


def check_pack_overlay_dir(directory: Path | str, *, profile: str = "annex3") -> None:
    """
    Load decode packs with ``TAC_DECODING_PACK_DIR`` set to ``directory``.

    Parameters
    ----------
    directory :
        Directory of pack YAML overlays.
    profile :
        Conversion profile id used when loading packs.

    Raises
    ------
    Exception
        Propagates loader failures (unknown ``extends``, bad headers, etc.).
    """
    path = Path(directory).expanduser().resolve()
    if not path.is_dir():
        msg = f"pack overlay directory is not a folder: {path}"
        raise FileNotFoundError(msg)
    previous = os.environ.get(ENV_PACK_DIR)
    os.environ[ENV_PACK_DIR] = str(path)
    clear_pack_cache()
    try:
        load_packs(profile=profile)
    finally:
        if previous is None:
            os.environ.pop(ENV_PACK_DIR, None)
        else:
            os.environ[ENV_PACK_DIR] = previous
        clear_pack_cache()
