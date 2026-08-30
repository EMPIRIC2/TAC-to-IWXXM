"""TC-EV088 — national profile playbook + scaffold enablement.

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: tests]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[3]
_PROFILES = _REPO / "docs" / "domain" / "profiles"
_PLAYBOOK = _PROFILES / "NATIONAL_PROFILE_PLAYBOOK.md"
_TEMPLATE = _PROFILES / "_template"
_SCAFFOLD = _REPO / "scripts" / "profiles" / "scaffold_national_profile.py"
_CATALOG = _PROFILES / "catalog.yaml"

_TEMPLATE_FILES = (
    "catalog-row.yaml",
    "semantic-profile.md",
    "tac-mining-notes.md",
    "iwxxm-mining-notes.md",
    "manifest.json.example",
)


def test_tc_ev088_001_playbook_lists_issue_types_a_through_p() -> None:
    """Playbook documents child issue types A-P."""
    assert _PLAYBOOK.is_file(), f"missing playbook: {_PLAYBOOK}"
    text = _PLAYBOOK.read_text(encoding="utf-8")
    for letter in "ABCDEFGHIJKLMNOP":
        assert f"| {letter} |" in text, f"playbook missing type {letter}"


def test_tc_ev088_002_template_stubs_present() -> None:
    """``_template/`` stubs required by #1044 exist."""
    assert _TEMPLATE.is_dir(), f"missing {_TEMPLATE}"
    for name in _TEMPLATE_FILES:
        path = _TEMPLATE / name
        assert path.is_file(), f"missing template: {path}"


def test_tc_ev088_003_catalog_yaml_parses() -> None:
    """Machine catalog remains parseable YAML with profiles list."""
    data = yaml.safe_load(_CATALOG.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert data.get("schema_version") == 1
    profiles = data.get("profiles")
    assert isinstance(profiles, list)
    assert len(profiles) >= 1
    ids = {p.get("id") for p in profiles if isinstance(p, dict)}
    assert "CA_ECCC" in ids
    assert "ICAO_2025" in ids


def test_tc_ev088_004_readme_and_adr_link_playbook() -> None:
    """Standing docs point at the playbook."""
    readme = (_PROFILES / "README.md").read_text(encoding="utf-8")
    assert "NATIONAL_PROFILE_PLAYBOOK.md" in readme
    adr = (_REPO / "docs" / "adr" / "ADR-036-semantic-vs-exchange-profiles.md").read_text(encoding="utf-8")
    assert "NATIONAL_PROFILE_PLAYBOOK.md" in adr
    assert "#1044" in adr or "1044" in adr


def test_tc_ev088_005_scaffold_dry_run() -> None:
    """Scaffold CLI dry-run exits 0 and prints checklist without writes."""
    assert _SCAFFOLD.is_file(), f"missing scaffold script: {_SCAFFOLD}"
    # Use a probe id that must not exist as a standing stub (UK_METOFFICE is real post-EV-089).
    probe_id = "ZZ_SCAFFOLD_PROBE"
    probe_stub = _PROFILES / "semantic" / f"{probe_id}.md"
    assert not probe_stub.exists(), f"probe stub must not pre-exist: {probe_stub}"
    proc = subprocess.run(
        [sys.executable, str(_SCAFFOLD), "--id", probe_id, "--dry-run"],
        cwd=_REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert probe_id in proc.stdout
    assert "Hand-edit checklist" in proc.stdout
    assert "profile_registry.py" in proc.stdout
    # dry-run must not create semantic stub
    assert not probe_stub.exists()


def test_tc_ev088_006_scaffold_rejects_bad_id() -> None:
    """Malformed profile ids fail closed."""
    proc = subprocess.run(
        [sys.executable, str(_SCAFFOLD), "--id", "bad-id"],
        cwd=_REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 2
    assert "invalid profile id" in proc.stderr.lower() or "error:" in proc.stderr.lower()
