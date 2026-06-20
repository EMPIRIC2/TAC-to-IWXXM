# Unusual Location Login Alert Template

Sent when login occurs from a significantly different geographic location.

## Subject
```
Login from a new location
```

## Plain Text
```
Hello {{ .Email }},

We detected a login to your account from a new location.

Previous Location: {{ .Data.previousLocation }}
Current Location: {{ .Data.currentLocation }}
Distance: {{ .Data.distance }} miles

If this was you, you can safely ignore this email. 

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
      .alert-box { background: #fff3cd; padding: 15px; border: 2px solid #ff9800; 
                  border-radius: 4px; margin: 15px 0; }
      .details-box { background: white; padding: 15px; border: 1px solid #ddd; 
                    border-radius: 4px; margin: 15px 0; }
      .button { background-color: #2196f3; color: white; padding: 12px 24px; 
               text-decoration: none; border-radius: 4px; display: inline-block; 
               margin: 20px 0; font-weight: bold; }
      .secondary-button { background-color: #d32f2f; color: white; padding: 12px 24px; 
                         text-decoration: none; border-radius: 4px; display: inline-block; 
                         margin: 10px 10px 10px 0; font-weight: bold; }
      .footer { font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; 
               border-top: 1px solid #eee; }
      .safe-note { background: #e8f5e9; padding: 12px; border-left: 4px solid #4caf50; 
                  margin: 15px 0; }
      .distance-badge { background: #ff9800; color: white; padding: 10px 15px; 
                       border-radius: 20px; font-weight: bold; font-size: 16px; 
                       display: inline-block; margin: 10px 0; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>✈️ Login from New Location</h1>
        <p>We detected a sign-in from an unfamiliar geographic location</p>
      </div>
      <div class="content">
        <p>Hello {{ .Email }},</p>
        
        <div class="alert-box">
          <p><strong>We detected a login to your account from a significantly different 
             geographic location than your last login.</strong></p>
          <p>This could be normal (e.g., traveling), but please verify it was you.</p>
        </div>
        
        <h2 style="color: #f57c00;">Location Comparison</h2>
        
        <div class="details-box">
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold; width: 40%;">Last Location:</td>
              <td style="padding: 8px;">{{ .Data.previousLocation }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">New Location:</td>
              <td style="padding: 8px;">{{ .Data.currentLocation }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Distance:</td>
              <td style="padding: 8px;">
                <span class="distance-badge">{{ .Data.distance }} miles</span>
              </td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
              <td style="padding: 8px; font-weight: bold;">Implied Speed:</td>
              <td style="padding: 8px;">{{ .Data.impliedSpeed }} mph</td>
            </tr>
            <tr>
              <td style="padding: 8px; font-weight: bold;">Time:</td>
              <td style="padding: 8px;">{{ .Data.timestamp }} UTC</td>
            </tr>
          </table>
        </div>
        
        <h2 style="color: #f57c00;">Common Reasons for Location Changes</h2>
        
        <ul>
          <li>✓ Travel to a new city or country</li>
          <li>✓ Using a VPN or proxy service</li>
          <li>✓ Different Wi-Fi network at home</li>
          <li>✓ Mobile device using cellular network</li>
        </ul>
        
        <h2 style="color: #f57c00;">Is This Expected?</h2>
        
        <div class="safe-note">
          <p><strong>✓ If this was you:</strong><br>
             Great! This is probably just a result of travel, using a VPN, or connecting 
             from a different network. You can safely ignore this email.</p>
        </div>
        
        <a href="{{ .SiteURL }}/account/security?action=mark-location-safe" class="button">
          Mark as Trusted Location
        </a>
        
        <h2 style="color: #f57c00; margin-top: 25px;">⚠️ If This Looks Suspicious</h2>
        
        <p style="background: #ffebee; padding: 12px; border-radius: 4px;">
          <strong>If you didn't travel or change networks:</strong>
        </p>
        
        <ol>
          <li>Someone may be accessing your account</li>
          <li><a href="{{ .SiteURL }}/account/password-reset">Change your password</a> immediately</li>
          <li><a href="{{ .SiteURL }}/account/security">Review all active sessions</a></li>
          <li>Look for unauthorized activity</li>
          <li><a href="mailto:support@yourapp.com">Contact support</a> if concerned</li>
        </ol>
        
        <a href="{{ .SiteURL }}/account/security" class="secondary-button">
          Review Account Security
        </a>
        
        <h2 style="color: #f57c00;">How We Calculate This</h2>
        
        <ul>
          <li>We track the geographic location of each login</li>
          <li>We calculate distance traveled between logins</li>
          <li>Abnormal speeds (>500 mph) are flagged as suspicious</li>
          <li>You can always mark trusted locations</li>
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

- **Template Type**: Location warning (login event)
- **When Sent**: On login from significantly different location
- **Calculation**: Based on IP geolocation
- **Threshold**: Typically >500 miles or >500 mph implied speed
- **Manual Send**: From login handler or backend

## Implementation

```typescript
// Detect unusual location changes
async function detectLocationAnomaly(
  userId: string,
  email: string,
  newLocation: GeoLocation
) {
  const lastLogin = await getLastLogin(userId);
  
  if (!lastLogin) return; // First login
  
  const distance = calculateDistance(
    lastLogin.location,
    newLocation
  );
  
  const timeDiff = (Date.now() - lastLogin.timestamp) / 3600000; // hours
  const impliedSpeed = distance / timeDiff;
  
  // Flag if distance >500 miles or impossible speed
  if (distance > 500 || impliedSpeed > 500) {
    await supabaseAdmin.functions.invoke('send-email', {
      body: {
        to: email,
        template: 'ip-mismatch',
        data: {
          previousLocation: formatLocation(lastLogin.location),
          currentLocation: formatLocation(newLocation),
          distance: Math.round(distance),
          impliedSpeed: Math.round(impliedSpeed),
          timestamp: new Date().toISOString(),
        }
      }
    });
  }
}
```

## Related Templates

- 04-new-device.md - New device login
- 06-suspicious-activity.md - Suspicious login
- 06-account-locked.md - Account lock
