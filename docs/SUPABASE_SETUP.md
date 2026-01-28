# Supabase Setup Guide

This guide will help you set up Supabase for the METAR to IWXXM Converter application.

## Prerequisites

- A Supabase account (free tier is sufficient)
- Basic understanding of PostgreSQL databases

## Step 1: Create a Supabase Project

1. Go to [Supabase](https://supabase.com) and sign in
2. Click "New Project"
3. Fill in the project details:
   - **Project Name**: metar-iwxxm-converter (or your preferred name)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose the region closest to your users
4. Click "Create new project"

Wait a few minutes for your project to be set up.

## Step 2: Get Your API Keys

1. In your Supabase project dashboard, go to **Settings** → **API**
2. You'll find two important values:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **Anon/Public Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (long string)

## Step 3: Configure Your Application

### For Docker Deployment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update the following values:
   ```env
   # Supabase Configuration
   VITE_SUPABASE_URL=https://your-project-id.supabase.co
   VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-anon-key-here
   ```

3. Also set the database URL if using Supabase for the auth service:
   ```env
   DATABASE_URL=postgresql://postgres:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require
   ```
   
   Replace:
   - `[PASSWORD]` with your database password
   - `[region]` with your region (e.g., us-west-2)

### For Local Development

1. Create `frontend/.env.local`:
   ```bash
   cd frontend
   cp .env.example .env.local
   ```

2. Add your Supabase credentials:
   ```env
   VITE_SUPABASE_URL=https://your-project-id.supabase.co
   VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-anon-key-here
   VITE_APP_URL=http://localhost:5173
   VITE_BACKEND_URL=http://localhost:8001
   VITE_AUTH_URL=http://localhost:8002
   ```

## Step 4: Configure Supabase Authentication

### Enable Email Authentication

1. In your Supabase dashboard, go to **Authentication** → **Providers**
2. Ensure **Email** is enabled
3. Configure email settings:
   - **Enable Email Confirmations**: Recommended for production
   - **Enable Email Change Confirmations**: Recommended
   - **Secure Email Change**: Enabled

### Configure Email Templates

1. Go to **Authentication** → **Email Templates**
2. Update the redirect URLs in each template to point to your frontend:
   
   For local development:
   ```
   {{ .SiteURL }}/auth/callback?token_hash={{ .TokenHash }}&type=email
   ```
   
   For production, replace with your production URL.

### Set Site URL

1. Go to **Authentication** → **URL Configuration**
2. Set **Site URL** to:
   - Local development: `http://localhost:8000`
   - Production: `https://your-domain.com`

3. Add redirect URLs (one per line):
   ```
   http://localhost:8000/*
   http://localhost:5173/*
   https://your-domain.com/*
   ```

## Step 5: Database Setup (Optional)

If you're using Supabase PostgreSQL as your auth database instead of SQLite:

1. Go to **SQL Editor** in your Supabase dashboard
2. Run the following SQL to create necessary tables:

```sql
-- Users table (Supabase creates this automatically with auth.users)

-- Optional: Create a public users table for additional profile data
CREATE TABLE IF NOT EXISTS public.users (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  full_name TEXT,
  email TEXT,
  address TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own profile"
  ON public.users FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
  ON public.users FOR UPDATE
  USING (auth.uid() = id);
```

## Step 6: Test the Connection

1. Start the services:
   ```bash
   docker-compose up
   ```

2. Open `http://localhost:8000` in your browser
3. Try to register a new account
4. Check your email for the confirmation link
5. After confirming, log in to test the authentication

## Troubleshooting

### "Invalid API key" Error

- Double-check that you copied the correct anon/public key from Supabase
- Ensure there are no extra spaces or line breaks in the `.env` file
- Restart the containers after changing `.env`: `docker-compose restart`

### Email Not Received

- Check your Supabase email rate limits (default: 2 emails/hour in development)
- For production, configure a custom SMTP provider
- Check the email in your spam folder
- Look at **Authentication** → **Logs** in Supabase dashboard

### "Token expired" Error

- Tokens expire after 1 hour by default
- Simply log out and log back in to get a new token
- To change expiration time, go to **Settings** → **Authentication** in Supabase

### CORS Errors

- Ensure your site URL and redirect URLs are properly configured in Supabase
- Check that the frontend is making requests to the correct backend URL
- Verify nginx proxy configuration in `frontend/nginx.conf`

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use environment-specific configurations**:
   - Development: Use the default Supabase email service
   - Production: Configure a custom SMTP provider
3. **Enable Row Level Security (RLS)** on all database tables
4. **Use strong database passwords**
5. **Regularly rotate API keys** for production
6. **Monitor authentication logs** in Supabase dashboard

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [PKCE Flow Guide](https://supabase.com/docs/guides/auth/server-side/pkce-flow)
- [Email Templates Guide](https://supabase.com/docs/guides/auth/auth-email-templates)

## Support

For issues specific to this application, please open an issue on GitHub.
For Supabase-specific issues, consult the [Supabase Community](https://github.com/supabase/supabase/discussions).
