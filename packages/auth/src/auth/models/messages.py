"""Input and output pydantic models for auth service operations."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


def validate_email_permissive(email: str) -> str:
    """
    Validate email; allow common development TLDs.

    Parameters
    ----------
    email : str
        Email address.

    Returns
    -------
    str
        Normalized email address.

    Raises
    ------
    ValueError
        If the email format is invalid.

    Examples
    --------
    >>> validate_email_permissive("User@Example.local")
    'user@example.local'
    """
    if not email or "@" not in email:
        raise ValueError("Invalid email format")
    local_part, domain = email.rsplit("@", 1)
    if not local_part or not domain:
        raise ValueError("Invalid email format")
    allowed_dev = (".local", ".test", ".localhost", ".dev", ".example")
    if any(domain.endswith(dev) or domain == dev[1:] for dev in allowed_dev):
        return email.lower()
    from email_validator import EmailNotValidError, validate_email

    try:
        return validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError as exc:
        raise ValueError(f"Invalid email: {exc}") from exc


class LoginRequest(BaseModel):
    """
    Login credentials.

    Attributes
    ----------
    email : str
        Email address.
    password : str
        Password.
    """

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _email(cls, value: str) -> str:
        """
        Normalize and validate login email.

        Parameters
        ----------
        value : str
            Raw email field.

        Returns
        -------
        str
            Normalized email address.
        """
        return validate_email_permissive(value)


class RegisterRequest(BaseModel):
    """
    Registration credentials (Supabase GoTrue signup).

    Attributes
    ----------
    email : str
        Email address.
    password : str
        Password.
    """

    email: str
    password: str = Field(min_length=6)

    @field_validator("email")
    @classmethod
    def _email(cls, value: str) -> str:
        """
        Normalize and validate registration email.

        Parameters
        ----------
        value : str
            Raw email field.

        Returns
        -------
        str
            Normalized email address.
        """
        return validate_email_permissive(value)


class ConfirmRequest(BaseModel):
    """
    Email confirmation via GoTrue ``token_hash`` (Auth email link).

    Attributes
    ----------
    token_hash : str
        GoTrue email confirmation token hash.
    type : str, optional
        GoTrue confirmation type. By default ``"email"``.
    """

    token_hash: str = Field(min_length=1)
    type: str = Field(default="email", min_length=1)

    @field_validator("type")
    @classmethod
    def _type(cls, value: str) -> str:
        """
        Normalize GoTrue confirmation type.

        Parameters
        ----------
        value : str
            Raw confirmation type.

        Returns
        -------
        str
            Lowercased allowed confirmation type.
        """
        allowed = {
            "email",
            "signup",
            "invite",
            "magiclink",
            "recovery",
            "email_change",
        }
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError(f"Unsupported confirmation type {value!r}")
        return normalized


class UserResponse(BaseModel):
    """
    Auth user projection.

    Attributes
    ----------
    id : str
        User id.
    email : str
        Email address.
    metadata : dict[str, Any], optional
        User metadata. By default an empty dict.
    """

    id: str
    email: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    """
    Session tokens.

    Attributes
    ----------
    access_token : str
        Access token.
    refresh_token : str
        Refresh token.
    expires_at : int
        Expiry time (unix seconds).
    """

    access_token: str
    refresh_token: str
    expires_at: int


class AuthResponse(BaseModel):
    """
    Auth operation response.

    Attributes
    ----------
    user : UserResponse
        User.
    session : SessionResponse or None, optional
        Session when tokens are issued.
    """

    user: UserResponse
    session: SessionResponse | None = None


class LogoutRequest(BaseModel):
    """
    Optional scoped logout body.

    Attributes
    ----------
    scope : str or None, optional
        GoTrue logout scope: ``global``, ``local``, or ``others``.
    """

    scope: str | None = Field(
        default=None,
        description="GoTrue logout scope: global, local, or others",
    )

    @field_validator("scope")
    @classmethod
    def _scope(cls, value: str | None) -> str | None:
        """
        Normalize optional GoTrue logout scope.

        Parameters
        ----------
        value : str or None
            Raw logout scope, empty string, or ``None``.

        Returns
        -------
        str or None
            Allowed scope, or ``None`` when unset.
        """
        if value is None or value == "":
            return None
        allowed = {"global", "local", "others"}
        if value not in allowed:
            raise ValueError(f"Unsupported logout scope {value!r}")
        return value


class Message(BaseModel):
    """
    Simple success message.

    Attributes
    ----------
    message : str
        Message text.
    """

    message: str
