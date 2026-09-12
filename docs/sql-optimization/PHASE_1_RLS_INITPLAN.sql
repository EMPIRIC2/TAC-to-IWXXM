-- ============================================================================
-- PHASE 1: RLS INITPLAN OPTIMIZATION
-- ============================================================================
-- Issue: 3 policies re-evaluating auth.uid() per row (inefficient)
-- Solution: Use subquery to evaluate auth.uid() once per query
-- Expected Impact: 30-50% faster RLS policy evaluation on SELECT/UPDATE
-- Execution Time: ~10 minutes
-- Priority: HIGH
-- ============================================================================

BEGIN;

-- Drop existing inefficient policies
DROP POLICY IF EXISTS "Users can read own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own username" ON public.user_profiles;

-- Recreate with optimized auth.uid() evaluation (subquery pattern)
CREATE POLICY "Users can read own profile" ON public.user_profiles
  FOR SELECT
  USING (user_id = (SELECT auth.uid()));

CREATE POLICY "Users can insert own profile" ON public.user_profiles
  FOR INSERT
  WITH CHECK (user_id = (SELECT auth.uid()));

CREATE POLICY "Users can update own username" ON public.user_profiles
  FOR UPDATE
  USING (user_id = (SELECT auth.uid()))
  WITH CHECK (user_id = (SELECT auth.uid()));

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run after Phase 1 to verify policies are correctly updated:

-- 1. Verify policies exist and have correct structure
SELECT schemaname, tablename, policyname, qual, with_check
FROM pg_policies
WHERE tablename = 'user_profiles'
ORDER BY policyname;

-- 2. Check query plan improvement (should show single subquery evaluation)
-- Replace with your actual filtering condition:
EXPLAIN ANALYZE
SELECT * FROM public.user_profiles
WHERE user_id = (SELECT auth.uid());

-- Expected: Subplan scanned once, not per-row
