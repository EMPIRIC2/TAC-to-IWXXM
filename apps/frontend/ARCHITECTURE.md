# METAR Converter - Architecture Documentation

## 🎯 Overview

This application uses a **simplified, frontend-first architecture** where the frontend talks directly to Supabase for all authentication and user management operations. The backend is minimal and only handles operations that require elevated privileges or complex business logic.

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                     (React + TypeScript)                    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Register   │  │    Login     │  │ File Convert │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │  Supabase Client  │
                   │   (Direct API)    │
                   └─────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐  ┌───────▼────────┐  ┌──────▼──────┐
│  Supabase Auth  │  │  Postgres DB   │  │   Backend   │
│   (Built-in)    │  │   (RLS + Pg)   │  │  (Optional) │
└─────────────────┘  └────────────────┘  └─────────────┘
  • signUp()           • user_profiles      • METAR convert
  • signIn()           • uploads            • Admin emails
  • signOut()          • RLS policies       (Future: AI, etc)
  • resend()
  • getSession()
```

---

## 📦 Data Storage Strategy

### **Frontend → Supabase Direct**

#### **1. Supabase Auth (Built-in)**
- **What**: User authentication and email verification
- **Stores**:
  - Email, password (hashed)
  - `email_confirmed_at` (email verification timestamp)
  - `user_metadata` (username, created_at)
- **Operations**:
  - `supabase.auth.signUp()` - Register
  - `supabase.auth.signInWithPassword()` - Login
  - `supabase.auth.signOut()` - Logout
  - `supabase.auth.resend()` - Resend verification email
  - `supabase.auth.getSession()` - Check current session

#### **2. Postgres Database (with RLS)**
- **Table**: `user_profiles`
- **Stores**:
  - `id` (references auth.users.id)
  - `username`
  - `email`
  - `approval_status` ('pending' | 'approved' | 'rejected')
  - `is_admin` (boolean)
  - `created_at`, `approved_at`, `approved_by`
  - `last_login`
- **Access**: RLS (Row Level Security) policies
  - Users can SELECT their own profile
  - Admins can SELECT/UPDATE all profiles
  - Auto-created via trigger on user signup

---

## 🔐 Authentication Flow

### **Registration** (`Register.tsx`)
```typescript
// Frontend calls Supabase directly
const { data, error } = await supabase.auth.signUp({
  email,
  password,
  options: {
    data: { username },  // Stored in user_metadata
  },
});
```

**What happens:**
1. Supabase creates user in `auth.users`
2. Supabase sends verification email automatically
3. Database trigger creates `user_profiles` row with `approval_status: 'pending'`
4. User redirected to Email Verification screen

---

### **Email Verification** (`EmailVerification.tsx`)
```typescript
// User clicks link in email → Supabase confirms automatically
// Frontend checks verification status
const { data: { session } } = await supabase.auth.getSession();

if (session?.user?.email_confirmed_at) {
  // Verified! Now check approval from database
  const { data: profile } = await supabase
    .from('user_profiles')
    .select('approval_status, is_admin')
    .eq('id', session.user.id)
    .single();
    
  if (profile.approval_status === 'approved') {
    // ✅ Login!
  }
}
```

**What happens:**
1. User clicks verification link in email
2. Supabase sets `email_confirmed_at` timestamp
3. User clicks "I've Verified My Email" button
4. Frontend checks BOTH:
   - Email verified? (from auth.users)
   - Account approved? (from user_profiles table)
5. Only proceeds if BOTH are true

---

### **Login** (`Login.tsx`)
```typescript
// Frontend authenticates with Supabase
const { data: authData } = await supabase.auth.signInWithPassword({
  email,
  password,
});

// Check email verification
if (!authData.user.email_confirmed_at) {
  // ❌ Email not verified
  return;
}

// Check approval status from database
const { data: profile } = await supabase
  .from('user_profiles')
  .select('approval_status, is_admin, username')
  .eq('id', authData.user.id)
  .single();

if (profile.approval_status !== 'approved') {
  // ❌ Not approved yet
  return;
}

// ✅ Both checks passed - grant access
```

**What happens:**
1. Supabase validates credentials
2. Frontend checks `email_confirmed_at` (email verified?)
3. Frontend queries `user_profiles` (approved?)
4. Frontend updates `last_login` timestamp
5. User granted access with session token

---

### **Admin Approval** (`UserApprovalPanel.tsx`)
```typescript
// Admin queries pending users from database
const { data } = await supabase
  .from('user_profiles')
  .select('*')
  .eq('approval_status', 'pending');

// Admin approves user - direct database update
const { error } = await supabase
  .from('user_profiles')
  .update({
    approval_status: 'approved',
    approved_at: new Date().toISOString(),
    approved_by: adminUserId,
  })
  .eq('id', userId);
```

**What happens:**
1. Admin sees list of pending users (RLS allows admins to see all)
2. Admin clicks "Approve" or "Reject"
3. Frontend directly updates `user_profiles` table
4. RLS policy ensures only admins can update approval_status
5. User can now log in (both verified + approved)

---

## 🔒 Security: Row Level Security (RLS)

The `user_profiles` table uses **Postgres Row Level Security** to control access:

### **Policies:**

```sql
-- Users can read their own profile
CREATE POLICY "Users can read own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid() = id);

-- Admins can read all profiles
CREATE POLICY "Admins can read all profiles"
  ON user_profiles FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE id = auth.uid() AND is_admin = true
    )
  );

-- Users can update their own username only
CREATE POLICY "Users can update own username"
  ON user_profiles FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (
    -- Can't change approval_status or is_admin
    approval_status = OLD.approval_status AND
    is_admin = OLD.is_admin
  );

-- Admins can update any profile
CREATE POLICY "Admins can update any profile"
  ON user_profiles FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE id = auth.uid() AND is_admin = true
    )
  );
```

**Benefits:**
- ✅ Security enforced at database level
- ✅ No backend needed for authorization
- ✅ Can't be bypassed by manipulating frontend code
- ✅ Automatic filtering based on user's role

---

## 🖥️ Backend (Minimal)

The backend (`/supabase/functions/server/`) is **optional** and only used for:

### **Current Backend Functions:**
1. **METAR Conversion** - Complex business logic
2. **File Uploads** - Database storage operations
3. **(Future) Admin Email Notifications** - Send emails on approval/rejection

### **NOT Used For:**
- ❌ User authentication (handled by Supabase Auth)
- ❌ Profile queries (handled by RLS)
- ❌ Approval/rejection (handled by RLS + frontend)
- ❌ Session management (handled by Supabase)

---

## 📊 Database Schema

### **`auth.users` (Supabase Built-in)**
```sql
CREATE TABLE auth.users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  encrypted_password TEXT,
  email_confirmed_at TIMESTAMPTZ,  -- Email verification
  user_metadata JSONB,              -- { username, created_at }
  created_at TIMESTAMPTZ,
  last_sign_in_at TIMESTAMPTZ
);
```

### **`public.user_profiles` (Custom Table)**
```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  approval_status TEXT NOT NULL DEFAULT 'pending',
  is_admin BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  approved_at TIMESTAMPTZ,
  approved_by UUID REFERENCES auth.users(id),
  last_login TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### **Auto-Create Profile Trigger**
```sql
-- Automatically create profile when user signs up
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, username, email)
  VALUES (
    NEW.id,
    NEW.raw_user_meta_data->>'username',
    NEW.email
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();
```

---

## 🚀 Benefits of This Architecture

### **1. Simpler**
- No complex backend API for auth
- Frontend talks directly to Supabase
- Fewer moving parts

### **2. Faster**
- No backend hop for queries
- Direct database access with RLS
- Reduced latency

### **3. More Secure**
- Security enforced at database level (RLS)
- Can't bypass via frontend manipulation
- Supabase handles password hashing, sessions

### **4. Easier to Maintain**
- Less backend code to maintain
- Supabase handles infrastructure
- Focus on business logic (METAR conversion)

### **5. Scalable**
- Supabase auto-scales
- Database pooling built-in
- CDN for static frontend

---

## 📝 Environment Variables

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-key-here  # Backend only
```

**Frontend uses**: `SUPABASE_URL` + `SUPABASE_ANON_KEY`  
**Backend uses**: `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`

---

## 🛠️ Setup Instructions

### **1. Run Migration**
```bash
# Apply the database migration to create tables and RLS policies
supabase db push
```

### **2. Configure Email**
- Go to Supabase Dashboard → Authentication → Email Templates
- Configure SMTP (or use built-in for dev)
- Customize verification email template

### **3. Create First Admin**
After a user registers and verifies email:
```sql
-- Manually set first admin via SQL Editor
UPDATE user_profiles
SET approval_status = 'approved', is_admin = true
WHERE email = 'admin@example.com';
```

### **4. Deploy**
- Frontend: Deploy to Vercel/Netlify
- Backend: Automatically deployed via Supabase Edge Functions

---

## 🔍 Debugging

### **Check User Status**
```sql
-- See all users and their approval status
SELECT 
  u.email,
  u.email_confirmed_at,
  p.approval_status,
  p.is_admin
FROM auth.users u
LEFT JOIN user_profiles p ON u.id = p.id;
```

### **Check RLS Policies**
```sql
-- View all policies on user_profiles
SELECT * FROM pg_policies WHERE tablename = 'user_profiles';
```

### **Test RLS as User**
```sql
-- Set session to specific user
SET SESSION "request.jwt.claims" = '{"sub":"user-id-here"}';

-- Now queries run with that user's permissions
SELECT * FROM user_profiles;
```

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `/src/app/components/auth/Register.tsx` | Direct Supabase signup |
| `/src/app/components/auth/Login.tsx` | Direct Supabase signin + DB query |
| `/src/app/components/auth/EmailVerification.tsx` | Check verification + approval |
| `/src/app/components/admin/UserApprovalPanel.tsx` | Direct DB updates via RLS |
| `/supabase/migrations/001_create_user_profiles.sql` | Database schema + RLS |
| `/utils/supabase/client.tsx` | Supabase client singleton |

---

## 🎓 Learning Resources

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Client Library](https://supabase.com/docs/reference/javascript)

---

**Architecture Philosophy**: Keep it simple. Use the database for what it's good at (authorization via RLS), use the backend only when necessary (complex logic, privileged operations).
