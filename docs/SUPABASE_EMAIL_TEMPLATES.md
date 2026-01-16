# Supabase Email Templates Customization Guide

This guide explains how to customize your Supabase email templates to work with the magic link (OTP) and password reset flows implemented in this application.

## Overview

The application uses Supabase's built-in email authentication with:
- **Magic Link (OTP) Authentication** for passwordless login/signup
- **Email Verification** for new account confirmation
- **Password Reset** for account recovery

All these flows require properly configured email templates with token hash URLs.

## Prerequisites

- Access to your Supabase Dashboard
- Your frontend domain URL (e.g., `http://localhost:5173` for development, `https://yourdomain.com` for production)

## Step 1: Configure Site URL

Before customizing templates, set your Site URL:

1. Go to **Supabase Dashboard** → Select your project
2. Navigate to **Authentication** → **URL Configuration**
3. Under **Site URL**, enter your frontend URL:
   - **Development**: `http://localhost:5173` (or your local Vite dev server port)
   - **Production**: `https://yourdomain.com`
   - **Staging**: `https://staging.yourdomain.com` (if applicable)

4. Under **Redirect URLs**, add:
   ```
   http://localhost:5173/auth/callback
   https://yourdomain.com/auth/callback
   ```

This ensures email links redirect to your application properly.

## Step 2: Customize Email Templates

### Access Email Templates

1. Go to **Supabase Dashboard** → Select your project
2. Navigate to **Authentication** → **Email Templates**

### Template 1: Confirm Sign Up

This template is used for:
- Email verification during registration
- Magic link signup

**Find and replace this line:**
```
{{ .ConfirmationURL }}
```

**Replace with:**
```
{{ .SiteURL }}?token_hash={{ .TokenHash }}&type=email
```

**Full example:**
```
Follow this link to confirm your sign up:

{{ .SiteURL }}?token_hash={{ .TokenHash }}&type=email

(Or click the button below)

[Confirm Email]
```

### Template 2: Password Reset

This template is used when users request a password reset.

**Find and replace this line:**
```
{{ .ConfirmationURL }}
```

**Replace with:**
```
{{ .SiteURL }}?token_hash={{ .TokenHash }}&type=recovery
```

**Full example:**
```
Follow this link to reset your password:

{{ .SiteURL }}?token_hash={{ .TokenHash }}&type=recovery

(Or click the button below)

[Reset Password]
```

### Template 3: Magic Link (OTP)

This template is used for passwordless login via magic link.

**Find and replace this line:**
```
{{ .ConfirmationURL }}
```

**Replace with:**
```
{{ .SiteURL }}?token_hash={{ .TokenHash }}&type=email
```

**Full example:**
```
Click this link to sign in to your account:

{{ .SiteURL }}?token_hash={{ .TokenHash }}&type=email

(Or click the button below)

[Sign In]
```

## How It Works

### Token Hash Flow (PKCE)

1. User initiates signup/login/password reset
2. Supabase generates a `token_hash` and sends email with special URL
3. User clicks link which redirects to: `https://yourdomain.com?token_hash=...&type=email`
4. Frontend app (`AuthCallback.tsx`) detects `token_hash` in URL
5. App calls `supabase.auth.verifyOtp()` with the token hash
6. Session is established securely

**Benefits:**
- More secure than traditional callback URLs
- Works with server-side rendering (SSR)
- Compatible with PKCE flow for enhanced security
- Prevents token exposure in browser history

## Environment Variables

Ensure these variables are set in `.env.local`:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-key-or-sb_publishable_xxx
```

## Testing Email Templates

### Local Development

1. Run Supabase locally or use the hosted dashboard
2. Use **Mailpit** (auto-included with Supabase CLI):
   ```bash
   supabase status
   ```
   Copy the **Mailpit** URL and open it in your browser
3. Perform a registration/password reset action
4. Check Mailpit to see the email with your custom template

### Production

- Supabase's default email service has a **2 emails/hour rate limit**
- For production, configure custom SMTP:
  - Go to **Settings** → **Email**
  - Add your SMTP provider (SendGrid, Mailgun, Twilio SendGrid, etc.)

## Troubleshooting

### Emails Not Received

- Check **Supabase Dashboard** → **Auth** → **Users** for signup events
- Verify **Site URL** matches your current domain
- Check email spam/junk folder
- For local dev, ensure **Mailpit** is running

### Token Hash Not Working

- Ensure URL template uses `{{ .TokenHash }}` (not `{{ .Token }}`)
- Verify `type=email` or `type=recovery` parameter is included
- Check browser console for errors in `AuthCallback.tsx`

### Redirect Loop

- Verify **Redirect URLs** in Supabase match your app's callback route
- Ensure `window.location.origin` in frontend is correctly configured
- Check that `AuthCallback.tsx` properly detects and processes token hash

## Frontend Handling

The frontend automatically handles token hash URLs in `AuthCallback.tsx`:

```tsx
// Detects token_hash in URL parameters
const token_hash = params.get('token_hash');
const type = params.get('type');

// Verifies OTP with Supabase
if (token_hash) {
  supabase.auth.verifyOtp({
    token_hash,
    type: type || 'email',
  });
}
```

No additional frontend configuration is needed once templates are updated.

## Best Practices

1. **Keep templates consistent** - Use same token hash format across all templates
2. **Test before production** - Send test emails to verify templates work
3. **Personalize emails** - Add your brand logo and branding to templates
4. **Monitor deliverability** - Track bounce rates and adjust SMTP as needed
5. **Document expiry** - Mention link expiration in email (typically 24 hours)

## References

- [Supabase Email Templates](https://supabase.com/docs/guides/auth/auth-email-templates)
- [Magic Links & OTP](https://supabase.com/docs/guides/auth/auth-otp)
- [PKCE Flow](https://supabase.com/docs/guides/auth#pkce-flow)
- [Token Hash Reference](https://supabase.com/docs/reference/auth/email-templates)
