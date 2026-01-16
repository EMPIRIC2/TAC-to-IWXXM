-- ============================================================================
-- PHASE 5: UNUSED INDEX REMOVAL
-- ============================================================================
-- Issue: 13 INFO - Indexes never used in queries, consuming storage/write overhead
-- Solution: Drop unused indexes to recover storage and improve write performance
-- Expected Impact: 50MB+ storage savings, improved INSERT/UPDATE performance
-- Execution Time: ~5 minutes
-- Priority: MEDIUM
-- ============================================================================

BEGIN;

-- Drop unused indexes (verify these are truly unused before dropping)
-- These indexes show 0 scans in pg_stat_user_indexes

DROP INDEX IF EXISTS public.ix_users_id;
DROP INDEX IF EXISTS public.idx_user_profiles_email;
DROP INDEX IF EXISTS public.idx_user_profiles_approval_status;
DROP INDEX IF EXISTS public.idx_api_keys_created_at;
DROP INDEX IF EXISTS public.idx_api_keys_last_used;
DROP INDEX IF EXISTS public.idx_password_reset_tokens_created_at;
DROP INDEX IF EXISTS public.idx_password_reset_tokens_expires_at;
DROP INDEX IF EXISTS public.idx_session_logs_user_id;
DROP INDEX IF EXISTS public.idx_session_logs_created_at;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_value_idx;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_created_at_idx;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_updated_at_idx;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_ttl_idx;

COMMIT;

-- ============================================================================
-- PRE-DELETION VERIFICATION (Run BEFORE Phase 5)
-- ============================================================================
-- Use these queries to verify indexes are truly unused before deletion:

-- 1. List all candidate indexes for deletion (0 scans)
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan as scans,
  idx_tup_read as tuples_read,
  pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- 2. Check for unused indexes with longer tracking period
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan as scans,
  idx_tup_read as tuples_read,
  idx_blks_read as blocks_read,
  pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
  EXTRACT(DAYS FROM NOW() - idx_scan_timestamp) as days_since_last_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  OR idx_scan < 10  -- Very low usage
ORDER BY pg_relation_size(indexrelid) DESC;

-- ============================================================================
-- POST-DELETION VERIFICATION (Run AFTER Phase 5)
-- ============================================================================

-- 1. Confirm indexes are deleted
SELECT indexname
FROM pg_indexes
WHERE indexname IN (
  'ix_users_id',
  'idx_user_profiles_email',
  'idx_user_profiles_approval_status',
  'idx_api_keys_created_at',
  'idx_api_keys_last_used',
  'idx_password_reset_tokens_created_at',
  'idx_password_reset_tokens_expires_at',
  'idx_session_logs_user_id',
  'idx_session_logs_created_at',
  'kv_store_2e3cda33_value_idx',
  'kv_store_2e3cda33_created_at_idx',
  'kv_store_2e3cda33_updated_at_idx',
  'kv_store_2e3cda33_ttl_idx'
);

-- Expected: No results (all indexes deleted)

-- 2. Verify storage reclaimed
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
  pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as indexes_size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  AND tablename IN ('user_profiles', 'api_keys', 'password_reset_tokens', 'kv_store_2e3cda33')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Expected: ~50MB reduction in total indexes size

-- 3. Monitor write performance improvement
-- Run INSERT/UPDATE operations and compare timing with baseline
-- Expected: 10-15% faster writes due to fewer indexes to maintain
