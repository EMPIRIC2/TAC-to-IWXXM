-- F7.e / ADR-020: expand-cutover metar_work_sessions → tac_work_sessions
-- S011 / EV-008 — unified multi-product sessions; one WIP per user total.
-- Admin browse policies intentionally omitted (ADR-021).

BEGIN;

CREATE TABLE IF NOT EXISTS public.tac_work_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  product TEXT NOT NULL CHECK (
    product IN ('airmet', 'metar', 'sigmet', 'speci', 'taf', 'vaa', 'tca')
  ),
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

CREATE INDEX IF NOT EXISTS idx_tac_work_sessions_user_updated
  ON public.tac_work_sessions (user_id, updated_at DESC)
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_tac_work_sessions_user_product
  ON public.tac_work_sessions (user_id, product)
  WHERE deleted_at IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS tac_work_sessions_one_wip_per_user
  ON public.tac_work_sessions (user_id)
  WHERE status = 'wip' AND deleted_at IS NULL;

-- Copy legacy F5 rows; default product=metar when conversion_params lacks product.
INSERT INTO public.tac_work_sessions (
  id,
  user_id,
  product,
  status,
  title,
  manual_tac,
  pending_files,
  converted_results,
  errors,
  issues,
  conversion_params,
  kv_upload_key,
  deleted_at,
  created_at,
  updated_at
)
SELECT
  src.id,
  src.user_id,
  CASE
    WHEN lower(coalesce(src.conversion_params->>'product', 'metar')) IN (
      'airmet', 'metar', 'sigmet', 'speci', 'taf', 'vaa', 'tca'
    )
      THEN lower(coalesce(src.conversion_params->>'product', 'metar'))
    WHEN lower(coalesce(src.conversion_params->>'product', '')) IN ('auto', '')
      THEN 'metar'
    ELSE 'metar'
  END AS product,
  src.status,
  src.title,
  src.manual_tac,
  src.pending_files,
  src.converted_results,
  src.errors,
  src.issues,
  src.conversion_params,
  src.kv_upload_key,
  src.deleted_at,
  src.created_at,
  src.updated_at
FROM public.metar_work_sessions AS src
ON CONFLICT (id) DO NOTHING;

ALTER TABLE public.tac_work_sessions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tac_work_sessions_select_own ON public.tac_work_sessions;
DROP POLICY IF EXISTS tac_work_sessions_insert_own ON public.tac_work_sessions;
DROP POLICY IF EXISTS tac_work_sessions_update_own ON public.tac_work_sessions;
DROP POLICY IF EXISTS tac_work_sessions_delete_own ON public.tac_work_sessions;

CREATE POLICY tac_work_sessions_select_own
  ON public.tac_work_sessions
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid()) = user_id);

CREATE POLICY tac_work_sessions_insert_own
  ON public.tac_work_sessions
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY tac_work_sessions_update_own
  ON public.tac_work_sessions
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY tac_work_sessions_delete_own
  ON public.tac_work_sessions
  FOR DELETE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id);

CREATE OR REPLACE FUNCTION public.tac_work_sessions_touch()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS tac_work_sessions_set_updated_at ON public.tac_work_sessions;
CREATE TRIGGER tac_work_sessions_set_updated_at
  BEFORE UPDATE ON public.tac_work_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.tac_work_sessions_touch();

CREATE OR REPLACE FUNCTION public.purge_stale_tac_work_sessions()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  DELETE FROM public.tac_work_sessions
  WHERE status = 'draft'
    AND deleted_at IS NULL
    AND updated_at < NOW() - INTERVAL '30 days';

  DELETE FROM public.tac_work_sessions
  WHERE deleted_at IS NOT NULL
    AND deleted_at < NOW() - INTERVAL '30 days';
END;
$$;

-- Retarget pg_cron; drop legacy purge job after scheduling the new one.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
    IF EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'purge-metar-work-sessions') THEN
      PERFORM cron.unschedule('purge-metar-work-sessions');
    END IF;
    IF NOT EXISTS (
      SELECT 1 FROM cron.job WHERE jobname = 'purge-tac-work-sessions'
    ) THEN
      PERFORM cron.schedule(
        'purge-tac-work-sessions',
        '0 3 * * *',
        $cmd$SELECT public.purge_stale_tac_work_sessions()$cmd$
      );
    END IF;
  END IF;
END;
$$;

-- Cutover: drop legacy F5 table (expand-cutover; no dual-write window).
DROP TRIGGER IF EXISTS metar_work_sessions_set_updated_at ON public.metar_work_sessions;
DROP TABLE IF EXISTS public.metar_work_sessions CASCADE;
DROP FUNCTION IF EXISTS public.purge_stale_metar_work_sessions();
DROP FUNCTION IF EXISTS public.metar_work_sessions_touch();

COMMIT;
