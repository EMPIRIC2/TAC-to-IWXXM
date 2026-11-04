# Supabase email templates customization guide

This guide explains how to customize Supabase email templates so they work with the
magic link (OTP) and password reset flows in this application.

**Supabase** is the auth and database platform. **OTP** means one-time password.
**Magic link** means a sign-in link sent by email. **PKCE** means Proof Key for Code
Exchange, an OAuth security flow.

## Overview

The application uses Supabase’s built-in email authentication with:

- **Magic link (OTP) authentication** for passwordless login and signup
- **Email verification** for new account confirmation
- **Password reset** for account recovery

Those flows need email templates that use token hash URLs.

## Prerequisites

- Access to your Supabase Dashboard
- Your frontend domain URL (for example, `http://localhost:5173` for development,
  `https://yourdomain.com` for production)

## Step 1: Configure Site URL

Before you customize templates, set your Site URL:

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

Those settings make email links redirect to your application.

## Step 2: Customize email templates

### Access email templates

1. Go to **Supabase Dashboard** → Select your project
2. Navigate to **Authentication** → **Email Templates**

### Template 1: Confirm Sign Up

Use this template for:

- Email verification during registration
- Magic link signup

**Find and replace this line:**
```
{{ .ConfirmationURL }}
```

**Replace with (recommended; matches FE `/auth/confirm`):**
```
{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=email
```

The app exchanges `token_hash` via `POST /auth/confirm` (GoTrue verify). Keep
**Confirm email** required (`mailer_autoconfirm` off) in production.

**Full example:**
```
Follow this link to confirm your sign up:

{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=email

(Or click the button below)

[Confirm Email]
```

### Template 2: Password Reset

Use this template when users request a password reset.

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

Use this template for passwordless login via magic link.

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

## How the flow works

### Token hash flow (PKCE)

1. The user starts signup, login, or password reset
2. Supabase generates a `token_hash` and sends an email with a special URL
3. The user clicks the link, which redirects to:
   `https://yourdomain.com?token_hash=...&type=email`
4. The frontend app (`AuthCallback.tsx`) detects `token_hash` in the URL
5. The app calls `supabase.auth.verifyOtp()` with the token hash
6. The session is established

**Benefits:**

- More secure than traditional callback URLs
- Works with server-side rendering (SSR)
- Compatible with the PKCE flow
- Limits token exposure in browser history

## Environment variables

Ensure these variables are set in `.env.local`:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-key-or-sb_publishable_xxx
```

## Testing email templates

### Local development

1. Run Supabase locally or use the hosted dashboard
2. Use **Mailpit** (included with Supabase CLI):
   ```bash
   supabase status
   ```
   Copy the **Mailpit** URL and open it in your browser
3. Perform a registration or password reset action
4. Check Mailpit for the email with your custom template

### Production

- Supabase’s default email service has a **2 emails/hour rate limit**
- For production, configure custom SMTP:
  - Go to **Settings** → **Email**
  - Add your SMTP provider (SendGrid, Mailgun, Twilio SendGrid, and so on)

## Troubleshooting

### Emails not received

- Check **Supabase Dashboard** → **Auth** → **Users** for signup events
- Verify **Site URL** matches your current domain
- Check the email spam or junk folder
- For local development, ensure **Mailpit** is running

### Token hash not working

- Ensure the URL template uses `{{ .TokenHash }}` (not `{{ .Token }}`)
- Verify the `type=email` or `type=recovery` parameter is included
- Check the browser console for errors in `AuthCallback.tsx`

### Redirect loop

- Verify **Redirect URLs** in Supabase match your app’s callback route
- Ensure `window.location.origin` in the frontend is configured correctly
- Check that `AuthCallback.tsx` detects and processes the token hash

## Frontend handling

The frontend handles token hash URLs in `AuthCallback.tsx`:

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

No extra frontend configuration is needed after you update the templates.

## Practices

1. **Keep templates consistent** — Use the same token hash format across all templates
2. **Test before production** — Send test emails to verify the templates work
3. **Personalize emails** — Add your brand logo and branding to templates
4. **Monitor deliverability** — Track bounce rates and adjust SMTP as needed
5. **Document expiry** — Mention link expiration in the email (typically 24 hours)

## References

- [Supabase Email Templates](https://supabase.com/docs/guides/auth/auth-email-templates)
- [Magic Links & OTP](https://supabase.com/docs/guides/auth/auth-otp)
- [PKCE Flow](https://supabase.com/docs/guides/auth#pkce-flow)
- [Token Hash Reference](https://supabase.com/docs/reference/auth/email-templates)
