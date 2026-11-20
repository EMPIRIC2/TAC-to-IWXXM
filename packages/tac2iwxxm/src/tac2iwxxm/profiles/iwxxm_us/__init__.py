"""Package split of former ``profiles/iwxxm_us.py`` (stable import path)."""

from __future__ import annotations

from importlib import import_module as _import_module
from pathlib import Path as _Path

__all__ = [
    "emit_airmet_iwxxm_us",
    "emit_metar_speci_iwxxm_us",
    "emit_sigmet_iwxxm_us",
    "emit_taf_iwxxm_us",
]

_shared = _import_module("tac2iwxxm.profiles.iwxxm_us._shared")
globals().update({k: v for k, v in _shared.__dict__.items() if not k.startswith("__")})

_parts_dir = _Path(__file__).resolve().parent
for _part in sorted(_parts_dir.glob("_part*.py")):
    _src = _part.read_text(encoding="utf-8")
    exec(compile(_src, str(_part), "exec"), globals())

del _import_module, _Path, _shared, _parts_dir, _part, _src
