-- ============================================================================
-- PHASE 4: UNINDEXED FOREIGN KEY OPTIMIZATION
-- ============================================================================
-- Issue: 3 INFO - Foreign Key constraints without covering indexes:
--   - api_keys.user_id (FK to auth.users.id)
--   - password_reset_tokens.user_id (FK to auth.users.id)
--   - user_profiles.approved_by (FK to auth.users.id)
-- Solution: Create indexes on FK columns for efficient lookup and joins
-- Expected Impact: 40% faster foreign key lookups and JOIN operations
-- Execution Time: ~10 minutes
-- Priority: MEDIUM
-- ============================================================================

BEGIN;

-- Create index on api_keys.user_id (if not exists)
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON public.api_keys(user_id);

-- Create index on password_reset_tokens.user_id (if not exists)
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON public.password_reset_tokens(user_id);

-- Create index on user_profiles.approved_by (if not exists)
CREATE INDEX IF NOT EXISTS idx_user_profiles_approved_by ON public.user_profiles(approved_by);

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- 1. Verify new indexes were created
SELECT
  schemaname,
  tablename,
  indexname,
  indexdef
FROM pg_indexes
WHERE indexname IN (
  'idx_api_keys_user_id',
  'idx_password_reset_tokens_user_id',
  'idx_user_profiles_approved_by'
)
ORDER BY tablename, indexname;

-- 2. Check index sizes and structure
SELECT
  schemaname,
  tablename,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
  idx_scan as scans,
  idx_tup_read as tuples_read
FROM pg_stat_user_indexes
WHERE indexname IN (
  'idx_api_keys_user_id',
  'idx_password_reset_tokens_user_id',
  'idx_user_profiles_approved_by'
)
ORDER BY tablename;

-- 3. Test JOIN performance improvement (api_keys with users)
EXPLAIN ANALYZE
SELECT 
  ak.id,
  ak.name,
  u.email
FROM public.api_keys ak
JOIN auth.users u ON ak.user_id = u.id
WHERE ak.user_id = 'specific-user-uuid';

-- Expected: Index scan on api_keys(user_id), significantly faster than sequential scan

-- 4. Test password_reset_tokens FK lookup
EXPLAIN ANALYZE
SELECT 
  prt.id,
  prt.token_hash,
  u.email
FROM public.password_reset_tokens prt
JOIN auth.users u ON prt.user_id = u.id
WHERE prt.user_id = 'specific-user-uuid';

-- 5. Test user_profiles.approved_by FK lookup
EXPLAIN ANALYZE
SELECT 
  up.id,
  up.username,
  approver.email
FROM public.user_profiles up
LEFT JOIN auth.users approver ON up.approved_by = approver.id
WHERE up.approved_by IS NOT NULL;

-- Expected: 40% improvement in FK lookup and JOIN execution time
