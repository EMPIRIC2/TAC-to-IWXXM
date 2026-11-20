"""Locale error and explanation hook models.

[Corpus: product §F9]
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


class LocaleError(ValueError):
    """
    The explanation locale or template is not allowed.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


def _empty_phrases() -> dict[str, str]:
    """
    Internal helper ``_empty_phrases``.

    Returns
    -------
    dict[str, str]
        Return value.
    """
    return {}


@dataclass(frozen=True, slots=True)
class ExplanationHook:
    """
    Optional English phrase table. Missing rule ids keep the pack template.

    Attributes
    ----------
    phrases : Mapping[str, str]
        Phrases.
    """

    phrases: Mapping[str, str] = field(default_factory=_empty_phrases)

    def template_for(self, rule_id: str, pack_template: str) -> str:
        """
        Return the hook phrase for ``rule_id``, or the pack template.

        Parameters
        ----------
        rule_id : str
            Rule id.

        pack_template : str
            Pack explanation template.

        Returns
        -------
        str
            The hook phrase for ``rule_id``, or the pack template.
        """
        phrase = self.phrases.get(rule_id)
        if phrase is None:
            return pack_template
        return phrase


__all__ = ["ExplanationHook", "LocaleError"]
