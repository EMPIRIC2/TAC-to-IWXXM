# MFA Enabled Confirmation Template

Sent when multi-factor authentication is enabled on an account.

## Subject
```
Multi-factor authentication has been enabled
```

## Plain Text
```
Hello {{ .Email }},

Multi-factor authentication (MFA) has been successfully enabled on your account.

Your login is now more secure. When you sign in, you'll need to provide both your 
password and an additional verification method.

If you didn't enable this, disable it immediately at:
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
      .header { background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%); 
                color: white; padding: 20px; border-radius: 4px 4px 0 0; }
      .content { background: #f9f9f9; padding: 20px; border: 1px solid #eee; }
      .success-box { background: #e8f5e9; padding: 15px; border: 2px solid #4caf50; 
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
        <h1>✓ MFA Enabled</h1>
        <p>Your account security has been enhanced</p>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <div class="success-box">
          <p><strong>🔒 Multi-factor authentication is now enabled!</strong></p>
          <p>Your account is now more secure. When you sign in, you'll need to provide 
             both your password and a verification code from your authenticator app.</p>
        </div>
        
        <h2 style="color: #4caf50;">What This Means</h2>
        
        <ul>
          <li><strong>Stronger Security:</strong> Even if your password is compromised, 
              your account is still protected</li>
          <li><strong>Faster Login:</strong> MFA code takes just a few seconds to generate</li>
          <li><strong>Peace of Mind:</strong> You'll be alerted of any unauthorized access</li>
        </ul>
        
        <h2 style="color: #4caf50;">Your MFA Details</h2>
        
        <ul>
          <li>Authentication App: {{ .Data.appName }} (or similar)</li>
          <li>Backup Codes: {{ .Data.backupCodeCount }} codes saved</li>
          <li>Status: Active and protecting your account</li>
        </ul>
        
        <p class="warning">
          <strong>⚠️ Important:</strong> Save your backup codes in a secure location. 
          You'll need them if you lose access to your authenticator app.
        </p>
        
        <a href="{{ .SiteURL }}/account/security" class="button">
          View MFA Settings
        </a>
        
        <h2 style="color: #4caf50; margin-top: 25px;">Didn't Enable This?</h2>
        
        <p>If you didn't enable MFA, someone may have access to your account. 
           <a href="{{ .SiteURL }}/account/security">Disable MFA immediately</a> and 
           <a href="{{ .SiteURL }}/account/password">change your password</a>.</p>
        
        <h2 style="color: #4caf50;">Next Steps</h2>
        
        <ol>
          <li>Open your authenticator app (Google Authenticator, Authy, Microsoft Authenticator, etc.)</li>
          <li>Scan the QR code or enter the setup key manually</li>
          <li>Your app will generate a 6-digit code</li>
          <li>Enter this code during next login</li>
        </ol>
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

- **Template Type**: Custom email (security event)
- **When Sent**: Immediately after MFA is enabled
- **Includes**: MFA app name, backup code count
- **Action**: User should save backup codes
- **Manual Send**: Not automated by Supabase

## Related Templates

- 05-password-changed.md - Password change notification
- 06-account-locked.md - Account lock
