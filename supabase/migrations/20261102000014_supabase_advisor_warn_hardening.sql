-- Harden remaining security advisor WARNs (GraphQL exposure + SECURITY DEFINER RPC).
-- Prefer revoke over waive. Intentional leftovers:
--   - lookup_email_by_username: EXECUTE for anon+authenticated (username login)
--   - is_admin: EXECUTE for authenticated only (RLS helper)
--   - authenticated SELECT on owner-scoped product tables (RLS / PostgREST)
-- Performance advisors are INFO-only (unused indexes / auth pool) — not in this migration.
-- [Corpus: tech-spec] [Corpus: deploy]

BEGIN;

-- ---------------------------------------------------------------------------
-- SECURITY DEFINER: revoke client RPC where not intentional
-- Triggers still run as owner; clients must not call these via /rest/v1/rpc.
-- ---------------------------------------------------------------------------
REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.prevent_privilege_escalation() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.set_updated_at() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.purge_stale_tac_work_sessions() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.set_user_verified(text, boolean) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.verify_api_key(text) FROM PUBLIC, anon, authenticated;

-- is_admin: needed inside RLS for authenticated; never for anon.
REVOKE ALL ON FUNCTION public.is_admin() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated;

-- lookup_email_by_username: username→email for login (anon + authenticated).
REVOKE ALL ON FUNCTION public.lookup_email_by_username(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.lookup_email_by_username(text) TO anon, authenticated;

-- ---------------------------------------------------------------------------
-- GraphQL / PostgREST: strip anon from all product tables still exposed
-- ---------------------------------------------------------------------------
REVOKE ALL ON TABLE public.api_keys FROM anon;
REVOKE ALL ON TABLE public.conversion_uploads FROM anon;
REVOKE ALL ON TABLE public.conversions FROM anon;
REVOKE ALL ON TABLE public.download_log FROM anon;
REVOKE ALL ON TABLE public.evaluation_jobs FROM anon;
REVOKE ALL ON TABLE public.evaluation_results FROM anon;
REVOKE ALL ON TABLE public.iwxxm_ingest_quarantine FROM anon;
REVOKE ALL ON TABLE public.iwxxm_ingest_results FROM anon;
REVOKE ALL ON TABLE public.job_results FROM anon;
REVOKE ALL ON TABLE public.metar_results FROM anon;
REVOKE ALL ON TABLE public.password_reset_tokens FROM anon;
REVOKE ALL ON TABLE public.storage_files FROM anon;
REVOKE ALL ON TABLE public.tac_work_sessions FROM anon;
REVOKE ALL ON TABLE public.upload_batches FROM anon;
REVOKE ALL ON TABLE public.user_profiles FROM anon;

-- Also strip anon from profile tables (already revoked in 013; idempotent).
REVOKE ALL ON TABLE public.tac_profile_rule_packs FROM anon;
REVOKE ALL ON TABLE public.tac_profile_overlays FROM anon;

-- ---------------------------------------------------------------------------
-- Service-role / backend-only tables: strip authenticated JWT exposure
-- (backend uses DATABASE_URL; worker uses service_role — both bypass RLS)
-- ---------------------------------------------------------------------------
REVOKE ALL ON TABLE public.iwxxm_ingest_quarantine FROM authenticated;
REVOKE ALL ON TABLE public.iwxxm_ingest_results FROM authenticated;
REVOKE ALL ON TABLE public.password_reset_tokens FROM authenticated;
REVOKE ALL ON TABLE public.api_keys FROM authenticated;
REVOKE ALL ON TABLE public.conversions FROM authenticated;
REVOKE ALL ON TABLE public.metar_results FROM authenticated;
REVOKE ALL ON TABLE public.job_results FROM authenticated;
REVOKE ALL ON TABLE public.storage_files FROM authenticated;
REVOKE ALL ON TABLE public.validation_results FROM authenticated;
REVOKE ALL ON TABLE public.accessibility_settings FROM authenticated;
REVOKE ALL ON TABLE public.admin_approvals FROM authenticated;
REVOKE ALL ON TABLE public.users FROM authenticated;

COMMIT;
