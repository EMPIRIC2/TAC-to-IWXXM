"""Import script package inits so empty modules stay at 100% under --cov=scripts."""

from __future__ import annotations


def test_import_script_package_inits() -> None:
    import scripts.bench
    import scripts.ci
    import scripts.codegen
    import scripts.deploy
    import scripts.iwxxm
    import scripts.openapi
    import scripts.ops
    import scripts.utilities
    import scripts.vendor

    import scripts

    assert scripts.__file__
    assert scripts.ci.__file__
    assert scripts.deploy.__file__
