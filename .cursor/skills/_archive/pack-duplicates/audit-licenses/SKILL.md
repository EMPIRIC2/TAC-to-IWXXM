---
name: audit-licenses
description: >
  Spawns the license-researcher subagent to recursively audit the full dependency tree
  (dependencies of dependencies via lockfiles) and corpus fixtures / staged data assets for
  closed-source, proprietary, EULA, non-commercial-only (NC), or unknown licenses. Produces
  a Flags report and optional drift check against docs/dependency-inventory.md and
  docs/spec.md §Data. Use before adding dependencies or weights, during evolve or
  tech-plan reviews, release prep, or when the user asks about OSS compliance, license risk,
  or closed-source packages.
---

# Audit Licenses

Find **closed-source, non-OSS, and non-commercial-only (NC) dependencies** — including
**recursive transitives** and **pre-trained corpus fixtures / staged data assets** — by
delegating to the **license-researcher** subagent (`.cursor/agents/license-researcher.md`).

**Default**: full tree from lockfile(s) **plus** every weight/data asset referenced in
`docs/spec.md §Data`, `docs/dependency-inventory.md` (Pre-trained Models / Weights),
and runtime download URLs in `src/weights.py` (or equivalent). A clean direct dependency can
still fail compliance if it pulls a proprietary or NC transitive; weights can fail even when
all pip packages are OSI-approved.

**Not legal advice** — engineering assessment only. Recommend legal review for redistribution
or SaaS when findings are ambiguous.

## Commercial-use policy (hard — cannot use)

This project **cannot ship or depend on anything licensed for non-commercial use only**.
Treat NC and equivalent terms as **BLOCKED** (same severity as hard-exclusion packages):
audit **fails** if any are found in scope — remove or replace before merge, staging, or deploy.

| Signal | Examples | Tier |
|--------|----------|------|
| SPDX / identifier | `CC-BY-NC-*`, `CC-BY-NC-SA-*`, `CC-NC-*`, `PolyForm-Noncommercial-*` | **BLOCKED** |
| License name / text | "Non-Commercial", "Noncommercial", "NC", "not for commercial use", "academic / research use only" when commercial use is excluded | **BLOCKED** |
| Asset terms | Zenodo/model-card "non-commercial", "NC", or research-only that forbids commercial SaaS or redistribution for profit | **BLOCKED** |
| Dual / multi-license | Any offered license line that is NC-only (user must not rely on a commercial option that is not actually granted) | **BLOCKED** |

**Not NC (do not auto-BLOCK)** — still may be FLAG for other reasons:

- Permissive OSI licenses (MIT, Apache-2.0, BSD) — OK for commercial use
- **COPYLEFT** (GPL, AGPL) — commercial use often allowed with obligations; tier COPYLEFT, not BLOCKED for NC
- Proprietary **runtime infra** (e.g. Modal SDK, NVIDIA CUDA EULA) — commercial SaaS may be permitted under vendor ToS; tier FLAG, document ToS — distinct from NC-only content licenses

When in doubt whether terms forbid commercial use, tier **BLOCKED** and cite evidence; do not mark OK.

## State management

**Canonical:** repo-root [`workflow-state.yaml`](../../workflow-state.yaml) §`stages.audit-licenses`.
Rules: [workflow-state-reference.md](../workflow-state-reference.md).

On start: `status: in_progress`. On completion: `status: completed`, set `report` path,
`flags_count`, append report to `artifacts`. On BLOCKED findings, add `issue_log` entries.

## When to use

| Trigger | Scope |
|---------|--------|
| Full repo audit | All lockfiles — **every** direct + transitive package — **and** all staged weights/data assets |
| New dependency | Named package(s) + **recursive** tree (re-resolve lock or dry-run install) |
| New weight / dataset | Named asset(s) + upstream license/terms (Zenodo record, model card, paper, host ToS) |
| PR / diff | Packages or weight URLs added or changed in the change |
| Inventory drift | Reconcile `docs/dependency-inventory.md` vs lockfile **and** weights vs `docs/spec.md §Data` |

Skip this skill for application code licensing (your repo's own LICENSE file) unless the
user explicitly includes it.

## Inputs

Collect from the user or conversation (ask only if missing):

| Input | Required | Default |
|-------|----------|---------|
| Repository root | Yes | Workspace root |
| Scope | No | `full-recursive` (default) — full lockfile tree **+ weights/data assets**; use `direct-only` or `packages-only` / `weights-only` only if user explicitly requests a subset |
| Write report file | No | `docs/license-audit-{YYYY-MM-DD}.md` when BLOCKED/FLAGS found or user asks |

## Workflow

### Phase 1 — Spawn license-researcher

Launch **one** Task with `subagent_type: license-researcher`.

**Prompt template** (fill placeholders):

```text
Audit dependency licenses for closed-source / non-OSS / non-commercial-only (NC) compliance
(recursive / full tree) and corpus fixtures / staged data assets.

Repository root: {repo_root}
Scope: {full-recursive | direct-only | packages-only | weights-only | packages: ... | assets: ... | PR paths: ...}

Requirements:
1. Follow .cursor/agents/license-researcher.md (Phases 0, 0b, 0c, 1–4) with these overrides:
2. **NC / non-commercial-only (BLOCKED):** Flag every package, transitive, and weight/data asset
   whose license or terms restrict use to non-commercial, academic-only, or research-only contexts
   where commercial deployment (including commercial SaaS) is not permitted. Use tier BLOCKED.
   Include SPDX NC variants (CC-BY-NC-*, CC-NC-*, PolyForm-Noncommercial-*), explicit "non-commercial"
   / "NC" text, and asset terms that forbid commercial use. List in "Blocked — hard exclusion list"
   under a subsection "Non-commercial-only (NC)".
3. **Recursive package audit (required unless scope is weights-only or direct-only):**
   enumerate every package in lockfile(s) via uv tree / npm ls --all / equivalent;
   license-check each node, not just top-level manifest entries.
4. **Weights / data assets audit (required unless scope is packages-only or direct-only):**
   enumerate every pretrained weight, checkpoint, and staged dataset from
   docs/spec.md §Data, docs/dependency-inventory.md (Pre-trained Models / Weights),
   and download URLs in src/weights.py (or equivalent). Resolve license/terms from Zenodo
   record metadata, upstream README/LICENSE, model cards, and host terms — not from pip.
5. Resolve SPDX from lockfiles + registry/LICENSE files; do not guess licenses.
6. Check the hard exclusion list (PyRosetta / pyrosetta — CANNOT use) at any depth and in
   weight/training-data references; BLOCKED if found.
7. Flag every proprietary, custom-EULA, UNKNOWN, and non-OSI package (direct or transitive)
   and every weight/data asset with restrictive or unclear redistribution terms (tier FLAG unless NC → BLOCKED).
8. For each FLAG/BLOCKED package: include depth and dependency chain (A → B → C).
9. Populate **Transitive issues summary** for depth ≥ 1 package findings.
10. Populate **Model weights and data assets** section with per-asset license/terms and tier.
11. Cross-check docs/dependency-inventory.md and docs/spec.md §Data if present; report drift.
12. Return the full markdown report from Phase 4 of the agent spec.

Deliverable: complete License audit report with Executive summary (direct vs transitive counts,
weights/data asset counts), Blocked section (PyRosetta + NC), Flags table, Transitive issues
summary, and Model weights section populated. State audit failed if any BLOCKED (including NC).
```

Wait for completion. Do not duplicate the audit in the parent — use the subagent output.

If Task fails or `license-researcher` is unavailable: read
`.cursor/agents/license-researcher.md` and run the same workflow in the parent (fallback),
applying the **Commercial-use policy** and NC → BLOCKED rules above.

### Phase 2 — Present findings to the user

1. **Lead with BLOCKED** — hard-exclusion hits (PyRosetta / pyrosetta) and **NC / non-commercial-only**
   licenses (packages, transitives, weights) — require immediate removal or replacement.
2. **Then other FLAGS** — closed-source / non-OSS / UNKNOWN (note depth and chain); NC must not appear here if already BLOCKED.
3. **Weights / data FLAGS** — proprietary, research-only (non-NC), or UNKNOWN terms.
4. **Transitive-only issues** — summarize depth ≥ 1 findings (dependencies of dependencies).
5. **COPYLEFT** — separate short list if any (commercial use may be OK with obligations).
6. **Executive summary** — direct vs transitive counts, weight/asset counts, max depth, overall risk.
7. **Drift** — if `docs/dependency-inventory.md` or `docs/spec.md §Data` differs from resolved findings.
8. **Recommendations** — remove, replace, pin alternate direct dep, choose NC-free checkpoint, or escalate to legal.

If **no BLOCKED** (including NC) or **FLAG-tier** packages or assets in scope, state that explicitly
and still list REVIEW-tier items.

### Phase 3 — Optional follow-up (user-driven)

Use **AskQuestion** only when the user needs a decision:

| Situation | Ask |
|-----------|-----|
| BLOCKED NC package or asset | Remove/replace now, or defer (audit remains failed)? |
| FLAG dep is required infra (e.g. Modal, CUDA) | Accept risk and document in inventory, or pursue alternative? |
| FLAG weight (research-only but not NC / unclear Zenodo terms) | Accept for internal use only, replace checkpoint, or escalate to legal? |
| New dep proposed | Approve add / find OSS + commercial-use alternative / defer |
| New weight URL proposed | Approve add / find openly licensed + commercial-OK checkpoint / defer |
| Inventory drift | Patch `docs/dependency-inventory.md` License column (packages **and** weights) now? |

Do not edit `docs/dependency-inventory.md` without user approval.

If the user approves a report file, write the subagent's full report to
`docs/license-audit-{YYYY-MM-DD}.md`.

## Integration

| Stage / skill | Use |
|---------------|-----|
| **04-tech-plan** / **16-evolve** | Run when adding dependencies, weights, or before phase gate |
| **data-staging** | Run before staging new checkpoints; verify terms allow commercial use |
| **dependency-inventory** | After audit, sync License column for BLOCKED/FLAG/REVIEW rows (packages **and** weights) |
| **09-qa** | Optional compliance pass before release |

## Parent agent rules

1. **Delegate** — Phase 1 is always the subagent; parent synthesizes Phase 2.
2. **Recursive by default** — reject audits that only checked `pyproject.toml` / `package.json` direct deps without lockfile tree.
3. **Weights by default** — reject audits that skipped `docs/spec.md §Data` / weight download URLs unless scope was `packages-only`.
4. **NC = fail** — any non-commercial-only license (package, transitive, or asset) is BLOCKED; audit fails until removed.
5. **No silent OK** — UNKNOWN licenses stay FLAG until resolved; OK direct + FLAG transitive = still fail; OK packages + FLAG/BLOCKED weight = still fail.
6. **Evidence** — preserve subagent citations and dependency chains in the user summary.
7. **Concise summary** — full tables live in the subagent report or saved markdown file.

## Example invocations

```
Run audit-licenses on this repo
```

```
Use audit-licenses to check if adding <package> introduces any closed-source or NC dependencies
(including transitives)
```

```
Run audit-licenses with full recursive tree from uv.lock
```

```
Run audit-licenses including all pretrained weights and data-staging assets
```
