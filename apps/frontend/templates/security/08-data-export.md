# Data Export Confirmation Template

Sent when user requests or completes a data export.

## Subject
```
Your data export is ready
```

## Plain Text
```
Hello {{ .Email }},

Your data export has been prepared and is ready for download.

Export Contents:
- User profile information
- Account settings and preferences  
- Activity logs
- All saved conversions

Download: {{ .SiteURL }}/account/data-export/{{ .Data.exportId }}/download

This link expires in 7 days.

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
      .button { background-color: #4caf50; color: white; padding: 12px 24px; 
               text-decoration: none; border-radius: 4px; display: inline-block; 
               margin: 20px 0; font-weight: bold; }
      .footer { font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; 
               border-top: 1px solid #eee; }
      .expire-warning { background: #fff3cd; padding: 12px; border-left: 4px solid #ffc107; 
                       margin: 15px 0; }
      .file-item { background: white; padding: 10px; margin: 8px 0; 
                  border: 1px solid #ddd; border-radius: 4px; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>📦 Data Export Ready</h1>
        <p>Your personal data export is prepared for download</p>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <div class="success-box">
          <p><strong>✓ Your data export has been prepared and is ready for download!</strong></p>
          <p>All your personal information has been compiled into a single file 
             for your records.</p>
        </div>
        
        <h2 style="color: #667eea;">Export Details</h2>
        
        <div class="details-box">
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold; width: 40%;">Export ID:</td>
              <td style="padding: 8px;">{{ .Data.exportId }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Requested:</td>
              <td style="padding: 8px;">{{ .Data.requestDate }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">File Size:</td>
              <td style="padding: 8px;">{{ .Data.fileSize }}</td>
            </tr>
            <tr>
              <td style="padding: 8px; font-weight: bold;">Format:</td>
              <td style="padding: 8px;">JSON (portable format)</td>
            </tr>
          </table>
        </div>
        
        <h2 style="color: #667eea;">What's Included</h2>
        
        <div class="file-item">
          <strong>📄 profile.json</strong>
          <p style="margin: 5px 0; font-size: 14px;">Your account profile information</p>
        </div>
        
        <div class="file-item">
          <strong>⚙️ settings.json</strong>
          <p style="margin: 5px 0; font-size: 14px;">Account preferences and settings</p>
        </div>
        
        <div class="file-item">
          <strong>📊 activity.json</strong>
          <p style="margin: 5px 0; font-size: 14px;">Login and activity history</p>
        </div>
        
        <div class="file-item">
          <strong>🔄 conversions.json</strong>
          <p style="margin: 5px 0; font-size: 14px;">All saved METAR conversions</p>
        </div>
        
        <h2 style="color: #667eea;">Download Your Data</h2>
        
        <a href="{{ .SiteURL }}/account/data-export/{{ .Data.exportId }}/download" class="button">
          Download Data Export
        </a>
        
        <p style="margin-top: 15px; font-size: 14px; color: #666;">
          <strong>Or use this link:</strong><br>
          <code style="background: #f0f0f0; padding: 5px; border-radius: 3px; 
                       word-break: break-all;">
            {{ .SiteURL }}/account/data-export/{{ .Data.exportId }}/download
          </code>
        </p>
        
        <div class="expire-warning">
          <strong>⏱️ Important:</strong> This download link expires in 7 days 
          ({{ .Data.expiryDate }}). Download your data before it expires.
        </div>
        
        <h2 style="color: #667eea; margin-top: 25px;">Privacy & Security</h2>
        
        <ul>
          <li>This file contains your personal data - store it securely</li>
          <li>The download link is unique and secure (one-time use)</li>
          <li>Only you can access this export</li>
          <li>Consider encrypting the file before storing</li>
          <li>Delete this file when no longer needed</li>
        </ul>
        
        <h2 style="color: #667eea;">Didn't Request This?</h2>
        
        <p>If you didn't request a data export, contact us immediately:</p>
        <a href="mailto:support@yourapp.com" style="color: #667eea;">Contact Support</a>
        
        <p style="margin-top: 20px; font-size: 14px; color: #666;">
          <strong>Need Help?</strong> See our 
          <a href="{{ .SiteURL }}/docs/data-export" style="color: #667eea;">data export guide</a> 
          for instructions.
        </p>
      </div>
      <div class="footer">
        <p>© 2024 METAR to IWXXM. All rights reserved.</p>
        <p style="margin-top: 10px;">
          <a href="{{ .SiteURL }}/account/settings" style="color: #667eea;">Account Settings</a> | 
          <a href="{{ .SiteURL }}/privacy" style="color: #667eea;">Privacy Policy</a> | 
          <a href="mailto:support@yourapp.com" style="color: #667eea;">Contact Support</a>
        </p>
      </div>
    </div>
  </body>
</html>
```

## Usage Notes

- **Template Type**: Confirmation email (data request)
- **When Sent**: When data export is complete and ready
- **Includes**: Export ID, file size, download link
- **Expiration**: Download link expires in 7 days
- **Manual Send**: From data export handler or backend

## Implementation

```typescript
// Send after export is generated
async function sendDataExportReady(userId: string, email: string, exportId: string) {
  const exportFile = await getExportFile(exportId);
  
  await supabaseAdmin.functions.invoke('send-email', {
    body: {
      to: email,
      template: 'data-export',
      data: {
        exportId,
        requestDate: new Date().toLocaleDateString(),
        fileSize: formatFileSize(exportFile.size),
        expiryDate: new Date(Date.now() + 7 * 24 * 60 * 60000).toLocaleDateString(),
      }
    }
  });
}
```

## Data Export Workflow

1. User requests data export in account settings
2. Backend compiles all user data into JSON
3. Files are encrypted and stored securely
4. This email is sent with download link
5. User downloads within 7 days
6. Files auto-delete after 7 days (optional)

## Related Templates

- 03-permission-revoked.md - Permission changes
- 05-password-changed.md - Security changes
