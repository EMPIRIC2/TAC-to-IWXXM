#!/usr/bin/env python3
"""Demo login interface for testing auth service.

This script provides a simple command-line interface for testing
the auth service endpoints. It can create demo users and test
authentication flows.

Usage:
    python demo_login.py
"""
import json
import os
import sys
from typing import Optional

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("AUTH_API_URL", "http://localhost:8000/auth")
DEMO_ADMIN_EMAIL = os.getenv("DEMO_ADMIN_EMAIL", "admin@demo.local")
DEMO_ADMIN_USERNAME = os.getenv("DEMO_ADMIN_USERNAME", "admin")
DEMO_ADMIN_PASSWORD = os.getenv("DEMO_ADMIN_PASSWORD", "Admin123!SecurePass")
DEMO_ADMIN_NAME = os.getenv("DEMO_ADMIN_NAME", "Demo Administrator")
DEMO_ADMIN_ADDRESS = os.getenv("DEMO_ADMIN_ADDRESS", "123 Demo Street")

DEMO_USER_EMAIL = os.getenv("DEMO_USER_EMAIL", "user@demo.local")
DEMO_USER_USERNAME = os.getenv("DEMO_USER_USERNAME", "demouser")
DEMO_USER_PASSWORD = os.getenv("DEMO_USER_PASSWORD", "User123!SecurePass")
DEMO_USER_NAME = os.getenv("DEMO_USER_NAME", "Demo User")
DEMO_USER_ADDRESS = os.getenv("DEMO_USER_ADDRESS", "456 User Avenue")


class AuthClient:
    """Simple client for auth service."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_info: Optional[dict] = None

    def register(self, name: str, email: str, address: str, username: str, password: str) -> dict:
        """Register a new user."""
        url = f"{self.base_url}/register"
        data = {
            "name": name,
            "email": email,
            "address": address,
            "username": username,
            "password": password
        }

        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def login(self, username: str, password: str) -> dict:
        """Login and get access token."""
        url = f"{self.base_url}/login"
        data = {
            "username": username,
            "password": password
        }

        response = requests.post(url, json=data)
        response.raise_for_status()

        result = response.json()
        self.token = result["access_token"]
        self.user_info = result["user"]

        return result

    def get_me(self) -> dict:
        """Get current user info."""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        url = f"{self.base_url}/me"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()

    def create_api_key(self) -> dict:
        """Create a new API key."""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        url = f"{self.base_url}/apikeys"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.post(url, headers=headers)
        response.raise_for_status()

        return response.json()

    def list_api_keys(self) -> list:
        """List all API keys."""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        url = f"{self.base_url}/apikeys"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()

    def revoke_api_key(self, key_id: int) -> dict:
        """Revoke an API key."""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")

        url = f"{self.base_url}/apikeys/{key_id}"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.delete(url, headers=headers)
        response.raise_for_status()

        return response.json()

    def request_password_reset(self, email: str) -> dict:
        """Request a password reset."""
        url = f"{self.base_url}/password-reset/request"
        data = {"email": email}

        response = requests.post(url, json=data)
        response.raise_for_status()

        return response.json()


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_json(data: dict):
    """Print JSON data nicely."""
    print(json.dumps(data, indent=2))


def demo_registration():
    """Demo user registration."""
    print_header("Demo: User Registration")

    client = AuthClient()

    print("\n📝 Registering demo admin user...")
    try:
        result = client.register(
            name=DEMO_ADMIN_NAME,
            email=DEMO_ADMIN_EMAIL,
            address=DEMO_ADMIN_ADDRESS,
            username=DEMO_ADMIN_USERNAME,
            password=DEMO_ADMIN_PASSWORD
        )
        print("✅ Registration successful!")
        print_json(result)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print("ℹ️  User already exists (this is expected if run multiple times)")
        else:
            print(f"❌ Registration failed: {e}")

    print("\n📝 Registering demo regular user...")
    try:
        result = client.register(
            name=DEMO_USER_NAME,
            email=DEMO_USER_EMAIL,
            address=DEMO_USER_ADDRESS,
            username=DEMO_USER_USERNAME,
            password=DEMO_USER_PASSWORD
        )
        print("✅ Registration successful!")
        print_json(result)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print("ℹ️  User already exists (this is expected if run multiple times)")
        else:
            print(f"❌ Registration failed: {e}")


def demo_login():
    """Demo user login."""
    print_header("Demo: User Login")

    client = AuthClient()

    print(f"\n🔐 Logging in as {DEMO_USER_USERNAME}...")
    try:
        result = client.login(DEMO_USER_USERNAME, DEMO_USER_PASSWORD)
        print("✅ Login successful!")
        print(f"   Token: {result['access_token'][:20]}...")
        print(f"   User: {result['user']['name']} ({result['user']['email']})")

        return client
    except requests.exceptions.HTTPError as e:
        print(f"❌ Login failed: {e}")
        return None


def demo_get_profile(client: AuthClient):
    """Demo getting user profile."""
    print_header("Demo: Get User Profile")

    print("\n👤 Fetching user profile...")
    try:
        result = client.get_me()
        print("✅ Profile retrieved!")
        print_json(result)
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to get profile: {e}")


def demo_api_keys(client: AuthClient):
    """Demo API key management."""
    print_header("Demo: API Key Management")

    print("\n🔑 Creating a new API key...")
    try:
        result = client.create_api_key()
        print("✅ API key created!")
        print(f"   Key ID: {result['id']}")
        print(f"   Raw Key (save this!): {result['raw_key']}")
        key_id = result['id']
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to create API key: {e}")
        return

    print("\n📋 Listing all API keys...")
    try:
        result = client.list_api_keys()
        print(f"✅ Found {len(result)} API key(s):")
        for key in result:
            status = "❌ Revoked" if key['revoked'] else "✅ Active"
            print(f"   - ID {key['id']}: {status} (created {key['created_at']})")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to list API keys: {e}")

    print(f"\n🗑️  Revoking API key {key_id}...")
    try:
        result = client.revoke_api_key(key_id)
        print("✅ API key revoked!")
        print_json(result)
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to revoke API key: {e}")


def demo_password_reset():
    """Demo password reset request."""
    print_header("Demo: Password Reset Request")

    client = AuthClient()

    print(f"\n📧 Requesting password reset for {DEMO_USER_EMAIL}...")
    try:
        result = client.request_password_reset(DEMO_USER_EMAIL)
        print("✅ Password reset requested!")
        print_json(result)
        print("\nℹ️  Check server logs for the reset link (in production, this would be emailed)")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to request password reset: {e}")


def run_full_demo():
    """Run complete demo flow."""
    print("\n" + "🚀 " * 20)
    print("AUTH SERVICE DEMO")
    print("🚀 " * 20)

    print(f"\n📍 API Base URL: {API_BASE_URL}")
    print("📍 Demo Users:")
    print(f"   - Admin: {DEMO_ADMIN_USERNAME}")
    print(f"   - User:  {DEMO_USER_USERNAME}")

    # Run demos
    demo_registration()

    client = demo_login()
    if client:
        demo_get_profile(client)
        demo_api_keys(client)

    demo_password_reset()

    print("\n" + "✨ " * 20)
    print("DEMO COMPLETE!")
    print("✨ " * 20)
    print("\nDemo users have been created. You can use these credentials:")
    print(f"  Username: {DEMO_USER_USERNAME}")
    print(f"  Password: {DEMO_USER_PASSWORD}")
    print("\nOr admin:")
    print(f"  Username: {DEMO_ADMIN_USERNAME}")
    print(f"  Password: {DEMO_ADMIN_PASSWORD}")
    print()


def interactive_mode():
    """Interactive mode for manual testing."""
    print_header("Interactive Mode")

    client = AuthClient()

    while True:
        print("\n📋 Available Actions:")
        print("  1. Register User")
        print("  2. Login")
        print("  3. Get Profile")
        print("  4. Create API Key")
        print("  5. List API Keys")
        print("  6. Revoke API Key")
        print("  7. Request Password Reset")
        print("  8. Run Full Demo")
        print("  0. Exit")

        choice = input("\n👉 Select action (0-8): ").strip()

        try:
            if choice == "0":
                print("\n👋 Goodbye!")
                break
            elif choice == "1":
                name = input("Name: ")
                email = input("Email: ")
                address = input("Address: ")
                username = input("Username: ")
                password = input("Password: ")
                result = client.register(name, email, address, username, password)
                print_json(result)
            elif choice == "2":
                username = input("Username: ")
                password = input("Password: ")
                result = client.login(username, password)
                print_json(result)
            elif choice == "3":
                result = client.get_me()
                print_json(result)
            elif choice == "4":
                result = client.create_api_key()
                print_json(result)
            elif choice == "5":
                result = client.list_api_keys()
                print_json(result)
            elif choice == "6":
                key_id = int(input("API Key ID to revoke: "))
                result = client.revoke_api_key(key_id)
                print_json(result)
            elif choice == "7":
                email = input("Email: ")
                result = client.request_password_reset(email)
                print_json(result)
            elif choice == "8":
                run_full_demo()
            else:
                print("❌ Invalid choice")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        run_full_demo()


if __name__ == "__main__":
    main()
