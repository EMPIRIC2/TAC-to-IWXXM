-- Deep dive into is_admin and approval_status columns

-- Check column-specific information
SELECT 
  column_name,
  data_type,
  is_nullable,
  column_default,
  ordinal_position,
  (SELECT COUNT(*) FROM information_schema.constraint_column_usage 
   WHERE table_name = 'user_profiles' 
   AND column_name = ic.column_name) as constraint_count
FROM information_schema.columns ic
WHERE table_name = 'user_profiles'
  AND column_name IN ('is_admin', 'approval_status')
ORDER BY ordinal_position;

-- Check for check constraints
SELECT 
  constraint_name,
  check_clause
FROM information_schema.check_constraints
WHERE constraint_name LIKE '%admin%' OR constraint_name LIKE '%approval%';

-- List ALL triggers on the table with their definitions
SELECT 
  t.trigger_name,
  t.event_manipulation,
  t.action_timing,
  pg_get_triggerdef(tr.oid) as full_definition
FROM information_schema.triggers t
JOIN pg_trigger tr ON t.trigger_name = tr.tgname
WHERE t.event_object_table = 'user_profiles'
ORDER BY t.trigger_name;

-- Check column privileges
SELECT 
  grantee,
  privilege_type,
  column_name,
  is_grantable
FROM information_schema.column_privileges
WHERE table_name = 'user_profiles'
  AND column_name IN ('is_admin', 'approval_status')
ORDER BY column_name, grantee;

-- Try to see if columns are part of any unique constraint
SELECT 
  tc.constraint_name,
  tc.constraint_type
FROM information_schema.constraint_column_usage ccu
JOIN information_schema.table_constraints tc 
  ON ccu.constraint_name = tc.constraint_name
WHERE ccu.table_name = 'user_profiles'
  AND ccu.column_name IN ('is_admin', 'approval_status');
