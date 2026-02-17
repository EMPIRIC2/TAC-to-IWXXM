#!/usr/bin/env pwsh

# Direct PostgreSQL connection via Session Pooler (better than Transaction pooler for this)
# Session pooler: port 5432, supports persistent connections and full SQL support

$url = "https://ktvxijislbtgqapllmuk.supabase.co"
$projectRef = $url.Split('//')[1].Split('.')[0]
$password = "P2wT^gJ2iLBSwQ!d4"
$host = "aws-0-us-west-2.pooler.supabase.com"
$port = "5432"  # Session pooler port
$user = "postgres.$projectRef"
$db = "postgres"
$userId = "27f7a37c-5575-4e19-a6d6-338755caec1d"

$env:PGPASSWORD = $password

Write-Host "🔌 Attempting direct PostgreSQL connection via Session Pooler..."
Write-Host "Host: $host:$port"
Write-Host "User: $user"
Write-Host "Database: $db"

# SQL commands to execute
$sql = @"
-- Disable RLS to allow update
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- Update admin profile
UPDATE user_profiles
SET 
  is_admin = true,
  approval_status = 'approved',
  updated_at = NOW()
WHERE id = '$userId'::uuid;

-- Re-enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Verify
SELECT id, email, username, is_admin, approval_status, updated_at
FROM user_profiles
WHERE id = '$userId'::uuid;
"@

Write-Host "`n📝 Executing SQL..."
Write-Host $sql
Write-Host "`n---"

# Execute via psql
$sql | & psql -h $host -p $port -U $user -d $db 2>&1

Write-Host "`n✅ Command completed"
