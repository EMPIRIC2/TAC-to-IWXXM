-- Enable RLS on ConversionProfile tables created via Alembic (F7.w).
-- Clears security advisor ERROR rls_disabled_in_public on:
--   public.tac_profile_rule_packs
--   public.tac_profile_overlays
-- Backend product paths use DATABASE_URL (role bypasses RLS); policies
-- protect PostgREST / direct JWT access. [Corpus: tech-spec] [Corpus: product §F7]

BEGIN;

-- ---------------------------------------------------------------------------
-- tac_profile_rule_packs — owner-scoped (no shared column)
-- ---------------------------------------------------------------------------
ALTER TABLE public.tac_profile_rule_packs ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.tac_profile_rule_packs FROM anon;
REVOKE ALL ON TABLE public.tac_profile_rule_packs FROM authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.tac_profile_rule_packs
  TO authenticated;

DROP POLICY IF EXISTS tac_profile_rule_packs_select_own ON public.tac_profile_rule_packs;
DROP POLICY IF EXISTS tac_profile_rule_packs_insert_own ON public.tac_profile_rule_packs;
DROP POLICY IF EXISTS tac_profile_rule_packs_update_own ON public.tac_profile_rule_packs;
DROP POLICY IF EXISTS tac_profile_rule_packs_delete_own ON public.tac_profile_rule_packs;

CREATE POLICY tac_profile_rule_packs_select_own
  ON public.tac_profile_rule_packs
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid()) = user_id);

CREATE POLICY tac_profile_rule_packs_insert_own
  ON public.tac_profile_rule_packs
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY tac_profile_rule_packs_update_own
  ON public.tac_profile_rule_packs
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY tac_profile_rule_packs_delete_own
  ON public.tac_profile_rule_packs
  FOR DELETE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id);

-- ---------------------------------------------------------------------------
-- tac_profile_overlays — owner writes; owner or shared=true reads
-- ---------------------------------------------------------------------------
ALTER TABLE public.tac_profile_overlays ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.tac_profile_overlays FROM anon;
REVOKE ALL ON TABLE public.tac_profile_overlays FROM authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.tac_profile_overlays
  TO authenticated;

DROP POLICY IF EXISTS tac_profile_overlays_select_own_or_shared
  ON public.tac_profile_overlays;
DROP POLICY IF EXISTS tac_profile_overlays_insert_own ON public.tac_profile_overlays;
DROP POLICY IF EXISTS tac_profile_overlays_update_own ON public.tac_profile_overlays;
DROP POLICY IF EXISTS tac_profile_overlays_delete_own ON public.tac_profile_overlays;

CREATE POLICY tac_profile_overlays_select_own_or_shared
  ON public.tac_profile_overlays
  FOR SELECT
  TO authenticated
  USING (
    (SELECT auth.uid()) = user_id
    OR shared IS TRUE
  );

CREATE POLICY tac_profile_overlays_insert_own
  ON public.tac_profile_overlays
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY tac_profile_overlays_update_own
  ON public.tac_profile_overlays
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY tac_profile_overlays_delete_own
  ON public.tac_profile_overlays
  FOR DELETE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id);

COMMIT;
