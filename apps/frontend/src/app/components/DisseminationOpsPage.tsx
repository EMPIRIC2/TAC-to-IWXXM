/**
 * Dissemination ops — plan, audit, SQL mapping, gateway health (UJ-071).
 * Complements the Convert destinations drawer; requires sign-in.
 */

import { useCallback, useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import {
  executeDisseminationPlan,
  fetchGatewayHealth,
  listDisseminationAudit,
  upsertDisseminationPlan,
  upsertMappingConfig,
  type AuditRecordOut,
  type DisseminationPlanOut,
  type GatewayHealthRow,
  type MappingConfigOut,
} from '@/utils/disseminationOpsApi';
import {
  DISSEMINATION_OPS_AUDIT_EMPTY,
  DISSEMINATION_OPS_AUDIT_HEADING,
  DISSEMINATION_OPS_AUDIT_LOADING,
  DISSEMINATION_OPS_ERROR_PREFIX,
  DISSEMINATION_OPS_HEALTH_EMPTY,
  DISSEMINATION_OPS_HEALTH_HEADING,
  DISSEMINATION_OPS_HEALTH_LOADING,
  DISSEMINATION_OPS_LOGIN_REQUIRED,
  DISSEMINATION_OPS_MAPPING_HEADING,
  DISSEMINATION_OPS_MAPPING_MODE_LABEL,
  DISSEMINATION_OPS_MAPPING_NAME_LABEL,
  DISSEMINATION_OPS_MAPPING_SAVE,
  DISSEMINATION_OPS_PLAN_DEST_LABEL,
  DISSEMINATION_OPS_PLAN_DRY_RUN,
  DISSEMINATION_OPS_PLAN_HEADING,
  DISSEMINATION_OPS_PLAN_POLICY_LABEL,
  DISSEMINATION_OPS_PLAN_SAVE,
  DISSEMINATION_OPS_PLAN_SLUG_LABEL,
  DISSEMINATION_OPS_SIGN_IN,
  DISSEMINATION_OPS_SUBTITLE,
  DISSEMINATION_OPS_TITLE,
} from '@/utils/disseminationOpsCopy';
import { Button } from './ui/button';
import { Card } from './ui/card';

export interface DisseminationOpsPageProps {
  /** Bearer JWT — when absent, show sign-in prompt. */
  accessToken?: string;
  /** Navigate to login. */
  onRequestLogin?: () => void;
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : 'Unknown error';
}

interface AuthedOpsProps {
  accessToken: string;
}

function DisseminationOpsAuthed({ accessToken }: AuthedOpsProps) {
  const [health, setHealth] = useState<GatewayHealthRow[] | null>(null);
  const [audit, setAudit] = useState<AuditRecordOut[] | null>(null);
  const [plan, setPlan] = useState<DisseminationPlanOut | null>(null);
  const [mapping, setMapping] = useState<MappingConfigOut | null>(null);
  const [executeNote, setExecuteNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [planSlug, setPlanSlug] = useState('default');
  const [planPolicy, setPlanPolicy] = useState<'valid-only' | 'warn-ok'>('valid-only');
  const [planDests, setPlanDests] = useState('file');
  const [mappingName, setMappingName] = useState('default');
  const [mappingMode, setMappingMode] = useState<'source' | 'sink'>('source');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthRes, auditRes] = await Promise.all([
        fetchGatewayHealth(accessToken),
        listDisseminationAudit(accessToken, { limit: 20 }),
      ]);
      setHealth(healthRes.items);
      setAudit(auditRes.items);
    } catch (err) {
      setError(`${DISSEMINATION_OPS_ERROR_PREFIX} ${errorMessage(err)}`);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when token changes */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const handleSavePlan = async () => {
    setError(null);
    setExecuteNote(null);
    try {
      const saved = await upsertDisseminationPlan(accessToken, planSlug, {
        slug: planSlug,
        validity_policy: planPolicy,
        destination_refs: planDests
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
      });
      setPlan(saved);
    } catch (err) {
      setError(`${DISSEMINATION_OPS_ERROR_PREFIX} ${errorMessage(err)}`);
    }
  };

  const handleDryRun = async () => {
    if (!plan) return;
    setError(null);
    try {
      const result = await executeDisseminationPlan(accessToken, plan.id, {
        dry_run: true,
        message_id: 'ops-sample',
      });
      const receiptSummary =
        result.receipts.map((r) => `${r.gateway}:${r.status}`).join(', ') || 'none';
      setExecuteNote(
        `Dry-run complete: ${result.receipts.length} receipt(s) — ${receiptSummary}`,
      );
      await load();
    } catch (err) {
      setError(`${DISSEMINATION_OPS_ERROR_PREFIX} ${errorMessage(err)}`);
    }
  };

  const handleSaveMapping = async () => {
    setError(null);
    try {
      const saved = await upsertMappingConfig(accessToken, mappingName, {
        name: mappingName,
        mode: mappingMode,
        config: {
          message: 'message',
          station: 'station',
          timestamp: 'timestamp',
          externalId: 'external_id',
        },
      });
      setMapping(saved);
    } catch (err) {
      setError(`${DISSEMINATION_OPS_ERROR_PREFIX} ${errorMessage(err)}`);
    }
  };

  return (
    <div
      className="mx-auto max-w-4xl space-y-6 px-4 py-8"
      data-testid="dissemination-ops-page"
    >
      <header>
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-50">
          {DISSEMINATION_OPS_TITLE}
        </h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
          {DISSEMINATION_OPS_SUBTITLE}
        </p>
      </header>

      {error ? (
        <p
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200"
          data-testid="dissemination-ops-error"
          role="alert"
        >
          {error}
        </p>
      ) : null}

      <Card className="space-y-3 p-4" data-testid="dissemination-ops-health">
        <h2 className="text-lg font-medium">{DISSEMINATION_OPS_HEALTH_HEADING}</h2>
        {loading && health === null ? (
          <p className="flex items-center gap-2 text-sm text-gray-600">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            {DISSEMINATION_OPS_HEALTH_LOADING}
          </p>
        ) : null}
        {health && health.length === 0 ? (
          <p className="text-sm text-gray-600">{DISSEMINATION_OPS_HEALTH_EMPTY}</p>
        ) : null}
        {health && health.length > 0 ? (
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {health.map((row) => (
              <li
                key={row.gateway}
                className="flex flex-wrap items-baseline justify-between gap-2 py-2 text-sm"
                data-testid={`gateway-health-${row.gateway}`}
              >
                <span className="font-medium">{row.gateway}</span>
                <span>
                  {row.ok ? 'OK' : 'Not OK'}
                  {row.connectivity_ok ? ' · connected' : ' · unreachable'}
                </span>
                {row.detail ? (
                  <span className="w-full text-gray-500">{row.detail}</span>
                ) : null}
              </li>
            ))}
          </ul>
        ) : null}
      </Card>

      <Card className="space-y-3 p-4" data-testid="dissemination-ops-plan">
        <h2 className="text-lg font-medium">{DISSEMINATION_OPS_PLAN_HEADING}</h2>
        <label className="block text-sm">
          <span className="text-gray-700 dark:text-gray-200">
            {DISSEMINATION_OPS_PLAN_SLUG_LABEL}
          </span>
          <input
            className="mt-1 w-full rounded border border-gray-300 px-2 py-1 dark:border-gray-600 dark:bg-gray-900"
            data-testid="plan-slug-input"
            value={planSlug}
            onChange={(e) => setPlanSlug(e.target.value)}
          />
        </label>
        <label className="block text-sm">
          <span className="text-gray-700 dark:text-gray-200">
            {DISSEMINATION_OPS_PLAN_POLICY_LABEL}
          </span>
          <select
            className="mt-1 w-full rounded border border-gray-300 px-2 py-1 dark:border-gray-600 dark:bg-gray-900"
            data-testid="plan-policy-select"
            value={planPolicy}
            onChange={(e) => setPlanPolicy(e.target.value as 'valid-only' | 'warn-ok')}
          >
            <option value="valid-only">Valid only</option>
            <option value="warn-ok">Allow warnings</option>
          </select>
        </label>
        <label className="block text-sm">
          <span className="text-gray-700 dark:text-gray-200">
            {DISSEMINATION_OPS_PLAN_DEST_LABEL}
          </span>
          <input
            className="mt-1 w-full rounded border border-gray-300 px-2 py-1 dark:border-gray-600 dark:bg-gray-900"
            data-testid="plan-dests-input"
            value={planDests}
            onChange={(e) => setPlanDests(e.target.value)}
          />
        </label>
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            data-testid="plan-save"
            onClick={() => void handleSavePlan()}
          >
            {DISSEMINATION_OPS_PLAN_SAVE}
          </Button>
          <Button
            type="button"
            variant="outline"
            data-testid="plan-dry-run"
            onClick={() => void handleDryRun()}
          >
            {DISSEMINATION_OPS_PLAN_DRY_RUN}
          </Button>
        </div>
        {plan ? (
          <p className="text-sm text-gray-600" data-testid="plan-saved-id">
            Saved plan id: {plan.id}
          </p>
        ) : null}
        {executeNote ? (
          <p
            className="text-sm text-gray-700 dark:text-gray-200"
            data-testid="plan-execute-note"
          >
            {executeNote}
          </p>
        ) : null}
      </Card>

      <Card className="space-y-3 p-4" data-testid="dissemination-ops-mapping">
        <h2 className="text-lg font-medium">{DISSEMINATION_OPS_MAPPING_HEADING}</h2>
        <label className="block text-sm">
          <span className="text-gray-700 dark:text-gray-200">
            {DISSEMINATION_OPS_MAPPING_NAME_LABEL}
          </span>
          <input
            className="mt-1 w-full rounded border border-gray-300 px-2 py-1 dark:border-gray-600 dark:bg-gray-900"
            data-testid="mapping-name-input"
            value={mappingName}
            onChange={(e) => setMappingName(e.target.value)}
          />
        </label>
        <label className="block text-sm">
          <span className="text-gray-700 dark:text-gray-200">
            {DISSEMINATION_OPS_MAPPING_MODE_LABEL}
          </span>
          <select
            className="mt-1 w-full rounded border border-gray-300 px-2 py-1 dark:border-gray-600 dark:bg-gray-900"
            data-testid="mapping-mode-select"
            value={mappingMode}
            onChange={(e) => setMappingMode(e.target.value as 'source' | 'sink')}
          >
            <option value="source">Source</option>
            <option value="sink">Sink</option>
          </select>
        </label>
        <Button
          type="button"
          data-testid="mapping-save"
          onClick={() => void handleSaveMapping()}
        >
          {DISSEMINATION_OPS_MAPPING_SAVE}
        </Button>
        {mapping ? (
          <p className="text-sm text-gray-600" data-testid="mapping-saved-id">
            Saved mapping id: {mapping.id} ({mapping.mode})
          </p>
        ) : null}
      </Card>

      <Card className="space-y-3 p-4" data-testid="dissemination-ops-audit">
        <h2 className="text-lg font-medium">{DISSEMINATION_OPS_AUDIT_HEADING}</h2>
        {loading && audit === null ? (
          <p className="flex items-center gap-2 text-sm text-gray-600">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            {DISSEMINATION_OPS_AUDIT_LOADING}
          </p>
        ) : null}
        {audit && audit.length === 0 ? (
          <p className="text-sm text-gray-600">{DISSEMINATION_OPS_AUDIT_EMPTY}</p>
        ) : null}
        {audit && audit.length > 0 ? (
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {audit.map((row) => (
              <li
                key={row.id}
                className="py-2 text-sm"
                data-testid={`audit-row-${row.id}`}
              >
                <span className="font-medium">{row.status}</span>
                {' · '}
                {row.gateway}
                {row.station ? ` · ${row.station}` : ''}
                {row.product ? ` · ${row.product}` : ''}
                {row.detail ? (
                  <span className="mt-1 block text-gray-500">{row.detail}</span>
                ) : null}
              </li>
            ))}
          </ul>
        ) : null}
      </Card>
    </div>
  );
}

/**
 * Authenticated Dissemination ops surface (plans, audit, mapping, health).
 */
export function DisseminationOpsPage({
  accessToken,
  onRequestLogin,
}: DisseminationOpsPageProps) {
  if (!accessToken) {
    return (
      <div
        className="mx-auto max-w-3xl px-4 py-10"
        data-testid="dissemination-ops-page"
      >
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-50">
          {DISSEMINATION_OPS_TITLE}
        </h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
          {DISSEMINATION_OPS_LOGIN_REQUIRED}
        </p>
        {onRequestLogin ? (
          <Button
            type="button"
            className="mt-4"
            data-testid="dissemination-ops-sign-in"
            onClick={onRequestLogin}
          >
            {DISSEMINATION_OPS_SIGN_IN}
          </Button>
        ) : null}
      </div>
    );
  }

  return <DisseminationOpsAuthed accessToken={accessToken} />;
}
