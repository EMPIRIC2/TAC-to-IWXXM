# Email Template Variables Reference

Complete documentation of all available variables in email templates.

## Supabase Predefined Variables

### Token and Link Variables
- **`{{ .TokenHash }}`** - Secure token hash for verification links
  - Used in: Confirmation, Password Reset, Magic Link
  - Format: URL-safe base64 encoded hash
  - Expires: 24 hours (configurable in Supabase)
  - Example: `https://yourapp.com/auth/callback?token_hash=abc123xyz&type=recovery`

- **`{{ .SiteURL }}`** - Your application's base URL
  - Used in: All templates (typically for links)
  - Example: `https://yourapp.com`
  - From: Supabase project settings → Auth → Site URL

- **`{{ .Email }}`** - User's email address
  - Used in: All templates (personalization)
  - Example: `user@example.com`

### Custom Data Variables
- **`{{ .Data }}`** - Custom JSON data passed from your app
  - Used in: Any template that needs custom context
  - Format: JSON object available in template context
  - Example in code:
    ```typescript
    await supabase.auth.resendPasswordRecoveryEmail(email, {
      redirectTo: 'https://yourapp.com/reset-password',
      data: { username: 'john_doe', reason: 'forgot_password' }
    });
    ```
  - Access in template: `{{ .Data.username }}`

## Complete Link Examples

### Confirmation Link
```
{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=signup
```

### Password Reset Link
```
{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=recovery
```

### Magic Link (OTP)
```
{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=magiclink
```

### Change Email Link
```
{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=email_change
```

## Link Handling in Your App

In your `frontend/src/app/pages/AuthCallback.tsx` or similar:

```typescript
const SearchParams = useSearchParams();
const hashParams = new URLSearchParams(window.location.hash.substring(1));
const tokenHash = SearchParams.get('token_hash') || hashParams.get('token_hash');
const type = SearchParams.get('type') || hashParams.get('type');

switch(type) {
  case 'signup':
    // Handle email confirmation
    break;
  case 'recovery':
    // Handle password reset
    break;
  case 'magiclink':
    // Handle magic link login
    break;
  case 'email_change':
    // Handle email change confirmation
    break;
}
```

## Template Building Blocks

### Greeting
```html
<h1>Hi {{ .Email }}</h1>
```

### Call-to-Action Button
```html
<a href="{{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=signup" 
   style="background-color: #007bff; color: white; padding: 12px 24px; 
          text-decoration: none; border-radius: 4px; display: inline-block;">
  Confirm Email
</a>
```

### Company Info
Add to Supabase settings → Auth → Email customization:
- Support Email: support@yourapp.com
- Phone: +1 (555) 123-4567
- Company Name: Your Company

## Testing Variables Locally

To test templates with variables before deployment:

```typescript
// Test variable substitution
const testVars = {
  TokenHash: 'test123abc456def789xyz',
  SiteURL: 'https://localhost:5173',
  Email: 'user@example.com',
  Data: { username: 'testuser' }
};

// Use in template testing
const templateTest = `
  Dear {{ .Email }},
  Click: {{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=signup
`;
```

## Common Issues

### Variables Not Rendering
- ✅ Use correct syntax: `{{ .VariableName }}`
- ✅ Check capitalization: `TokenHash` not `tokenHash`
- ✅ Ensure variables are available in template type (some may not apply)

### Links Not Working
- ✅ Verify Site URL in Supabase settings matches your domain
- ✅ Confirm `{{ .TokenHash }}` is properly encoded
- ✅ Test redirect URL configuration
- ✅ Check browser console for query parameter issues

### Secure Token Hash Not Present
- ✅ Only available in: Signup, Password Reset, Email Change templates
- ✅ NOT available in: Custom templates without auth events
- ✅ Verify template type is properly configured

## Advanced Usage

### Conditional Content (if supported)
Some email providers support conditionals:
```html
{{if .Data.isAdmin}}
  <p>You have admin privileges</p>
{{end}}
```

### Dynamic Expiration Messages
```html
<p>This link expires in 24 hours (until {{ .ExpiryTime }})</p>
```
*Note: Exact implementation depends on your Supabase template version*

## Migration Checklist

When moving to these templates:
1. ✅ Copy template content to Supabase Auth → Email Templates
2. ✅ Test with real email address (check spam folder)
3. ✅ Verify links work with correct token_hash
4. ✅ Confirm redirect URLs match your app settings
5. ✅ Test on mobile device (email client rendering)
6. ✅ Monitor email delivery in Supabase logs
