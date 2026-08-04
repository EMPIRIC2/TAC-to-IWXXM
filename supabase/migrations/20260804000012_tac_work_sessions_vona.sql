-- S040 / EV-032 / F32 — allow product=vona on tac_work_sessions (T2.7).
ALTER TABLE public.tac_work_sessions
  DROP CONSTRAINT IF EXISTS tac_work_sessions_product_check;

ALTER TABLE public.tac_work_sessions
  ADD CONSTRAINT tac_work_sessions_product_check
  CHECK (
    product IN ('airmet', 'metar', 'sigmet', 'speci', 'taf', 'vaa', 'tca', 'swxa', 'vona')
  );
