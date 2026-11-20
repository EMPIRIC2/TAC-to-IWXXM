"""Tests for scripts/docs/strip_doctest_smokes.py (TC-EVDOC-002 / TC-EVDOC-004)."""

from __future__ import annotations

from pathlib import Path

from scripts.docs.strip_doctest_smokes import (
    main,
    strip_smoke_examples,
)

ROOT = Path(__file__).resolve().parents[2]


def test_strip_smoke_success_removes_placeholder_block() -> None:
    """Success: smoke Examples block removed; prose kept."""
    src = (
        "def f() -> int:\n"
        '    """Return one.\n\n'
        "    Returns\n"
        "    -------\n"
        "    int\n"
        "        One.\n\n"
        "    Examples\n"
        "    --------\n"
        "    >>> 1 + 1  # docstring smoke (f)\n"
        "    2\n"
        '    """\n'
        "    return 1\n"
    )
    out = strip_smoke_examples(src)
    assert ">>> 1 + 1" not in out
    assert "Examples" not in out
    assert "Return one." in out
    assert '"""' in out
    assert "catalog." not in out or "catalog.    " not in out


def test_strip_preserves_real_examples() -> None:
    """Validation success: real Examples stay intact."""
    src = (
        "def greet(name: str) -> str:\n"
        '    """Greet.\n\n'
        "    Parameters\n"
        "    ----------\n"
        "    name : str\n"
        "        Name.\n\n"
        "    Returns\n"
        "    -------\n"
        "    str\n"
        "        Greeting.\n\n"
        "    Examples\n"
        "    --------\n"
        '    >>> greet("Ada")\n'
        "    'Hello, Ada'\n"
        '    """\n'
        '    return f"Hello, {name}"\n'
    )
    assert strip_smoke_examples(src) == src


def test_strip_idempotent_mutation() -> None:
    """Mutation: second strip is a no-op (update then delete-noop)."""
    src = (
        "def f() -> None:\n"
        '    """Doc.\n\n'
        "    Examples\n"
        "    --------\n"
        "    >>> 1 + 1\n"
        "    2\n"
        '    """\n'
        "    return None\n"
    )
    once = strip_smoke_examples(src)
    twice = strip_smoke_examples(once)
    assert once == twice
    assert ">>> 1 + 1" not in once


def test_strip_check_mode_failure_when_smoke_present(tmp_path: Path) -> None:
    """Failure / validation fail: --check exits 1 when stubs remain."""
    sample = tmp_path / "smoke.py"
    sample.write_text(
        "def f() -> int:\n"
        '    """X.\n\n'
        "    Examples\n"
        "    --------\n"
        "    >>> 1 + 1  # docstring smoke (f)\n"
        "    2\n"
        '    """\n'
        "    return 1\n",
        encoding="utf-8",
    )
    assert main([str(tmp_path), "--check"]) == 1


def test_strip_check_mode_success_on_clean(tmp_path: Path) -> None:
    """Validation success: --check exits 0 on clean tree."""
    sample = tmp_path / "clean.py"
    sample.write_text(
        "def f() -> int:\n"
        '    """Return one.\n\n'
        "    Returns\n"
        "    -------\n"
        "    int\n"
        "        One.\n"
        '    """\n'
        "    return 1\n",
        encoding="utf-8",
    )
    assert main([str(tmp_path), "--check"]) == 0


def test_check_docs_rejects_smoke_stub(tmp_path: Path) -> None:
    """check_docs_py validation failure for placeholder smoke."""
    from scripts.docs.check_docs_py import check_file

    sample = tmp_path / "smoke.py"
    sample.write_text(
        '"""Mod."""\n\n'
        "def f() -> int:\n"
        '    """Return one.\n\n'
        "    Returns\n"
        "    -------\n"
        "    int\n"
        "        One.\n\n"
        "    Examples\n"
        "    --------\n"
        "    >>> 1 + 1  # docstring smoke (f)\n"
        "    2\n"
        '    """\n'
        "    return 1\n",
        encoding="utf-8",
    )
    joined = "\n".join(check_file(sample))
    assert "placeholder doctest smoke" in joined


def test_check_docs_accepts_public_fn_without_examples(tmp_path: Path) -> None:
    """check_docs_py success when Examples omitted."""
    from scripts.docs.check_docs_py import check_file

    sample = tmp_path / "ok.py"
    sample.write_text(
        '"""Mod."""\n\n'
        "def f() -> int:\n"
        '    """Return one.\n\n'
        "    Returns\n"
        "    -------\n"
        "    int\n"
        "        One.\n"
        '    """\n'
        "    return 1\n",
        encoding="utf-8",
    )
    assert check_file(sample) == []


def test_backfill_no_longer_injects_smoke() -> None:
    """Mutation create: backfill public docs without Examples smoke."""
    import ast

    from scripts.docs import backfill_py_docs as bf

    src = "def brand_new(x: int) -> int:\n    return x\n"
    updated = bf.backfill_source(src, Path("x.py"))
    assert updated is not None
    assert ">>> 1 + 1" not in updated
    assert "docstring smoke" not in updated
    assert bf.ensure_examples_in_existing(updated) == updated
    tree = ast.parse(updated)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
    assert ast.get_docstring(fn)


def test_strip_write_mode_mutates_file(tmp_path: Path) -> None:
    """Mutation update: default mode writes stripped content to disk."""
    sample = tmp_path / "smoke.py"
    sample.write_text(
        "def f() -> int:\n"
        '    """X.\n\n'
        "    Examples\n"
        "    --------\n"
        "    >>> 1 + 1  # docstring smoke (f)\n"
        "    2\n"
        '    """\n'
        "    return 1\n",
        encoding="utf-8",
    )
    assert main([str(tmp_path)]) == 0
    out = sample.read_text(encoding="utf-8")
    assert ">>> 1 + 1" not in out
    assert "Examples" not in out


def test_strip_remaining_when_strip_is_noop(tmp_path: Path, monkeypatch) -> None:
    """Failure: residual smoke after a no-op strip increments remaining."""
    import scripts.docs.strip_doctest_smokes as mod

    monkeypatch.setattr(mod, "strip_smoke_examples", lambda src: src)
    sample = tmp_path / "smoke.py"
    sample.write_text(
        "def f() -> int:\n"
        '    """X.\n\n'
        "    Examples\n"
        "    --------\n"
        "    >>> 1 + 1\n"
        "    2\n"
        '    """\n'
        "    return 1\n",
        encoding="utf-8",
    )
    # --check: changed_would + remaining both non-zero → exit 1
    assert main([str(tmp_path), "--check"]) == 1


def test_private_fn_rejects_smoke_stub() -> None:
    """Private helpers also reject placeholder doctest smoke."""
    from scripts.docs.check_docs_py import _doc_ok_private_fn

    issues = _doc_ok_private_fn(
        "helper\n\nExamples\n--------\n>>> 1 + 1\n2\n",
        has_args=False,
        has_return=False,
    )
    assert any("placeholder doctest smoke" in i for i in issues)
