-- METAR application tables required before advisor remediation migrations.
-- Schema mirrors production METAR project (ktvxijislbtgqapllmuk) at a minimal level for local `supabase db reset`.

CREATE TABLE IF NOT EXISTS public.kv_store_2e3cda33 (
  key TEXT NOT NULL PRIMARY KEY,
  value JSONB NOT NULL
);

ALTER TABLE public.kv_store_2e3cda33 ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS public.upload_batches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.upload_batch_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  batch_id UUID NOT NULL REFERENCES public.upload_batches(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.conversion_uploads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  batch_id UUID REFERENCES public.upload_batches(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.metar_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversion_id UUID NOT NULL REFERENCES public.conversion_uploads(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.storage_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversion_id UUID NOT NULL REFERENCES public.conversion_uploads(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.validation_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversion_id UUID NOT NULL REFERENCES public.conversion_uploads(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.download_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  upload_id UUID NOT NULL REFERENCES public.conversion_uploads(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_uid UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  token TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  used BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.admin_approvals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.evaluation_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  mode TEXT NOT NULL CHECK (mode IN ('single', 'random', 'all')),
  station_count INTEGER NOT NULL DEFAULT 0,
  progress INTEGER NOT NULL DEFAULT 0,
  total_stations INTEGER NOT NULL,
  summary_stats JSONB,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS public.evaluation_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID NOT NULL REFERENCES public.evaluation_jobs(id) ON DELETE CASCADE,
  station_id TEXT NOT NULL,
  tac_input TEXT,
  our_iwxxm TEXT,
  their_iwxxm TEXT,
  comparison_status TEXT NOT NULL CHECK (comparison_status IN ('pass', 'fail', 'error')),
  comparison_detail JSONB,
  errors JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.translation_statistics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  translation_id UUID NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  translation_timestamp TIMESTAMPTZ NOT NULL,
  icao_airport_code VARCHAR(4) NOT NULL CHECK (length(icao_airport_code) = 4),
  icao_region VARCHAR(10) NOT NULL CHECK (icao_region IN ('AFI', 'APAC', 'ESAF', 'EUR', 'MID', 'NAM', 'NAT', 'SAM', 'WAFR')),
  tac_message TEXT NOT NULL,
  iwxxm_version VARCHAR(10) NOT NULL,
  iwxxm_output TEXT,
  translation_status VARCHAR(20) NOT NULL CHECK (translation_status IN ('success', 'partial', 'failed', 'validation_error')),
  validation_layers_passed TEXT[],
  validation_errors JSONB,
  translation_duration_ms INTEGER NOT NULL CHECK (translation_duration_ms >= 0),
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  session_id VARCHAR(255),
  translation_centre_designator VARCHAR(50) NOT NULL DEFAULT 'NOAA-MDL',
  bulletin_reception_time TIMESTAMPTZ,
  bulletin_id VARCHAR(100),
  CONSTRAINT valid_iwxxm_version CHECK (iwxxm_version IN ('2025-2', '2023-1'))
);

CREATE TABLE IF NOT EXISTS public.translation_statistics_summary (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  period_start TIMESTAMPTZ NOT NULL,
  period_end TIMESTAMPTZ NOT NULL,
  interval_type VARCHAR(10) NOT NULL CHECK (interval_type IN ('1h', '1d', '7d', '30d')),
  icao_region VARCHAR(10) CHECK (icao_region IN ('AFI', 'APAC', 'ESAF', 'EUR', 'MID', 'NAM', 'NAT', 'SAM', 'WAFR')),
  iwxxm_version VARCHAR(10),
  total_translations INTEGER NOT NULL,
  successful_translations INTEGER NOT NULL,
  failed_translations INTEGER NOT NULL,
  partial_translations INTEGER NOT NULL,
  success_rate NUMERIC(5,2) NOT NULL,
  average_duration_ms NUMERIC(10,2) NOT NULL,
  median_duration_ms NUMERIC(10,2),
  translations_by_region JSONB,
  translations_by_version JSONB,
  translations_by_airport JSONB,
  validation_layer_success_rates JSONB,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT unique_summary_period UNIQUE (period_start, period_end, interval_type, icao_region, iwxxm_version)
);

ALTER TABLE public.upload_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.upload_batch_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversion_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.download_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evaluation_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evaluation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.translation_statistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.translation_statistics_summary ENABLE ROW LEVEL SECURITY;

CREATE OR REPLACE FUNCTION public.conversion_uploads_touch()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.upload_batches_touch()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.verify_api_key(p_key text)
RETURNS boolean AS $$
BEGIN
  RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION public.set_user_verified(p_email text, p_verified boolean)
RETURNS void AS $$
BEGIN
  NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE OR REPLACE FUNCTION public.update_evaluation_job_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS evaluation_jobs_updated_at ON public.evaluation_jobs;
CREATE TRIGGER evaluation_jobs_updated_at
  BEFORE UPDATE ON public.evaluation_jobs
  FOR EACH ROW
  EXECUTE FUNCTION public.update_evaluation_job_updated_at();

CREATE INDEX IF NOT EXISTS idx_evaluation_jobs_user_id ON public.evaluation_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_results_job_id ON public.evaluation_results(job_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
