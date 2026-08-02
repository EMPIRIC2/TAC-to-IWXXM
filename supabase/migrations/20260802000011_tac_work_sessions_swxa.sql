-- S036 / EV-029 / F28 — allow product=swxa on tac_work_sessions (T11.5).
ALTER TABLE public.tac_work_sessions
  DROP CONSTRAINT IF EXISTS tac_work_sessions_product_check;

ALTER TABLE public.tac_work_sessions
  ADD CONSTRAINT tac_work_sessions_product_check
  CHECK (
    product IN ('airmet', 'metar', 'sigmet', 'speci', 'taf', 'vaa', 'tca', 'swxa')
  );
