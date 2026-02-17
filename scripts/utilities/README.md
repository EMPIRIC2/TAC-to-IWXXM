# Utility Scripts

Active utility scripts for data processing, administration, and configuration management.

## Scripts

### parse_airports_csv.py
Parses airport data from CSV files and imports into the database or generates output files.

**Usage:**
```bash
python parse_airports_csv.py [input_file.csv] [options]
```

**Features:**
- Parses ICAO airport codes
- Extracts location coordinates
- Handles elevation data
- Validates airport identifiers

### create_admin_user.py
Creates admin users in the Supabase authentication system.

**Usage:**
```bash
python create_admin_user.py
```

**Required Environment Variables:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Service role key for admin operations
- `ADMIN_EMAIL` - Email address for the admin user
- `ADMIN_PASSWORD` - Password for the admin user

**Features:**
- Creates user with email confirmation
- Sets admin role in user metadata
- Configures appropriate permissions
- Creates user profile with admin and approval status

**Security Note:**
This script requires the service role key, which has full database access. Keep credentials secure in a `.env` file and never commit them to version control.

### extract_email_templates.py
Extracts email templates from Supabase Auth configuration.

**Usage:**
```bash
python extract_email_templates.py
```

**Output:**
Creates JSON files with email template content:
- `email_templates/confirm.json`
- `email_templates/invite.json`
- `email_templates/magic_link.json`
- `email_templates/recovery.json`

**Use Cases:**
- Backup email templates
- Version control for templates
- Template migration between environments

### upload_email_templates.py
Uploads email templates to Supabase Auth configuration.

**Usage:**
```bash
python upload_email_templates.py
```

**Input:**
Reads from JSON files in `email_templates/` directory (created by `extract_email_templates.py`).

**Features:**
- Validates template format
- Updates Supabase Auth configuration
- Preserves template formatting
- Supports all email types (confirmation, invitation, password recovery, magic link)

**Use Cases:**
- Deploy template updates
- Restore templates from backup
- Clone templates across environments

## Prerequisites

### Python Dependencies
```bash
pip install supabase python-dotenv requests
```

Or using uv:
```bash
uv pip install supabase python-dotenv requests
```

### Environment Variables
Create a `.env` file in the project root:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
```

## Email Template Workflow

### Backup Current Templates
```bash
python utilities/extract_email_templates.py
```

### Edit Templates
Edit the JSON files in the `email_templates/` directory.

### Deploy Changes
```bash
python utilities/upload_email_templates.py
```

### Verify
Check your Supabase Dashboard → Authentication → Email Templates

## Security Considerations

### Service Role Key
- Required for: `create_admin_user.py`, `upload_email_templates.py`
- Grants full database access
- Never expose in client-side code
- Rotate periodically
- Store securely (environment variables, secrets manager)

### Best Practices
1. Use `.env` files (added to `.gitignore`)
2. Use separate credentials for dev/staging/production
3. Limit script execution to trusted environments
4. Audit admin user creation regularly
5. Review template changes before deployment

## Troubleshooting

### Authentication Errors
```
Error: Invalid API key
```
- Verify `SUPABASE_URL` is correct
- Check that `SUPABASE_SERVICE_ROLE_KEY` is the service role key (not anon key)
- Ensure no extra whitespace in environment variables

### Permission Errors
```
Error: Insufficient permissions
```
- Service role key required for admin operations
- Check RLS policies if accessing tables directly

### Import Errors
```
ModuleNotFoundError: No module named 'supabase'
```
Install dependencies:
```bash
pip install -r requirements.txt
# or
uv pip install supabase python-dotenv requests
```

## Related Documentation

- [Supabase Auth API](https://supabase.com/docs/reference/javascript/auth-api)
- [Email Template Customization](https://supabase.com/docs/guides/auth/auth-email-templates)
- Backend API: `/backend/README.md`
