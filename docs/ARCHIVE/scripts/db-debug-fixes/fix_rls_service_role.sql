-- Fix RLS to allow reading is_admin status via service role
-- The current policy blocks service role from reading the is_admin and approval_status fields

-- Check current RLS policies
SELECT 
  policyname,
  permissive,
  roles,
  qual,
  with_check
FROM pg_policies
WHERE tablename = 'user_profiles'
ORDER BY policyname;

-- Drop the restrictive SELECT policy if it exists
DROP POLICY IF EXISTS user_profiles_select_own ON user_profiles;

-- Create new policy that allows users to read their own row AND allows service_role full access
CREATE POLICY user_profiles_select_own ON user_profiles
  FOR SELECT
  USING (
    auth.uid() = id OR
    auth.role() = 'service_role'
  );

-- Verify the new policy
SELECT 
  policyname,
  permissive,
  roles,
  qual
FROM pg_policies
WHERE tablename = 'user_profiles' AND policyname = 'user_profiles_select_own';
