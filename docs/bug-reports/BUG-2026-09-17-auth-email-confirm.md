# BUG-2026-09-17 — Auth email confirm never completes (register OK, login blocked)

| Field | Value |
|-------|-------|
| **Status** | fixed (code); deploy pending for stage/main API+FE |
| **Feature** | F31 (hybrid Auth sessions) |
| **Severity** | high — new accounts cannot sign in on stage/main |
| **Classification** | app + Auth mailer callback (Supabase GoTrue) |
| **Remediation path** | hotfix HF-auth-register-login; local checks (CI down) |
| **Corpus** | [Corpus: product §F31] [Corpus: api] [Corpus: tests] |

## Error description

Operators can register on stage and production. Confirmation email is sent. Clicking
the link does not confirm the account. Login then fails with Supabase
`email_not_confirmed`. Existing admin login still works.

## Error logs

Auth logs (2026-09-17) — signup succeeds, then password grant fails:

```
path=/signup status=200 action=user_confirmation_requested
  actor=oscar.lovell@metoffice.gov.tt

path=/token grant_type=password status=400
  error_code=email_not_confirmed msg="Email not confirmed"
```

API probe (shared Auth project for stage + main):

```
POST /auth/register → 200 (real mailbox) / 502 only for blocked test domains
POST /auth/login (unconfirmed) → 401 with email_not_confirmed in GoTrue body
```

## Investigation

| Time | Finding |
|------|---------|
| 2026-09-17 | Confirm template uses `{{ .SiteURL }}/auth/confirm?token_hash=…&type=email` |
| 2026-09-17 | FE only routes `/auth/callback` and reads hash `access_token` — no `token_hash` / `verifyOtp` |
| 2026-09-17 | Recent Auth users almost all `email_confirmed_at=null` |
| 2026-09-17 | Keep `mailer_autoconfirm=false` (Supabase best practice) |

**Root cause:** Email confirmation callback is not implemented end-to-end. GoTrue never
receives `verify` with `token_hash`, so accounts stay unconfirmed and login is denied.

## Repro test

- `tests/bugs/test_bug_2026_09_17_auth_email_confirm.py`
- FE: `AuthCallback` / `authService` token_hash confirm coverage

## Fix plan

1. `POST /auth/confirm` → GoTrue `POST /auth/v1/verify` (`token_hash` + `type`)
2. FE `/auth/confirm` (+ `/auth/callback`) exchange via authService; store session
3. Plain-language login error when email is not confirmed
4. Admin-confirm stuck real users after verify path is green
