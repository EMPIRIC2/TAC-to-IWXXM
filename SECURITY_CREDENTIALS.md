# ⚠️ Security: Credentials & Secrets Management

## Critical Issue: Never commit secrets to Git

**Status**: ✅ Fixed
- Removed hardcoded Supabase keys from `frontend/src/utils/supabase/info.ts`
- Updated `.gitignore` to ignore all `.env` files
- Keys must be provided at **build time via environment variables**

## What We Changed

### Before (❌ UNSAFE):
```typescript
// frontend/src/utils/supabase/info.ts
export const projectId = 'ktvxijislbtgqapllmuk';  // ❌ EXPOSED!
export const publicAnonKey = 'eyJhbGciOiJIUzI1NiI...'  // ❌ EXPOSED!
```

### After (✅ SAFE):
```typescript
// frontend/src/utils/supabase/info.ts
export const projectId = import.meta.env.VITE_SUPABASE_URL.split('//')[1]?.split('.')[0] || '';
export const publicAnonKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY || '';

// Shows warnings if not provided
if (!publicAnonKey) {
  console.warn('⚠️ VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY not set.');
}
```

## Files Protected

### .gitignore Configuration

| File | Status | Rule |
|------|--------|------|
| `.env` (root) | ✅ Ignored | Line 138: `Environments` section |
| `.env` (frontend) | ✅ Ignored | Updated to block all `.env` |
| `auth/.env` | ✅ Ignored | Line 5: `# .env contains secrets` |
| `.env.example` | ✓ Tracked | Safe - template with no credentials |

## Environment Variables Required

### For Building the Frontend
```bash
# Required at build time (docker-compose or npm run build)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### For Docker Deployment
```bash
# Copy .env.example and add real credentials
cp .env.example .env
# Edit .env with your actual Supabase keys
docker-compose build  # Keys baked into container at build time
```

### For Local Development
```bash
# Create .env from template (already in .gitignore)
cp .env.example .env

# Add your development Supabase credentials
cat >> .env << 'EOF'
SUPABASE_URL=https://your-dev-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VITE_SUPABASE_URL=https://your-dev-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
EOF

npm run dev  # Frontend reads from .env via Vite
```

## Security Best Practices

### ✅ DO:
- [ ] Use environment variables for all credentials
- [ ] Keep `.env` in `.gitignore` (never commit)
- [ ] Use `.env.example` as a template for developers
- [ ] Provide secrets at **build time** (CI/CD or local setup)
- [ ] Rotate keys if accidentally exposed
- [ ] Use short-lived tokens where possible

### ❌ DON'T:
- [ ] Hardcode secrets in source files
- [ ] Commit `.env` files to Git
- [ ] Log or print credentials
- [ ] Store keys in version control
- [ ] Use the same keys for dev/prod
- [ ] Share credentials in Slack/Email

## If You Accidentally Committed Secrets

1. **Rotate immediately** - Regenerate keys in Supabase dashboard
2. **Remove from history** - Use `git filter-branch` or tools like `git-secrets`
3. **Monitor for abuse** - Check Supabase logs for suspicious activity
4. **Force push** - Only if not yet pushed to public repos

```bash
# Example: Remove file from all commits
git filter-branch --tree-filter 'rm -f frontend/src/utils/supabase/info.ts' HEAD

# Force push (dangerous - only if you're the only contributor)
git push --force-with-lease
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Build Frontend
  env:
    VITE_SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
    VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY: ${{ secrets.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY }}
  run: npm run build
```

### Docker Build Example
```bash
docker build \
  --build-arg VITE_SUPABASE_URL=$VITE_SUPABASE_URL \
  --build-arg VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=$VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY \
  -f frontend/Dockerfile \
  .
```

## Verification Checklist

- [ ] No hardcoded credentials in source files
- [ ] All `.env` files ignored in `.gitignore`
- [ ] `info.ts` only reads from `import.meta.env`
- [ ] `.env.example` provides template without secrets
- [ ] Local `.env` created from `.example` with real creds
- [ ] CI/CD uses GitHub/GitLab secrets, not `.env` files
- [ ] Docker builds pass credentials as build arguments

## References

- [OWASP: Secrets Management](https://owasp.org/www-community/attacks/Sensitive_Data_Exposure)
- [GitHub: Managing secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Supabase: API Keys](https://supabase.com/docs/guides/api#api-keys)
- [12 Factor App: Config](https://12factor.net/config)

---

**Last Updated**: February 10, 2026  
**Status**: Reviewed and updated ✅
