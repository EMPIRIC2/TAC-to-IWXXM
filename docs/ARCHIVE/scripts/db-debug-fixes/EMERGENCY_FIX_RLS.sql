-- EMERGENCY FIX: Remove infinite recursion in RLS policies
-- Run this in Supabase Dashboard SQL Editor: https://supabase.com/dashboard/project/YOUR_PROJECT_REF/sql

-- Step 1: Disable RLS temporarily
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- Step 2: Drop ALL policies (including any hidden ones)
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'user_profiles') 
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON user_profiles';
    END LOOP;
END $$;

-- Step 3: Verify all policies are gone
SELECT policyname FROM pg_policies WHERE tablename = 'user_profiles';
-- Should return 0 rows

-- Step 4: Create simple, non-recursive policies
CREATE POLICY user_profiles_select_own ON user_profiles
  FOR SELECT
  USING (id = auth.uid());

CREATE POLICY user_profiles_update_own ON user_profiles
  FOR UPDATE
  USING (id = auth.uid());

CREATE POLICY user_profiles_insert_own ON user_profiles
  FOR INSERT
  WITH CHECK (id = auth.uid());

-- Step 5: Re-enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Step 6: Verify new policies
SELECT schemaname, tablename, policyname, permissive, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'user_profiles'
ORDER BY policyname;
