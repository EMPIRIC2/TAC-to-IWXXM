#!/usr/bin/env bash
# EV-933 staging ops: Alembic head + PROFILE_OVERLAY_HMAC_SECRET on staging API.
#
# Requires kubectl context for metar-iwxxm-staging (CI: staging env KUBE_CONFIG).
# Prefer Secret patch; if RBAC denies secrets, fall back to Deployment literal env
# (staging unblock — move into metar-api-secrets when SA can patch secrets).
#
# Usage: bash scripts/deploy/doks_staging_ev933_ops.sh
set -euo pipefail

NS="${DOKS_NAMESPACE:-metar-iwxxm-staging}"
JOB_NAME="${ALEMBIC_JOB_NAME:-metar-alembic-upgrade-ev933}"
SECRET_NAME="${API_SECRET_NAME:-metar-api-secrets}"

echo "EV-933 staging ops ns=${NS}"

API_IMG="$(
  kubectl -n "${NS}" get deploy metar-api \
    -o jsonpath='{.spec.template.spec.containers[?(@.name=="api")].image}'
)"
if [[ -z "${API_IMG}" ]]; then
  echo "error: could not resolve metar-api container image" >&2
  exit 1
fi
echo "api image: ${API_IMG}"

# Align initContainer with the rolled API image (rollout historically only set api=).
kubectl -n "${NS}" set image "deploy/metar-api" "alembic-upgrade=${API_IMG}"

HMAC="$(openssl rand -hex 32)"
HMAC_SET_VIA=""

if kubectl -n "${NS}" auth can-i get secrets >/dev/null 2>&1; then
  EXISTING="$(
    kubectl -n "${NS}" get secret "${SECRET_NAME}" \
      -o jsonpath='{.data.PROFILE_OVERLAY_HMAC_SECRET}' 2>/dev/null || true
  )"
  if [[ -z "${EXISTING}" ]]; then
    B64="$(printf '%s' "${HMAC}" | base64 | tr -d '\n')"
    kubectl -n "${NS}" patch secret "${SECRET_NAME}" --type=json \
      -p="[{\"op\":\"add\",\"path\":\"/data/PROFILE_OVERLAY_HMAC_SECRET\",\"value\":\"${B64}\"}]"
    echo "PROFILE_OVERLAY_HMAC_SECRET: added to Secret ${SECRET_NAME}"
    HMAC_SET_VIA="secret"
  else
    echo "PROFILE_OVERLAY_HMAC_SECRET: already present on Secret (left unchanged)"
    HMAC_SET_VIA="secret-existing"
    HMAC=""
  fi
else
  echo "warn: SA cannot get secrets — setting PROFILE_OVERLAY_HMAC_SECRET on Deployment env"
  # Clear any prior literal then set (idempotent for re-runs).
  kubectl -n "${NS}" set env "deploy/metar-api" "PROFILE_OVERLAY_HMAC_SECRET-" >/dev/null 2>&1 || true
  kubectl -n "${NS}" set env "deploy/metar-api" "PROFILE_OVERLAY_HMAC_SECRET=${HMAC}"
  echo "PROFILE_OVERLAY_HMAC_SECRET: set on deploy/metar-api (literal env fallback)"
  HMAC_SET_VIA="deploy-env"
fi
unset HMAC

# One-shot alembic Job on the current API image (init may still have been stale).
kubectl -n "${NS}" delete job "${JOB_NAME}" --ignore-not-found=true
cat <<EOF | kubectl -n "${NS}" apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: ${JOB_NAME}
  labels:
    app.kubernetes.io/name: metar-alembic-upgrade
    app.kubernetes.io/component: migrate
    app.kubernetes.io/part-of: ev-933
spec:
  ttlSecondsAfterFinished: 600
  backoffLimit: 1
  template:
    metadata:
      labels:
        app.kubernetes.io/name: metar-alembic-upgrade
        app.kubernetes.io/component: migrate
    spec:
      restartPolicy: Never
      imagePullSecrets:
        - name: ghcr-pull
      containers:
        - name: alembic-upgrade
          image: ${API_IMG}
          imagePullPolicy: Always
          workingDir: /app/apps/backend
          command: ["python", "-m", "alembic", "-c", "alembic.ini", "upgrade", "head"]
          envFrom:
            - configMapRef:
                name: metar-api-config
            - secretRef:
                name: ${SECRET_NAME}
EOF

echo "Waiting for Job ${JOB_NAME}…"
kubectl -n "${NS}" wait --for=condition=complete "job/${JOB_NAME}" --timeout=180s
echo "--- alembic job logs ---"
kubectl -n "${NS}" logs "job/${JOB_NAME}"
echo "--- end logs ---"

kubectl -n "${NS}" rollout restart "deploy/metar-api"
kubectl -n "${NS}" rollout status "deploy/metar-api" --timeout=180s

INIT_IMG="$(
  kubectl -n "${NS}" get deploy metar-api \
    -o jsonpath='{.spec.template.spec.initContainers[?(@.name=="alembic-upgrade")].image}'
)"
echo "confirm: HMAC via=${HMAC_SET_VIA}"
echo "confirm: initContainer image=${INIT_IMG}"
echo "EV-933 staging ops complete"
