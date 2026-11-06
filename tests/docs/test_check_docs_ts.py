"""TC-EVDOC-009: TS checker covers class methods and interface method signatures."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "docs" / "check_docs_ts.mjs"


def test_analyze_flags_undocumented_class_method(tmp_path: Path) -> None:
    """Class methods without TSDoc are reported."""
    sample = tmp_path / "sample.ts"
    sample.write_text(
        """
export class Foo {
  /**
   * Documented.
   */
  ok(): void {}

  missing(): void {}
}
""",
        encoding="utf-8",
    )
    # Run analyze via node -e importing the module
    script = f"""
import {{ analyze }} from 'file://{CHECKER.as_posix()}';
import fs from 'node:fs';
const text = fs.readFileSync({sample.as_posix()!r}, 'utf8');
const {{ missingDoc }} = analyze(text);
const names = missingDoc.map((h) => h.name);
if (!names.includes('missing')) {{
  console.error('expected missing method', names);
  process.exit(1);
}}
if (names.includes('ok')) {{
  console.error('ok should be documented', names);
  process.exit(1);
}}
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_package_json_lists_eslint_plugin_jsdoc() -> None:
    """Workspace package.json declares eslint-plugin-jsdoc."""
    text = (ROOT / "package.json").read_text(encoding="utf-8")
    assert "eslint-plugin-jsdoc" in text
