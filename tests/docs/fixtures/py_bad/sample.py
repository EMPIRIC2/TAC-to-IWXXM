"""Module with intentional ADR-048 gaps."""


def bare(name: str) -> str:
    return f"x{name}"


def _no_doc():
    return 1


def _private_missing_shape(name: str) -> str:
    """Private helper without Parameters/Returns."""
    return name
