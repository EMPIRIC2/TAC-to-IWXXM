# Password Reset Template

Sent when a user requests to reset their password.

## Subject
```
Reset your password
```

## Plain Text
```
Hello {{ .Email }},

We received a request to reset your password. Click the link below to proceed:

{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=recovery

This link expires in 1 hour.

If you didn't request this reset, you can safely ignore this email.

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
      .button { background-color: #d32f2f; color: white; padding: 12px 24px; 
               text-decoration: none; border-radius: 4px; display: inline-block; 
               margin: 20px 0; font-weight: bold; }
      .footer { font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; 
               border-top: 1px solid #eee; }
      .warning { background: #ffebee; padding: 12px; border-left: 4px solid #d32f2f; 
                margin: 15px 0; color: #c62828; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>Reset Your Password</h1>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <p>We received a request to reset the password for your account. 
           Click the button below to create a new password:</p>
        
        <a href="{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=recovery" 
           class="button">
          Reset Password
        </a>
        
        <p>Or copy this link into your browser:</p>
        <p style="word-break: break-all; font-size: 12px; color: #666;">
          {{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=recovery
        </p>
        
        <div class="warning">
          <strong>⚠️ Important Security Notice</strong><br>
          This link expires in 1 hour. If you didn't request this password reset, 
          please ignore this email.
        </div>
        
        <p><strong>Password Reset Guidelines:</strong></p>
        <ul>
          <li>Use at least 8 characters</li>
          <li>Mix uppercase and lowercase letters</li>
          <li>Include numbers and special characters</li>
          <li>Don't reuse a password you've used before</li>
        </ul>
      </div>
      <div class="footer">
        <p>© 2024 METAR to IWXXM. All rights reserved.</p>
        <p style="margin-top: 10px;">If you need help, contact support@yourapp.com</p>
      </div>
    </div>
  </body>
</html>
```

## Usage Notes

- **Template Type**: Password Recovery in Supabase
- **When Sent**: When user requests password reset on login page
- **Token Expiration**: 1 hour (configurable in Supabase)
- **Next Step**: User creates new password via callback link
- **Security**: Email verification (user must access email account)

## Implementation in Your App

In `frontend/src/app/components/auth/PasswordReset.tsx`:
```typescript
// Step 1: Request password reset
const handleResetRequest = async (email: string) => {
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/auth/callback`,
  });
  if (error) toast.error(error.message);
  else {
    toast.success('Password reset link sent! Check your email.');
    setStep('reset');
  }
};

// Step 2: Update password after clicking link
const handlePasswordUpdate = async (newPassword: string) => {
  const { error } = await supabase.auth.updateUser({ password: newPassword });
  if (error) toast.error(error.message);
  else {
    toast.success('Password updated successfully!');
    navigate('/login');
  }
};
```

## Customization Tips

1. **Adjust expiration time**:
   - More security: 30 minutes
   - More convenience: 2 hours
   - Change in Supabase Auth settings

2. **Add recovery codes section**:
   ```html
   <p><strong>Don't have access to your email?</strong><br>
      Contact support@yourapp.com with verification information.</p>
   ```

3. **Add password requirements details**:
   ```html
   <p>Your new password must be at least 8 characters and should include 
      uppercase, lowercase, and numbers for best security.</p>
   ```

## Security Best Practices

- ✅ Reset link expires after 1 hour
- ✅ Each link can only be used once
- ✅ User must have email access to reset
- ✅ New password doesn't take effect until confirmed
- ✅ Uses `{{ .TokenHash }}` for secure token exchange

## Two-Step Password Reset Flow

1. **Email Verification Step**: User receives this email with reset link
2. **Password Update Step**: User clicks link, enters new password in your app
3. **Confirmation**: New password is saved, user is logged out of all sessions
4. **Notification**: Consider sending "Password Changed" confirmation email (05-password-changed.md)

## Testing

1. Go to Login page
2. Click "Forgot password?"
3. Enter email address
4. Check email (spam folder)
5. Click reset link
6. Enter new password
7. Verify login with new password

## Related Templates

- 01-confirmation.md - Account confirmation
- 05-password-changed.md - Password change notification
- 06-account-locked.md - Account security lock
