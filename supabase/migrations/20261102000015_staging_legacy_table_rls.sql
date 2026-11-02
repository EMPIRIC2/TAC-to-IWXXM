-- Enable RLS on legacy METAR result tables that preview/staging branches inherit
-- without the older advisor remediations that ran only on primary.
-- No anon/authenticated policies: service_role / DATABASE_URL bypass RLS.
-- Clears security ERROR rls_disabled_in_public on staging-env.
-- [Corpus: tech-spec] [Corpus: deploy]

BEGIN;

DO $$
DECLARE
  tbl text;
BEGIN
  FOREACH tbl IN ARRAY ARRAY[
    'metar_results',
    'storage_files',
    'validation_results'
  ]
  LOOP
    IF to_regclass('public.' || tbl) IS NOT NULL THEN
      EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', tbl);
      EXECUTE format('REVOKE ALL ON TABLE public.%I FROM anon', tbl);
      EXECUTE format('REVOKE ALL ON TABLE public.%I FROM authenticated', tbl);
    END IF;
  END LOOP;
END
$$;

COMMIT;
