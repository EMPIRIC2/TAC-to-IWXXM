# Password Changed Confirmation Template

Sent when user successfully changes their password.

## Subject
```
Your password has been changed
```

## Plain Text
```
Hello {{ .Email }},

Your password has been successfully changed.

If you didn't make this change, please reset your password immediately at:
{{ .SiteURL }}/account/password-reset

All other sessions have been logged out for security.

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
      .success-box { background: #e8f5e9; padding: 15px; border: 2px solid #4caf50; 
                    border-radius: 4px; margin: 15px 0; }
      .details-box { background: white; padding: 15px; border: 1px solid #ddd; 
                    border-radius: 4px; margin: 15px 0; }
      .button { background-color: #2196f3; color: white; padding: 12px 24px; 
               text-decoration: none; border-radius: 4px; display: inline-block; 
               margin: 20px 0; font-weight: bold; }
      .footer { font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; 
               border-top: 1px solid #eee; }
      .warning { background: #fff3cd; padding: 12px; border-left: 4px solid #ffc107; 
                margin: 15px 0; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>✓ Password Changed</h1>
        <p>Your account security has been updated</p>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <div class="success-box">
          <p><strong>✓ Your password has been successfully changed.</strong></p>
          <p>Your account is now more secure. All other sessions have been 
             automatically logged out as a security measure.</p>
        </div>
        
        <h2 style="color: #667eea;">Change Details</h2>
        
        <div class="details-box">
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold; width: 40%;">Changed:</td>
              <td style="padding: 8px;">Today at {{ .Data.changeTime }} UTC</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Method:</td>
              <td style="padding: 8px;">{{ .Data.method }}</td>
            </tr>
            <tr>
              <td style="padding: 8px; font-weight: bold;">Sessions Ended:</td>
              <td style="padding: 8px;">{{ .Data.sessionsEnded }} (except current)</td>
            </tr>
          </table>
        </div>
        
        <div class="warning">
          <strong>⚠️ Important:</strong> All your other active sessions have been 
          automatically logged out. You'll need to log in again on those devices.
        </div>
        
        <h2 style="color: #667eea;">If You Didn't Change Your Password</h2>
        
        <p><strong style="color: #d32f2f;">Your account may be compromised!</strong></p>
        
        <p>If you didn't make this change, take action immediately:</p>
        
        <ol>
          <li><a href="{{ .SiteURL }}/account/password-reset">Reset your password again</a></li>
          <li><a href="{{ .SiteURL }}/account/security">Review your account security</a></li>
          <li>Check for unauthorized sessions</li>
          <li>Review connected applications</li>
          <li><a href="mailto:support@yourapp.com">Contact support</a> if needed</li>
        </ol>
        
        <h2 style="color: #667eea;">Password Security Tips</h2>
        
        <ul>
          <li>Use at least 12 characters</li>
          <li>Mix uppercase, lowercase, numbers, and symbols</li>
          <li>Avoid personal information or common words</li>
          <li>Never reuse passwords</li>
          <li>Change password every 90 days</li>
          <li>Consider using a password manager</li>
        </ul>
        
        <a href="{{ .SiteURL }}/account/security" class="button">
          Review Account Security
        </a>
        
        <p style="margin-top: 20px; font-size: 14px; color: #666;">
          <strong>Need to log in again?</strong> Just use your email and your new password.
        </p>
      </div>
      <div class="footer">
        <p>© 2024 METAR to IWXXM. All rights reserved.</p>
        <p style="margin-top: 10px;">
          <a href="{{ .SiteURL }}/security" style="color: #667eea;">Security Center</a> | 
          <a href="mailto:support@yourapp.com" style="color: #667eea;">Contact Support</a>
        </p>
      </div>
    </div>
  </body>
</html>
```

## Usage Notes

- **Template Type**: Confirmation email (security event)
- **When Sent**: Immediately after password change
- **Includes**: Change timestamp, number of sessions ended
- **Action**: Sessions auto-logout for security
- **Manual Send**: Not automated by Supabase (send from backend)

## Implementation

```typescript
// Send after password change
async function notifyPasswordChanged(userId: string, email: string) {
  const activeSessions = await getActiveSessions(userId);
  
  await supabaseAdmin.functions.invoke('send-email', {
    body: {
      to: email,
      template: 'password-changed',
      data: {
        changeTime: new Date().toISOString(),
        method: 'Account settings',
        sessionsEnded: activeSessions.length - 1,
      }
    }
  });
}
```

## Related Templates

- 03-password-reset.md - Password reset flow
- 05-email-changed.md - Email change notification
- 06-account-locked.md - Account lock notice
