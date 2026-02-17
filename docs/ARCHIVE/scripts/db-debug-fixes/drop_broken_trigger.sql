-- Drop the broken trigger that references a non-existent function
-- This trigger was blocking updates to is_admin and approval_status
DROP TRIGGER prevent_privilege_escalation_trigger ON user_profiles;

-- Verify the trigger is gone
SELECT 
  trigger_name,
  event_manipulation,
  action_timing
FROM information_schema.triggers
WHERE event_object_table = 'user_profiles'
ORDER BY trigger_name;
