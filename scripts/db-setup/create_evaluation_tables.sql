-- Evaluation Jobs Table
CREATE TABLE IF NOT EXISTS evaluation_jobs (
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

-- Evaluation Results Table
CREATE TABLE IF NOT EXISTS evaluation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES evaluation_jobs(id) ON DELETE CASCADE,
    station_id TEXT NOT NULL,
    tac_input TEXT,
    our_iwxxm TEXT,
    their_iwxxm TEXT,
    comparison_status TEXT NOT NULL CHECK (comparison_status IN ('pass', 'fail', 'error')),
    comparison_detail JSONB,
    errors JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_evaluation_jobs_user_id ON evaluation_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_jobs_status ON evaluation_jobs(status);
CREATE INDEX IF NOT EXISTS idx_evaluation_jobs_created_at ON evaluation_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_evaluation_results_job_id ON evaluation_results(job_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_results_station_id ON evaluation_results(station_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_results_status ON evaluation_results(comparison_status);

-- Row Level Security
ALTER TABLE evaluation_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluation_results ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only see their own jobs and results
CREATE POLICY evaluation_jobs_select_own ON evaluation_jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY evaluation_jobs_insert_own ON evaluation_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY evaluation_jobs_update_own ON evaluation_jobs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY evaluation_results_select_own ON evaluation_results
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM evaluation_jobs
            WHERE evaluation_jobs.id = evaluation_results.job_id
            AND evaluation_jobs.user_id = auth.uid()
        )
    );

CREATE POLICY evaluation_results_insert_system ON evaluation_results
    FOR INSERT WITH CHECK (true);  -- System can insert results

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_evaluation_job_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER evaluation_jobs_updated_at
    BEFORE UPDATE ON evaluation_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_evaluation_job_updated_at();
