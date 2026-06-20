# Magic Link Sign-In Template

Sent when a user requests a passwordless sign-in link.

## Subject
```
Your login link for METAR to IWXXM
```

## Plain Text
```
Hello {{ .Email }},

Click the link below to sign in to your account:

{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=magiclink

This link expires in 15 minutes.

If you didn't request this link, you can safely ignore this email.

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
               margin: 20px 0; font-weight: bold; }
      .footer { font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; 
               border-top: 1px solid #eee; }
      .security { background: #fff3cd; padding: 12px; border-left: 4px solid #ffc107; 
                 margin: 15px 0; }
      .code-style { font-family: monospace; background: #f0f0f0; padding: 2px 6px; 
                   border-radius: 3px; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>Sign In to METAR to IWXXM</h1>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <p>Click the button below to sign in to your account:</p>
        
        <a href="{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=magiclink" 
           class="button">
          Sign In to My Account
        </a>
        
        <p>Or copy this link into your browser:</p>
        <p style="word-break: break-all; font-size: 12px; color: #666;">
          {{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=magiclink
        </p>
        
        <div class="security">
          <strong>🔒 Security Note:</strong> This link expires in 15 minutes and can only 
          be used once. If you didn't request this link, please delete this email.
        </div>
        
        <p><strong>Why did you get this email?</strong><br>
           You (or someone) requested a magic link sign-in for {{ .Email }}. Magic links 
           are a secure alternative to passwords.</p>
      </div>
      <div class="footer">
        <p>© 2024 METAR to IWXXM. All rights reserved.</p>
        <p style="margin-top: 10px;">Questions? Contact support@yourapp.com</p>
      </div>
    </div>
  </body>
</html>
```

## Usage Notes

- **Template Type**: Magic Link (OTP) in Supabase
- **When Sent**: When user clicks "Sign in with magic link" and provides email
- **Token Expiration**: 15 minutes (configurable in Supabase)
- **Security**: Each link can only be used once
- **Mobile Friendly**: Designed for click-through on mobile devices

## Implementation in Your App

In `frontend/src/app/components/auth/Login.tsx`:
```typescript
const handleMagicLink = async (email: string) => {
  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo: `${window.location.origin}/auth/callback`,
    },
  });
  if (error) toast.error(error.message);
  else toast.success('Check your email for the sign-in link!');
};
```

## Customization Tips

1. **Shorten expiration for higher security**:
   - Default: 15 minutes
   - Change in Supabase → Auth settings

2. **Add usage instructions**:
   ```html
   <ol>
     <li>Click the sign-in button above</li>
     <li>You'll be automatically logged in</li>
     <li>No password needed!</li>
   </ol>
   ```

3. **Add FAQ section**:
   ```html
   <h3>How does magic link work?</h3>
   <p>Magic links provide a password-free way to sign in. When you click the link, 
      we verify your identity and log you in securely.</p>
   ```

## Security Best Practices

- ✅ Link is unique and disposable
- ✅ Expires after 15 minutes
- ✅ Only works once
- ✅ Uses `{{ .TokenHash }}` for security
- ✅ Delivered via email (user verification)

## Testing

1. Go to Login page
2. Enter email address
3. Click "Sign in with magic link"
4. Check email within 15 minutes
5. Click the link
6. Verify automatic login

## Related Templates

- 01-confirmation.md - Account confirmation email
- 03-password-reset.md - Password reset process
