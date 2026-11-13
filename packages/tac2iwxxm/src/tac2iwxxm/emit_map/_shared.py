"""Declarative convert emit maps (ADR-047 / #1229).

Builtin YAML under ``data/emit_maps/`` selects the python plugin for
``profile x product x iwxxm_version``. Optional ``TAC2IWXXM_EMIT_MAP_DIR`` overlays
may replace a builtin via ``extends`` or add a new map id.
"""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.

import importlib

import os

from collections.abc import Callable

from pathlib import Path

from typing import Any, cast

import yaml

from tac2iwxxm.models import EmitMap, EmitMapError

ENV_EMIT_MAP_DIR = "TAC2IWXXM_EMIT_MAP_DIR"

EmitFn = Callable[..., str]

_CATALOG_CACHE: dict[str, dict[str, EmitMap]] = {}

_PLUGIN_CACHE: dict[str, EmitFn] = {}
