# Supabase Security Linter Fixes

Complete remediation guide for all 8 Supabase security issues identified in the audit.

## Executive Summary

| Priority | Issues | Status | Action |
|----------|--------|--------|--------|
| **CRITICAL** 🔴 | 3 ERROR | Enable RLS, create policies | Week 1 |
| **HIGH** 🟠 | 4 WARN | Fix functions, optimize policies | Week 2 |
| **INFO** 🔵 | 1 INFO | Add/remove policies | Week 3 |

---

## WEEK 1: Critical Security Fixes (ERRORS)

### Issue 1: RLS Disabled on `users` Table
**Severity**: 🔴 CRITICAL ERROR  
**Risk**: Unauthorized access to user records  
**Fix Time**: 5 minutes

```sql
-- Enable RLS on users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only read their own record
CREATE POLICY "Users can read own profile" ON public.users
  FOR SELECT
  USING (auth.uid() = id);

-- Create policy: Users can update their own record
CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Create policy: Service role (backend) can do everything
CREATE POLICY "Service role can manage all" ON public.users
  AS PERMISSIVE
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
```

### Issue 2: RLS Disabled on `api_keys` Table
**Severity**: 🔴 CRITICAL ERROR  
**Risk**: Unauthorized access to API credentials  
**Fix Time**: 5 minutes

```sql
-- Enable RLS on api_keys table
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only read/update their own keys
CREATE POLICY "Users can read own API keys" ON public.api_keys
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create API keys" ON public.api_keys
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own API keys" ON public.api_keys
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own API keys" ON public.api_keys
  FOR DELETE
  USING (auth.uid() = user_id);

-- Create policy: Service role bypass
CREATE POLICY "Service role manages all" ON public.api_keys
  AS PERMISSIVE
  FOR ALL
  USING (auth.role() = 'service_role');
```

### Issue 3: RLS Disabled on `password_reset_tokens` Table
**Severity**: 🔴 CRITICAL ERROR  
**Risk**: Token exposure, unauthorized password resets  
**Fix Time**: 5 minutes

```sql
-- Enable RLS on password_reset_tokens table
ALTER TABLE public.password_reset_tokens ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only see their own tokens
CREATE POLICY "Users can read own reset tokens" ON public.password_reset_tokens
  FOR SELECT
  USING (auth.uid() = user_id);

-- Create policy: Service role manages all
CREATE POLICY "Service role manages all tokens" ON public.password_reset_tokens
  AS PERMISSIVE
  FOR ALL
  USING (auth.role() = 'service_role');

-- Additional: Automatically delete expired tokens
CREATE OR REPLACE FUNCTION delete_expired_reset_tokens()
RETURNS void AS $$
BEGIN
  DELETE FROM public.password_reset_tokens
  WHERE created_at < NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schedule to run daily (if using pg_cron)
-- SELECT cron.schedule('delete-expired-tokens', '0 0 * * *', 'SELECT delete_expired_reset_tokens()');
```

### Issue 4: Sensitive Token Column Exposed
**Severity**: 🔴 CRITICAL ERROR  
**Risk**: Direct token exposure in queries  
**Fix Time**: 10 minutes

```sql
-- Create a view that hashes/masks tokens (don't expose directly)
CREATE OR REPLACE VIEW api_keys_safe AS
SELECT 
  id,
  user_id,
  name,
  -- Show only first 8 and last 4 characters
  CASE WHEN key IS NOT NULL 
    THEN CONCAT(LEFT(key, 8), '...', RIGHT(key, 4))
    ELSE NULL 
  END AS key_preview,
  created_at,
  last_used_at,
  is_active
FROM public.api_keys
WHERE auth.uid() = user_id
  OR auth.role() = 'service_role';

-- Grant access to view
GRANT SELECT ON api_keys_safe TO authenticated;
GRANT ALL ON api_keys_safe TO service_role;

-- Revoke direct access to key column
ALTER TABLE public.api_keys DISABLE ROW LEVEL SECURITY;
CREATE POLICY "No direct key access" ON public.api_keys
  FOR ALL
  USING (false);
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
```

---

## WEEK 2: High-Priority Fixes (WARNINGS)

### Issue 5: Function Search Path Mutable
**Severity**: 🟠 HIGH WARNING  
**Risk**: Security vulnerability in custom functions  
**Fix Time**: 10 minutes

```sql
-- Fix: Set search_path to restricted value in functions
CREATE OR REPLACE FUNCTION get_user_profile(user_id uuid)
RETURNS TABLE (id uuid, email text, username text) 
SECURITY DEFINER
SET search_path = public, extensions
AS $$
BEGIN
  RETURN QUERY
  SELECT u.id, u.email, u.username
  FROM public.users u
  WHERE u.id = user_id
    AND u.id = auth.uid();
END;
$$ LANGUAGE plpgsql;

-- Apply to all functions that might be vulnerable
-- List functions to update:
SELECT p.proname, n.nspname 
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
  AND prosecdef = true;  -- SECURITY DEFINER functions

-- For each function, add: SET search_path = public
```

### Issue 6: Leaked Password Protection Disabled
**Severity**: 🟠 HIGH WARNING  
**Risk**: Compromised password use not detected  
**Fix Time**: 5 minutes

```sql
-- Enable leaked password check
UPDATE auth.config
SET leaked_password_check_enabled = true;

-- Verify setting
SELECT * FROM auth.config WHERE key = 'leaked_password_check_enabled';

-- Or use Supabase Dashboard:
-- 1. Go to Authentication → Security
-- 2. Enable "Check password for compromises"
-- 3. Save changes
```

### Issue 7: Auth RLS Initplan Issues (Performance)
**Severity**: 🟠 HIGH WARNING  
**Risk**: Performance degradation, slow queries  
**Fix Time**: 15 minutes

```sql
-- Issue: Using auth.uid() in multiple places causes re-evaluation
-- Solution: Use SELECT with subquery pattern

-- BEFORE (Bad - evaluates auth.uid() multiple times):
SELECT * FROM public.users u
WHERE u.id = auth.uid()
  AND EXISTS (
    SELECT 1 FROM public.api_keys k
    WHERE k.user_id = auth.uid()  -- Evaluated again
      AND k.is_active = true
  );

-- AFTER (Good - evaluates auth.uid() once):
SELECT * FROM public.users u
WHERE u.id = (SELECT auth.uid())
  AND EXISTS (
    SELECT 1 FROM public.api_keys k
    WHERE k.user_id = (SELECT auth.uid())
      AND k.is_active = true
  );

-- Update all policies to use this pattern:
DROP POLICY IF EXISTS "policy_name" ON table_name;

CREATE POLICY "policy_name" ON table_name
  FOR SELECT
  USING (user_id = (SELECT auth.uid()));
```

### Issue 8: Multiple Permissive Policies (Performance)
**Severity**: 🟠 HIGH WARNING  
**Risk**: Multiple policy evaluations, poor performance  
**Fix Time**: 20 minutes

```sql
-- Issue: Too many separate permissive policies
-- Solution: Combine policies into one with OR conditions

-- BEFORE (Bad - 3 separate policies):
CREATE POLICY "own_records" ON table_name
  USING (user_id = auth.uid());

CREATE POLICY "admin_access" ON table_name
  USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "service_role" ON table_name
  USING (auth.role() = 'service_role');

-- AFTER (Good - single combined policy):
DROP POLICY "own_records" ON table_name;
DROP POLICY "admin_access" ON table_name;
DROP POLICY "service_role" ON table_name;

CREATE POLICY "users_select_policy" ON table_name
  FOR SELECT
  USING (
    user_id = (SELECT auth.uid())
    OR auth.jwt() ->> 'role' = 'admin'
    OR auth.role() = 'service_role'
  );
```

### Issue 9: Duplicate Indexes on `kv_store`
**Severity**: 🟠 HIGH WARNING  
**Risk**: Wasted storage, slower writes  
**Fix Time**: 5 minutes

```sql
-- Find duplicate indexes
SELECT
  schemaname, tablename, indexname
FROM pg_indexes
WHERE tablename = 'kv_store'
ORDER BY indexname;

-- Identify and drop duplicates (keep one)
-- Example if you have duplicate key indexes:
DROP INDEX IF EXISTS idx_kv_store_key_2;  -- Drop duplicate
DROP INDEX IF EXISTS idx_kv_store_key_old; -- Drop old version

-- Keep only necessary index:
CREATE UNIQUE INDEX IF NOT EXISTS idx_kv_store_key 
ON public.kv_store(key);

-- Analyze to update statistics
ANALYZE public.kv_store;
```

---

## WEEK 3: Informational Fix (INFO)

### Issue 10: RLS Enabled but No Policy on `kv_store`
**Severity**: 🔵 INFO  
**Risk**: Table is locked down completely (may be intentional)  
**Fix Time**: 5 minutes  
**Options**: 1) Add policies OR 2) Disable RLS

#### Option A: Add RLS Policies (Recommended if table is user-specific)

```sql
-- If kv_store is application-wide settings (not user-specific):
CREATE POLICY "Allow service role" ON public.kv_store
  AS PERMISSIVE
  FOR ALL
  USING (auth.role() = 'service_role');

-- If kv_store stores user preferences:
ALTER TABLE public.kv_store ADD COLUMN user_id uuid REFERENCES auth.users(id);

CREATE POLICY "Users can read/write own kv_store" ON public.kv_store
  FOR ALL
  USING (user_id = (SELECT auth.uid()) OR auth.role() = 'service_role');
```

#### Option B: Disable RLS if Not Needed

```sql
-- If this table doesn't need security restrictions:
ALTER TABLE public.kv_store DISABLE ROW LEVEL SECURITY;
```

---

## Implementation Timeline

### Week 1 (Critical - Do First!)
- [ ] Enable RLS on `users` table + create policies (5 min)
- [ ] Enable RLS on `api_keys` table + create policies (5 min)
- [ ] Enable RLS on `password_reset_tokens` table + create policies (5 min)
- [ ] Create view for safe token access (10 min)
- **Total: ~25 minutes**

### Week 2 (High Priority)
- [ ] Fix function search_path (10 min)
- [ ] Enable leaked password check (5 min)
- [ ] Update all queries to use (SELECT auth.uid()) pattern (15 min)
- [ ] Combine multiple policies (20 min)
- [ ] Drop duplicate indexes (5 min)
- **Total: ~55 minutes**

### Week 3 (Information)
- [ ] Add/remove kv_store policies (5 min)
- **Total: ~5 minutes**

---

## Testing Your Fixes

### Test RLS Policies
```sql
-- Test as authenticated user
SET ROLE authenticated;
SELECT current_user, auth.uid();

-- Try to read other user's data (should fail)
SELECT * FROM public.users WHERE id != auth.uid();

-- Try to read own data (should succeed)
SELECT * FROM public.users WHERE id = auth.uid();

-- Reset role
SET ROLE postgres;
```

### Test Performance
```sql
-- Check query performance before/after
EXPLAIN ANALYZE
SELECT * FROM public.users
WHERE id = (SELECT auth.uid());

-- Compare with slow version
EXPLAIN ANALYZE
SELECT * FROM public.users
WHERE id = auth.uid();
```

### Verify Indexes
```sql
-- List all indexes on kv_store
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'kv_store';

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE tablename = 'kv_store';
```

---

## Monitoring After Implementation

### Monitor for Policy Issues
```sql
-- Check for policy enforcement
SELECT tablename, policyname, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename;
```

### Monitor for Performance Issues
```sql
-- Find slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
WHERE query LIKE '%users%' OR query LIKE '%api_keys%'
ORDER BY mean_time DESC;
```

---

## Rollback Plan

If something breaks, you can rollback changes:

```sql
-- Disable RLS on a table
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;

-- Drop all policies on a table
DROP POLICY IF EXISTS "Users can read own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "Service role can manage all" ON public.users;

-- Restore original function
CREATE OR REPLACE FUNCTION get_user_profile(user_id uuid)
RETURNS TABLE (id uuid, email text, username text) 
AS $$ /* original implementation */ $$ LANGUAGE plpgsql;
```

---

## Additional Resources

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/sql-security.html)
- [Function Security](https://www.postgresql.org/docs/current/sql-createfunction.html)
- [Performance Tuning](https://www.postgresql.org/docs/current/performance.html)

---

## Checklist for Completion

- [ ] All CRITICAL issues fixed and tested
- [ ] All HIGH priority issues fixed and tested
- [ ] Performance verified with EXPLAIN ANALYZE
- [ ] RLS policies confirmed working
- [ ] Team trained on new policies
- [ ] Documentation updated
- [ ] Monitoring configured
- [ ] Backup created before deployment
