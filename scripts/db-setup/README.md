# Database Setup Scripts

SQL scripts for creating and configuring database tables in Supabase.

## Scripts

### create_evaluation_tables.sql
Creates tables for the evaluation system that tracks conversion quality and results.

**Tables created:**
- `evaluation_jobs` - Tracks evaluation job status, progress, and metadata
- `evaluation_results` - Stores individual station evaluation results
- `evaluation_stats` - Contains aggregated statistics per job

**Features:**
- UUID primary keys with automatic generation
- Foreign key constraints with CASCADE delete
- Check constraints for valid enum values (status, mode)
- Timestamps with timezone support
- JSONB columns for flexible data storage

**Usage:**
```sql
-- In Supabase Dashboard SQL Editor
-- Copy and paste the contents, then run
```

Or via psql:
```bash
psql -h db.project.supabase.co \
     -U postgres \
     -d postgres \
     -f create_evaluation_tables.sql
```

### create_translation_statistics_tables.sql
Creates tables for tracking METAR to IWXXM translation statistics and metrics.

**Features:**
- Tracks conversion success rates
- Stores validation results
- Records performance metrics
- Enables analytics and reporting

**Usage:**
Same as above - run in Supabase SQL Editor or via psql.

## Prerequisites

- Supabase project with admin access
- PostgreSQL 12+ (provided by Supabase)
- Proper authentication (service role key or direct psql access)

## Notes

### RLS (Row Level Security)
These scripts create tables but don't automatically configure RLS policies. You may need to add policies based on your security requirements:

```sql
-- Example: Enable RLS
ALTER TABLE evaluation_jobs ENABLE ROW LEVEL SECURITY;

-- Example: Policy for user access
CREATE POLICY "Users can view their own jobs"
  ON evaluation_jobs
  FOR SELECT
  USING (auth.uid() = user_id);
```

### Indexes
The scripts include basic indexes for foreign keys. For production workloads, consider adding additional indexes based on your query patterns:

```sql
-- Example: Index for common queries
CREATE INDEX idx_evaluation_jobs_status 
  ON evaluation_jobs(status);

CREATE INDEX idx_evaluation_jobs_created 
  ON evaluation_jobs(created_at DESC);
```

## Maintenance

### Dropping Tables
To drop tables and start fresh (⚠️ **DESTRUCTIVE**):

```sql
DROP TABLE IF EXISTS evaluation_stats CASCADE;
DROP TABLE IF EXISTS evaluation_results CASCADE;
DROP TABLE IF EXISTS evaluation_jobs CASCADE;
```

### Migrations
For production systems, consider using a migration tool like:
- Supabase Migrations (`supabase db push`)
- Flyway
- Liquibase
- Custom versioned migration scripts

## Related Documentation

- [Supabase SQL Editor](https://supabase.com/docs/guides/database/overview)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- API Evaluation System: `/docs/ARCHITECTURE.md`
