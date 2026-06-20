# Email Templates

This directory contains customizable email templates for your METAR to IWXXM application.

## Template Categories

### Authentication (6 templates)
User authentication and verification emails:
- `01-confirmation.md` - Email confirmation for new accounts
- `02-magic-link.md` - Passwordless sign-in link
- `03-password-reset.md` - Password reset request
- `04-welcome.md` - Welcome email after signup
- `05-email-changed.md` - Email address change confirmation
- `06-suspicious-activity.md` - Suspicious login attempt alert

### Security (8 templates)
Security notifications and alerts:
- `01-mfa-enabled.md` - Multi-factor authentication enabled
- `02-session-timeout.md` - Session timeout warning
- `03-permission-revoked.md` - Access permission revoked
- `04-new-device.md` - Login from new device
- `05-password-changed.md` - Password change confirmation
- `06-account-locked.md` - Account temporarily locked
- `07-ip-mismatch.md` - Unusual location login attempt
- `08-data-export.md` - Data export request confirmation

## Quick Reference

### Template Variables
All templates support Supabase predefined variables:
- `{{ .TokenHash }}` - Secure token for verification links
- `{{ .SiteURL }}` - Your application's base URL
- `{{ .Email }}` - User's email address
- `{{ .Data }}` - Custom JSON data from your app

See `VARIABLES.md` for complete documentation.

## Customization

1. Open the template file you want to customize
2. Update the subject, body, and HTML content
3. Test in development with `npm run test:templates` (if available)
4. Deploy to Supabase:
   - Go to Auth → Email Templates
   - Click "Edit" on the template type
   - Copy/paste your custom content
   - Save and send test email

## Security Best Practices

- Never expose tokens in plain links
- Always use `{{ .TokenHash }}` for secure links
- Include redirect URLs as query parameters
- Set appropriate token expiration in Supabase settings
- Review `SECURITY_FIXES.md` for RLS policy recommendations

## See Also

- [Complete Supabase Implementation Guide](../SUPABASE_AUTH_IMPLEMENTATION.md)
- [Email Template Variables Reference](VARIABLES.md)
- [Security Linter Fixes](SECURITY_FIXES.md)
