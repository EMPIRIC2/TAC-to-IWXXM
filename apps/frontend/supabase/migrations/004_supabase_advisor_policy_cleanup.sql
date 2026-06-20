BEGIN;

DROP POLICY IF EXISTS "Admins can read all profiles" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can read own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Admins can update any profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own username" ON public.user_profiles;

CREATE POLICY user_profiles_select_access
  ON public.user_profiles
  FOR SELECT
  TO authenticated
  USING (((SELECT auth.uid()) = id) OR (SELECT public.is_admin()));

CREATE POLICY user_profiles_update_access
  ON public.user_profiles
  FOR UPDATE
  TO authenticated
  USING (((SELECT auth.uid()) = id) OR (SELECT public.is_admin()))
  WITH CHECK (((SELECT auth.uid()) = id) OR (SELECT public.is_admin()));

COMMIT;