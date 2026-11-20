"""EV-080 M4 — 100% coverage for scripts/iwxxm/harvest_ca_eccc_ops.py."""

from __future__ import annotations

import subprocess
import sys
import urllib.error
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from scripts.iwxxm import harvest_ca_eccc_ops as mod

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def fixtures_root(tmp_path: Path) -> Path:
    root = tmp_path / "CA_ECCC"
    met_dir = root / "METAR" / "valid"
    met_dir.mkdir(parents=True)
    (met_dir / "metar_basic.tac").write_text(
        "METAR CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012=\n", encoding="utf-8"
    )
    (met_dir / "metar_auto.tac").write_text(
        "METAR CYUL 231800Z AUTO 24010KT 9999 FEW240 22/12 A3012=\n", encoding="utf-8"
    )
    (met_dir / "metar_lwis.tac").write_text("METAR CYUL 231800Z=\n", encoding="utf-8")
    (met_dir / "metar_sawr.tac").write_text("METAR CYUL 231800Z=\n", encoding="utf-8")
    (met_dir / "metar_vis_sm.tac").write_text("METAR CYUL 231800Z=\n", encoding="utf-8")
    return root


def test_fetch_url(monkeypatch: pytest.MonkeyPatch) -> None:
    resp = MagicMock()
    resp.read.return_value = b"<xml/>"
    resp.__enter__ = lambda s: s
    resp.__exit__ = lambda *a: None
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_a, **_k: resp)
    assert mod._fetch_url("https://example.test/x") == b"<xml/>"


def test_bootstrap_encoder_reference(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda tac, **_k: SimpleNamespace(ok=True, xml=f"<xml>{tac[:8]}</xml>"),
    )
    cases = mod._bootstrap_encoder_reference(
        fixtures_root, dry_run=False, product_filter="ALL"
    )
    assert len(cases) == len(mod._ENCODER_REFERENCE)
    assert (fixtures_root / "METAR/ops/metar_basic_ops.xml").is_file()

    dry = mod._bootstrap_encoder_reference(
        fixtures_root, dry_run=True, product_filter="ALL"
    )
    assert len(dry) == len(mod._ENCODER_REFERENCE)


def test_bootstrap_encoder_reference_failure(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda *_a, **_k: SimpleNamespace(ok=False, xml=None, issues=["bad"]),
    )
    with pytest.raises(RuntimeError, match="encoder reference failed"):
        mod._bootstrap_encoder_reference(
            fixtures_root, dry_run=False, product_filter="ALL"
        )


def test_harvest_network_and_manifest(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    resp = MagicMock()
    resp.read.return_value = b"<collect/>"
    resp.__enter__ = lambda s: s
    resp.__exit__ = lambda *a: None
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_a, **_k: resp)
    monkeypatch.setattr(mod.time, "sleep", lambda *_a: None)

    manifest = mod.harvest(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        datamart_base=mod.DEFAULT_BASE,
        rate_limit=0.0,
        dry_run=False,
        skip_network=False,
    )
    assert len(manifest["cases"]) == len(mod._PINNED_FETCHES) + len(
        mod._ENCODER_REFERENCE
    )
    assert (fixtures_root / "ops_manifest.json").is_file()
    sigmet = next(c for c in manifest["cases"] if c["id"] == "sigmet_czeg_15_001")
    assert sigmet["sigmet_kind"] == "weather"


def test_harvest_http_error(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _boom(*_a: object, **_k: object) -> None:
        raise urllib.error.HTTPError("url", 404, "missing", hdrs=None, fp=None)

    monkeypatch.setattr(mod, "_fetch_url", _boom)
    with pytest.raises(RuntimeError, match="fetch failed"):
        mod.harvest(
            fixtures_root=fixtures_root,
            pin_date="2026-08-24",
            datamart_base=mod.DEFAULT_BASE,
            rate_limit=0.0,
            dry_run=False,
            skip_network=False,
        )


def test_harvest_skip_network_and_dry_run(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<xml/>"),
    )
    manifest = mod.harvest(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        datamart_base="https://other.example",
        rate_limit=0.0,
        dry_run=True,
        skip_network=True,
    )
    assert manifest["datamart_base"] == "https://other.example"
    assert not (fixtures_root / "ops_manifest.json").exists()
    # skip_network still bootstraps encoder refs and keeps on-disk fixture rows
    encoder_ids = {row["id"] for row in mod._ENCODER_REFERENCE}
    case_ids = {row["id"] for row in manifest["cases"]}
    assert encoder_ids <= case_ids
    assert len(manifest["cases"]) >= len(mod._ENCODER_REFERENCE)


def test_harvest_dry_run_with_network_plan(
    fixtures_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<xml/>"),
    )
    manifest = mod.harvest(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        datamart_base="https://other.example",
        rate_limit=0.0,
        dry_run=True,
        skip_network=False,
    )
    assert len(manifest["cases"]) == len(mod._PINNED_FETCHES) + len(
        mod._ENCODER_REFERENCE
    )


def test_main_entrypoint_subprocess() -> None:

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/iwxxm/harvest_ca_eccc_ops.py"),
            "--skip-network",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0


def test_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "CA_ECCC"
    root.mkdir()
    monkeypatch.setattr(mod, "_REPO", tmp_path)
    monkeypatch.setattr(mod, "ops_fixture_root", lambda _r: root)
    monkeypatch.setattr(
        mod,
        "harvest",
        lambda **_k: {"cases": [{"id": "x"}], "manifest_sha256": "abc123def456"},
    )
    monkeypatch.setattr(sys, "argv", ["harvest_ca_eccc_ops.py"])
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "cases=1" in out
    assert "checksum=abc123def456" in out


def test_main_rejects_non_ca_profile(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Validation failure: CA-only alias rejects other profiles."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["harvest_ca_eccc_ops.py", "--profile", "AU_BOM", "--dry-run"],
    )
    assert mod.main() == 2
    assert "CA_ECCC-only" in capsys.readouterr().err


def test_harvest_skip_network_missing_fixture_fails(
    fixtures_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failure: skip-network write requires committed pinned fixtures on disk."""
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<xml/>"),
    )
    with pytest.raises(RuntimeError, match="skip-network requires committed fixture"):
        mod.harvest(
            fixtures_root=fixtures_root,
            pin_date="2026-08-24",
            datamart_base=mod.DEFAULT_BASE,
            rate_limit=0.0,
            dry_run=False,
            skip_network=True,
            product_filter="TAF",
        )


def test_harvest_product_filter_keeps_sibling_cases(
    fixtures_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Update mutation: filtered harvest keeps non-matching cases from prior manifest."""
    import json

    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<xml/>"),
    )
    (fixtures_root / "ops_manifest.json").write_text(
        json.dumps(
            {
                "vaa_harvest": "custom_vaa",
                "vaa_harvest_note": "keep note",
                "cases": [
                    {"id": "taf_old", "product": "TAF"},
                    {"id": "metar_old", "product": "METAR"},
                    {"id": "vaa_old", "product": "VAA"},
                ],
            }
        ),
        encoding="utf-8",
    )
    manifest = mod.harvest(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        datamart_base=mod.DEFAULT_BASE,
        rate_limit=0.0,
        dry_run=True,
        skip_network=True,
        product_filter="METAR",
    )
    assert manifest["vaa_harvest"] == "custom_vaa"
    assert manifest["vaa_harvest_note"] == "keep note"
    ids = {case["id"] for case in manifest["cases"]}
    assert "taf_old" in ids
    assert "vaa_old" in ids
    assert "metar_old" not in ids
    assert any(case["product"] == "METAR" for case in manifest["cases"])


def test_harvest_existing_manifest_without_vaa_keys_keeps_defaults(
    fixtures_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Validation: prior manifest without vaa_* keys keeps deferred defaults; ALL keeps VAA."""
    import json

    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<xml/>"),
    )
    (fixtures_root / "ops_manifest.json").write_text(
        json.dumps(
            {
                "cases": [
                    {"id": "vaa_old", "product": "VAA"},
                    {"id": "taf_old", "product": "TAF"},
                ]
            }
        ),
        encoding="utf-8",
    )
    manifest = mod.harvest(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        datamart_base=mod.DEFAULT_BASE,
        rate_limit=0.0,
        dry_run=True,
        skip_network=True,
        product_filter="ALL",
    )
    assert manifest["vaa_harvest"] == "deferred_no_datamart_tree"
    assert "Montreal VAAC" in manifest["vaa_harvest_note"]
    assert any(case["id"] == "vaa_old" for case in manifest["cases"])


@pytest.mark.parametrize(
    ("product_filter", "mode", "expect_metar", "expect_speci"),
    [
        ("ALL", "success", True, True),
        ("METAR", "success", True, False),
        ("SPECI", "success", False, True),
        ("NOTAPRODUCT", "failure", False, False),
        ("", "validation", True, True),
        ("  metar  ", "validation", True, False),
    ],
    ids=[
        "all",
        "metar-only",
        "speci-only",
        "unknown-product",
        "blank-filter",
        "normalized-metar",
    ],
)
def test_bootstrap_product_filter_modes(
    fixtures_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    product_filter: str,
    mode: str,
    expect_metar: bool,
    expect_speci: bool,
) -> None:
    """Success / failure / validation modes for product_filter bootstrap."""
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda tac, **_k: SimpleNamespace(ok=True, xml=f"<xml>{tac[:8]}</xml>"),
    )
    cases = mod._bootstrap_encoder_reference(
        fixtures_root, dry_run=True, product_filter=product_filter
    )
    products = {row["product"] for row in cases}
    if expect_metar:
        assert "METAR" in products
    else:
        assert "METAR" not in products
    if expect_speci:
        assert "SPECI" in products or (mode == "validation" and product_filter == "")
    else:
        assert "SPECI" not in products or (mode == "failure" and cases == [])
    if mode == "failure":
        assert cases == []
    assert mode in {"success", "failure", "validation"}


@pytest.mark.parametrize(
    ("skip_network", "dry_run", "mutation"),
    [
        (True, True, "read-plan"),
        (True, False, "create-write"),
        (False, True, "update-plan"),
    ],
    ids=["skip-dry", "skip-write", "network-dry"],
)
def test_harvest_mutation_modes(
    fixtures_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    skip_network: bool,
    dry_run: bool,
    mutation: str,
) -> None:
    """Mutation permutations for harvest create/update planning vs write."""
    import tac2iwxxm

    monkeypatch.setattr(
        tac2iwxxm,
        "convert",
        lambda *_a, **_k: SimpleNamespace(ok=True, xml="<xml/>"),
    )
    monkeypatch.setattr(mod.time, "sleep", lambda *_a: None)
    if not skip_network:
        resp = MagicMock()
        resp.read.return_value = b"<collect/>"
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda *a: None
        monkeypatch.setattr(urllib.request, "urlopen", lambda *_a, **_k: resp)

    manifest = mod.harvest(
        fixtures_root=fixtures_root,
        pin_date="2026-08-24",
        datamart_base=mod.DEFAULT_BASE,
        rate_limit=0.0,
        dry_run=dry_run,
        skip_network=skip_network,
        product_filter="METAR",
    )
    assert manifest["cases"]
    wrote = (fixtures_root / "ops_manifest.json").exists()
    assert wrote is (not dry_run)
    assert mutation in {"read-plan", "create-write", "update-plan"}
