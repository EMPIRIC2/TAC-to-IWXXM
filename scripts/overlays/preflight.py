#!/usr/bin/env python3
"""Fail-closed overlay preflight for decode / TAC / IWXXM / profile bindings (#1224).

Validates example (or arbitrary) overlay directories using each package's loaders.
Exit 0 when all checks pass; exit 1 on the first failure.
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from collections.abc import Callable
from contextlib import redirect_stderr
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]

_EXAMPLE_ROOTS: tuple[tuple[str, Path], ...] = (
    ("pack", _REPO / "packages" / "tac-decoding" / "examples" / "overlays"),
    ("tac-policy", _REPO / "packages" / "tac-validate" / "examples" / "overlays"),
    ("iwxxm-policy", _REPO / "packages" / "iwxxm-validate" / "examples" / "overlays"),
    ("profile-binding", _REPO / "packages" / "tac2iwxxm" / "examples" / "overlays"),
)


def _die(message: str) -> None:
    print(f"overlay-preflight: {message}", file=sys.stderr)
    raise SystemExit(1)


def _check_pack(directory: Path) -> None:
    from tac_decoding.packs import clear_pack_cache, load_packs

    os.environ["TAC_DECODING_PACK_DIR"] = str(directory)
    clear_pack_cache()
    try:
        load_packs(profile="annex3")
    except Exception as exc:
        _die(f"pack overlay failed in {directory}: {exc}")
    finally:
        os.environ.pop("TAC_DECODING_PACK_DIR", None)
        clear_pack_cache()


def _check_tac_policy(directory: Path) -> None:
    from tac_validate.policy import PolicyError, load_policy_catalog

    os.environ["TAC_VALIDATE_POLICY_DIR"] = str(directory)
    try:
        load_policy_catalog(profile="annex3")
    except PolicyError as exc:
        _die(f"TAC policy overlay failed in {directory}: {exc}")
    except Exception as exc:
        _die(f"TAC policy overlay failed in {directory}: {exc}")
    finally:
        os.environ.pop("TAC_VALIDATE_POLICY_DIR", None)


def _check_iwxxm_policy(directory: Path) -> None:
    from iwxxm_validate.policy import PolicyError, load_output_policy_catalog

    os.environ["IWXXM_VALIDATE_POLICY_DIR"] = str(directory)
    try:
        load_output_policy_catalog(profile="annex3")
    except PolicyError as exc:
        _die(f"IWXXM policy overlay failed in {directory}: {exc}")
    except Exception as exc:
        _die(f"IWXXM policy overlay failed in {directory}: {exc}")
    finally:
        os.environ.pop("IWXXM_VALIDATE_POLICY_DIR", None)


def _check_profile_binding(directory: Path) -> None:
    from tac2iwxxm.profile_resolve import (
        ProfileResolveError,
        resolve_validation_policies,
    )

    os.environ["TAC2IWXXM_PROFILE_DIR"] = str(directory)
    try:
        resolve_validation_policies("annex3")
    except ProfileResolveError as exc:
        _die(f"profile-binding overlay failed in {directory}: {exc}")
    except Exception as exc:
        _die(f"profile-binding overlay failed in {directory}: {exc}")
    finally:
        os.environ.pop("TAC2IWXXM_PROFILE_DIR", None)


_CHECKERS: dict[str, Callable[[Path], None]] = {
    "pack": _check_pack,
    "tac-policy": _check_tac_policy,
    "iwxxm-policy": _check_iwxxm_policy,
    "profile-binding": _check_profile_binding,
}


def _expect_fail(kind: str, directory: Path) -> None:
    """Require fail-closed; suppress expected stderr from _die."""
    checker = _CHECKERS[kind]
    sink = io.StringIO()
    try:
        with redirect_stderr(sink):
            checker(directory)
    except SystemExit as exc:
        if exc.code == 1:
            return
        raise
    _die(f"expected {kind} overlay in {directory} to fail, but it passed")


def _run_examples() -> None:
    for kind, root in _EXAMPLE_ROOTS:
        valid = root / "valid"
        invalid = root / "invalid-bad-extends"
        if not valid.is_dir() or not invalid.is_dir():
            _die(f"missing example dirs under {root}")
        print(f"overlay-preflight: checking {kind} valid …")
        _CHECKERS[kind](valid)
        print(f"overlay-preflight: checking {kind} invalid (expect fail) …")
        _expect_fail(kind, invalid)
    print("overlay-preflight: all example overlays OK")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all-examples",
        action="store_true",
        help="Validate package examples/overlays valid + invalid-bad-extends trees",
    )
    parser.add_argument(
        "--kind",
        choices=sorted(_CHECKERS),
        help="Overlay family when checking a single directory",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        help="Overlay directory (YAML files) for a single --kind check",
    )
    parser.add_argument(
        "--expect-fail",
        action="store_true",
        help="Require the single-directory check to fail closed",
    )
    args = parser.parse_args(argv)

    if args.all_examples:
        _run_examples()
        return 0

    if args.kind and args.dir:
        directory = args.dir.expanduser().resolve()
        if not directory.is_dir():
            _die(f"not a directory: {directory}")
        if args.expect_fail:
            _expect_fail(args.kind, directory)
            print(f"overlay-preflight: {args.kind} failed as expected")
        else:
            _CHECKERS[args.kind](directory)
            print(f"overlay-preflight: {args.kind} OK ({directory})")
        return 0

    parser.error("use --all-examples, or both --kind and --dir")
    return 2


if __name__ == "__main__":
    # Ensure workspace packages importable when run via `uv run`.
    sys.path[:0] = [
        str(_REPO / "packages" / "tac-decoding" / "src"),
        str(_REPO / "packages" / "tac-validate" / "src"),
        str(_REPO / "packages" / "iwxxm-validate" / "src"),
        str(_REPO / "packages" / "tac2iwxxm" / "src"),
    ]
    raise SystemExit(main())
