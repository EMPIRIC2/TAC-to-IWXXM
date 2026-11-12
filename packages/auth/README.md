# auth

Service library for Supabase Auth JWT verification and Auth API proxy helpers.

HTTP route handlers are not part of this package. Operator login uses the
frontend Supabase client; the backend verifies access tokens with JWKS.
