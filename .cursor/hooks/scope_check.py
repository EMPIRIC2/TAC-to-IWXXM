#!/usr/bin/env python3
"""Deprecated shim — hooks.json uses .cursor/hooks/pack/scope_check.py (EV-027)."""

from __future__ import annotations

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "pack" / "scope_check.py"))
