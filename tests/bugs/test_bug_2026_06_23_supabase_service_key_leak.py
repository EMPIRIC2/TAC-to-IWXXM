"""BUG-2026-06-23 — Supabase service role key hardcoded in admin script.

GitHub Secret Scanning alert #1 flagged a Supabase ``service_role`` JWT committed
in ``scripts/create_admin_user.py``. The script was refactored to read the secret
from the environment (``SUPABASE_SECRET_KEY``) and the project URL from config.

This regression guard keeps operator scripts free of hardcoded Supabase
credentials so the leak class cannot silently return.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_SCRIPT = REPO_ROOT / "scripts" / "utilities" / "create_admin_user.py"

# A Supabase service/anon key is a JWT: three base64url segments separated by
# dots, the first decoding to a JOSE header beginning ``eyJ``. We flag any long
# JWT-looking literal embedded in operator scripts (env reads are short strings).
_JWT_LITERAL = re.compile(
    r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
)


def test_create_admin_script_exists() -> None:
    """Admin script must live at the documented monorepo path."""
    assert ADMIN_SCRIPT.is_file(), f"Missing operator script: {ADMIN_SCRIPT}"


def test_create_admin_script_has_no_hardcoded_jwt() -> None:
    """No Supabase JWT (service_role/anon) literal may be committed in the script."""
    source = ADMIN_SCRIPT.read_text(encoding="utf-8")
    matches = _JWT_LITERAL.findall(source)
    assert not matches, (
        "Hardcoded Supabase JWT found in scripts/utilities/create_admin_user.py "
        "(GitHub secret-scanning alert #1). Read SUPABASE_SECRET_KEY from the "
        f"environment instead. Offending literal(s): {matches}"
    )


def test_create_admin_script_reads_secret_from_env() -> None:
    """Script must source the secret key + URL from env/config helpers, not inline."""
    source = ADMIN_SCRIPT.read_text(encoding="utf-8")
    assert "get_supabase_secret_key()" in source, (
        "create_admin_user.py must obtain the secret via get_supabase_secret_key() "
        "(reads SUPABASE_SECRET_KEY from the environment)."
    )
    assert "get_supabase_url()" in source, (
        "create_admin_user.py must resolve the project URL via get_supabase_url() "
        "(config/SUPABASE_URL), not a hardcoded https://*.supabase.co literal."
    )
