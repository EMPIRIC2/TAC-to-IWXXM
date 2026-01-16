"""
Upload email templates to Supabase using Management API

Usage:
    python upload_email_templates.py --access-token <token> --project-id <id>

Get your access token from: https://supabase.com/dashboard/account/tokens
"""
import argparse
import os
import re
import sys
import requests
from pathlib import Path
from typing import Optional

# Configuration
SUPABASE_API_URL = "https://api.supabase.com/v1"

# Template mapping: (template_type, file_path, subject)
TEMPLATES = [
    ("confirmation", "frontend/templates/authentication/01-confirmation.md", "Confirm your email address"),
    ("magic_link", "frontend/templates/authentication/02-magic-link.md", "Your magic link to sign in"),
    ("recovery", "frontend/templates/authentication/03-password-reset.md", "Reset your password"),
    ("email_change", "frontend/templates/authentication/05-email-changed.md", "Email address changed"),
]

def extract_html_from_template(file_path: str) -> Optional[str]:
    """Extract HTML content from markdown template file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find HTML section between ```html and ```
        match = re.search(r"## HTML\s*```html\s*(.*?)\s*```", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback: look for any ```html block
        match = re.search(r"```html\s*(.*?)\s*```", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return None
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None


def upload_template(
    access_token: str,
    project_id: str,
    template_type: str,
    subject: str,
    html: str
) -> bool:
    """Upload a single template to Supabase via auth config endpoint."""
    url = f"{SUPABASE_API_URL}/projects/{project_id}/config/auth"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    # Map template type to config keys
    config_key_content = f"mailer_templates_{template_type}_content"
    config_key_subject = f"mailer_subjects_{template_type}"
    
    payload = {
        config_key_content: html,
        config_key_subject: subject,
    }
    
    print(f"📤 Uploading {template_type}...", end=" ")
    sys.stdout.flush()
    
    try:
        response = requests.patch(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in (200, 201):
            print("✅")
            return True
        else:
            print(f"❌ ({response.status_code})")
            if response.status_code == 401:
                print(f"   Invalid access token")
            elif response.status_code == 404:
                print(f"   Project not found")
            else:
                print(f"   {response.text[:200]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Upload Supabase email templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--access-token",
        required=True,
        help="Supabase Management API access token"
    )
    parser.add_argument(
        "--project-id",
        required=True,
        help="Supabase project ID"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify templates can be read (don't upload)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🚀 Supabase Email Templates Upload")
    print("="*60)
    
    # Verify files exist and extract HTML
    templates_data = []
    all_ok = True
    
    for template_type, file_path, subject in TEMPLATES:
        print(f"\n📖 Reading {template_type}...", end=" ")
        sys.stdout.flush()
        
        html = extract_html_from_template(file_path)
        if html:
            print("✅")
            templates_data.append((template_type, subject, html))
        else:
            print("❌")
            all_ok = False
    
    if not all_ok:
        print("\n❌ Failed to read some templates.")
        return 1
    
    if args.verify_only:
        print("\n✅ All templates verified!")
        return 0
    
    # Upload templates
    print("\n" + "-"*60)
    print("📡 Uploading to Supabase...")
    print("-"*60 + "\n")
    
    success_count = 0
    for template_type, subject, html in templates_data:
        if upload_template(args.access_token, args.project_id, template_type, subject, html):
            success_count += 1
    
    # Summary
    print("\n" + "="*60)
    print(f"✅ Complete: {success_count}/{len(templates_data)} templates uploaded")
    print("="*60)
    
    return 0 if success_count == len(templates_data) else 1


if __name__ == "__main__":
    sys.exit(main())
    print()
    print("Note: Custom templates (welcome, suspicious-activity, etc.) must be")
    print("configured manually in Supabase Dashboard → Authentication → Email Templates")

if __name__ == "__main__":
    main()
