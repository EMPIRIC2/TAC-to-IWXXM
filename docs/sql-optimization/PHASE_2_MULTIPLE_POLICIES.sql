-- ============================================================================
-- PHASE 2: MULTIPLE PERMISSIVE POLICIES CONSOLIDATION
-- ============================================================================
-- Issue: 7 WARN - separate policies for same operation (e.g., "Admins can read all"
--        + "Users can read own") cause dual policy evaluation per row
-- Solution: Combine into single policies using OR conditions
-- Expected Impact: 20% reduction in per-row policy evaluation overhead
-- Execution Time: ~20 minutes
-- Priority: HIGH
-- ============================================================================

BEGIN;

-- Example: Consolidate SELECT policies on user_profiles
-- Before: 2 separate policies (admins + users reading own)
-- After: 1 combined policy with OR condition

DROP POLICY IF EXISTS "select_own_profile" ON public.user_profiles;
DROP POLICY IF EXISTS "select_all_profiles_admin" ON public.user_profiles;

CREATE POLICY "select_all_profiles" ON public.user_profiles
  FOR SELECT
  USING (
    user_id = (SELECT auth.uid())  -- Users can read own
    OR (
      SELECT is_admin 
      FROM auth.users 
      WHERE id = (SELECT auth.uid())
    ) = true  -- Admins can read all
  );

-- Example: Consolidate UPDATE policies
DROP POLICY IF EXISTS "update_own_profile" ON public.user_profiles;
DROP POLICY IF EXISTS "update_any_profile_admin" ON public.user_profiles;

CREATE POLICY "update_all_profiles" ON public.user_profiles
  FOR UPDATE
  USING (
    user_id = (SELECT auth.uid())  -- Users can update own
    OR (
      SELECT is_admin 
      FROM auth.users 
      WHERE id = (SELECT auth.uid())
    ) = true  -- Admins can update any
  )
  WITH CHECK (
    user_id = (SELECT auth.uid())
    OR (
      SELECT is_admin 
      FROM auth.users 
      WHERE id = (SELECT auth.uid())
    ) = true
  );

-- Example: Consolidate DELETE policies
DROP POLICY IF EXISTS "delete_own_profile" ON public.user_profiles;
DROP POLICY IF EXISTS "delete_any_profile_admin" ON public.user_profiles;

CREATE POLICY "delete_all_profiles" ON public.user_profiles
  FOR DELETE
  USING (
    user_id = (SELECT auth.uid())  -- Users can delete own
    OR (
      SELECT is_admin 
      FROM auth.users 
      WHERE id = (SELECT auth.uid())
    ) = true  -- Admins can delete any
  );

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- 1. Count policies before/after (should reduce from 6 to 3)
SELECT COUNT(*) as policy_count, tablename
FROM pg_policies
WHERE tablename = 'user_profiles'
GROUP BY tablename;

-- 2. Verify combined policies exist
SELECT policyname, qual, with_check
FROM pg_policies
WHERE tablename = 'user_profiles'
ORDER BY policyname;

-- 3. Performance test - query plan should show OR conditions evaluated efficiently
EXPLAIN ANALYZE
SELECT * FROM public.user_profiles
WHERE user_id = (SELECT auth.uid())
   OR (SELECT is_admin FROM auth.users WHERE id = (SELECT auth.uid())) = true;

-- Expected: 20% improvement in execution time vs. separate policy evaluation
