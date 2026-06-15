# Docker Configuration

This directory contains Docker configuration files for the METAR to IWXXM backend.

## Files

### Dockerfile
Main application container for the METAR to IWXXM conversion API.

**Build:**
```bash
docker build -f docker/Dockerfile -t metar-backend:latest .
docker build -f docker/Dockerfile -t metar-backend:v1.0.0 .
```

**Run:**
```bash
docker run -p 8000:8000 metar-backend:latest
```

**With environment vars:**
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SUPABASE_URL=... \
  -e SUPABASE_KEY=... \
  metar-backend:latest
```

### Dockerfile.schematron
Specialized container for Schematron XML validation.

Provides `schematron_validator` command-line interface for validating IWXXM XML documents against Schematron rules.

**Build:**
```bash
docker build -f docker/Dockerfile.schematron -t metar-schematron:latest .
```

**Run:**
```bash
docker run -v /path/to/xml:/data metar-schematron:latest validate /data/output.xml
```

## Docker Compose

The repository includes a `docker-compose.yml` at the root level for orchestrating both services:

```bash
docker-compose up -d
```

This starts:
- FastAPI backend (port 8000)
- Frontend (port 3000)
- Database services
- Schema validator services

## Tags & Versioning

Use semantic versioning for tags:
```bash
docker build -f docker/Dockerfile -t metar-backend:v1.2.3 .
docker tag metar-backend:v1.2.3 metar-backend:latest
```

## Environment Variables

Configure via:
1. `.env` file (local development)
2. Docker `--env` / `-e` flags
3. Docker Compose `.env` or `environment` section
4. Kubernetes ConfigMaps/Secrets

### Key Variables

- `DATABASE_URL` - PostgreSQL connection
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key
- `DISABLE_AUTH` - Set to `true` for development
- `LOG_LEVEL` - Logging level (debug, info, warning, error)

## Troubleshooting

### Build fails
```bash
# Clear build cache
docker builder prune

# Rebuild
docker build --no-cache -f docker/Dockerfile .
```

### Container won't start
```bash
# Check logs
docker logs container_id

# Interactive shell
docker run -it metar-backend:latest /bin/bash
```

### Port already in use
```bash
# Use different port
docker run -p 8001:8000 metar-backend:latest
```

---

For more information, see [BACKEND_STRUCTURE.md](../BACKEND_STRUCTURE.md) and [README.md](../README.md).
