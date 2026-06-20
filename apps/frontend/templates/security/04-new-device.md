# New Device Login Notification Template

Sent when user logs in from a new device or browser.

## Subject
```
New login from your account
```

## Plain Text
```
Hello {{ .Email }},

Someone just signed into your account from a new device.

Device: {{ .Data.deviceName }}
Location: {{ .Data.location }}
Time: {{ .Data.timestamp }}

If this was you, you can safely ignore this email. If not, review your 
account security immediately at:

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
      .header { background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%); 
                color: white; padding: 20px; border-radius: 4px 4px 0 0; }
      .content { background: #f9f9f9; padding: 20px; border: 1px solid #eee; }
      .info-box { background: #e3f2fd; padding: 15px; border: 2px solid #2196f3; 
                 border-radius: 4px; margin: 15px 0; }
      .details-box { background: white; padding: 15px; border: 1px solid #ddd; 
                    border-radius: 4px; margin: 15px 0; }
      .button { background-color: #4caf50; color: white; padding: 12px 24px; 
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
        <h1>ℹ️ New Device Login</h1>
        <p>Your account was accessed from a new device</p>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <div class="info-box">
          <p><strong>We detected a login to your account from a new device.</strong></p>
          <p>Review the details below and let us know if this was you.</p>
        </div>
        
        <h2 style="color: #2196f3;">Login Details</h2>
        
        <div class="details-box">
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold; width: 40%;">Device:</td>
              <td style="padding: 8px;">{{ .Data.deviceName }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Browser:</td>
              <td style="padding: 8px;">{{ .Data.browser }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Operating System:</td>
              <td style="padding: 8px;">{{ .Data.os }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Location:</td>
              <td style="padding: 8px;">{{ .Data.location }}</td>
            </tr>
            <tr>
              <td style="padding: 8px; font-weight: bold;">Time:</td>
              <td style="padding: 8px;">{{ .Data.timestamp }} UTC</td>
            </tr>
          </table>
        </div>
        
        <h2 style="color: #2196f3;">Was This You?</h2>
        
        <div class="safe-note">
          <p><strong>✓ If this was you:</strong><br>
             Great! You can mark this device as trusted so we won't bother you about 
             future logins from it.</p>
        </div>
        
        <a href="{{ .SiteURL }}/account/security?action=mark-device-safe" class="secondary-button">
          Mark Device as Trusted
        </a>
        
        <h2 style="color: #2196f3; margin-top: 25px;">If This Wasn't You</h2>
        
        <p style="background: #fff3cd; padding: 12px; border-radius: 4px;">
          <strong>Your account may have been compromised. Take action immediately:</strong>
        </p>
        
        <ol>
          <li><strong>Change your password</strong>
            <a href="{{ .SiteURL }}/account/password-reset" class="button">
              Change Password
            </a>
          </li>
          <li><strong>Review all active sessions</strong>
            <a href="{{ .SiteURL }}/account/security">
              View All Sessions
            </a>
          </li>
          <li><strong>Check for suspicious activity</strong></li>
          <li><strong>Contact support if needed</strong>
            <a href="mailto:support@yourapp.com" class="secondary-button">
              Contact Support
            </a>
          </li>
        </ol>
        
        <h2 style="color: #2196f3;">Device Management</h2>
        
        <p>You can manage your devices at any time:</p>
        <ul>
          <li>Review all active sessions</li>
          <li>Mark trusted devices</li>
          <li>Revoke access from compromised devices</li>
          <li>Set up automatic logout</li>
        </ul>
      </div>
      <div class="footer">
        <p>© 2024 METAR to IWXXM. All rights reserved.</p>
        <p style="margin-top: 10px;">
          <a href="{{ .SiteURL }}/account/security" style="color: #667eea;">Account Security</a> | 
          <a href="mailto:support@yourapp.com" style="color: #667eea;">Contact Support</a>
        </p>
      </div>
    </div>
  </body>
</html>
```

## Usage Notes

- **Template Type**: Informational notification (login event)
- **When Sent**: On first login from new device
- **Includes**: Device details, location, timestamp
- **Action**: Mark as trusted or review security
- **Manual Send**: From login handler or backend

## Related Templates

- 06-suspicious-activity.md - Suspicious login alert
- 07-ip-mismatch.md - Unusual location warning
