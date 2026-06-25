-- F5 fix: allow owner soft-delete/restore of METAR work sessions.
-- BUG-2026-06-25-work-session-soft-delete-rls-42501
--
-- PostgreSQL enforces a table's SELECT policy USING expression as an implicit
-- WITH CHECK on UPDATE. The original SELECT policy required `deleted_at IS NULL`,
-- so setting `deleted_at` (soft-delete) produced a row that no longer satisfied
-- SELECT and the UPDATE was rejected with 42501
-- ("new row violates row-level security policy"). It also hid soft-deleted rows
-- from owners, breaking `include_deleted` listing and restore.
--
-- Fix: scope SELECT visibility to ownership only. Filtering of soft-deleted rows
-- is handled at the application/query layer (WorkSessionService applies
-- `deleted_at IS NULL` unless include_deleted), so this does not widen
-- cross-user access.

BEGIN;

DROP POLICY IF EXISTS metar_work_sessions_select_own ON public.metar_work_sessions;

CREATE POLICY metar_work_sessions_select_own
  ON public.metar_work_sessions
  FOR SELECT
  TO authenticated
  USING (
    (SELECT auth.uid()) = user_id
    OR (SELECT public.is_admin())
  );

COMMIT;
