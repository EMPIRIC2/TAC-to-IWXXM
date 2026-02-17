# Archived Database Debug and Fix Scripts

This directory contains historical one-off scripts used for debugging, fixing, and diagnosing database issues during development. These scripts are preserved for reference but are not part of active development workflows.

## Why Archived?

These scripts were:
- **One-time fixes** for specific issues
- **Emergency patches** that have been superseded by proper migrations
- **Debugging utilities** used during development
- **Experimental scripts** that helped diagnose problems

They are kept for:
- Historical reference
- Understanding past issues and solutions
- Potential future debugging needs
- Documentation of problem-solving approaches

## Categories

### Admin User Management
Scripts for debugging admin user approval and role assignment issues:
- `approve_admin_api.py` - Direct admin approval via API
- `approve_admin.sql` - SQL script for admin approval
- `approve_admin_final.sql` - Final version of admin approval fix
- `approve_admin_psql.ps1` - PowerShell wrapper for psql execution
- `create_admin_user.py` - ⚠️ **Moved to `/scripts/utilities/`** (still active)
- `fix_admin_profile.sql` - Fix corrupt admin profile data
- `debug_admin_update.sql` - Debug admin update operations

### RLS (Row Level Security) Issues
Scripts for fixing Row Level Security policy problems:
- `EMERGENCY_FIX_RLS.sql` - Emergency RLS infinite recursion fix
- `fix_rls_policies.sql` - RLS policy corrections
- `fix_rls_service_role.sql` - Service role RLS access fix

### Trigger Management
Scripts for diagnosing and fixing database triggers:
- `check_triggers.sql` - Comprehensive trigger inspection
- `check_triggers_simple.sql` - Simple trigger check
- `get_trigger_function.sql` - Extract trigger function definitions
- `drop_broken_trigger.sql` - Remove broken triggers
- `disable_trigger_update.sql` - Temporarily disable triggers

### Audit and Diagnostics
Scripts for auditing database state and diagnosing issues:
- `full_audit.sql` - Complete database audit
- `deep_column_audit.sql` - Detailed column-level audit
- `test_column_updates.sql` - Test column update operations
- `get_check_constraint.sql` - Extract check constraint definitions

## Usage Guidelines

### ⚠️ Important Warnings

1. **DO NOT run these scripts in production** without careful review
2. Many scripts were **one-time fixes** and may not be idempotent
3. Some scripts use **destructive operations** (DROP, DELETE, ALTER)
4. Scripts may reference **outdated schema** versions
5. **EMERGENCY_FIX_RLS.sql** disables security - use with extreme caution

### If You Need to Use These Scripts

1. **Review the script thoroughly** - Understand what it does
2. **Check if the issue still exists** - Schema may have changed
3. **Test in development first** - Never run untested SQL in production
4. **Backup your data** - Take a snapshot before running
5. **Consider modern alternatives** - Proper migrations or new scripts may be better

### Better Alternatives

Instead of using these archived scripts:

- **For schema changes**: Create proper migrations in `/scripts/db-setup/`
- **For admin operations**: Use `/scripts/utilities/create_admin_user.py`
- **For debugging**: Use Supabase Dashboard SQL Editor with read-only queries
- **For RLS issues**: Review current policies in dashboard and docs

## Historical Context

### Admin Approval Issues (2024-2025)
Early in development, admin user approval had issues with:
- Trigger conflicts
- RLS policy recursion
- Transaction pooler complications
- Role assignment timing

These scripts were created to diagnose and patch those issues. The root causes have since been fixed in the application code and proper migrations.

### RLS Infinite Recursion (2025)
The `EMERGENCY_FIX_RLS.sql` script was created when RLS policies caused infinite recursion. The issue was:
- Policies that referenced the table they protected
- Nested policy evaluations
- Service role not properly bypassing RLS

**Resolution**: RLS policies were redesigned and the emergency fix is no longer needed.

### Trigger Debugging (2024-2025)
Various trigger issues required debugging:
- Triggers firing in wrong order
- Trigger functions with errors
- Performance issues from heavy triggers

Scripts helped identify and fix these. Current schema has properly designed triggers.

## Archived On

February 16, 2026

## Related Documentation

- Current database setup: `/scripts/db-setup/`
- Active utilities: `/scripts/utilities/`
- Supabase documentation: https://supabase.com/docs
- Project architecture: `/docs/ARCHITECTURE.md`

## Notes for Future Developers

If you encounter similar issues:

1. Check if these scripts provide insights
2. Don't copy-paste blindly - adapt to current schema
3. Consider whether a proper migration is better
4. Document new diagnostic scripts if you create them
5. Update this README with lessons learned
