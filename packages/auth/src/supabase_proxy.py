"""Supabase authentication proxy.

This module provides a middleware layer between the frontend/backend and Supabase,
allowing centralized authentication management, logging, and monitoring.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional, cast

# Load environment variables
from dotenv import load_dotenv
from fastapi import HTTPException, status
from metar_shared.supabase_env import (
    assert_modern_supabase_publishable_key,
    get_supabase_publishable_key,
    get_supabase_url,
)
from supabase import Client, create_client

load_dotenv()

logger = logging.getLogger(__name__)


def _is_session_not_found_error(error: Exception) -> bool:
    """Return True when Supabase indicates the JWT session no longer exists."""
    message = str(error).lower()
    return "session_not_found" in message or "session from session_id claim in jwt does not exist" in message


class SupabaseAuthProxy:
    """Proxy for Supabase authentication operations."""

    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_url = get_supabase_url()
        self.supabase_key = get_supabase_publishable_key()

        if not self.supabase_url or not self.supabase_key:
            legacy_anon = os.getenv("SUPABASE_ANON_KEY", "").strip()
            if legacy_anon.startswith("eyJ") and os.getenv("METAR_CONFIG_ENV", "local").strip().lower() == "prod":
                raise ValueError(
                    "Legacy Supabase JWT anon key detected; Supabase has disabled legacy API keys. "
                    "Set SUPABASE_PUBLISHABLE_KEY to your sb_publishable_* key in Render."
                )
            raise ValueError("Supabase URL and publishable key must be set (SUPABASE_PUBLISHABLE_KEY or config)")

        assert_modern_supabase_publishable_key(self.supabase_key)

        logger.info(f"Initializing Supabase client for URL: {self.supabase_url}")
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def sign_up(self, email: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register a new user with Supabase.

        Args:
            email: User's email address
            password: User's password
            metadata: Additional user metadata (name, username, etc.)

        Returns:
            Dict containing user data and session
        """
        logger.info(f"[REGISTER] Starting registration for email: {email}")
        try:
            payload = {"email": email, "password": password, "options": {"data": metadata or {}}}
            logger.debug(f"[REGISTER] Calling Supabase sign_up with payload: {payload}")

            response = self.client.auth.sign_up(cast(Any, payload))

            logger.info(
                f"[REGISTER] Supabase response: user={response.user is not None}, session={response.session is not None}"
            )

            if not response.user:
                logger.error(f"[REGISTER] No user in response for {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed - no user data returned"
                )

            result = {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "metadata": response.user.user_metadata or {},
                },
                "session": {
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None,
                    "expires_at": response.session.expires_at if response.session else None,
                }
                if response.session
                else None,
            }

            logger.info(f"[REGISTER] Successfully registered user {email} with ID {response.user.id}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"[REGISTER] Error during registration for {email}: {type(e).__name__}: {str(e)}", exc_info=True
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {str(e)}")

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in with email and password.

        Args:
            email: User's email
            password: User's password

        Returns:
            Dict containing user data and session tokens
        """
        logger.info(f"[LOGIN] Starting login for email: {email}")
        try:
            payload = {"email": email, "password": password}
            logger.debug("[LOGIN] Calling Supabase sign_in_with_password")

            response = self.client.auth.sign_in_with_password(cast(Any, payload))

            logger.info(
                f"[LOGIN] Supabase response: user={response.user is not None}, session={response.session is not None}"
            )

            if not response.user or not response.session:
                logger.warning(f"[LOGIN] Failed login attempt for {email} - invalid credentials or missing session")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            result = {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "metadata": response.user.user_metadata or {},
                },
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                },
            }

            logger.info(f"[LOGIN] Successfully logged in user {email}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[LOGIN] Error during login for {email}: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication failed: {str(e)}")

    def sign_out(self, access_token: str) -> Dict[str, str]:
        """Sign out the current user.

        Args:
            access_token: User's access token

        Returns:
            Success message
        """
        logger.info("[LOGOUT] Starting logout")
        try:
            # Set the session for this client
            self.client.auth.set_session(access_token, "")
            self.client.auth.sign_out()
            logger.info("[LOGOUT] Successfully signed out user")
            return {"message": "Successfully signed out"}
        except Exception as e:
            if _is_session_not_found_error(e):
                logger.info("[LOGOUT] Session already invalidated in Supabase; treating as successful logout")
                return {"message": "Successfully signed out"}
            logger.error(f"[LOGOUT] Error during logout: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Sign out failed: {str(e)}")

    def get_user(self, access_token: str) -> Dict[str, Any]:
        """Get user information from access token.

        Args:
            access_token: User's access token

        Returns:
            User information
        """
        logger.info("[GET_USER] Retrieving user info from token")
        try:
            response = self.client.auth.get_user(access_token)
            if response is None:
                logger.warning("[GET_USER] Invalid or expired token")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            user = response.user
            if user is None:
                logger.warning("[GET_USER] Invalid or expired token")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            logger.info(f"[GET_USER] Retrieved user {user.email}")
            return {
                "id": user.id,
                "email": user.email,
                "metadata": user.user_metadata or {},
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[GET_USER] Error retrieving user: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Failed to get user: {str(e)}")

    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired session.

        Args:
            refresh_token: User's refresh token

        Returns:
            New session tokens
        """
        logger.info("[REFRESH_TOKEN] Refreshing session")
        try:
            response = self.client.auth.refresh_session(refresh_token)

            if not response.session:
                logger.warning("[REFRESH_TOKEN] Invalid refresh token")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

            logger.info("[REFRESH_TOKEN] Successfully refreshed session")
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_at": response.session.expires_at,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[REFRESH_TOKEN] Error refreshing session: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Failed to refresh session: {str(e)}")

    def reset_password_email(self, email: str) -> Dict[str, str]:
        """Send password reset email.

        Args:
            email: User's email address

        Returns:
            Success message
        """
        logger.info(f"[PASSWORD_RESET_REQUEST] Requesting password reset for {email}")
        try:
            self.client.auth.reset_password_email(
                email, {"redirect_to": f"{os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173')}/password-reset"}
            )
            logger.info(f"[PASSWORD_RESET_REQUEST] Password reset email sent for {email}")
            return {"message": "Password reset email sent"}
        except Exception as e:
            logger.error(f"[PASSWORD_RESET_REQUEST] Error for {email}: {type(e).__name__}: {str(e)}", exc_info=True)
            # Don't reveal whether email exists
            return {"message": "If the email exists, a password reset link has been sent"}

    def update_password(self, access_token: str, new_password: str) -> Dict[str, str]:
        """Update user's password.

        Args:
            access_token: User's access token
            new_password: New password

        Returns:
            Success message
        """
        logger.info("[UPDATE_PASSWORD] Starting password update")
        try:
            # Set the session for this operation
            self.client.auth.set_session(access_token, "")
            self.client.auth.update_user({"password": new_password})
            logger.info("[UPDATE_PASSWORD] Password updated successfully")
            return {"message": "Password updated successfully"}
        except Exception as e:
            logger.error(f"[UPDATE_PASSWORD] Error: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update password: {str(e)}")

    def verify_token(self, access_token: str) -> bool:
        """Verify if an access token is valid.

        Args:
            access_token: Token to verify

        Returns:
            True if valid, False otherwise
        """
        logger.debug("[VERIFY_TOKEN] Verifying token")
        try:
            user_response = self.client.auth.get_user(access_token)
            is_valid = user_response is not None and user_response.user is not None
            logger.debug(f"[VERIFY_TOKEN] Token valid: {is_valid}")
            return is_valid
        except Exception as e:
            logger.debug(f"[VERIFY_TOKEN] Token verification failed: {type(e).__name__}")
            return False


# Singleton instance
_proxy: Optional[SupabaseAuthProxy] = None


def get_supabase_proxy() -> SupabaseAuthProxy:
    """Get or create the Supabase proxy singleton."""
    global _proxy
    if _proxy is None:
        _proxy = SupabaseAuthProxy()
    return _proxy
