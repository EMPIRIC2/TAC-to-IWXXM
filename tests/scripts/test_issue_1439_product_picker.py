"""#1439 — a missing product picker must fail the spec.

[Corpus: tests] [Corpus: product]

``make test-coverage-scripts`` collects this file on every pull request.
The picker spec is also on the E2E smoke list. E2E Full stays limited to promote.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "apps" / "e2e" / "f6e-product-profile-pickers.e2e.spec.ts"


def picker_absence_still_passes(helper: str) -> bool:
    """True when the helper can skip or swallow a missing picker."""
    return "test.skip" in helper or "isVisible()" in helper or ".catch(" in helper


def test_skip_or_catch_lets_a_missing_picker_pass() -> None:
    assert picker_absence_still_passes("test.skip(true, 'not deployed');\n")
    assert picker_absence_still_passes(
        "await product.isVisible().catch(() => false);\n"
    )
    assert not picker_absence_still_passes(
        "await expect(page.locator('#param-product')).toBeVisible();\n"
    )


def test_product_picker_spec_fails_when_the_picker_is_absent() -> None:
    spec = SPEC.read_text(encoding="utf-8")
    helper = spec.split("function requireF6ePickers", 1)[1].split("test.describe", 1)[0]
    assert not picker_absence_still_passes(helper)
    assert "#param-product" in helper
    assert "toBeVisible" in helper
    assert "if (!(await requireF6ePickers" not in spec
    smoke = (ROOT / "Makefile").read_text(encoding="utf-8")
    recipe = smoke.split("test-e2e-playwright-smoke:", 1)[1].split(
        "\ntest-e2e-t2-product:", 1
    )[0]
    assert "f6e-product-profile-pickers.e2e.spec.ts" in recipe
