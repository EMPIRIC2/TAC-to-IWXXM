"""Package split of former ``profiles/ca_eccc.py`` (stable import path)."""

from __future__ import annotations

from importlib import import_module as _import_module
from pathlib import Path as _Path

__all__ = [
    "CA_IWXXM_CA_SUBSTITUTION_ROOTS",
    "CA_IWXXM_VERSION",
    "CA_METAR_FAMILY_TAC_LEADS",
    "CA_NS",
    "CA_OBS_AWOS",
    "CA_OBS_LWIS",
    "CA_OBS_SAWR",
    "CA_PRES_FALLING",
    "CA_PRES_RISING",
    "_nclws_extension",
    "emit_airmet_ca_eccc",
    "emit_metar_speci_ca_eccc",
    "emit_taf_ca_eccc",
]

_shared = _import_module("tac2iwxxm.profiles.ca_eccc._shared")
globals().update({k: v for k, v in _shared.__dict__.items() if not k.startswith("__")})

_parts_dir = _Path(__file__).resolve().parent
for _part in sorted(_parts_dir.glob("_part*.py")):
    _src = _part.read_text(encoding="utf-8")
    exec(compile(_src, str(_part), "exec"), globals())

del _import_module, _Path, _shared, _parts_dir, _part, _src
