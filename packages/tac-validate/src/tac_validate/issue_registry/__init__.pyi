"""Type stub for Auto-split package (exec chunks) — basedpyright."""
from typing import Any
from tac_validate.models import Issue as Issue
from pathlib import Path as Path

__all__ = ['ISSUES', 'Issue', 'IssueSpec', 'Path', '_BY_CODE', '_row', 'by_code', 'catalog_entries', 'issue_from']

ISSUES: Any
class IssueSpec:
    code: Any
    message_template: Any
    product: Any
    severity: Any
    tags: Any
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
_BY_CODE: Any
def _row(*args: Any, **kwargs: Any) -> Any: ...
def by_code(*args: Any, **kwargs: Any) -> Any: ...
def catalog_entries(*args: Any, **kwargs: Any) -> Any: ...
def issue_from(*args: Any, **kwargs: Any) -> Any: ...
