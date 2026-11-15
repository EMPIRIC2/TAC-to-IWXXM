"""IssueSpec registry row type and builder."""

# pyright: reportUnusedFunction=false, reportPrivateUsage=false
from __future__ import annotations

from tac_validate.models import IssueSpec


def _row(
    code: str,
    severity: str,
    message_template: str,
    *,
    product: str | None = None,
    tags: tuple[str, ...] = (),
) -> IssueSpec:
    """Build one frozen IssueSpec registry row."""
    return IssueSpec(
        code=code,
        severity=severity,
        message_template=message_template,
        product=product,
        tags=tags,
    )


__all__ = ["IssueSpec", "_row"]
