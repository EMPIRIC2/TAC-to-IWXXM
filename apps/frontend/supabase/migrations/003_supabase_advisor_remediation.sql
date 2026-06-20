BEGIN;

-- Fix mutable search_path warnings on existing functions.
ALTER FUNCTION public.conversion_uploads_touch() SET search_path = public;
ALTER FUNCTION public.upload_batches_touch() SET search_path = public;
ALTER FUNCTION public.verify_api_key(text) SET search_path = public;
ALTER FUNCTION public.set_user_verified(text, boolean) SET search_path = public;
ALTER FUNCTION public.prevent_privilege_escalation() SET search_path = public;
ALTER FUNCTION public.set_updated_at() SET search_path = public;
ALTER FUNCTION public.handle_new_user() SET search_path = public;
ALTER FUNCTION public.handle_updated_at() SET search_path = public;

-- Add covering indexes for foreign keys flagged by the advisor.
CREATE INDEX IF NOT EXISTS idx_conversion_uploads_batch_id
  ON public.conversion_uploads(batch_id);

CREATE INDEX IF NOT EXISTS idx_metar_results_conversion_id
  ON public.metar_results(conversion_id);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id
  ON public.password_reset_tokens(user_id);

CREATE INDEX IF NOT EXISTS idx_storage_files_conversion_id
  ON public.storage_files(conversion_id);

CREATE INDEX IF NOT EXISTS idx_validation_results_conversion_id
  ON public.validation_results(conversion_id);

-- Tighten public exposure on internal-only tables.
ALTER TABLE public.translation_statistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.translation_statistics_summary ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.translation_statistics FROM anon, authenticated;
REVOKE ALL ON TABLE public.translation_statistics_summary FROM anon, authenticated;
REVOKE ALL ON TABLE public.kv_store_2e3cda33 FROM anon, authenticated;

-- Recreate user_profiles policies with initplan-safe auth calls.
DROP POLICY IF EXISTS "Admins can read all profiles" ON public.user_profiles;
DROP POLICY IF EXISTS "Admins can update any profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can read own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own username" ON public.user_profiles;
DROP POLICY IF EXISTS user_profiles_insert_own ON public.user_profiles;
DROP POLICY IF EXISTS user_profiles_select_own ON public.user_profiles;
DROP POLICY IF EXISTS user_profiles_update_own ON public.user_profiles;

CREATE POLICY "Users can read own profile"
  ON public.user_profiles
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid()) = id);

CREATE POLICY "Admins can read all profiles"
  ON public.user_profiles
  FOR SELECT
  TO authenticated
  USING ((SELECT public.is_admin()));

CREATE POLICY "Users can update own username"
  ON public.user_profiles
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid()) = id)
  WITH CHECK ((SELECT auth.uid()) = id);

CREATE POLICY "Admins can update any profile"
  ON public.user_profiles
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.is_admin()))
  WITH CHECK ((SELECT public.is_admin()));

CREATE POLICY "Users can insert own profile"
  ON public.user_profiles
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = id);

-- Recreate upload-related policies with initplan-safe auth calls.
DROP POLICY IF EXISTS batches_owner_select ON public.upload_batches;
DROP POLICY IF EXISTS batches_owner_insert ON public.upload_batches;
DROP POLICY IF EXISTS batches_owner_update ON public.upload_batches;

CREATE POLICY batches_owner_select
  ON public.upload_batches
  FOR SELECT
  TO authenticated
  USING (((SELECT auth.uid()) = user_id) OR (SELECT public.is_admin()));

CREATE POLICY batches_owner_insert
  ON public.upload_batches
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY batches_owner_update
  ON public.upload_batches
  FOR UPDATE
  TO authenticated
  USING (((SELECT auth.uid()) = user_id) OR (SELECT public.is_admin()))
  WITH CHECK (((SELECT auth.uid()) = user_id) OR (SELECT public.is_admin()));

DROP POLICY IF EXISTS batch_items_owner_select ON public.upload_batch_items;
DROP POLICY IF EXISTS batch_items_owner_insert ON public.upload_batch_items;

CREATE POLICY batch_items_owner_select
  ON public.upload_batch_items
  FOR SELECT
  TO authenticated
  USING (((SELECT auth.uid()) = user_id) OR (SELECT public.is_admin()));

CREATE POLICY batch_items_owner_insert
  ON public.upload_batch_items
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS uploads_owner_select ON public.conversion_uploads;
DROP POLICY IF EXISTS uploads_owner_insert ON public.conversion_uploads;
DROP POLICY IF EXISTS uploads_owner_update ON public.conversion_uploads;

CREATE POLICY uploads_owner_select
  ON public.conversion_uploads
  FOR SELECT
  TO authenticated
  USING (((SELECT auth.uid()) = user_id) OR (SELECT public.is_admin()));

CREATE POLICY uploads_owner_insert
  ON public.conversion_uploads
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY uploads_owner_update
  ON public.conversion_uploads
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS downloads_owner_select ON public.download_log;
DROP POLICY IF EXISTS downloads_insert_self ON public.download_log;

CREATE POLICY downloads_owner_select
  ON public.download_log
  FOR SELECT
  TO authenticated
  USING (
    (SELECT public.is_admin())
    OR EXISTS (
      SELECT 1
      FROM public.conversion_uploads AS cu
      WHERE cu.id = download_log.upload_id
        AND cu.user_id = (SELECT auth.uid())
    )
  );

CREATE POLICY downloads_insert_self
  ON public.download_log
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS owner_delete_uuid ON public.password_reset_tokens;
DROP POLICY IF EXISTS owner_insert_uuid ON public.password_reset_tokens;
DROP POLICY IF EXISTS owner_select_uuid ON public.password_reset_tokens;
DROP POLICY IF EXISTS service_manage_uuid ON public.password_reset_tokens;

CREATE POLICY owner_select_uuid
  ON public.password_reset_tokens
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid()) = auth_uid);

CREATE POLICY owner_insert_uuid
  ON public.password_reset_tokens
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = auth_uid);

CREATE POLICY owner_delete_uuid
  ON public.password_reset_tokens
  FOR DELETE
  TO authenticated
  USING ((SELECT auth.uid()) = auth_uid);

CREATE POLICY password_reset_tokens_service_all
  ON public.password_reset_tokens
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Add missing policies for evaluation and approval tables.
DROP POLICY IF EXISTS evaluation_jobs_select_own ON public.evaluation_jobs;
DROP POLICY IF EXISTS evaluation_jobs_insert_own ON public.evaluation_jobs;
DROP POLICY IF EXISTS evaluation_jobs_update_own ON public.evaluation_jobs;
DROP POLICY IF EXISTS evaluation_results_select_own ON public.evaluation_results;
DROP POLICY IF EXISTS evaluation_results_insert_system ON public.evaluation_results;
DROP POLICY IF EXISTS evaluation_results_service_all ON public.evaluation_results;
DROP POLICY IF EXISTS evaluation_jobs_service_all ON public.evaluation_jobs;

CREATE POLICY evaluation_jobs_select_own
  ON public.evaluation_jobs
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid()) = user_id);

CREATE POLICY evaluation_jobs_insert_own
  ON public.evaluation_jobs
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY evaluation_jobs_update_own
  ON public.evaluation_jobs
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY evaluation_jobs_service_all
  ON public.evaluation_jobs
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY evaluation_results_select_own
  ON public.evaluation_results
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1
      FROM public.evaluation_jobs
      WHERE evaluation_jobs.id = evaluation_results.job_id
        AND evaluation_jobs.user_id = (SELECT auth.uid())
    )
  );

CREATE POLICY evaluation_results_insert_system
  ON public.evaluation_results
  FOR INSERT
  TO service_role
  WITH CHECK (true);

CREATE POLICY evaluation_results_service_all
  ON public.evaluation_results
  FOR SELECT
  TO service_role
  USING (true);

DROP POLICY IF EXISTS admin_approvals_requester_select ON public.admin_approvals;
DROP POLICY IF EXISTS admin_approvals_requester_insert ON public.admin_approvals;
DROP POLICY IF EXISTS admin_approvals_service_all ON public.admin_approvals;

CREATE POLICY admin_approvals_requester_select
  ON public.admin_approvals
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid()) = user_id);

CREATE POLICY admin_approvals_requester_insert
  ON public.admin_approvals
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY admin_approvals_service_all
  ON public.admin_approvals
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS kv_store_service_all ON public.kv_store_2e3cda33;

CREATE POLICY kv_store_service_all
  ON public.kv_store_2e3cda33
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS translation_stats_insert_system ON public.translation_statistics;
DROP POLICY IF EXISTS translation_stats_select_admin ON public.translation_statistics;
DROP POLICY IF EXISTS translation_stats_select_own ON public.translation_statistics;
DROP POLICY IF EXISTS translation_stats_admin_select ON public.translation_statistics;
DROP POLICY IF EXISTS translation_stats_service_all ON public.translation_statistics;

CREATE POLICY translation_stats_admin_select
  ON public.translation_statistics
  FOR SELECT
  TO authenticated
  USING ((SELECT public.is_admin()));

CREATE POLICY translation_stats_service_all
  ON public.translation_statistics
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS translation_summary_select_admin ON public.translation_statistics_summary;
DROP POLICY IF EXISTS translation_summary_insert_system ON public.translation_statistics_summary;
DROP POLICY IF EXISTS translation_summary_admin_select ON public.translation_statistics_summary;
DROP POLICY IF EXISTS translation_summary_service_all ON public.translation_statistics_summary;

CREATE POLICY translation_summary_admin_select
  ON public.translation_statistics_summary
  FOR SELECT
  TO authenticated
  USING ((SELECT public.is_admin()));

CREATE POLICY translation_summary_service_all
  ON public.translation_statistics_summary
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Remove indexes the project already treats as unnecessary or clearly duplicated.
DROP INDEX IF EXISTS public.idx_user_profiles_email;
DROP INDEX IF EXISTS public.idx_api_keys_client_id;
DROP INDEX IF EXISTS public.idx_accessibility_user_id;
DROP INDEX IF EXISTS public.idx_evaluation_jobs_status;
DROP INDEX IF EXISTS public.idx_evaluation_jobs_created_at;
DROP INDEX IF EXISTS public.idx_evaluation_results_station_id;
DROP INDEX IF EXISTS public.idx_evaluation_results_status;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx1;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx2;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx3;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx4;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx5;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx6;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx7;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx8;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx9;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx10;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx11;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx12;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx13;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx14;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx15;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx16;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx17;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx18;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx19;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx20;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx21;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx22;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx23;
DROP INDEX IF EXISTS public.kv_store_2e3cda33_key_idx24;

COMMIT;