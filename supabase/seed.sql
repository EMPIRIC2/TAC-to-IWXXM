-- Local seed data for `supabase db reset`.
-- Profiles for auth users are created by the handle_new_user trigger on signup.
-- Use Supabase Studio (http://127.0.0.1:54323) or auth API to create test users locally.

-- Example: after creating auth user UUID via Studio, approve admin locally:
-- UPDATE public.user_profiles
-- SET approval_status = 'approved', is_admin = true, approved_at = NOW()
-- WHERE email = 'admin@example.com';
