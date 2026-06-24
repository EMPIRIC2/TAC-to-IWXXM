-- Fix infinite recursion in RLS policies by using a helper function

DROP POLICY IF EXISTS "Admins can read all profiles" ON public.user_profiles;
DROP POLICY IF EXISTS "Admins can update any profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own username" ON public.user_profiles;

CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.user_profiles
    WHERE id = auth.uid() AND is_admin = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE POLICY "Admins can read all profiles"
  ON public.user_profiles
  FOR SELECT
  USING (public.is_admin());

CREATE POLICY "Users can update own username"
  ON public.user_profiles
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Admins can update any profile"
  ON public.user_profiles
  FOR UPDATE
  USING (public.is_admin());

GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated;

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

GRANT EXECUTE ON FUNCTION public.lookup_email_by_username(TEXT) TO authenticated, anon;

CREATE OR REPLACE FUNCTION public.prevent_privilege_escalation()
RETURNS TRIGGER AS $$
BEGIN
  IF NOT (SELECT public.is_admin()) THEN
    NEW.approval_status := OLD.approval_status;
    NEW.is_admin := OLD.is_admin;
    NEW.approved_at := OLD.approved_at;
    NEW.approved_by := OLD.approved_by;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS prevent_privilege_escalation_trigger ON public.user_profiles;
CREATE TRIGGER prevent_privilege_escalation_trigger
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.prevent_privilege_escalation();
