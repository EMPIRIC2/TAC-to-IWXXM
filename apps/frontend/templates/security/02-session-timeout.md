# Session Timeout Warning Template

Sent before user's session expires due to inactivity.

## Subject
```
Your session is about to expire
```

## Plain Text
```
Hello {{ .Email }},

Your session will expire in 15 minutes due to inactivity. Click the link below 
to extend your session and keep working.

{{ .SiteURL }}/account/extend-session

If you don't take action, you'll be automatically logged out.

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
      .header { background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); 
                color: white; padding: 20px; border-radius: 4px 4px 0 0; }
      .content { background: #f9f9f9; padding: 20px; border: 1px solid #eee; }
      .warning-box { background: #fff3cd; padding: 15px; border: 2px solid #ff9800; 
                    border-radius: 4px; margin: 15px 0; }
      .button { background-color: #ff9800; color: white; padding: 12px 24px; 
               text-decoration: none; border-radius: 4px; display: inline-block; 
               margin: 20px 0; font-weight: bold; }
      .footer { font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; 
               border-top: 1px solid #eee; }
      .timer { background: white; padding: 15px; border: 2px dashed #ff9800; 
              border-radius: 4px; margin: 15px 0; text-align: center; 
              font-size: 18px; font-weight: bold; color: #f57c00; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>⏱️ Session Timeout Warning</h1>
        <p>Your session is about to expire</p>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <div class="warning-box">
          <p><strong>Your session will expire in 15 minutes.</strong></p>
          <p>We haven't detected any activity on your account recently. 
             If you're still working, click the button below to extend your session.</p>
        </div>
        
        <div class="timer">
          ⏱️ Time Remaining: {{ .Data.minutesRemaining }} minutes
        </div>
        
        <a href="{{ .SiteURL }}/account/extend-session" class="button">
          Extend My Session
        </a>
        
        <h2 style="color: #f57c00;">Why Am I Getting This?</h2>
        
        <p>For security reasons, sessions automatically expire after a period of inactivity. 
           This helps protect your account from unauthorized access if you step away 
           from your computer.</p>
        
        <h2 style="color: #f57c00;">What Happens if I Don't Act?</h2>
        
        <ul>
          <li>Your session will expire automatically</li>
          <li>You'll be logged out of the application</li>
          <li>Any unsaved work will be lost</li>
          <li>You'll need to log in again to continue</li>
        </ul>
        
        <h2 style="color: #f57c00;">How to Avoid This</h2>
        
        <ul>
          <li>Keep your browser window active while working</li>
          <li>Click on the application regularly to refresh your session</li>
          <li>Use "Remember me" on login for longer sessions</li>
          <li>Adjust session timeout in account settings</li>
        </ul>
        
        <p><strong>Session details:</strong></p>
        <ul>
          <li>Session ID: {{ .Data.sessionId }}</li>
          <li>Started: {{ .Data.sessionStart }}</li>
          <li>Current time: {{ .Data.currentTime }}</li>
        </ul>
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

- **Template Type**: Inactivity warning (optional)
- **When Sent**: 15 minutes before session expires
- **Requires**: Server-side session tracking
- **Optional**: May not send by default
- **Time Zone**: Use user's local timezone in timestamp

## Related Templates

- 06-account-locked.md - Account temporarily locked
- 07-suspicious-activity.md - Suspicious login alert
