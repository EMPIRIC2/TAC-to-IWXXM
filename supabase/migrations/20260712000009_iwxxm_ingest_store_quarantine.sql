-- F8: near-RT ingest results + quarantine (ADR-018 / UJ-014)
-- Writers: Supabase service-role JWT from apps/worker (Q20=C)

BEGIN;

CREATE TABLE IF NOT EXISTS public.iwxxm_ingest_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT NOT NULL,
  product TEXT NOT NULL,
  profile TEXT NOT NULL DEFAULT 'annex3',
  source_url TEXT NOT NULL DEFAULT '',
  tac_input TEXT NOT NULL DEFAULT '',
  iwxxm_xml TEXT NOT NULL,
  issues JSONB NOT NULL DEFAULT '[]'::jsonb,
  stage_failed TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_iwxxm_ingest_results_job_created
  ON public.iwxxm_ingest_results (job_id, created_at DESC);

CREATE TABLE IF NOT EXISTS public.iwxxm_ingest_quarantine (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id TEXT NOT NULL,
  product TEXT NOT NULL,
  profile TEXT NOT NULL DEFAULT 'annex3',
  source_url TEXT NOT NULL DEFAULT '',
  tac_input TEXT NOT NULL DEFAULT '',
  iwxxm_xml TEXT,
  issues JSONB NOT NULL DEFAULT '[]'::jsonb,
  stage_failed TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_iwxxm_ingest_quarantine_job_created
  ON public.iwxxm_ingest_quarantine (job_id, created_at DESC);

ALTER TABLE public.iwxxm_ingest_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.iwxxm_ingest_quarantine ENABLE ROW LEVEL SECURITY;

-- No anon/authenticated policies: service_role bypasses RLS for worker writers.
-- Optional read for authenticated admins can be added later.

COMMIT;
