"""Package split of former ``emit_map.py`` (stable import path)."""

from __future__ import annotations

from importlib import import_module as _import_module
from pathlib import Path as _Path

__all__ = [
    "ENV_EMIT_MAP_DIR",
    "EmitMap",
    "EmitMapError",
    "check_emit_map_overlay_dir",
    "clear_emit_map_catalog_cache",
    "emit_with_map",
    "load_emit_map_catalog",
    "resolve_emit_map",
]

_shared = _import_module("tac2iwxxm.emit_map._shared")
globals().update({k: v for k, v in _shared.__dict__.items() if not k.startswith("__")})

_parts_dir = _Path(__file__).resolve().parent
for _part in sorted(_parts_dir.glob("_part*.py")):
    _src = _part.read_text(encoding="utf-8")
    exec(compile(_src, str(_part), "exec"), globals())

del _import_module, _Path, _shared, _parts_dir, _part, _src
