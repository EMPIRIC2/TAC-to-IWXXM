"""BUG-2026-06-25 — Supabase Sync CI: server edge function missing admin.tsx.

CI ``supabase functions deploy`` failed bundling ``server`` because
``index.ts`` imports ``./admin.tsx`` which was absent (present only under
``make-server-2e3cda33/`` since monorepo move T6.2).
"""

from __future__ import annotations

import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FUNCTIONS_ROOT = REPO_ROOT / "apps" / "frontend" / "supabase" / "functions"
RELATIVE_IMPORT = re.compile(r"""from\s+['"]\./([^'"]+)['"]""")

SERVER_ADMIN = FUNCTIONS_ROOT / "server" / "admin.tsx"


def _relative_import_targets(source_dir: pathlib.Path) -> list[tuple[str, pathlib.Path]]:
    missing: list[tuple[str, pathlib.Path]] = []
    for source in sorted(source_dir.glob("*.ts*")):
        text = source.read_text(encoding="utf-8")
        for match in RELATIVE_IMPORT.finditer(text):
            rel = match.group(1)
            target = source_dir / rel
            if not target.is_file():
                missing.append((f"{source_dir.name}/{source.name} -> ./{rel}", target))
    return missing


def test_server_admin_module_exists() -> None:
    """server/index.ts imports ./admin.tsx — file must exist for CI bundle."""
    assert SERVER_ADMIN.is_file(), f"Missing edge function module: {SERVER_ADMIN}"


def test_edge_function_relative_imports_resolve() -> None:
    """Every ./ import in each function directory must point at an existing file."""
    assert FUNCTIONS_ROOT.is_dir(), f"Expected functions root: {FUNCTIONS_ROOT}"
    all_missing: list[tuple[str, pathlib.Path]] = []
    for function_dir in sorted(p for p in FUNCTIONS_ROOT.iterdir() if p.is_dir()):
        all_missing.extend(_relative_import_targets(function_dir))
    assert not all_missing, "Unresolved edge function imports:\n" + "\n".join(
        f"  {ref} (expected {path})" for ref, path in all_missing
    )
