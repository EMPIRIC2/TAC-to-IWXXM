#!/usr/bin/env python3
"""Create an admin user in Supabase with email verification.

Required environment variables (repo-root ``.env``):
    SUPABASE_SECRET_KEY — Secret key for Auth Admin API (legacy SUPABASE_SERVICE_ROLE_KEY shim)
    ADMIN_EMAIL — Email address for the admin user
    ADMIN_PASSWORD — Password for the admin user

Supabase project URL is read from ``config/local.json`` or ``config/prod.json``
(``METAR_CONFIG_ENV``) unless ``SUPABASE_URL`` is set.
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

from metar_shared.supabase_env import get_supabase_secret_key, get_supabase_url

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env")

SUPABASE_URL = get_supabase_url()
SERVICE_KEY = get_supabase_secret_key()
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not all([SUPABASE_URL, SERVICE_KEY, ADMIN_EMAIL, ADMIN_PASSWORD]):
    print("❌ Error: Missing required environment variables")
    print("   Required: SUPABASE_SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD")
    print("   Supabase URL: config/*.json supabase.url or SUPABASE_URL")
    sys.exit(1)


def create_admin():
    """Create admin user via Supabase Auth API."""
    try:
        headers = {
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "email_confirm": True,
            "user_metadata": {"username": "admin"},
        }

        print(f"🔐 Creating admin user: {ADMIN_EMAIL}")

        response = requests.post(
            f"{SUPABASE_URL}/auth/v1/admin/users",
            headers=headers,
            json=payload,
            timeout=10,
        )

        if response.status_code not in (200, 201):
            print(f"❌ Error creating user: {response.status_code}")
            print(f"   {response.text}")
            return 1

        user_data = response.json()
        user_id = user_data.get("id")
        print(f"✅ User created: {user_id}")

        print("📝 Creating admin profile...")
        profile_payload = {
            "id": user_id,
            "email": ADMIN_EMAIL,
            "username": "admin",
            "is_admin": True,
            "approval_status": "approved",
        }

        profile_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/user_profiles",
            headers=headers,
            json=profile_payload,
            timeout=10,
        )

        if profile_response.status_code not in (200, 201):
            print(f"⚠️  Warning: Profile creation status {profile_response.status_code}")
            print(f"   {profile_response.text}")
        else:
            print("✅ Admin profile created")

        print("\n🎉 Admin user ready!")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"   ID: {user_id}")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(create_admin())
