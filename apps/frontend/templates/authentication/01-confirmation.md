# Email Confirmation Template

Sent when a user signs up for an account.

## Subject
```
Confirm your email address
```

## Plain Text
```
Hello {{ .Email }},

Thank you for signing up! Please confirm your email address by clicking the link below:

{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=signup

This link expires in 24 hours.

If you didn't create this account, you can safely ignore this email.

Best regards,
METAR to IWXXM Team
```

## HTML
```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
      .container { max-width: 600px; margin: 0 auto; padding: 20px; }
      .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 20px; border-radius: 4px 4px 0 0; }
      .content { background: #f9f9f9; padding: 20px; border: 1px solid #eee; }
      .button { background-color: #667eea; color: white; padding: 12px 24px; 
               text-decoration: none; border-radius: 4px; display: inline-block; 
               margin: 20px 0; }
      .footer { font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; 
               border-top: 1px solid #eee; }
      .warning { color: #d32f2f; font-size: 14px; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>Welcome to METAR to IWXXM</h1>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <p>Thank you for signing up! Your account is almost ready. Please confirm your email 
           address to get started.</p>
        
        <a href="{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=signup" 
           class="button">
          Confirm Email
        </a>
        
        <p>Or copy this link into your browser:</p>
        <p style="word-break: break-all; font-size: 12px; color: #666;">
          {{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=signup
        </p>
        
        <p class="warning">⚠️ This link expires in 24 hours.</p>
        
        <p>If you didn't create this account, you can safely ignore this email.</p>
      </div>
      <div class="footer">
        <p>© 2024 METAR to IWXXM. All rights reserved.</p>
      </div>
    </div>
  </body>
</html>
```

## Usage Notes

- **Template Type**: Signup confirmation in Supabase
- **When Sent**: Immediately after user registration
- **Token Expiration**: 24 hours (change in Supabase settings)
- **Redirect URL**: Must be configured in Supabase Auth → Redirect URLs
- **Rate Limit**: 2 emails/hour per Supabase email service

## Customization Tips

1. **Add company logo**: Use absolute URL (HTTPS required)
   ```html
   <img src="https://yourapp.com/logo.png" alt="Logo" style="max-width: 200px;">
   ```

2. **Change button color**: Modify `background-color` in `.button` style
   ```css
   background-color: #28a745;  /* Green */
   ```

3. **Add company details**: Include in footer
   ```html
   <p>Support: support@yourapp.com</p>
   ```

## Testing

1. Invite a test user in Supabase
2. Check email (including spam folder)
3. Click confirmation link
4. Verify user email status in Supabase Auth → Users

## Related Templates

- 02-magic-link.md - Passwordless sign-in
- 04-welcome.md - Welcome email after confirmation
