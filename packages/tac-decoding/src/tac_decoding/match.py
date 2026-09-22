"""Match a TAC report against a loaded pack.

The caller passes ``iwxxm_version`` and ``profile``. This module does not
choose a pin and does not emit XML. Legacy parsers and validation stay in
``tac2iwxxm``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tac_decoding.locale import ENGLISH, ExplanationHook, render_template, require_locale
from tac_decoding.packs import Pack, Rule

MATCH_STEP_BUDGET = 10_000
_TOKEN = re.compile(r"=|[^\s=]+")


class MatchBudgetError(ValueError):
    """
    The matcher stopped because it used its step budget.

    Attributes
    ----------
    _ : object
        See implementation.
    """


@dataclass(frozen=True, slots=True)
class MatchContext:
    """
    Caller-owned version and profile. Packs do not select these.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    iwxxm_version: str | None = None
    profile: str | None = None


@dataclass(frozen=True, slots=True)
class MatchSpan:
    """
    One matched or residual slice of the original TAC.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    start: int
    end: int
    code: str
    explanation: str
    rule_id: str


@dataclass(frozen=True, slots=True)
class MatchResult:
    """
    Spans, leftovers, and the version context the caller supplied.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    spans: tuple[MatchSpan, ...]
    residuals: tuple[MatchSpan, ...]
    steps: int
    iwxxm_version: str | None
    profile: str | None


def match_tac(
    tac: str,
    pack: Pack,
    *,
    context: MatchContext | None = None,
    max_steps: int = MATCH_STEP_BUDGET,
    locale: str = ENGLISH,
    hook: ExplanationHook | None = None,
) -> MatchResult:
    """
    Match ``tac`` with ``pack``. The same text explains the same way on every pin.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (match_tac)
    2

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    pack : object
        Argument ``pack``.
    context : object
        Argument ``context``.
    max_steps : object
        Argument ``max_steps``.
    locale : object
        Argument ``locale``.
    hook : object
        Argument ``hook``.

    Returns
    -------
    object
        Return value.
    """
    require_locale(locale)
    ctx = context or MatchContext()
    explain = _Explain(locale, hook or ExplanationHook())
    if pack.layout == "stub":
        return _stub(tac, ctx)
    if pack.layout == "token_stream":
        return _match_tokens(tac, pack, ctx, max_steps, explain)
    return _match_labels(tac, pack, ctx, max_steps, explain)


@dataclass(frozen=True, slots=True)
class _Explain:
    """Internal helper ``_Explain``."""

    locale: str
    hook: ExplanationHook

    def __call__(self, rule: Rule, groups: tuple[str, ...] = (), value: str | None = None) -> str:
        """
        Internal helper ``__call__``.

        Parameters
        ----------
        rule : object
            Argument ``rule``.
        groups : object
            Argument ``groups``.
        value : object
            Argument ``value``.

        Returns
        -------
        object
            Return value.
        """
        template = self.hook.template_for(rule.id, rule.explain)
        return render_template(template, groups, value=value, locale=self.locale)


def _result(
    ctx: MatchContext,
    spans: list[MatchSpan],
    residuals: list[MatchSpan],
    steps: int,
) -> MatchResult:
    """
    Internal helper ``_result``.

    Parameters
    ----------
    ctx : object
        Argument ``ctx``.
    spans : object
        Argument ``spans``.
    residuals : object
        Argument ``residuals``.
    steps : object
        Argument ``steps``.

    Returns
    -------
    object
        Return value.
    """
    return MatchResult(tuple(spans), tuple(residuals), steps, ctx.iwxxm_version, ctx.profile)


def _stub(tac: str, ctx: MatchContext) -> MatchResult:
    """
    Internal helper ``_stub``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    ctx : object
        Argument ``ctx``.

    Returns
    -------
    object
        Return value.
    """
    if not tac:
        return _result(ctx, [], [], 0)
    span = MatchSpan(0, len(tac), tac, "", "")
    return _result(ctx, [], [span], 0)


def _bump(steps: int, max_steps: int) -> int:
    """
    Internal helper ``_bump``.

    Parameters
    ----------
    steps : object
        Argument ``steps``.
    max_steps : object
        Argument ``max_steps``.

    Returns
    -------
    object
        Return value.
    """
    steps += 1
    if steps > max_steps:
        msg = f"Matcher stopped after {max_steps} steps"
        raise MatchBudgetError(msg)
    return steps


def _match_tokens(
    tac: str,
    pack: Pack,
    ctx: MatchContext,
    max_steps: int,
    explain: _Explain,
) -> MatchResult:
    """
    Internal helper ``_match_tokens``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    pack : object
        Argument ``pack``.
    ctx : object
        Argument ``ctx``.
    max_steps : object
        Argument ``max_steps``.
    explain : object
        Argument ``explain``.

    Returns
    -------
    object
        Return value.
    """
    tokens = list(_TOKEN.finditer(tac))
    spans: list[MatchSpan] = []
    residuals: list[MatchSpan] = []
    index = 0
    steps = 0
    while index < len(tokens):
        matched, consumed, steps = _take_tokens(tac, tokens, index, pack.rules, steps, max_steps, explain)
        if matched is None:
            token = tokens[index]
            residuals.append(MatchSpan(token.start(), token.end(), token.group(0), "", ""))
            index += 1
            continue
        spans.append(matched)
        index += consumed
    return _result(ctx, spans, residuals, steps)


def _take_tokens(
    tac: str,
    tokens: list[re.Match[str]],
    index: int,
    rules: tuple[Rule, ...],
    steps: int,
    max_steps: int,
    explain: _Explain,
) -> tuple[MatchSpan | None, int, int]:
    """
    Internal helper ``_take_tokens``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    tokens : object
        Argument ``tokens``.
    index : object
        Argument ``index``.
    rules : object
        Argument ``rules``.
    steps : object
        Argument ``steps``.
    max_steps : object
        Argument ``max_steps``.
    explain : object
        Argument ``explain``.

    Returns
    -------
    object
        Return value.
    """
    for rule in rules:
        steps = _bump(steps, max_steps)
        count = len(rule.patterns)
        if index + count > len(tokens):
            continue
        chunk = tokens[index : index + count]
        if not all(pattern.fullmatch(token.group(0)) for pattern, token in zip(rule.patterns, chunk, strict=True)):
            continue
        start = chunk[0].start()
        end = chunk[-1].end()
        groups = tuple(token.group(0) for token in chunk)
        span = MatchSpan(start, end, tac[start:end], explain(rule, groups), rule.id)
        return span, count, steps
    return None, 0, steps


def _match_labels(
    tac: str,
    pack: Pack,
    ctx: MatchContext,
    max_steps: int,
    explain: _Explain,
) -> MatchResult:
    """
    Internal helper ``_match_labels``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    pack : object
        Argument ``pack``.
    ctx : object
        Argument ``ctx``.
    max_steps : object
        Argument ``max_steps``.
    explain : object
        Argument ``explain``.

    Returns
    -------
    object
        Return value.
    """
    rules = tuple(sorted(pack.rules, key=lambda rule: len(rule.label), reverse=True))
    spans: list[MatchSpan] = []
    residuals: list[MatchSpan] = []
    steps = 0
    offset = 0
    for line in tac.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if content.strip():
            span, steps = _take_label(content, offset, rules, steps, max_steps, explain)
            if span is None:
                residuals.append(MatchSpan(offset, offset + len(content), content, "", ""))
            else:
                spans.append(span)
        offset += len(line)
    return _result(ctx, spans, residuals, steps)


def _take_label(
    content: str,
    offset: int,
    rules: tuple[Rule, ...],
    steps: int,
    max_steps: int,
    explain: _Explain,
) -> tuple[MatchSpan | None, int]:
    """
    Internal helper ``_take_label``.

    Parameters
    ----------
    content : object
        Argument ``content``.
    offset : object
        Argument ``offset``.
    rules : object
        Argument ``rules``.
    steps : object
        Argument ``steps``.
    max_steps : object
        Argument ``max_steps``.
    explain : object
        Argument ``explain``.

    Returns
    -------
    object
        Return value.
    """
    for rule in rules:
        steps = _bump(steps, max_steps)
        matched = re.match(re.escape(rule.label) + r"\s*:\s*(.*)$", content, re.IGNORECASE)
        if matched is None:
            continue
        value = matched.group(1)
        span = MatchSpan(
            offset,
            offset + len(content),
            content,
            explain(rule, value=value),
            rule.id,
        )
        return span, steps
    return None, steps
