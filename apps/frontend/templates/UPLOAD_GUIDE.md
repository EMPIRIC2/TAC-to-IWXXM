# Email Templates Upload Guide

This directory contains 14 professional email templates ready for Supabase.

## Quick Upload Instructions

Supabase provides 4 built-in template types that you can customize:
1. **Confirmation** (Email Verification)
2. **Magic Link** (Passwordless Login)
3. **Recovery** (Password Reset)
4. **Email Change** (Email Update Notification)

### How to Upload

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Select your project**: metar-to-iwxxm
3. **Navigate to**: Authentication → Email Templates
4. **For each template below**:
   - Select the template type
   - Copy the Subject line
   - Copy the HTML content
   - Paste into Supabase
   - Click "Save"

---

## 1. Confirmation Template (Email Verification)

**File**: `authentication/01-confirmation.md`

**Subject**:
```
Confirm your email address
```

**HTML**: See file for complete HTML

**Supabase Template Type**: `Confirmation`

---

## 2. Magic Link Template (Passwordless Login)

**File**: `authentication/02-magic-link.md`

**Subject**:
```
Your magic link to sign in
```

**HTML**: See file for complete HTML

**Supabase Template Type**: `Magic Link`

---

## 3. Password Reset Template

**File**: `authentication/03-password-reset.md`

**Subject**:
```
Reset your password
```

**HTML**: See file for complete HTML

**Supabase Template Type**: `Recovery`

---

## 4. Email Change Template

**File**: `authentication/05-email-changed.md`

**Subject**:
```
Email address changed
```

**HTML**: See file for complete HTML

**Supabase Template Type**: `Email Change`

---

## Custom Templates (Not Supported by Supabase Built-in)

These templates require custom implementation via your application:
- ✉️ Welcome email (04-welcome.md)
- 🚨 Suspicious activity alert (06-suspicious-activity.md)
- 🔐 MFA enabled (security/01-mfa-enabled.md)
- ⏰ Session timeout warning (security/02-session-timeout.md)
- 👤 Permission revoked (security/03-permission-revoked.md)
- 💻 New device login (security/04-new-device.md)
- 🔑 Password changed (security/05-password-changed.md)
- 🔒 Account locked (security/06-account-locked.md)
- 🌍 IP mismatch (security/07-ip-mismatch.md)
- 📦 Data export ready (security/08-data-export.md)

These can be sent via your backend using Supabase's email service or a service like SendGrid/Mailgun.

---

## Alternative: Programmatic Upload

If you have a Supabase Management API token, you can use the Python script:

```bash
# Set your access token (get from https://supabase.com/dashboard/account/tokens)
$env:SUPABASE_ACCESS_TOKEN = "your-token-here"

# Run the upload script
python scripts/upload_email_templates.py
```

**Note**: This only works for the 4 built-in template types.
