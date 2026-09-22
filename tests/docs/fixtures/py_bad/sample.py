"""Module with intentional ADR-048 gaps."""


def bare(name: str) -> str:
    return f"x{name}"


def _no_doc():
    return 1
