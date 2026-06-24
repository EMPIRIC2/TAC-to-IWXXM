BEGIN;

-- S003: Remaining METAR advisor fixes (idempotent).

ALTER FUNCTION public.is_admin() SET search_path = public;
ALTER FUNCTION public.lookup_email_by_username(text) SET search_path = public;

-- Allow authenticated inserts for evaluation results on owned jobs (no service_role REST).
DROP POLICY IF EXISTS evaluation_results_insert_own ON public.evaluation_results;

CREATE POLICY evaluation_results_insert_own
  ON public.evaluation_results
  FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1
      FROM public.evaluation_jobs
      WHERE evaluation_jobs.id = evaluation_results.job_id
        AND evaluation_jobs.user_id = (SELECT auth.uid())
    )
  );

COMMIT;
