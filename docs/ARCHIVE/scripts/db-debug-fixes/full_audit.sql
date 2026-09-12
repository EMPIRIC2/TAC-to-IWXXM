-- COMPREHENSIVE SCHEMA & DATA AUDIT
-- Run this entire script in Supabase Dashboard SQL Editor

-- 1. Get exact table definition
SELECT 
  column_name,
  data_type,
  is_nullable,
  column_default,
  ordinal_position
FROM information_schema.columns
WHERE table_name = 'user_profiles'
ORDER BY ordinal_position;

-- 2. List ALL indexes on this table
SELECT 
  indexname,
  indexdef
FROM pg_indexes
WHERE tablename = 'user_profiles';

-- 3. List ALL constraints
SELECT 
  constraint_name,
  constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'user_profiles'
ORDER BY constraint_name;

-- 4. List ALL triggers (including disabled ones)
SELECT 
  trigger_name,
  event_manipulation,
  event_object_table,
  action_timing,
  action_orientation,
  trigger_name IN (
    SELECT trigger_name FROM information_schema.triggers WHERE trigger_name ILIKE '%disable%'
  ) AS is_disabled
FROM information_schema.triggers
WHERE event_object_table = 'user_profiles'
ORDER BY trigger_name;

-- 5. Get trigger source code
SELECT
  tgname,
  tgisinternal,
  pg_get_triggerdef(oid) as definition
FROM pg_trigger
WHERE tgrelid = 'user_profiles'::regclass
ORDER BY tgname;

-- 6. Show current admin row with all columns
SELECT * 
FROM user_profiles
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';

-- 7. Try update with RETURNING to see what actually gets returned
UPDATE user_profiles
SET 
  is_admin = true,
  approval_status = 'approved',
  updated_at = NOW()
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d'::uuid
RETURNING id, email, is_admin, approval_status, updated_at;
