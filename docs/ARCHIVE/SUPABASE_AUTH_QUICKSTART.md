# Quick Start: Supabase Auth Implementation

## 🚀 5-Minute Setup

### 1. Environment Configuration

Copy `.env.example` to `.env.local` and fill in your Supabase credentials:

```bash
cp frontend/.env.example frontend/.env.local
```

Edit `frontend/.env.local`:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-key-here
```

Get these from Supabase Dashboard:
- Go to **Project Settings** → **API Keys**
- Copy **Project URL**
- Copy **Publishable key** (or anon key for legacy projects)

### 2. Email Templates (Manual Step)

Visit your Supabase Dashboard and update email templates:

**Go to**: Authentication → Email Templates

For each template below, find the line starting with `{{ .ConfirmationURL }}` and replace with:

**Confirm Sign Up Template:**
```
{{ .SiteURL }}?token_hash={{ .TokenHash }}&type=email
```

**Password Reset Template:**
```
{{ .SiteURL }}?token_hash={{ .TokenHash }}&type=recovery
```

**Magic Link Template (OTP):**
```
{{ .SiteURL }}?token_hash={{ .TokenHash }}&type=email
```

### 3. Configure Site URL

**Go to**: Authentication → URL Configuration

Set **Site URL** to your frontend URL:
- Development: `http://localhost:5173`
- Production: `https://yourdomain.com`

Add **Redirect URLs**:
- `http://localhost:5173/auth/callback`
- `https://yourdomain.com/auth/callback`

### 4. Test

Start your frontend:
```bash
npm run dev
```

Visit `http://localhost:5173` and test:
1. **Register with Password** - Create account, verify email
2. **Register with Magic Link** - New account via email link
3. **Login with Password** - Use credentials
4. **Login with Magic Link** - Click email link
5. **Password Reset** - Two-step reset flow
6. **Logout** - Try different scopes (This Device, All Devices, Other Devices)

## 📋 What's New

### New Auth Methods
- ✨ **Magic Link**: Passwordless login via email
- 🔑 **Traditional Password**: Still available as option

### Security Improvements
- 🔐 **PKCE Flow**: Modern auth standard
- 🔒 **Token Hash**: Safer than URL fragments
- 🚪 **Scoped Logout**: Sign out specific devices

### Better UX
- 🎨 **Auth Method Toggle**: Choose password or magic link
- 📧 **Two-Step Password Reset**: Verify before changing password
- 🎯 **Clear Environment Validation**: Errors if config missing

## 🐛 Troubleshooting

### "Missing VITE_SUPABASE_URL"
→ Check `.env.local` file exists and has correct URL

### "Email not received"
→ Check Supabase Dashboard → Auth → Users to confirm signup  
→ For local testing, use Mailpit: `supabase status`

### "Token_hash not working"
→ Verify email template uses `{{ .TokenHash }}` format  
→ Check Site URL matches your current domain  
→ Verify redirect URLs in Supabase config

### "Logout menu not appearing"
→ Make sure you're on FileConverter or AdminDashboard page  
→ Click the "Logout" button to open dropdown menu

## 📚 Full Documentation

- `docs/SUPABASE_EMAIL_TEMPLATES.md` - Email template customization
- `docs/SUPABASE_AUTH_IMPLEMENTATION.md` - Complete implementation details
- `frontend/.env.example` - All available environment variables

## 🔄 Migration from Old Auth

If you're updating existing authentication:

1. **User Data**: All existing users preserved in `user_profiles` table
2. **Sessions**: Previous sessions invalidated (users re-authenticate)
3. **Admin Approval**: Still required for all users
4. **Email Verification**: Still required before login

## 🎓 Key Concepts

### Magic Link
- User enters email → Gets link → Clicks link → Auto-login
- No password needed
- More secure than password-based auth

### PKCE Flow
- Modern OAuth 2.0 standard
- Token exchange instead of direct token in URL
- Prevents authorization code interception
- Works with SSR frameworks

### Scoped Logout
- **Local**: Only this browser/device
- **Global**: All devices (most secure)
- **Others**: Keep current device, logout elsewhere

### Token Hash
- URL format: `?token_hash=XYZ&type=email`
- Replaces old `?access_token=XYZ#...` format
- Safer, SSR-compatible, more flexible

## ✅ Validation Checklist

Before going to production:

```
Development Ready:
☐ .env.local configured
☐ Email templates updated
☐ Site URL set to localhost
☐ All auth flows tested

Production Ready:
☐ .env configured with production credentials
☐ Email templates verified
☐ Site URL set to production domain
☐ Redirect URLs updated
☐ Custom SMTP configured (optional but recommended)
☐ Test emails sent and received
```

## 📞 Support

For issues or questions:
1. Check the full documentation at `docs/SUPABASE_EMAIL_TEMPLATES.md`
2. Review `docs/SUPABASE_AUTH_IMPLEMENTATION.md` for detailed info
3. Check Supabase official docs: https://supabase.com/docs/guides/auth
4. Check console errors in browser DevTools

## 🎉 You're All Set!

Your authentication system now includes:
- ✅ Passwordless magic links
- ✅ Modern PKCE security flow
- ✅ Scoped device logout
- ✅ Environment validation
- ✅ Two-step password reset
- ✅ All existing features preserved

Start using the new auth methods and enjoy a more secure, user-friendly experience!
