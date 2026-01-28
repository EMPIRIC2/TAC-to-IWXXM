# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Build arguments for environment variables
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY
ARG VITE_APP_URL=http://localhost:8000
ARG VITE_BACKEND_URL=http://localhost:8001
ARG VITE_AUTH_URL=http://localhost:8002

# Set environment variables for build
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=$VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY
ENV VITE_APP_URL=$VITE_APP_URL
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL
ENV VITE_AUTH_URL=$VITE_AUTH_URL

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
