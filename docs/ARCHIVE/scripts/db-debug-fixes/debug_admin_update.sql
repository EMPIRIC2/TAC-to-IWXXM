-- DIAGNOSTIC: Check why UPDATE isn't working
-- Step 1: Check table structure and constraints
\d user_profiles

-- Step 2: Check for triggers
SELECT trigger_name, event_manipulation, event_object_table
FROM information_schema.triggers
WHERE event_object_table = 'user_profiles';

-- Step 3: Check current RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, qual, with_check
FROM pg_policies
WHERE tablename = 'user_profiles'
ORDER BY policyname;

-- Step 4: Try a simple test UPDATE with explicit casting
UPDATE user_profiles
SET 
  is_admin = true::boolean,
  approval_status = 'approved'::text
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d'::uuid;

-- Step 5: Check if it worked
SELECT id, email, username, is_admin, approval_status
FROM user_profiles
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';

-- Step 6: If still not working, check row-level details
SELECT id, email, is_admin, approval_status, 
       pg_column_size(is_admin) as is_admin_size,
       pg_column_size(approval_status) as approval_status_size
FROM user_profiles
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';
