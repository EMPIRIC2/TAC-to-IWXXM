-- FINAL ADMIN APPROVAL - Run in Supabase Dashboard SQL Editor
-- This disables RLS temporarily to ensure UPDATE executes

-- Step 1: Disable RLS on user_profiles table
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- Step 2: Update admin user approval status and permissions
UPDATE user_profiles
SET 
  approval_status = 'approved',
  is_admin = true,
  updated_at = NOW()
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';

-- Step 3: Re-enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Step 4: Verify the update was successful
SELECT id, email, username, is_admin, approval_status, created_at, updated_at
FROM user_profiles
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';
