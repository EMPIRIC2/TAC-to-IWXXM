-- Disable the privilege escalation trigger, update admin, then re-enable it
-- Run this in Supabase Dashboard SQL Editor

-- Step 1: Disable the trigger
ALTER TABLE user_profiles DISABLE TRIGGER prevent_privilege_escalation_trigger;

-- Step 2: Update admin profile
UPDATE user_profiles
SET 
  is_admin = true,
  approval_status = 'approved',
  updated_at = NOW()
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d'::uuid;

-- Step 3: Re-enable the trigger
ALTER TABLE user_profiles ENABLE TRIGGER prevent_privilege_escalation_trigger;

-- Step 4: Verify the update worked
SELECT id, email, username, is_admin, approval_status, updated_at
FROM user_profiles
WHERE id = '27f7a37c-5575-4e19-a6d6-338755caec1d';
