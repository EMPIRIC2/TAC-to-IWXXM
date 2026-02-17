-- Check if admin profile exists
SELECT id, email, username, is_admin, approval_status
FROM user_profiles
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';

-- If the above returns a row, run this UPDATE:
UPDATE user_profiles
SET 
  approval_status = 'approved',
  is_admin = true
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';

-- If the above returns NO rows, run this INSERT instead:
INSERT INTO user_profiles (id, email, username, is_admin, approval_status)
VALUES (
  '27f7a37c-5575-4e19-a6d6-338755caec1d',
  'admin@metar.local',
  'admin',
  true,
  'approved'
)
ON CONFLICT (id) DO UPDATE
SET 
  approval_status = 'approved',
  is_admin = true;

-- Verify the result
SELECT id, email, username, is_admin, approval_status
FROM user_profiles
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';
