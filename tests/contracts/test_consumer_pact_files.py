"""Every OpenAPI operation has a row in the local interaction contract.

The contract layer is ``scripts/ci/check_openapi_contract.py`` and
``tests/contracts/openapi-interactions.json``. This repository does not keep
Pact consumer documents. The check fails when an operation has no interaction
row.

[Corpus: tests] [Corpus: api]
"""

from __future__ import annotations

import pytest
from tests.scripts.conftest import REPO_ROOT, load_script

SPEC = REPO_ROOT / "apps" / "frontend" / "openapi" / "openapi.json"
INTERACTIONS = REPO_ROOT / "tests" / "contracts" / "openapi-interactions.json"


@pytest.mark.unit
def test_openapi_interactions_cover_every_operation() -> None:
    """Each OpenAPI operation has at least one interaction row."""
    checker = load_script(
        "ci/check_openapi_contract.py",
        "check_openapi_contract_for_operations",
    )
    report = checker.run_check(SPEC, INTERACTIONS)
    missing = report["missing"]["operations"]
    assert not missing, (
        f"{report['operations_missing']} operations have no interaction row"
    )
