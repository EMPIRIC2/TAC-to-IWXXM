-- Check for ANY triggers on user_profiles table
SELECT 
  trigger_name,
  event_manipulation,
  action_timing,
  action_orientation
FROM information_schema.triggers
WHERE event_object_table = 'user_profiles'
ORDER BY trigger_name;

-- Get trigger definitions
SELECT 
  n.nspname as schema_name,
  t.relname as table_name,
  tg.tgname as trigger_name,
  pg_get_triggerdef(tg.oid) as trigger_definition
FROM pg_trigger tg
JOIN pg_class t ON tg.tgrelid = t.oid
JOIN pg_namespace n ON t.relnamespace = n.oid
WHERE t.relname = 'user_profiles'
ORDER BY tg.tgname;
