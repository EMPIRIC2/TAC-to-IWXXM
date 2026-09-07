"""Import empty scripts package __init__ modules for coverage."""

from __future__ import annotations

import importlib

import pytest

_INIT_MODULES = [
    "scripts",
    "scripts.bench",
    "scripts.ci",
    "scripts.codegen",
    "scripts.deploy",
    "scripts.iwxxm",
    "scripts.openapi",
    "scripts.ops",
    "scripts.utilities",
    "scripts.vendor",
]


@pytest.mark.parametrize("module_name", _INIT_MODULES)
@pytest.mark.unit
def test_init_import(module_name: str) -> None:
    importlib.import_module(module_name)
