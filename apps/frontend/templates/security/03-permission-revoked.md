# Permission Revoked Notification Template

Sent when user's access permissions are revoked or downgraded.

## Subject
```
Your account permissions have been changed
```

## Plain Text
```
Hello {{ .Email }},

Your permissions on the account have been changed by an administrator.

Changed By: {{ .Data.changedBy }}
Reason: {{ .Data.reason }}
Effective: Immediately

If you have questions about this change, contact the account administrator.

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
      .header { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); 
                color: white; padding: 20px; border-radius: 4px 4px 0 0; }
      .content { background: #f9f9f9; padding: 20px; border: 1px solid #eee; }
      .alert-box { background: #ffe3e3; padding: 15px; border: 2px solid #ff6b6b; 
                  border-radius: 4px; margin: 15px 0; }
      .details-box { background: white; padding: 15px; border: 1px solid #ddd; 
                    border-radius: 4px; margin: 15px 0; }
      .button { background-color: #2196f3; color: white; padding: 12px 24px; 
               text-decoration: none; border-radius: 4px; display: inline-block; 
               margin: 20px 0; font-weight: bold; }
      .footer { font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; 
               border-top: 1px solid #eee; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>⚠️ Permissions Changed</h1>
        <p>Your account access level has been modified</p>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <div class="alert-box">
          <p><strong>Your account permissions have been changed by an administrator.</strong></p>
          <p>This change is effective immediately and may affect your access to 
             certain features and resources.</p>
        </div>
        
        <h2 style="color: #ff6b6b;">Change Details</h2>
        
        <div class="details-box">
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold; width: 40%;">Changed By:</td>
              <td style="padding: 8px;">{{ .Data.changedBy }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Reason:</td>
              <td style="padding: 8px;">{{ .Data.reason }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Previous Role:</td>
              <td style="padding: 8px;">{{ .Data.previousRole }}</td>
            </tr>
            <tr>
              <td style="padding: 8px; font-weight: bold;">New Role:</td>
              <td style="padding: 8px;"><strong style="color: #ff6b6b;">{{ .Data.newRole }}</strong></td>
            </tr>
          </table>
        </div>
        
        <h2 style="color: #ff6b6b;">What Changed?</h2>
        
        <p><strong>Previous Permissions:</strong></p>
        <ul>
          <li>{{ .Data.previousPermission1 }}</li>
          <li>{{ .Data.previousPermission2 }}</li>
          <li>{{ .Data.previousPermission3 }}</li>
        </ul>
        
        <p><strong>Current Permissions:</strong></p>
        <ul>
          <li>{{ .Data.currentPermission1 }}</li>
          <li>{{ .Data.currentPermission2 }}</li>
        </ul>
        
        <h2 style="color: #ff6b6b;">What You Can Do</h2>
        
        <ul>
          <li>Review your new permissions in account settings</li>
          <li>Contact the account administrator if you have questions</li>
          <li>Request permission restoration if needed</li>
          <li>Review activity log to understand what changed</li>
        </ul>
        
        <a href="{{ .SiteURL }}/account/permissions" class="button">
          View My Permissions
        </a>
        
        <p style="background: #e3f2fd; padding: 12px; border-radius: 4px; margin-top: 15px;">
          <strong>Need Help?</strong> Contact your account administrator: {{ .Data.adminEmail }}
        </p>
      </div>
      <div class="footer">
        <p>© 2024 METAR to IWXXM. All rights reserved.</p>
        <p style="margin-top: 10px;">
          <a href="{{ .SiteURL }}/account/settings" style="color: #667eea;">Account Settings</a> | 
          <a href="mailto:support@yourapp.com" style="color: #667eea;">Contact Support</a>
        </p>
      </div>
    </div>
  </body>
</html>
```

## Usage Notes

- **Template Type**: Custom notification (admin action)
- **When Sent**: When admin changes user permissions
- **Includes**: Previous role, new role, change reason
- **Action**: User should review new permissions
- **Manual Send**: From admin dashboard or backend

## Related Templates

- 03-session-timeout.md - Session expiration warning
- 08-data-export.md - Data export confirmation
