"""ADR-048 OK module."""


def greet(name: str) -> str:
    """Return a greeting.

    Parameters
    ----------
    name : str
        Person name.

    Returns
    -------
    str
        Greeting text.

    Examples
    --------
    >>> greet("Ada")
    'Hello, Ada'
    """
    return f"Hello, {name}"


def _helper(name: str) -> str:
    """Build a private greeting fragment.

    Parameters
    ----------
    name : str
        Person name.

    Returns
    -------
    str
        Fragment text.
    """
    return name


class Greeter:
    """Greeter object.

    Attributes
    ----------
    prefix : str
        Greeting prefix.
    """

    def __init__(self, prefix: str = "Hello") -> None:
        """Create a greeter.

        Parameters
        ----------
        prefix : str
            Greeting prefix.
        """
        self.prefix = prefix
