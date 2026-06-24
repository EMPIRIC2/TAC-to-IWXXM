-- F5: per-user METAR work sessions (Draft → WIP → Finished + Failed)
-- ADR-011, ADR-012

BEGIN;

CREATE TABLE IF NOT EXISTS public.metar_work_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  status TEXT NOT NULL CHECK (status IN ('draft', 'wip', 'finished', 'failed')),
  title TEXT NOT NULL DEFAULT '',
  manual_tac TEXT NOT NULL DEFAULT '',
  pending_files JSONB NOT NULL DEFAULT '[]'::jsonb,
  converted_results JSONB NOT NULL DEFAULT '[]'::jsonb,
  errors JSONB NOT NULL DEFAULT '[]'::jsonb,
  issues JSONB NOT NULL DEFAULT '[]'::jsonb,
  conversion_params JSONB NOT NULL DEFAULT '{}'::jsonb,
  kv_upload_key TEXT,
  deleted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metar_work_sessions_user_updated
  ON public.metar_work_sessions (user_id, updated_at DESC)
  WHERE deleted_at IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS metar_work_sessions_one_wip_per_user
  ON public.metar_work_sessions (user_id)
  WHERE status = 'wip' AND deleted_at IS NULL;

ALTER TABLE public.metar_work_sessions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS metar_work_sessions_select_own ON public.metar_work_sessions;
DROP POLICY IF EXISTS metar_work_sessions_insert_own ON public.metar_work_sessions;
DROP POLICY IF EXISTS metar_work_sessions_update_own ON public.metar_work_sessions;
DROP POLICY IF EXISTS metar_work_sessions_delete_own ON public.metar_work_sessions;
DROP POLICY IF EXISTS metar_work_sessions_admin_select ON public.metar_work_sessions;

CREATE POLICY metar_work_sessions_select_own
  ON public.metar_work_sessions
  FOR SELECT
  TO authenticated
  USING (
    deleted_at IS NULL
    AND (
      (SELECT auth.uid()) = user_id
      OR (SELECT public.is_admin())
    )
  );

CREATE POLICY metar_work_sessions_insert_own
  ON public.metar_work_sessions
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY metar_work_sessions_update_own
  ON public.metar_work_sessions
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY metar_work_sessions_delete_own
  ON public.metar_work_sessions
  FOR DELETE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id);

CREATE OR REPLACE FUNCTION public.metar_work_sessions_touch()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS metar_work_sessions_set_updated_at ON public.metar_work_sessions;
CREATE TRIGGER metar_work_sessions_set_updated_at
  BEFORE UPDATE ON public.metar_work_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.metar_work_sessions_touch();

CREATE OR REPLACE FUNCTION public.purge_stale_metar_work_sessions()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  DELETE FROM public.metar_work_sessions
  WHERE status = 'draft'
    AND deleted_at IS NULL
    AND updated_at < NOW() - INTERVAL '30 days';

  DELETE FROM public.metar_work_sessions
  WHERE deleted_at IS NOT NULL
    AND deleted_at < NOW() - INTERVAL '30 days';
END;
$$;

-- pg_cron schedule (idempotent)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
    IF NOT EXISTS (
      SELECT 1 FROM cron.job WHERE jobname = 'purge-metar-work-sessions'
    ) THEN
      PERFORM cron.schedule(
        'purge-metar-work-sessions',
        '0 3 * * *',
        $cmd$SELECT public.purge_stale_metar_work_sessions()$cmd$
      );
    END IF;
  END IF;
END;
$$;

COMMIT;
