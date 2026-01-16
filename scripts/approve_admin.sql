-- Approve admin user and set admin flag
UPDATE user_profiles
SET 
  approval_status = 'approved',
  is_admin = true
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';

-- Verify the update
SELECT id, email, username, is_admin, approval_status
FROM user_profiles
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';
