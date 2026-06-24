# Development stage
FROM node:20-alpine AS dev

WORKDIR /app

# Accept development-time Vite environment variables
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY
ARG VITE_APP_URL
ARG VITE_API_BASE_URL

ENV VITE_SUPABASE_URL=${VITE_SUPABASE_URL}
ENV VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=${VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY}
ENV VITE_APP_URL=${VITE_APP_URL}
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 8000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "8000"]

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build arguments for Vite environment variables
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY
ARG VITE_APP_URL
ARG VITE_API_BASE_URL

# Set them as environment variables for the build
ENV VITE_SUPABASE_URL=${VITE_SUPABASE_URL}
ENV VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=${VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY}
ENV VITE_APP_URL=${VITE_APP_URL}
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Generate runtime config.json from VITE_* build args (Alpine lacks bash/python for
# prepare-config.sh; Docker context is apps/frontend only — no repo config/scripts).
RUN node -e "\
const fs = require('fs'); \
const cfg = { \
  environment: 'prod', \
  api: { \
    baseUrl: process.env.VITE_API_BASE_URL || '', \
    frontendUrl: process.env.VITE_APP_URL || '', \
    corsOrigins: process.env.VITE_APP_URL ? [process.env.VITE_APP_URL] : [], \
    disableAuth: false, \
  }, \
  supabase: { \
    url: process.env.VITE_SUPABASE_URL || '', \
    publishableKey: process.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY || '', \
  }, \
}; \
fs.mkdirSync('public', { recursive: true }); \
fs.writeFileSync('public/config.json', JSON.stringify(cfg, null, 2) + '\\n'); \
"

# Build the application (Vite inlines VITE_* env vars; config.json served at runtime)
RUN npx vite build

# Production stage
FROM nginx:alpine AS production

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Runtime substitution: replace placeholder Supabase URL from CI with
# the real value from the VITE_SUPABASE_URL Render environment variable.
COPY <<'SCRIPT' /docker-entrypoint-init.sh
#!/bin/sh
set -e
if [ -n "${VITE_SUPABASE_URL}" ]; then
  find /usr/share/nginx/html -name "*.js" -exec \
    sed -i "s|https://YOUR_PROJECT_REF\.supabase\.co|${VITE_SUPABASE_URL}|g" {} +
fi
exec nginx -g "daemon off;"
SCRIPT
RUN chmod +x /docker-entrypoint-init.sh

EXPOSE 80

CMD ["/docker-entrypoint-init.sh"]