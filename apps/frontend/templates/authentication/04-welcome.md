# Welcome Email Template

Sent after user successfully confirms their email address.

## Subject
```
Welcome to METAR to IWXXM!
```

## Plain Text
```
Hello {{ .Email }},

Welcome to METAR to IWXXM! Your account is now active and ready to use.

Getting Started:
1. Visit {{ .SiteURL }} and log in
2. Convert METAR data to IWXXM format
3. Export and integrate with your systems

Need help? Check our documentation at {{ .SiteURL }}/docs

Questions? Reply to this email or contact support@yourapp.com

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
                color: white; padding: 30px 20px; text-align: center; border-radius: 4px 4px 0 0; }
      .content { background: #f9f9f9; padding: 20px; border: 1px solid #eee; }
      .button { background-color: #667eea; color: white; padding: 12px 24px; 
               text-decoration: none; border-radius: 4px; display: inline-block; 
               margin: 20px 0; font-weight: bold; }
      .footer { font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; 
               border-top: 1px solid #eee; }
      .feature-box { background: white; padding: 15px; margin: 15px 0; 
                    border-left: 4px solid #667eea; }
      .feature-box h3 { margin: 0 0 5px 0; color: #667eea; }
      .success-badge { background: #4caf50; color: white; padding: 5px 10px; 
                      border-radius: 20px; font-size: 12px; display: inline-block; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>🎉 Welcome!</h1>
        <p>Your account is ready to use</p>
        <p style="margin-top: 10px;"><span class="success-badge">✓ Email Verified</span></p>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <p>Welcome to METAR to IWXXM! Your account has been successfully created and 
           verified. You're all set to start converting METAR data.</p>
        
        <a href="{{ .SiteURL }}/converter" class="button">
          Start Converting Now
        </a>
        
        <h2 style="margin-top: 30px; color: #667eea;">Getting Started</h2>
        
        <div class="feature-box">
          <h3>1. Upload METAR Data</h3>
          <p>Paste your METAR observations or upload files in standard format. 
             Our parser handles multiple formats automatically.</p>
        </div>
        
        <div class="feature-box">
          <h3>2. Configure Conversion</h3>
          <p>Customize conversion settings to match your requirements. 
             Adjust IWXXM output parameters as needed.</p>
        </div>
        
        <div class="feature-box">
          <h3>3. Export Results</h3>
          <p>Download converted IWXXM data in XML format or integrate directly 
             with your systems via our API.</p>
        </div>
        
        <h2 style="margin-top: 30px; color: #667eea;">Quick Links</h2>
        <ul>
          <li><a href="{{ .SiteURL }}/docs">Documentation</a></li>
          <li><a href="{{ .SiteURL }}/docs/api">API Reference</a></li>
          <li><a href="{{ .SiteURL }}/account/settings">Account Settings</a></li>
        </ul>
        
        <h2 style="margin-top: 30px; color: #667eea;">Account Security</h2>
        <p>Your account is protected by:</p>
        <ul>
          <li>End-to-end encryption for all data</li>
          <li>Regular security audits</li>
          <li>Secure token-based authentication</li>
          <li>Role-based access controls</li>
        </ul>
        
        <p><strong>⚠️ Important:</strong> Never share your password or reset links. 
           If you suspect unauthorized access, change your password immediately.</p>
      </div>
      <div class="footer">
        <p>© 2024 METAR to IWXXM. All rights reserved.</p>
        <p style="margin-top: 10px;">Support: support@yourapp.com | 
           <a href="{{ .SiteURL }}/privacy" style="color: #667eea;">Privacy Policy</a> | 
           <a href="{{ .SiteURL }}/terms" style="color: #667eea;">Terms of Service</a></p>
      </div>
    </div>
  </body>
</html>
```

## Usage Notes

- **Template Type**: Custom email (not automated by Supabase)
- **When Sent**: After successful email confirmation in your app
- **Timing**: Usually sent within 1 minute of verification
- **Purpose**: Onboarding and education
- **Manual Send**: Use Supabase Admin API or send via your backend

## Implementation

Send this email manually after email confirmation:

```typescript
// In your backend (Node.js example with Supabase Admin SDK)
import { createClient } from '@supabase/supabase-js';

const supabaseAdmin = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

// Send welcome email
const { data, error } = await supabaseAdmin.functions.invoke('send-email', {
  body: {
    to: userEmail,
    template: 'welcome',
    data: {
      displayName: user.user_metadata?.username || userEmail,
      siteUrl: process.env.SITE_URL,
    }
  }
});
```

## Customization Tips

1. **Add onboarding video link**:
   ```html
   <a href="https://yourapp.com/onboarding-video" class="button">
     Watch 5-min Getting Started Video
   </a>
   ```

2. **Include conversion limits**:
   ```html
   <p><strong>Your Plan:</strong> 100 conversions/month | 50 MB file size limit</p>
   ```

3. **Add team invitation**:
   ```html
   <p>Have teammates? <a href="{{ .SiteURL }}/invite">Invite them to collaborate</a></p>
   ```

4. **Personalize with username**:
   ```html
   <p>Hello {{ .Data.username }},</p>
   ```

## Testing

1. Complete registration
2. Confirm email address via confirmation link
3. Check for welcome email (should arrive within 1 minute)
4. Click "Start Converting Now" button
5. Verify user can access converter

## Related Templates

- 01-confirmation.md - Email confirmation
- 04-welcome.md - This template
- 05-email-changed.md - Email change notification
