-- Fix infinite recursion in RLS policies
-- Execute this in Supabase SQL Editor: https://supabase.com/dashboard/project/YOUR_PROJECT_REF/sql

-- Drop all existing policies on user_profiles
DROP POLICY IF EXISTS user_profiles_select_policy ON user_profiles;
DROP POLICY IF EXISTS user_profiles_insert_policy ON user_profiles;
DROP POLICY IF EXISTS user_profiles_update_policy ON user_profiles;
DROP POLICY IF EXISTS user_profiles_delete_policy ON user_profiles;
DROP POLICY IF EXISTS user_profiles_unified_read_policy ON user_profiles;
DROP POLICY IF EXISTS user_profiles_unified_write_policy ON user_profiles;
DROP POLICY IF EXISTS user_profiles_admin_all_policy ON user_profiles;

-- Create simple, non-recursive policies
-- Policy 1: Users can read their own profile
CREATE POLICY user_profiles_read_own ON user_profiles
  FOR SELECT
  USING (auth.uid() = id);

-- Policy 2: Users can update their own profile (non-admin fields only)
CREATE POLICY user_profiles_update_own ON user_profiles
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Policy 3: Service role can do everything (for triggers and admin operations)
CREATE POLICY user_profiles_service_role_all ON user_profiles
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- Policy 4: Allow insert for authenticated users (for profile creation trigger)
CREATE POLICY user_profiles_insert_authenticated ON user_profiles
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- Verify policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'user_profiles'
ORDER BY policyname;
