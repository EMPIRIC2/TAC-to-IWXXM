-- Check for triggers that might be modifying the values
-- Run this in Supabase Dashboard SQL Editor

-- List all triggers on user_profiles
SELECT 
  t.trigger_name,
  t.event_manipulation,
  t.event_object_table,
  t.action_timing,
  t.action_orientation,
  pg_get_triggerdef(tr.oid) as trigger_definition
FROM information_schema.triggers t
JOIN pg_trigger tr ON t.trigger_name = tr.tgname
WHERE t.event_object_table = 'user_profiles';

-- If there are triggers, check what they're doing by looking at trigger functions
SELECT 
  p.oid,
  p.proname as function_name,
  p.prosrc as function_source
FROM pg_proc p
WHERE p.proname LIKE '%profile%' OR p.proname LIKE '%user%';

-- Also check for any constraints
SELECT
  constraint_name,
  constraint_type,
  table_name
FROM information_schema.table_constraints
WHERE table_name = 'user_profiles';

-- Check column defaults that might be overriding values
SELECT 
  column_name,
  data_type,
  column_default,
  is_nullable
FROM information_schema.columns
WHERE table_name = 'user_profiles'
ORDER BY ordinal_position;
