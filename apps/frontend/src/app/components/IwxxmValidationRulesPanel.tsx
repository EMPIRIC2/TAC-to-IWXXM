/**
 * IWXXM validation assert authoring panel (EVWB P2).
 * Enable/disable Schematron asserts + custom overlays; foundation read-only.
 */

import { Loader2 } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import {
  createLibraryAsset,
  listLibraryAssets,
  updateLibraryAsset,
  type LibraryAssetOut,
} from '../../utils/conversionProfilesApi';
import {
  PROFILES_IWXXM_RULES_ADD,
  PROFILES_IWXXM_RULES_CHECK_OP,
  PROFILES_IWXXM_RULES_CHECK_VALUE,
  PROFILES_IWXXM_RULES_CONTEXT,
  PROFILES_IWXXM_RULES_EMPTY,
  PROFILES_IWXXM_RULES_ENABLED,
  PROFILES_IWXXM_RULES_FORK,
  PROFILES_IWXXM_RULES_HEADING,
  PROFILES_IWXXM_RULES_HELP,
  PROFILES_IWXXM_RULES_LOADING,
  PROFILES_IWXXM_RULES_PATTERN,
  PROFILES_IWXXM_RULES_READONLY,
  PROFILES_IWXXM_RULES_SAVE,
  PROFILES_IWXXM_RULES_SAVED,
  PROFILES_IWXXM_RULES_SEARCH,
  PROFILES_IWXXM_RULES_SEARCH_PLACEHOLDER,
  PROFILES_IWXXM_RULES_SELECT,
  PROFILES_IWXXM_RULES_TEST,
  PROFILES_TAC_RULES_CHECK_NONE,
} from '../../utils/conversionProfilesCopy';
import { Card } from './ui/card';

export type IwxxmValidationRulesPanelProps = {
  accessToken: string;
};

type NumericOp = 'min' | 'max' | 'eq' | 'in' | '';

type IwxxmRule = {
  id: string;
  label: string;
  context?: string;
  test?: string;
  pattern?: string;
  enabled: boolean;
  custom: boolean;
  checkOp: NumericOp;
  checkValue: string;
};

function yamlQuote(value: string): string {
  return JSON.stringify(value);
}

function rulesToYaml(name: string, rules: IwxxmRule[]): string {
  const mined = rules.filter((r) => !r.custom);
  const custom = rules.filter((r) => r.custom);
  const lines = ['kind: iwxxm_validation', `name: ${yamlQuote(name)}`, 'rules:'];
  for (const rule of mined) {
    lines.push(`  - id: ${yamlQuote(rule.id)}`);
    lines.push(`    label: ${yamlQuote(rule.label)}`);
    lines.push(`    enabled: ${rule.enabled ? 'true' : 'false'}`);
    if (rule.context) {
      lines.push(`    context: ${yamlQuote(rule.context)}`);
    }
    if (rule.test) {
      lines.push(`    test: ${yamlQuote(rule.test)}`);
    }
  }
  if (custom.length > 0) {
    lines.push('custom_rules:');
    for (const rule of custom) {
      lines.push(`  - id: ${yamlQuote(rule.id)}`);
      lines.push(`    label: ${yamlQuote(rule.label)}`);
      lines.push(`    enabled: ${rule.enabled ? 'true' : 'false'}`);
      if (rule.pattern) {
        lines.push(`    regex: ${yamlQuote(rule.pattern)}`);
      }
      if (rule.checkOp && rule.checkValue.trim()) {
        lines.push('    check:');
        lines.push(`      op: ${rule.checkOp}`);
        lines.push(`      value: ${rule.checkValue.trim()}`);
      }
    }
  }
  return `${lines.join('\n')}\n`;
}

function parseRules(body: Record<string, unknown> | undefined): IwxxmRule[] {
  const out: IwxxmRule[] = [];
  const mined = Array.isArray(body?.rules) ? body.rules : [];
  for (const entry of mined) {
    if (!entry || typeof entry !== 'object') {
      continue;
    }
    const rec = entry as Record<string, unknown>;
    const id = String(rec.id ?? rec.pattern_id ?? '').trim();
    if (!id) {
      continue;
    }
    const check =
      rec.check && typeof rec.check === 'object'
        ? (rec.check as Record<string, unknown>)
        : null;
    const opRaw = typeof check?.op === 'string' ? check.op : '';
    const checkOp: NumericOp =
      opRaw === 'min' || opRaw === 'max' || opRaw === 'eq' || opRaw === 'in'
        ? opRaw
        : '';
    out.push({
      id,
      label: String(rec.label ?? id),
      context: typeof rec.context === 'string' ? rec.context : undefined,
      test: typeof rec.test === 'string' ? rec.test : undefined,
      enabled: rec.enabled === false || rec.enabled_default === false ? false : true,
      custom: false,
      checkOp,
      checkValue:
        check && check.value !== undefined && check.value !== null
          ? String(check.value)
          : '',
    });
  }
  const custom = Array.isArray(body?.custom_rules) ? body.custom_rules : [];
  for (const entry of custom) {
    if (!entry || typeof entry !== 'object') {
      continue;
    }
    const rec = entry as Record<string, unknown>;
    const id = String(rec.id ?? `CUSTOM.${out.length}`).trim();
    const check =
      rec.check && typeof rec.check === 'object'
        ? (rec.check as Record<string, unknown>)
        : null;
    const opRaw = typeof check?.op === 'string' ? check.op : '';
    const checkOp: NumericOp =
      opRaw === 'min' || opRaw === 'max' || opRaw === 'eq' || opRaw === 'in'
        ? opRaw
        : '';
    out.push({
      id,
      label: String(rec.label ?? id),
      pattern:
        typeof rec.regex === 'string'
          ? rec.regex
          : typeof rec.pattern === 'string'
            ? rec.pattern
            : undefined,
      enabled: rec.enabled === false ? false : true,
      custom: true,
      checkOp,
      checkValue:
        check && check.value !== undefined && check.value !== null
          ? String(check.value)
          : '',
    });
  }
  return out;
}

function rulesToBody(rules: IwxxmRule[]): {
  rules: Record<string, unknown>[];
  custom_rules: Record<string, unknown>[];
} {
  return {
    rules: rules
      .filter((r) => !r.custom)
      .map((r) => ({
        id: r.id,
        label: r.label,
        enabled: r.enabled,
        ...(r.context ? { context: r.context } : {}),
        ...(r.test ? { test: r.test } : {}),
      })),
    custom_rules: rules
      .filter((r) => r.custom)
      .map((r) => {
        const row: Record<string, unknown> = {
          id: r.id,
          label: r.label,
          enabled: r.enabled,
        };
        if (r.pattern) {
          row.regex = r.pattern;
        }
        if (r.checkOp && r.checkValue.trim()) {
          row.check = { op: r.checkOp, value: Number(r.checkValue.trim()) };
        }
        return row;
      }),
  };
}

/**
 * Author IWXXM validation asserts and custom overlay rules.
 *
 * @param props.accessToken - Bearer JWT
 */
export function IwxxmValidationRulesPanel({
  accessToken,
}: IwxxmValidationRulesPanelProps) {
  const [assets, setAssets] = useState<LibraryAssetOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState('');
  const [rules, setRules] = useState<IwxxmRule[]>([]);
  const [ruleQuery, setRuleQuery] = useState('');
  const [selectedRuleId, setSelectedRuleId] = useState('');
  const [busy, setBusy] = useState(false);
  const [saveNote, setSaveNote] = useState<string | null>(null);

  const selected = assets.find((a) => a.id === selectedId) ?? assets[0];
  const isBuiltin = selected?.access === 'first_party';
  const editable = Boolean(selected && !isBuiltin);

  const applyAsset = useCallback((asset: LibraryAssetOut) => {
    setSelectedId(asset.id);
    const next = parseRules(asset.body);
    setRules(next);
    setSelectedRuleId(next[0]?.id ?? '');
    setSaveNote(null);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listLibraryAssets(accessToken, 'iwxxm_validation');
      setAssets(res.items);
      if (res.items[0]) {
        applyAsset(res.items[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load asserts');
    } finally {
      setLoading(false);
    }
  }, [accessToken, applyAsset]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when token changes */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const filteredRules = useMemo(() => {
    const q = ruleQuery.trim().toLowerCase();
    if (!q) {
      return rules;
    }
    return rules.filter(
      (r) => r.id.toLowerCase().includes(q) || r.label.toLowerCase().includes(q),
    );
  }, [rules, ruleQuery]);

  /* eslint-disable react-hooks/set-state-in-effect -- keep selection inside filtered set */
  useEffect(() => {
    if (filteredRules.length === 0) {
      return;
    }
    if (!filteredRules.some((r) => r.id === selectedRuleId)) {
      setSelectedRuleId(filteredRules[0]!.id);
    }
  }, [filteredRules, selectedRuleId]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const selectedRule =
    rules.find((r) => r.id === selectedRuleId) ?? filteredRules[0] ?? null;

  const updateRule = (ruleId: string, patch: Partial<IwxxmRule>) => {
    if (!editable) {
      return;
    }
    setRules((prev) => prev.map((r) => (r.id === ruleId ? { ...r, ...patch } : r)));
    setSaveNote(null);
  };

  const addCustom = () => {
    if (!editable) {
      return;
    }
    const id = `CUSTOM.IWXXM_${Date.now().toString(36).toUpperCase()}`;
    const next: IwxxmRule = {
      id,
      label: 'Custom overlay rule',
      pattern: 'iwxxm:Observation',
      enabled: true,
      custom: true,
      checkOp: '',
      checkValue: '',
    };
    setRules((prev) => [...prev, next]);
    setSelectedRuleId(id);
    setSaveNote(null);
  };

  const forkSelected = async () => {
    if (!selected) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const slug = `fork-iwxxm-${Date.now().toString(36)}`.slice(0, 120);
      const bodyParts = rulesToBody(rules);
      const created = await createLibraryAsset(accessToken, {
        slug,
        name: `${selected.name} (custom)`,
        kind: 'iwxxm_validation',
        engineProfileId: selected.engineProfileId,
        attachedNationalLine: selected.attachedNationalLine,
        body: { ...(selected.body ?? {}), ...bodyParts },
        forkOf: selected.id,
        yamlBody: rulesToYaml(`${selected.name} (custom)`, rules),
        status: 'draft',
      });
      const res = await listLibraryAssets(accessToken, 'iwxxm_validation');
      setAssets(res.items);
      applyAsset(created);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fork failed');
    } finally {
      setBusy(false);
    }
  };

  const saveSelected = async () => {
    if (!selected || selected.access === 'first_party') {
      setError(PROFILES_IWXXM_RULES_READONLY);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const bodyParts = rulesToBody(rules);
      const updated = await updateLibraryAsset(accessToken, selected.id, {
        body: { ...(selected.body ?? {}), ...bodyParts },
        yamlBody: rulesToYaml(selected.name, rules),
      });
      setAssets((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
      applyAsset(updated);
      setSaveNote(PROFILES_IWXXM_RULES_SAVED);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card className="space-y-3 p-4" data-testid="iwxxm-validation-rules-panel">
      <div>
        <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">
          {PROFILES_IWXXM_RULES_HEADING}
        </h2>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          {PROFILES_IWXXM_RULES_HELP}
        </p>
      </div>

      {error ? (
        <p className="text-sm text-red-600" data-testid="iwxxm-validation-rules-error">
          {error}
        </p>
      ) : null}
      {saveNote ? (
        <p
          className="text-sm text-green-700"
          data-testid="iwxxm-validation-rules-saved"
        >
          {saveNote}
        </p>
      ) : null}

      {loading ? (
        <p className="flex items-center gap-2 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          {PROFILES_IWXXM_RULES_LOADING}
        </p>
      ) : !selected ? (
        <p className="text-sm text-gray-500">{PROFILES_IWXXM_RULES_EMPTY}</p>
      ) : (
        <>
          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_IWXXM_RULES_SELECT}
            </span>
            <select
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="iwxxm-validation-asset-select"
              value={selected.id}
              onChange={(e) => {
                const next = assets.find((a) => a.id === e.target.value);
                if (next) {
                  applyAsset(next);
                }
              }}
            >
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} · {a.access === 'first_party' ? 'built-in' : 'custom'}
                </option>
              ))}
            </select>
          </label>

          {isBuiltin ? (
            <p
              className="rounded border border-amber-200 bg-amber-50 p-2 text-xs text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-100"
              data-testid="iwxxm-validation-rules-readonly"
            >
              {PROFILES_IWXXM_RULES_READONLY}
            </p>
          ) : null}

          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_IWXXM_RULES_SEARCH}
            </span>
            <input
              type="search"
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="iwxxm-validation-rules-search"
              placeholder={PROFILES_IWXXM_RULES_SEARCH_PLACEHOLDER}
              value={ruleQuery}
              onChange={(e) => setRuleQuery(e.target.value)}
            />
          </label>

          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">Assert</span>
            <select
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="iwxxm-validation-rule-select"
              value={selectedRule?.id ?? ''}
              onChange={(e) => setSelectedRuleId(e.target.value)}
            >
              {filteredRules.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.enabled ? '' : '[off] '}
                  {r.label.slice(0, 80)}
                </option>
              ))}
            </select>
          </label>

          {filteredRules.length === 0 ? (
            <p className="text-sm text-gray-500">{PROFILES_IWXXM_RULES_EMPTY}</p>
          ) : null}

          {selectedRule ? (
            <div
              className="space-y-2 rounded border border-gray-200 p-3 dark:border-gray-700"
              data-testid={`iwxxm-validation-rule-editor-${selectedRule.id}`}
            >
              <p
                className="text-xs text-gray-500"
                data-testid="iwxxm-validation-rule-id"
              >
                {selectedRule.id}
                {selectedRule.custom ? ' · custom overlay' : ''}
              </p>
              <label className="flex items-center gap-2 text-xs">
                <input
                  type="checkbox"
                  data-testid="iwxxm-validation-rule-enabled"
                  checked={selectedRule.enabled}
                  disabled={!editable}
                  onChange={(e) =>
                    updateRule(selectedRule.id, { enabled: e.target.checked })
                  }
                />
                <span>{PROFILES_IWXXM_RULES_ENABLED}</span>
              </label>
              {selectedRule.context ? (
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  <span className="font-medium">{PROFILES_IWXXM_RULES_CONTEXT}: </span>
                  <span data-testid="iwxxm-validation-rule-context">
                    {selectedRule.context}
                  </span>
                </p>
              ) : null}
              {selectedRule.test ? (
                <p className="max-h-24 overflow-auto text-xs text-gray-600 dark:text-gray-400">
                  <span className="font-medium">{PROFILES_IWXXM_RULES_TEST}: </span>
                  <span data-testid="iwxxm-validation-rule-test">
                    {selectedRule.test}
                  </span>
                </p>
              ) : null}
              {selectedRule.custom ? (
                <>
                  <label className="block text-xs">
                    <span className="text-gray-600 dark:text-gray-400">
                      {PROFILES_IWXXM_RULES_PATTERN}
                    </span>
                    <input
                      className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 font-mono dark:border-gray-600 dark:bg-gray-900"
                      data-testid="iwxxm-validation-rule-pattern"
                      value={selectedRule.pattern ?? ''}
                      disabled={!editable}
                      onChange={(e) =>
                        updateRule(selectedRule.id, {
                          pattern: e.target.value,
                        })
                      }
                    />
                  </label>
                  <label className="block text-xs">
                    <span className="text-gray-600 dark:text-gray-400">
                      {PROFILES_IWXXM_RULES_CHECK_OP}
                    </span>
                    <select
                      className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                      data-testid="iwxxm-validation-rule-check-op"
                      value={selectedRule.checkOp}
                      disabled={!editable}
                      onChange={(e) =>
                        updateRule(selectedRule.id, {
                          checkOp: e.target.value as NumericOp,
                        })
                      }
                    >
                      <option value="">{PROFILES_TAC_RULES_CHECK_NONE}</option>
                      <option value="min">min</option>
                      <option value="max">max</option>
                      <option value="eq">eq</option>
                      <option value="in">in</option>
                    </select>
                  </label>
                  {selectedRule.checkOp ? (
                    <label className="block text-xs">
                      <span className="text-gray-600 dark:text-gray-400">
                        {PROFILES_IWXXM_RULES_CHECK_VALUE}
                      </span>
                      <input
                        className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                        data-testid="iwxxm-validation-rule-check-value"
                        value={selectedRule.checkValue}
                        disabled={!editable}
                        onChange={(e) =>
                          updateRule(selectedRule.id, {
                            checkValue: e.target.value,
                          })
                        }
                      />
                    </label>
                  ) : null}
                </>
              ) : null}
            </div>
          ) : null}

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
              data-testid="iwxxm-validation-rules-fork"
              disabled={busy}
              onClick={() => void forkSelected()}
            >
              {PROFILES_IWXXM_RULES_FORK}
            </button>
            {editable ? (
              <>
                <button
                  type="button"
                  className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
                  data-testid="iwxxm-validation-rules-add"
                  disabled={busy}
                  onClick={addCustom}
                >
                  {PROFILES_IWXXM_RULES_ADD}
                </button>
                <button
                  type="button"
                  className="rounded border border-sky-700 px-3 py-1.5 text-sm text-sky-800 disabled:opacity-50 dark:text-sky-200"
                  data-testid="iwxxm-validation-rules-save"
                  disabled={busy}
                  onClick={() => void saveSelected()}
                >
                  {PROFILES_IWXXM_RULES_SAVE}
                </button>
              </>
            ) : null}
          </div>
        </>
      )}
    </Card>
  );
}
