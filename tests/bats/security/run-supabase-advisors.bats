# scripts/security/run-supabase-advisors.sh — bats smoke
load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/security/run-supabase-advisors.sh: is executable and has shebang" {
  [ -x scripts/security/run-supabase-advisors.sh ]
  run head -1 scripts/security/run-supabase-advisors.sh
  [[ "$output" == *"bash"* ]]
}

@test "scripts/security/supabase_advisors.py: is executable python entrypoint" {
  [ -f scripts/security/supabase_advisors.py ]
  run head -1 scripts/security/supabase_advisors.py
  [[ "$output" == *"python"* ]]
}
