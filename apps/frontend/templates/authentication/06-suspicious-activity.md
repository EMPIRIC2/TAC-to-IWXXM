# Suspicious Activity Alert Template

Sent when login activity appears unusual or from unexpected location.

## Subject
```
Unusual login activity on your account
```

## Plain Text
```
Hello {{ .Email }},

We detected an unusual login attempt on your account from an unfamiliar device or location.

Location: {{ .Data.location }}
Device: {{ .Data.deviceType }}
Time: {{ .Data.timestamp }}

If this was you, you can ignore this email. If not, please change your password immediately:

{{ .SiteURL }}/account/security

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
      .safe-note { background: #e8f5e9; padding: 12px; border-left: 4px solid #4caf50; 
                  margin: 15px 0; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>🔒 Unusual Login Activity</h1>
        <p>We detected a sign-in from an unfamiliar location or device</p>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <div class="alert-box">
          <p><strong>We detected an unusual login attempt on your account.</strong></p>
          <p>This could be a sign of unauthorized access. Please review the details below.</p>
        </div>
        
        <h2 style="color: #d32f2f;">Activity Details</h2>
        
        <div class="details-box">
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold; width: 40%;">Location:</td>
              <td style="padding: 8px;">{{ .Data.location }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Device Type:</td>
              <td style="padding: 8px;">{{ .Data.deviceType }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Browser:</td>
              <td style="padding: 8px;">{{ .Data.browser }}</td>
            </tr>
            <tr>
              <td style="padding: 8px; font-weight: bold;">Time:</td>
              <td style="padding: 8px;">{{ .Data.timestamp }} UTC</td>
            </tr>
          </table>
        </div>
        
        <h2 style="color: #d32f2f; margin-top: 25px;">Was This You?</h2>
        
        <div class="safe-note">
          <p><strong>✓ If this was you:</strong><br>
             Great! You can safely ignore this email. We'll learn this as a trusted device 
             and won't bother you about future logins from here.</p>
        </div>
        
        <h2 style="color: #d32f2f;">Quick Actions</h2>
        
        <a href="{{ .SiteURL }}/account/security?action=mark-safe" class="secondary-button">
          Mark as Trusted
        </a>
        
        <a href="{{ .SiteURL }}/account/security?action=review-sessions" class="secondary-button">
          Review Sessions
        </a>
        
        <h2 style="color: #d32f2f; margin-top: 25px;">⚠️ If This Wasn't You</h2>
        
        <p style="background: #ffebee; padding: 12px; border-radius: 4px;">
          <strong>Take these actions immediately:</strong>
        </p>
        
        <ol>
          <li><strong>Change your password</strong>
            <a href="{{ .SiteURL }}/account/password-reset" class="button">
              Change Password Now
            </a>
          </li>
          <li><strong>Review active sessions</strong>
            <a href="{{ .SiteURL }}/account/security">
              View All Active Sessions
            </a>
          </li>
          <li><strong>Enable additional security</strong>
            <ul>
              <li>Review connected apps</li>
              <li>Check email forwarding rules</li>
              <li>Update recovery email</li>
            </ul>
          </li>
          <li><strong>Contact support</strong>
            <a href="mailto:support@yourapp.com">Report the incident</a>
          </li>
        </ol>
        
        <h2 style="color: #667eea; margin-top: 25px;">Security Tips</h2>
        
        <ul>
          <li>Use strong, unique passwords (12+ characters)</li>
          <li>Don't reuse passwords across services</li>
          <li>Enable 2FA on your email account</li>
          <li>Review devices regularly in account settings</li>
          <li>Log out of sessions you don't recognize</li>
        </ul>
      </div>
      <div class="footer">
        <p>© 2024 METAR to IWXXM. All rights reserved.</p>
        <p style="margin-top: 10px;">
          <a href="{{ .SiteURL }}/security" style="color: #667eea;">Security Center</a> | 
          <a href="{{ .SiteURL }}/account/security" style="color: #667eea;">Account Security</a> | 
          <a href="mailto:support@yourapp.com" style="color: #667eea;">Contact Support</a>
        </p>
      </div>
    </div>
  </body>
</html>
```

## Usage Notes

- **Template Type**: Custom email (triggered by auth events)
- **When Sent**: When login from new device/location detected
- **Trigger Logic**: Geolocation change, new browser, new OS
- **Purpose**: Security alert and user verification
- **Manual Review**: Requires server-side tracking

## Implementation

Track logins and send alerts:

```typescript
// In your backend auth hook
export async function handleNewLoginActivity(
  userId: string,
  email: string,
  ipAddress: string
) {
  // Get geolocation from IP
  const location = await getLocationFromIP(ipAddress);
  const lastLogin = await getLastLoginLocation(userId);
  
  // Detect suspicious activity
  if (isUnusualLocation(location, lastLogin)) {
    // Send alert
    await supabaseAdmin.functions.invoke('send-email', {
      body: {
        to: email,
        template: 'suspicious-activity',
        data: {
          location: location.city + ', ' + location.country,
          deviceType: getDeviceType(userAgent),
          browser: getBrowserName(userAgent),
          timestamp: new Date().toISOString(),
        }
      }
    });
  }
}
```

## Customization Tips

1. **Add confidence score**:
   ```html
   <p><strong>Confidence:</strong> 85% likely suspicious</p>
   ```

2. **Include similar logins**:
   ```html
   <p>Last login from this location: 30 days ago</p>
   ```

3. **Add quick block option**:
   ```html
   <a href="{{ .SiteURL }}/account/security?action=block-device" class="button">
     Block This Device
   </a>
   ```

4. **Include recovery codes option**:
   ```html
   <p>Don't have access to your email? 
      <a href="{{ .SiteURL }}/account/recovery">Use recovery codes</a></p>
   ```

## Testing

1. Login with one device
2. Clear cookies/cache
3. Login from same account with different geolocation simulator
4. Should receive alert email
5. Test "Mark as Trusted" action
6. Verify no alert on next login from same location

## Related Templates

- 03-password-reset.md - Password reset
- 05-email-changed.md - Email change notification
- 06-account-locked.md - Account lock notice
