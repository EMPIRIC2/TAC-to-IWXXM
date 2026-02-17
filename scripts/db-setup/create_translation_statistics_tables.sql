-- Translation Statistics Table for ICAO OPMET Compliance
-- Implements indefinite retention policy (User Decision 1)

CREATE TABLE IF NOT EXISTS translation_statistics (
    -- Primary identifier
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    translation_id UUID NOT NULL UNIQUE,
    
    -- Timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    translation_timestamp TIMESTAMPTZ NOT NULL,
    
    -- Airport and region identification
    icao_airport_code VARCHAR(4) NOT NULL CHECK (length(icao_airport_code) = 4),
    icao_region VARCHAR(10) NOT NULL CHECK (icao_region IN ('AFI', 'APAC', 'ESAF', 'EUR', 'MID', 'NAM', 'NAT', 'SAM', 'WAFR')),
    
    -- Input/Output
    tac_message TEXT NOT NULL,
    iwxxm_version VARCHAR(10) NOT NULL,
    iwxxm_output TEXT,  -- NULL if translation failed
    
    -- Translation result
    translation_status VARCHAR(20) NOT NULL CHECK (translation_status IN ('success', 'partial', 'failed', 'validation_error')),
    validation_layers_passed TEXT[],  -- Array of passed layers
    validation_errors JSONB,  -- Detailed validation errors by layer
    
    -- Performance metrics
    translation_duration_ms INTEGER NOT NULL CHECK (translation_duration_ms >= 0),
    
    -- User context
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    
    -- Translation Centre metadata
    translation_centre_designator VARCHAR(50) NOT NULL DEFAULT 'NOAA-MDL',
    bulletin_reception_time TIMESTAMPTZ,
    bulletin_id VARCHAR(100),
    
    -- Indexes for common queries
    CONSTRAINT valid_iwxxm_version CHECK (iwxxm_version IN ('2025-2', '2023-1'))
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_translation_stats_timestamp ON translation_statistics(translation_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_translation_stats_airport ON translation_statistics(icao_airport_code);
CREATE INDEX IF NOT EXISTS idx_translation_stats_region ON translation_statistics(icao_region);
CREATE INDEX IF NOT EXISTS idx_translation_stats_version ON translation_statistics(iwxxm_version);
CREATE INDEX IF NOT EXISTS idx_translation_stats_status ON translation_statistics(translation_status);
CREATE INDEX IF NOT EXISTS idx_translation_stats_user ON translation_statistics(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_translation_stats_created ON translation_statistics(created_at DESC);

-- Composite index for date range queries with filters
CREATE INDEX IF NOT EXISTS idx_translation_stats_timestamp_region ON translation_statistics(translation_timestamp DESC, icao_region);
CREATE INDEX IF NOT EXISTS idx_translation_stats_timestamp_version ON translation_statistics(translation_timestamp DESC, iwxxm_version);

-- GIN index for JSONB validation_errors
CREATE INDEX IF NOT EXISTS idx_translation_stats_validation_errors ON translation_statistics USING GIN(validation_errors);

-- Row Level Security (RLS)
ALTER TABLE translation_statistics ENABLE ROW LEVEL SECURITY;

-- Policies: Allow system to insert, admins to query all, users to query own
CREATE POLICY translation_stats_insert_system ON translation_statistics
    FOR INSERT WITH CHECK (true);  -- System/service can always insert

CREATE POLICY translation_stats_select_admin ON translation_statistics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.user_id = auth.uid()
            AND user_profiles.is_admin = true
        )
    );

CREATE POLICY translation_stats_select_own ON translation_statistics
    FOR SELECT USING (
        user_id = auth.uid()
        OR user_id IS NULL  -- Allow viewing non-authenticated translations
    );

-- Summary statistics table for pre-computed aggregations
CREATE TABLE IF NOT EXISTS translation_statistics_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Time period
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    interval_type VARCHAR(10) NOT NULL CHECK (interval_type IN ('1h', '1d', '7d', '30d')),
    
    -- Filters (NULL means "all")
    icao_region VARCHAR(10) CHECK (icao_region IN ('AFI', 'APAC', 'ESAF', 'EUR', 'MID', 'NAM', 'NAT', 'SAM', 'WAFR')),
    iwxxm_version VARCHAR(10),
    
    -- Aggregated metrics
    total_translations INTEGER NOT NULL,
    successful_translations INTEGER NOT NULL,
    failed_translations INTEGER NOT NULL,
    partial_translations INTEGER NOT NULL,
    success_rate NUMERIC(5,2) NOT NULL,
    average_duration_ms NUMERIC(10,2) NOT NULL,
    median_duration_ms NUMERIC(10,2),
    
    -- Distributions (JSONB for flexibility)
    translations_by_region JSONB,
    translations_by_version JSONB,
    translations_by_airport JSONB,
    validation_layer_success_rates JSONB,
    
    -- Metadata
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate summaries
    CONSTRAINT unique_summary_period UNIQUE (period_start, period_end, interval_type, icao_region, iwxxm_version)
);

-- Indexes for summary table
CREATE INDEX IF NOT EXISTS idx_summary_period ON translation_statistics_summary(period_start DESC, period_end DESC);
CREATE INDEX IF NOT EXISTS idx_summary_interval ON translation_statistics_summary(interval_type);
CREATE INDEX IF NOT EXISTS idx_summary_region ON translation_statistics_summary(icao_region) WHERE icao_region IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_summary_version ON translation_statistics_summary(iwxxm_version) WHERE iwxxm_version IS NOT NULL;

-- RLS for summary table
ALTER TABLE translation_statistics_summary ENABLE ROW LEVEL SECURITY;

CREATE POLICY translation_summary_select_admin ON translation_statistics_summary
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.user_id = auth.uid()
            AND user_profiles.is_admin = true
        )
    );

CREATE POLICY translation_summary_insert_system ON translation_statistics_summary
    FOR INSERT WITH CHECK (true);

-- Function to refresh summary statistics
CREATE OR REPLACE FUNCTION refresh_translation_statistics_summary(
    p_interval_type VARCHAR,
    p_period_start TIMESTAMPTZ,
    p_period_end TIMESTAMPTZ
)
RETURNS void AS $$
BEGIN
    -- Delete existing summary for this period
    DELETE FROM translation_statistics_summary
    WHERE interval_type = p_interval_type
    AND period_start = p_period_start
    AND period_end = p_period_end;
    
    -- Insert new summary (overall, no filters)
    INSERT INTO translation_statistics_summary (
        period_start,
        period_end,
        interval_type,
        icao_region,
        iwxxm_version,
        total_translations,
        successful_translations,
        failed_translations,
        partial_translations,
        success_rate,
        average_duration_ms,
        median_duration_ms,
        translations_by_region,
        translations_by_version,
        translations_by_airport,
        validation_layer_success_rates
    )
    SELECT
        p_period_start,
        p_period_end,
        p_interval_type,
        NULL,  -- Overall summary
        NULL,
        COUNT(*),
        SUM(CASE WHEN translation_status = 'success' THEN 1 ELSE 0 END),
        SUM(CASE WHEN translation_status = 'failed' THEN 1 ELSE 0 END),
        SUM(CASE WHEN translation_status = 'partial' THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN translation_status = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2),
        ROUND(AVG(translation_duration_ms)::numeric, 2),
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY translation_duration_ms),
        (SELECT jsonb_object_agg(icao_region, cnt) FROM (
            SELECT icao_region, COUNT(*) as cnt
            FROM translation_statistics
            WHERE translation_timestamp >= p_period_start AND translation_timestamp < p_period_end
            GROUP BY icao_region
        ) r),
        (SELECT jsonb_object_agg(iwxxm_version, cnt) FROM (
            SELECT iwxxm_version, COUNT(*) as cnt
            FROM translation_statistics
            WHERE translation_timestamp >= p_period_start AND translation_timestamp < p_period_end
            GROUP BY iwxxm_version
        ) v),
        NULL,  -- Skip airport breakdown for performance
        NULL   -- Skip validation details for performance
    FROM translation_statistics
    WHERE translation_timestamp >= p_period_start
    AND translation_timestamp < p_period_end;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust role names as needed)
GRANT SELECT ON translation_statistics TO authenticated;
GRANT INSERT ON translation_statistics TO service_role;
GRANT SELECT ON translation_statistics_summary TO authenticated;
GRANT INSERT, UPDATE, DELETE ON translation_statistics_summary TO service_role;

-- Comments for documentation
COMMENT ON TABLE translation_statistics IS 'ICAO OPMET compliant translation records with indefinite retention';
COMMENT ON TABLE translation_statistics_summary IS 'Pre-computed aggregated statistics for performance';
COMMENT ON COLUMN translation_statistics.translation_id IS 'Unique UUID for each translation operation';
COMMENT ON COLUMN translation_statistics.icao_region IS 'ICAO regional office jurisdiction (9 regions)';
COMMENT ON COLUMN translation_statistics.validation_layers_passed IS 'Array of validation layers successfully passed';
COMMENT ON COLUMN translation_statistics.translation_duration_ms IS 'Processing time in milliseconds';
