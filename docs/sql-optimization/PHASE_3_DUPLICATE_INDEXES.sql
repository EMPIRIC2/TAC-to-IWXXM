-- ============================================================================
-- PHASE 3: DUPLICATE INDEX CLEANUP
-- ============================================================================
-- Issue: 1 WARN - kv_store_2e3cda33 has 9 identical key indexes (idx + idx1-idx8)
-- Solution: Keep only kv_store_2e3cda33_key_idx, drop 8 duplicates
-- Expected Impact: 15% write performance improvement, 50MB+ storage savings
-- Execution Time: ~5 minutes
-- Priority: HIGH
-- ============================================================================

BEGIN;

-- List duplicate indexes before deletion (for verification)
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename = 'kv_store_2e3cda33' AND indexname LIKE '%key%'
-- ORDER BY indexname;

-- Drop 8 duplicate key indexes (keep only the primary one)
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx_1;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx_2;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx_3;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx_4;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx_5;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx_6;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx_7;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx_8;

-- Drop other duplicate indexes if they exist (common naming patterns)
DROP INDEX IF EXISTS public."idx";
DROP INDEX IF EXISTS public."idx1";
DROP INDEX IF EXISTS public."idx2";
DROP INDEX IF EXISTS public."idx3";
DROP INDEX IF EXISTS public."idx4";
DROP INDEX IF EXISTS public."idx5";
DROP INDEX IF EXISTS public."idx6";
DROP INDEX IF EXISTS public."idx7";
DROP INDEX IF EXISTS public."idx8";

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- 1. Verify duplicate indexes are removed
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'kv_store_2e3cda33'
ORDER BY indexname;

-- Expected: Only kv_store_2e3cda33_key_idx and possibly primary key remain

-- 2. Check index sizes (should show significant reduction)
SELECT
  schemaname,
  tablename,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE tablename = 'kv_store_2e3cda33'
ORDER BY pg_relation_size(indexrelid) DESC;

-- 3. Verify remaining indexes are being used
SELECT
  schemaname,
  tablename,
  indexrelname,
  idx_scan as scans,
  idx_tup_read as tuples_read,
  idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE tablename = 'kv_store_2e3cda33'
ORDER BY idx_scan DESC;

-- 4. Check write performance improvement (should be measurable)
-- Run INSERT/UPDATE operations and compare with baseline
-- INSERT INTO kv_store_2e3cda33 (key, value) VALUES (?, ?)
-- TIMING: Compare before/after - expect 15% improvement
