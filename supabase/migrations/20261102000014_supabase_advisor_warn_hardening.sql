-- Harden remaining security advisor WARNs (GraphQL exposure + SECURITY DEFINER RPC).
-- Prefer revoke over waive. Intentional leftovers:
--   - lookup_email_by_username: EXECUTE for anon+authenticated (username login)
--   - is_admin: EXECUTE for authenticated only (RLS helper)
--   - authenticated SELECT on owner-scoped product tables (RLS / PostgREST)
-- Performance advisors are INFO-only (unused indexes / auth pool) — not in this migration.
-- Existence-guarded so preview/staging branches missing legacy tables still apply.

BEGIN;

-- ---------------------------------------------------------------------------
-- SECURITY DEFINER: revoke client RPC where not intentional
-- Triggers still run as owner; clients must not call these via /rest/v1/rpc.
-- ---------------------------------------------------------------------------
DO $$
DECLARE
  fn text;
BEGIN
  FOREACH fn IN ARRAY ARRAY[
    'public.handle_new_user()',
    'public.prevent_privilege_escalation()',
    'public.set_updated_at()',
    'public.purge_stale_tac_work_sessions()',
    'public.set_user_verified(text, boolean)',
    'public.verify_api_key(text)'
  ]
  LOOP
    IF to_regprocedure(fn) IS NOT NULL THEN
      EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC, anon, authenticated', fn);
    END IF;
  END LOOP;

  IF to_regprocedure('public.is_admin()') IS NOT NULL THEN
    EXECUTE 'REVOKE ALL ON FUNCTION public.is_admin() FROM PUBLIC, anon';
    EXECUTE 'GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated';
  END IF;

  IF to_regprocedure('public.lookup_email_by_username(text)') IS NOT NULL THEN
    EXECUTE 'REVOKE ALL ON FUNCTION public.lookup_email_by_username(text) FROM PUBLIC';
    EXECUTE 'GRANT EXECUTE ON FUNCTION public.lookup_email_by_username(text) TO anon, authenticated';
  END IF;
END
$$;

-- ---------------------------------------------------------------------------
-- GraphQL / PostgREST: strip anon (and selected authenticated) where tables exist
-- ---------------------------------------------------------------------------
DO $$
DECLARE
  tbl text;
  anon_tables text[] := ARRAY[
    'api_keys', 'conversion_uploads', 'conversions', 'download_log',
    'evaluation_jobs', 'evaluation_results', 'iwxxm_ingest_quarantine',
    'iwxxm_ingest_results', 'job_results', 'metar_results',
    'password_reset_tokens', 'storage_files', 'tac_work_sessions',
    'upload_batches', 'user_profiles', 'tac_profile_rule_packs',
    'tac_profile_overlays'
  ];
  auth_strip text[] := ARRAY[
    'iwxxm_ingest_quarantine', 'iwxxm_ingest_results', 'password_reset_tokens',
    'api_keys', 'conversions', 'metar_results', 'job_results', 'storage_files',
    'validation_results', 'accessibility_settings', 'admin_approvals', 'users'
  ];
BEGIN
  FOREACH tbl IN ARRAY anon_tables
  LOOP
    IF to_regclass('public.' || tbl) IS NOT NULL THEN
      EXECUTE format('REVOKE ALL ON TABLE public.%I FROM anon', tbl);
    END IF;
  END LOOP;

  FOREACH tbl IN ARRAY auth_strip
  LOOP
    IF to_regclass('public.' || tbl) IS NOT NULL THEN
      EXECUTE format('REVOKE ALL ON TABLE public.%I FROM authenticated', tbl);
    END IF;
  END LOOP;
END
$$;

COMMIT;
