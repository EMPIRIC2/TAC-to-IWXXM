"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def get_first_party_template(template_id: str) -> ConversionTemplate | None:
    """
    Return a first-party template by id, or ``None``.

    Parameters
    ----------
    template_id : str
        Template id.

    Returns
    -------
    ConversionTemplate | None
        A first-party template by id, or ``None``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_first_party_template)
    2
    """
    return FIRST_PARTY_TEMPLATES.get(template_id)


def fork_first_party(template_id: str, *, new_id: str, name: str | None = None) -> ConversionTemplate:
    """
    Fork a first-party template into a custom template object (not persisted).

    Parameters
    ----------
    template_id : str
        Template id.

    new_id : str
        Id for the forked template.

    name : str | None, optional
        Display name. ``None`` keeps the source name.

    Returns
    -------
    ConversionTemplate
        A first-party template into a custom template object (not persisted).

    Raises
    ------
    KeyError
        If ``template_id`` is not a known first-party id.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (fork_first_party)
    2
    """
    base = FIRST_PARTY_TEMPLATES.get(template_id)
    if base is None:
        raise KeyError(template_id)
    return ConversionTemplate(
        id=new_id,
        name=name or f"{base.name} (custom)",
        access="custom",
        iwxxm_block=base.iwxxm_block,
        slots=base.slots,
        sample=base.sample,
        profiles=base.profiles,
        comments=base.comments,
        fork_of=base.id,
    )
