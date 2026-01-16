-- ============================================================================
-- PHASE 6: QUERY STATISTICS REFRESH
-- ============================================================================
-- Issue: PostgreSQL query planner using stale statistics after index changes
-- Solution: Run ANALYZE on all affected tables to update statistics
-- Expected Impact: 10-20% planner accuracy improvement, better query plans
-- Execution Time: ~5 minutes
-- Priority: HIGH (run after all other phases)
-- ============================================================================

BEGIN;

-- Refresh statistics on all affected tables
-- This allows the query planner to make better decisions

ANALYZE public.user_profiles;
ANALYZE public.api_keys;
ANALYZE public.password_reset_tokens;
ANALYZE public.kv_store_2e3cda33;
ANALYZE auth.users;

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- 1. Check statistics were updated
SELECT
  schemaname,
  tablename,
  n_live_tup as live_rows,
  n_dead_tup as dead_rows,
  last_vacuum,
  last_autovacuum,
  last_analyze,
  last_autoanalyze
FROM pg_stat_user_tables
WHERE tablename IN (
  'user_profiles',
  'api_keys',
  'password_reset_tokens',
  'kv_store_2e3cda33'
)
ORDER BY tablename;

-- Expected: last_analyze shows recent timestamp

-- 2. Check column statistics are current
SELECT
  schemaname,
  tablename,
  attname,
  n_distinct,
  avg_width,
  correlation
FROM pg_stats
WHERE tablename IN (
  'user_profiles',
  'api_keys',
  'password_reset_tokens',
  'kv_store_2e3cda33'
)
ORDER BY tablename, attname;

-- 3. Run EXPLAIN on complex queries to verify improved plans
-- Test with a complex query that benefits from updated statistics
EXPLAIN ANALYZE
SELECT 
  up.id,
  up.username,
  COUNT(ak.id) as api_key_count
FROM public.user_profiles up
LEFT JOIN public.api_keys ak ON up.user_id = ak.user_id
WHERE up.created_at > NOW() - INTERVAL '30 days'
GROUP BY up.id, up.username
ORDER BY api_key_count DESC
LIMIT 10;

-- Expected: Query planner makes better join/aggregate decisions with updated stats

-- 4. Check index usage statistics are current
SELECT
  schemaname,
  tablename,
  indexrelname,
  idx_scan as scans,
  idx_tup_read as tuples_read,
  idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE tablename IN (
  'user_profiles',
  'api_keys',
  'password_reset_tokens'
)
ORDER BY tablename, idx_scan DESC;

-- ============================================================================
-- OPTIONAL: VACUUM FULL MAINTENANCE (if needed)
-- ============================================================================
-- Only run if you notice excessive dead rows or bloated tables
-- Note: This locks tables, so run during maintenance window

-- VACUUM FULL ANALYZE public.user_profiles;
-- VACUUM FULL ANALYZE public.api_keys;
-- VACUUM FULL ANALYZE public.password_reset_tokens;
-- VACUUM FULL ANALYZE public.kv_store_2e3cda33;

-- ============================================================================
-- SUMMARY OF EXPECTED IMPROVEMENTS
-- ============================================================================
-- After all 6 phases, expect:
--   Phase 1 (RLS Initplan): 30-50% faster RLS policy evaluation
--   Phase 2 (Policies): 20% reduction in per-row overhead
--   Phase 3 (Indexes): 15% faster writes, 50MB+ storage savings
--   Phase 4 (FK Indexes): 40% faster FK lookups and JOINs
--   Phase 5 (Unused): 10-15% faster writes, additional storage savings
--   Phase 6 (Stats): 10-20% better query planner accuracy
--
-- Overall Expected: 30-50% improvement on RLS queries, 20% on general queries
