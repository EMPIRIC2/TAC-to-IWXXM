"""Typed errors for the auth service library (no HTTPException)."""

from __future__ import annotations


class AuthProxyError(Exception):
    """
    Supabase Auth HTTP call failed.

    Attributes
    ----------
    status_code : int
        Suggested HTTP status for API mapping (not raised as HTTP here).
    """

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        """
        Parameters
        ----------
        message : str
            Error message.
        status_code : int, optional
            Suggested HTTP status. By default ``400``.
        """
        super().__init__(message)
        self.status_code = status_code


class JwtVerificationError(Exception):
    """
    Raised when a bearer token fails JWKS verification.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """
