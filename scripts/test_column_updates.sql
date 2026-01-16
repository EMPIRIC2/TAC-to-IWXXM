-- TEST: Update different columns individually to see which ones work

-- Test 1: Update only is_admin
UPDATE user_profiles
SET is_admin = true
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d'
RETURNING id, is_admin;

-- Test 2: Update only approval_status  
UPDATE user_profiles
SET approval_status = 'approved'
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d'
RETURNING id, approval_status;

-- Test 3: Update only username (control test with a different column)
UPDATE user_profiles
SET username = 'admin_test'
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d'
RETURNING id, username;

-- Verify all current values
SELECT id, email, username, is_admin, approval_status
FROM user_profiles
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';
