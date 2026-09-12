-- Get the CHECK constraint definition
SELECT 
  constraint_name,
  check_clause
FROM information_schema.check_constraints
WHERE constraint_name = 'user_profiles_approval_status_check';

-- Also check if there's a similar one for is_admin
SELECT 
  constraint_name,
  check_clause
FROM information_schema.check_constraints
WHERE constraint_name LIKE '%is_admin%' OR constraint_name LIKE '%admin%';

-- Get ALL check constraints on the table
SELECT 
  constraint_name,
  check_clause
FROM information_schema.check_constraints
WHERE constraint_name IN (
  SELECT constraint_name FROM information_schema.table_constraints 
  WHERE table_name = 'user_profiles'
);
