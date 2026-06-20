# Account Locked Notification Template

Sent when account is temporarily locked due to multiple failed login attempts.

## Subject
```
Your account has been temporarily locked
```

## Plain Text
```
Hello {{ .Email }},

Your account has been temporarily locked for security reasons after multiple 
failed login attempts.

Lock Reason: {{ .Data.reason }}
Locked At: {{ .Data.lockedTime }}
Unlock Time: In {{ .Data.minutesRemaining }} minutes ({{ .Data.unlockTime }})

Verify this was you, or reset your password:
{{ .SiteURL }}/account/unlock

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
      .header { background: linear-gradient(135deg, #d32f2f 0%, #c62828 100%); 
                color: white; padding: 20px; border-radius: 4px 4px 0 0; }
      .content { background: #f9f9f9; padding: 20px; border: 1px solid #eee; }
      .alert-box { background: #ffebee; padding: 15px; border: 2px solid #d32f2f; 
                  border-radius: 4px; margin: 15px 0; }
      .details-box { background: white; padding: 15px; border: 1px solid #ddd; 
                    border-radius: 4px; margin: 15px 0; }
      .button { background-color: #d32f2f; color: white; padding: 12px 24px; 
               text-decoration: none; border-radius: 4px; display: inline-block; 
               margin: 20px 0; font-weight: bold; }
      .secondary-button { background-color: #2196f3; color: white; padding: 12px 24px; 
                         text-decoration: none; border-radius: 4px; display: inline-block; 
                         margin: 10px 10px 10px 0; font-weight: bold; }
      .footer { font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; 
               border-top: 1px solid #eee; }
      .timer { background: white; padding: 15px; border: 2px dashed #d32f2f; 
              border-radius: 4px; margin: 15px 0; text-align: center; 
              font-size: 18px; font-weight: bold; color: #d32f2f; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>🔒 Account Locked</h1>
        <p>Temporary security lock due to failed login attempts</p>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <div class="alert-box">
          <p><strong>Your account has been temporarily locked for security.</strong></p>
          <p>This happened after multiple failed login attempts. The lock is temporary 
             and will automatically expire in {{ .Data.minutesRemaining }} minutes.</p>
        </div>
        
        <div class="timer">
          🔒 Locked | Expires: {{ .Data.unlockTime }} UTC
        </div>
        
        <h2 style="color: #d32f2f;">Lock Details</h2>
        
        <div class="details-box">
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold; width: 40%;">Reason:</td>
              <td style="padding: 8px;">{{ .Data.reason }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Locked At:</td>
              <td style="padding: 8px;">{{ .Data.lockedTime }} UTC</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Will Unlock:</td>
              <td style="padding: 8px;">{{ .Data.unlockTime }} UTC</td>
            </tr>
            <tr>
              <td style="padding: 8px; font-weight: bold;">Failed Attempts:</td>
              <td style="padding: 8px;">{{ .Data.failedAttempts }} attempts</td>
            </tr>
          </table>
        </div>
        
        <h2 style="color: #d32f2f;">What You Can Do</h2>
        
        <p><strong>Option 1: Unlock Immediately</strong></p>
        <p>Verify your identity to unlock your account now:</p>
        <a href="{{ .SiteURL }}/account/unlock" class="button">
          Verify & Unlock Account
        </a>
        
        <p style="margin-top: 20px;"><strong>Option 2: Reset Password</strong></p>
        <p>If you forgot your password or suspect unauthorized access:</p>
        <a href="{{ .SiteURL }}/account/password-reset" class="secondary-button">
          Reset Password
        </a>
        
        <h2 style="color: #d32f2f; margin-top: 25px;">Is This Suspicious?</h2>
        
        <p style="background: #fff3cd; padding: 12px; border-radius: 4px;">
          <strong>If you didn't attempt to log in:</strong>
        </p>
        
        <ol>
          <li>Someone may be trying to break into your account</li>
          <li>Reset your password immediately</li>
          <li>Review connected applications</li>
          <li>Check account activity log</li>
          <li>Contact support if needed</li>
        </ol>
        
        <h2 style="color: #d32f2f;">Security Recommendations</h2>
        
        <ul>
          <li>Use a strong, unique password (12+ characters)</li>
          <li>Avoid passwords found in data breaches</li>
          <li>Enable multi-factor authentication (MFA)</li>
          <li>Review recent login activity regularly</li>
          <li>Keep your email account secure</li>
        </ul>
        
        <a href="{{ .SiteURL }}/account/security" class="secondary-button">
          Review Account Security
        </a>
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

- **Template Type**: Security alert (failed login attempts)
- **When Sent**: After 5+ consecutive failed login attempts
- **Lock Duration**: 30 minutes (configurable)
- **Unlock Options**: Auto-unlock or manual verification
- **Manual Send**: From failed login handler

## Implementation

```typescript
// Track failed login attempts
async function handleFailedLogin(email: string, ipAddress: string) {
  const attempts = await incrementFailedAttempts(email, ipAddress);
  
  if (attempts >= 5) {
    // Lock account
    await lockAccount(email, 30); // 30 minute lock
    
    // Send notification
    await supabaseAdmin.functions.invoke('send-email', {
      body: {
        to: email,
        template: 'account-locked',
        data: {
          reason: `${attempts} failed login attempts`,
          lockedTime: new Date().toISOString(),
          unlockTime: new Date(Date.now() + 30 * 60000).toISOString(),
          minutesRemaining: 30,
          failedAttempts: attempts,
        }
      }
    });
  }
}
```

## Related Templates

- 03-password-reset.md - Password reset
- 06-suspicious-activity.md - Suspicious login
- 07-ip-mismatch.md - Unusual location
