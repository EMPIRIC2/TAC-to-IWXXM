"""Package split of former ``slot_builders/vaa_tca.py`` (stable import path)."""

from __future__ import annotations

from importlib import import_module as _import_module
from pathlib import Path as _Path

__all__ = [
    "parse_tca",
    "parse_vaa",
]

_shared = _import_module("tac2iwxxm.slot_builders.vaa_tca._shared")
globals().update({k: v for k, v in _shared.__dict__.items() if not k.startswith("__")})

_parts_dir = _Path(__file__).resolve().parent
for _part in sorted(_parts_dir.glob("_part*.py")):
    _src = _part.read_text(encoding="utf-8")
    exec(compile(_src, str(_part), "exec"), globals())

del _import_module, _Path, _shared, _parts_dir, _part, _src
