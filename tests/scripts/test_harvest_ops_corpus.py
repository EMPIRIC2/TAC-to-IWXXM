"""Unit + regression coverage for scripts/iwxxm/harvest_ops_corpus.py (#1036).

Matrix: success / failure / validation x dry-run vs write / unsupported profile.
[Corpus: product §F36] [Corpus: tests]
"""

from __future__ import annotations

import importlib.util
import runpy
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import scripts.iwxxm.harvest_ops_corpus as mod

ROOT = Path(__file__).resolve().parents[2]


def _fake_ca_module(*, fixtures: Path) -> types.ModuleType:
    """Minimal stand-in for harvest_ca_eccc_ops used by the dispatcher."""
    module = types.ModuleType("harvest_ca_eccc_ops")
    module.DEFAULT_PIN_DATE = "2026-08-24"
    module.DEFAULT_BASE = "https://dd.weather.gc.ca"
    module.DEFAULT_RATE_LIMIT = 1.0
    module.ops_fixture_root = lambda _repo, profile="CA_ECCC": fixtures
    module.harvest = MagicMock(
        return_value={
            "cases": [{"id": "x", "product": "METAR"}],
            "manifest_sha256": "abcdef0123456789",
        }
    )
    return module


@pytest.mark.parametrize(
    ("argv", "expect_code", "mode"),
    [
        (["--profile", "CA_ECCC", "--product", "ALL", "--dry-run"], 0, "success"),
        (["--profile", "ca_eccc", "--product", "TAF", "--skip-network"], 0, "success"),
        (["--profile", "AU_BOM", "--dry-run"], 2, "failure"),
        (["--profile", "  ", "--dry-run"], 2, "validation"),
        (
            ["--profile", "CA_ECCC", "--product", "NOTAPRODUCT", "--dry-run"],
            0,
            "validation",
        ),
    ],
    ids=[
        "create-plan-all",
        "update-skip-network-taf",
        "unsupported-profile",
        "blank-profile",
        "unknown-product-passthrough",
    ],
)
def test_main_profile_product_modes(
    argv: list[str],
    expect_code: int,
    mode: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Success / failure / validation permutations for --profile and --product."""
    fixtures = tmp_path / "CA_ECCC"
    fixtures.mkdir()
    fake = _fake_ca_module(fixtures=fixtures)
    monkeypatch.setattr(mod, "_load_ca_harvest", lambda: fake)
    code = mod.main(argv)
    assert code == expect_code
    out = capsys.readouterr()
    if expect_code == 0:
        assert "cases=1" in out.out
        assert "checksum=abcdef012345" in out.out
        fake.harvest.assert_called_once()
        kwargs = fake.harvest.call_args.kwargs
        assert kwargs["dry_run"] is ("--dry-run" in argv)
        assert kwargs["skip_network"] is ("--skip-network" in argv)
        product = "ALL"
        if "--product" in argv:
            product = argv[argv.index("--product") + 1]
        assert kwargs["product_filter"] == product
    else:
        assert "unsupported profile" in out.err.lower()
        fake.harvest.assert_not_called()
    assert mode in {"success", "failure", "validation"}


@pytest.mark.parametrize(
    ("dry_run", "expect_phrase"),
    [(True, "would write"), (False, "wrote")],
    ids=["create-plan", "create-write"],
)
def test_main_mutation_dry_run_vs_write(
    dry_run: bool,
    expect_phrase: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Mutation modes: dry-run plans vs write path wording."""
    fixtures = tmp_path / "CA_ECCC"
    fixtures.mkdir()
    fake = _fake_ca_module(fixtures=fixtures)
    monkeypatch.setattr(mod, "_load_ca_harvest", lambda: fake)
    argv = ["--profile", "CA_ECCC", "--product", "METAR"]
    if dry_run:
        argv.append("--dry-run")
    assert mod.main(argv) == 0
    assert expect_phrase in capsys.readouterr().out


def test_main_custom_fixtures_root_and_rate_limit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Validation success: custom fixtures root + rate limit + pin date + base."""
    fixtures = tmp_path / "custom"
    fixtures.mkdir()
    fake = _fake_ca_module(fixtures=fixtures)
    monkeypatch.setattr(mod, "_load_ca_harvest", lambda: fake)
    assert (
        mod.main(
            [
                "--profile",
                "CA_ECCC",
                "--fixtures-root",
                str(fixtures),
                "--pin-date",
                "2026-01-01",
                "--datamart-base",
                "https://example.test",
                "--rate-limit",
                "0.0",
                "--dry-run",
            ]
        )
        == 0
    )
    kwargs = fake.harvest.call_args.kwargs
    assert kwargs["fixtures_root"] == fixtures
    assert kwargs["pin_date"] == "2026-01-01"
    assert kwargs["datamart_base"] == "https://example.test"
    assert kwargs["rate_limit"] == 0.0


def test_load_ca_harvest_success() -> None:
    """Success path: load real harvest_ca_eccc_ops module by path."""
    loaded = mod._load_ca_harvest()
    assert hasattr(loaded, "harvest")
    assert hasattr(loaded, "ops_fixture_root")


@pytest.mark.parametrize(
    "spec",
    [None, types.SimpleNamespace(loader=None)],
    ids=["missing-spec", "missing-loader"],
)
def test_load_ca_harvest_failure(
    monkeypatch: pytest.MonkeyPatch,
    spec: object,
) -> None:
    """Failure mode: importlib returns an unloadable spec or loader."""
    monkeypatch.setattr(
        importlib.util,
        "spec_from_file_location",
        lambda *_a, **_k: spec,
    )
    with pytest.raises(RuntimeError, match="cannot load harvest module"):
        mod._load_ca_harvest()


def test_main_relative_path_outside_repo(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Success when fixtures_root is outside the repo (relative_to ValueError)."""
    outside = tmp_path / "outside"
    outside.mkdir()
    fake = _fake_ca_module(fixtures=outside)
    monkeypatch.setattr(mod, "_load_ca_harvest", lambda: fake)
    monkeypatch.setattr(mod, "_REPO", ROOT)
    assert mod.main(["--profile", "CA_ECCC", "--fixtures-root", str(outside)]) == 0
    assert "ops_manifest.json" in capsys.readouterr().out


def test_main_entrypoint_runpy(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """__main__ SystemExit for unsupported profile (no CA harvest load)."""
    script = ROOT / "scripts/iwxxm/harvest_ops_corpus.py"
    monkeypatch.setattr(
        sys,
        "argv",
        [str(script), "--profile", "AU_BOM", "--dry-run"],
    )
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(script), run_name="__main__")
    assert exc.value.code == 2
