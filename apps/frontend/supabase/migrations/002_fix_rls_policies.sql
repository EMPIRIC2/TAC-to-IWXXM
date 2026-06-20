-- Fix infinite recursion in RLS policies by using a helper function

-- Drop existing problematic policies
DROP POLICY IF EXISTS "Admins can read all profiles" ON user_profiles;
DROP POLICY IF EXISTS "Admins can update any profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own username" ON user_profiles;

-- Create a helper function to check if current user is admin
-- This function uses SECURITY DEFINER to bypass RLS
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.user_profiles
    WHERE id = auth.uid() AND is_admin = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Create new policies using the helper function

-- Policy: Admins can read all profiles (using helper function to avoid recursion)
CREATE POLICY "Admins can read all profiles"
  ON user_profiles
  FOR SELECT
  USING (public.is_admin());

-- Policy: Users can update their own non-sensitive fields
-- Note: This allows users to update their username, but they cannot
-- change approval_status or is_admin due to the column-level trigger
CREATE POLICY "Users can update own username"
  ON user_profiles
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Policy: Admins can update any profile (for approvals)
CREATE POLICY "Admins can update any profile"
  ON user_profiles
  FOR UPDATE
  USING (public.is_admin());

-- Grant execute permission on the helper function
GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated;

-- Create a function to lookup email by username (bypasses RLS for login purposes)
CREATE OR REPLACE FUNCTION public.lookup_email_by_username(p_username TEXT)
RETURNS TEXT AS $$
DECLARE
  v_email TEXT;
BEGIN
  SELECT email INTO v_email
  FROM public.user_profiles
  WHERE username = p_username
  LIMIT 1;
  
  RETURN v_email;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Grant execute permission to authenticated and anon users (for login)
GRANT EXECUTE ON FUNCTION public.lookup_email_by_username(TEXT) TO authenticated, anon;

-- Create a trigger function to prevent users from modifying sensitive fields
CREATE OR REPLACE FUNCTION public.prevent_privilege_escalation()
RETURNS TRIGGER AS $$
BEGIN
  -- If user is not admin, prevent them from changing approval_status or is_admin
  IF NOT (SELECT public.is_admin()) THEN
    -- Preserve original values for sensitive fields
    NEW.approval_status := OLD.approval_status;
    NEW.is_admin := OLD.is_admin;
    NEW.approved_at := OLD.approved_at;
    NEW.approved_by := OLD.approved_by;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply the trigger
DROP TRIGGER IF EXISTS prevent_privilege_escalation_trigger ON user_profiles;
CREATE TRIGGER prevent_privilege_escalation_trigger
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.prevent_privilege_escalation();
