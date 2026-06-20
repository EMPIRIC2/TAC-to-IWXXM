# Email Changed Confirmation Template

Sent when a user successfully changes their email address on their account.

## Subject
```
Your email address has been changed
```

## Plain Text
```
Hello {{ .Email }},

This is a confirmation that your account email has been successfully changed to {{ .Email }}.

If you didn't make this change, please contact us immediately at support@yourapp.com

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
      .info-box { background: #e3f2fd; padding: 12px; border-left: 4px solid #2196f3; 
                 margin: 15px 0; }
      .details { background: white; padding: 15px; border: 1px solid #ddd; 
                border-radius: 4px; margin: 15px 0; font-family: monospace; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>✓ Email Address Changed</h1>
      </div>
      <div class="content">
        <p>Hello,</p>
        
        <p>This is a confirmation that your account email address has been 
           successfully changed.</p>
        
        <div class="details">
          <strong>New Email:</strong> {{ .Email }}<br>
          <strong>Changed:</strong> Today<br>
          <strong>Account Status:</strong> Active
        </div>
        
        <div class="info-box">
          <strong>ℹ️ What This Means:</strong><br>
          You will use {{ .Email }} for all future sign-ins and account communications.
          Your old email address will no longer be associated with this account.
        </div>
        
        <h2 style="color: #667eea; margin-top: 25px;">Need to Undo This Change?</h2>
        
        <p>If you didn't make this change, please take action immediately:</p>
        
        <ol>
          <li><a href="{{ .SiteURL }}/account/security">Review account security</a></li>
          <li>Change your password immediately</li>
          <li>Check for unauthorized access</li>
          <li><a href="{{ .SiteURL }}/contact-support">Contact support</a> if compromised</li>
        </ol>
        
        <a href="{{ .SiteURL }}/account/settings" class="button">
          Manage Account
        </a>
        
        <h2 style="color: #667eea; margin-top: 25px;">Security Tips</h2>
        
        <ul>
          <li>Keep your email account secure (enable 2FA on email provider)</li>
          <li>Never share your password or password reset links</li>
          <li>Log out from devices you don't recognize</li>
          <li>Review connected applications in account settings</li>
        </ul>
        
        <p style="background: #fff3cd; padding: 10px; border-radius: 4px; margin-top: 15px;">
          <strong>⚠️ Suspicious Activity?</strong> Contact us immediately at 
          support@yourapp.com with details about the unauthorized change.
        </p>
      </div>
      <div class="footer">
        <p>© 2024 METAR to IWXXM. All rights reserved.</p>
        <p style="margin-top: 10px;">
          <a href="{{ .SiteURL }}/account/settings" style="color: #667eea;">Account Settings</a> | 
          <a href="{{ .SiteURL }}/security" style="color: #667eea;">Security Center</a> | 
          <a href="mailto:support@yourapp.com" style="color: #667eea;">Contact Support</a>
        </p>
      </div>
    </div>
  </body>
</html>
```

## Usage Notes

- **Template Type**: Custom email (sent on email change)
- **When Sent**: After user updates email in account settings
- **Verification**: New email must be verified first
- **Old Email**: Email is also sent to old address for security
- **Action Required**: User may need to verify new email

## Implementation

Send after email change is confirmed:

```typescript
// Backend function to send on email change
export async function notifyEmailChanged(oldEmail: string, newEmail: string) {
  // Send to NEW email (this template)
  await supabaseAdmin.functions.invoke('send-email', {
    body: {
      to: newEmail,
      template: 'email-changed',
      data: { newEmail },
    }
  });
  
  // Also send to OLD email for security
  await supabaseAdmin.functions.invoke('send-email', {
    body: {
      to: oldEmail,
      template: 'email-changed-old',
      data: { newEmail },
    }
  });
}
```

## Customization Tips

1. **Add change timestamp**:
   ```html
   <p><strong>Changed At:</strong> {{ .Data.changedAt }} UTC</p>
   ```

2. **Include IP address for security audit**:
   ```html
   <p style="font-size: 12px; color: #999;">
     Changed from IP: {{ .Data.ipAddress }}
   </p>
   ```

3. **Add device information**:
   ```html
   <p><strong>Device:</strong> {{ .Data.deviceName }}</p>
   <p><strong>Browser:</strong> {{ .Data.browserName }}</p>
   ```

4. **Link to verify new email**:
   ```html
   <p>Didn't verify your new email yet? 
      <a href="{{ .SiteURL }}/verify-email">Verify now</a></p>
   ```

## Testing

1. Create account with email A
2. Login and go to account settings
3. Change email to email B
4. Verify new email (click link sent to B)
5. Check both A and B for notifications
6. Verify login works with email B

## Security Considerations

- ✅ Confirmation sent to BOTH old and new email
- ✅ User must verify new email first
- ✅ Old email gets security alert
- ✅ Consider requiring password re-entry
- ✅ Monitor for abuse patterns

## Related Templates

- 01-confirmation.md - Account confirmation
- 03-password-reset.md - Password reset
- 06-account-locked.md - Security lock
- 07-suspicious-activity.md - Suspicious login alert
