# Porkbun DNS cutover — apex → DOKS LB (#948)

> **Target LB (prod)**: `168.144.12.70`  
> **Goal**: `tac-to-iwxxm.com` and `www.tac-to-iwxxm.com` resolve to the DOKS load balancer so Ingress `metar-frontend-apex` can redirect to `https://app.tac-to-iwxxm.com$request_uri`.  
> **Corpus**: [Corpus: deploy] [Corpus: product §F30]

Do **not** change `app` or `api` records (they already point at the LB).

## 1. Open DNS for the domain

1. Sign in at [https://porkbun.com](https://porkbun.com).
2. **Account** → **Domain Management** → select **`tac-to-iwxxm.com`**.
3. Open **DNS** / **DNS Records** (sometimes under **Details** → **DNS**).

## 2. Remove parking / URL forward

1. If **URL Forwarding** / **Link** / parking is enabled for the apex or `www`, **disable or delete** it (this is what sends traffic to `tac-to-iwxxm-com.l.ink`).
2. Delete any leftover **ALIAS**, **CNAME**, or **A** records that point apex/`www` at Porkbun parking (`uixie.porkbun.com`, `*.porkbun.com`, or A `207.207.210.*`).

## 3. Set apex (root) → LB

Add (or replace with):

| Type | Host | Answer / Value | TTL |
|------|------|----------------|-----|
| **A** | `@` (or blank / `tac-to-iwxxm.com`) | `168.144.12.70` | 600 (or default) |

- Only **one** apex A to the LB (remove duplicate parking As).
- Prefer **A**, not CNAME, at the apex (and better for cert-manager HTTP-01).

## 4. Set www → LB

Either:

| Type | Host | Answer | Notes |
|------|------|--------|-------|
| **A** | `www` | `168.144.12.70` | Preferred (same as apex) |

or, if you already use apex A and Porkbun allows:

| Type | Host | Answer |
|------|------|--------|
| **CNAME** | `www` | `tac-to-iwxxm.com` |

Do **not** leave `www` as CNAME → `uixie.porkbun.com`.

## 5. Leave alone

| Host | Expected |
|------|----------|
| `app` | A → `168.144.12.70` (already) |
| `api` | A → `168.144.12.70` (already) |
| `*.staging` / staging hosts | unchanged |

## 6. Save and wait

1. Save records in Porkbun.
2. Wait for TTL (often a few minutes; up to the old TTL).
3. Check from your machine:

```bash
dig +short A tac-to-iwxxm.com
# expect: 168.144.12.70

dig +short A www.tac-to-iwxxm.com
# expect: 168.144.12.70 (or CNAME then that A)

curl -sI "https://tac-to-iwxxm.com/foo?bar=1" | egrep -i '^(HTTP|location):'
# After Ingress is applied on prod: 301/308 → https://app.tac-to-iwxxm.com/foo?bar=1
# Before Ingress apply: may be 404/default backend until metar-frontend-apex is live
```

## 7. Apply Ingress on prod (when DNS is correct)

Manifests are already on branch `evolve/EV-057-…` (`deploy/doks/overlays/prod/ingress-frontend-apex.yaml`). After merge to `stage` / promote path you choose:

```bash
# kube context = prod cluster
kubectl apply -k deploy/doks/overlays/prod
kubectl -n metar-iwxxm get ingress metar-frontend-apex
kubectl -n metar-iwxxm describe certificate metar-frontend-apex-tls   # if cert-manager CR exists
```

cert-manager should issue `metar-frontend-apex-tls` for `tac-to-iwxxm.com` + `www.tac-to-iwxxm.com` once DNS hits the LB.

## 8. Done checklist

- [ ] No Porkbun URL forward / `l.ink`
- [ ] Apex A → `168.144.12.70`
- [ ] `www` → LB (A or CNAME to apex)
- [ ] `dig` shows LB IPs
- [ ] Ingress `metar-frontend-apex` applied on prod
- [ ] `curl -sI https://tac-to-iwxxm.com/foo?bar=1` → permanent redirect to app with path/query
