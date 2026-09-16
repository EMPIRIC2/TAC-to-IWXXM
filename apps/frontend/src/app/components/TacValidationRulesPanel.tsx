/**
 * TAC validation rule authoring panel (EVWB P2).
 * Searchable identity, severity, regex, numeric bounds; foundation read-only.
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
  PROFILES_TAC_RULES_ADD,
  PROFILES_TAC_RULES_CHECK_NONE,
  PROFILES_TAC_RULES_CHECK_OP,
  PROFILES_TAC_RULES_CHECK_UNIT,
  PROFILES_TAC_RULES_CHECK_VALUE,
  PROFILES_TAC_RULES_CHECK_VALUES,
  PROFILES_TAC_RULES_EMPTY,
  PROFILES_TAC_RULES_ENABLED,
  PROFILES_TAC_RULES_FORK,
  PROFILES_TAC_RULES_HEADING,
  PROFILES_TAC_RULES_HELP,
  PROFILES_TAC_RULES_IDENTITY,
  PROFILES_TAC_RULES_LABEL,
  PROFILES_TAC_RULES_LOADING,
  PROFILES_TAC_RULES_PATTERN,
  PROFILES_TAC_RULES_READONLY,
  PROFILES_TAC_RULES_SAMPLE,
  PROFILES_TAC_RULES_SAVE,
  PROFILES_TAC_RULES_SAVED,
  PROFILES_TAC_RULES_SEARCH,
  PROFILES_TAC_RULES_SEARCH_PLACEHOLDER,
  PROFILES_TAC_RULES_SELECT,
  PROFILES_TAC_RULES_SEVERITY,
} from '../../utils/conversionProfilesCopy';
import { Card } from './ui/card';

export type TacValidationRulesPanelProps = {
  accessToken: string;
};

type NumericOp = 'min' | 'max' | 'eq' | 'in' | '';

type TacRule = {
  id: string;
  code?: string;
  label: string;
  severity: string;
  pattern?: string;
  sample?: string;
  enabled: boolean;
  checkOp: NumericOp;
  checkValue: string;
  checkValues: string;
  checkUnit: string;
  checkField: string;
};

const SEVERITIES = ['error', 'warning', 'info'] as const;

function yamlQuote(value: string): string {
  return JSON.stringify(value);
}

function rulesToYaml(name: string, rules: TacRule[]): string {
  const lines = ['kind: tac_validation', `name: ${yamlQuote(name)}`, 'rules:'];
  for (const rule of rules) {
    lines.push(`  - id: ${yamlQuote(rule.id)}`);
    lines.push(`    label: ${yamlQuote(rule.label)}`);
    lines.push(`    severity: ${rule.severity}`);
    lines.push(`    enabled: ${rule.enabled ? 'true' : 'false'}`);
    if (rule.pattern) {
      lines.push(`    pattern: ${yamlQuote(rule.pattern)}`);
    }
    if (rule.sample) {
      lines.push(`    sample: ${yamlQuote(rule.sample)}`);
    }
    if (rule.checkOp) {
      lines.push('    check:');
      lines.push(`      op: ${rule.checkOp}`);
      if (rule.checkOp === 'in') {
        const values = rule.checkValues
          .split(',')
          .map((v) => v.trim())
          .filter(Boolean);
        lines.push(`      values: [${values.join(', ')}]`);
      } else if (rule.checkValue.trim()) {
        lines.push(`      value: ${rule.checkValue.trim()}`);
      }
      if (rule.checkField.trim()) {
        lines.push(`      field: ${yamlQuote(rule.checkField.trim())}`);
      }
      if (rule.checkUnit.trim()) {
        lines.push(`      unit: ${yamlQuote(rule.checkUnit.trim())}`);
      }
    }
  }
  return `${lines.join('\n')}\n`;
}

function parseRules(body: Record<string, unknown> | undefined): TacRule[] {
  const raw = body?.rules;
  if (!Array.isArray(raw)) {
    return [];
  }
  const out: TacRule[] = [];
  for (const entry of raw) {
    if (!entry || typeof entry !== 'object') {
      continue;
    }
    const rec = entry as Record<string, unknown>;
    const id = String(rec.id ?? rec.code ?? '').trim();
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
      code: typeof rec.code === 'string' ? rec.code : undefined,
      label: String(rec.label ?? rec.code ?? id),
      severity: String(rec.severity ?? 'info'),
      pattern:
        typeof rec.pattern === 'string'
          ? rec.pattern
          : typeof rec.regex === 'string'
            ? rec.regex
            : undefined,
      sample: typeof rec.sample === 'string' ? rec.sample : undefined,
      enabled: rec.enabled === false || rec.enabled_default === false ? false : true,
      checkOp,
      checkValue:
        check && check.value !== undefined && check.value !== null
          ? String(check.value)
          : '',
      checkValues: Array.isArray(check?.values)
        ? check.values.map((v) => String(v)).join(', ')
        : '',
      checkUnit: typeof check?.unit === 'string' ? check.unit : '',
      checkField: typeof check?.field === 'string' ? check.field : 'value',
    });
  }
  return out;
}

function rulesToBody(rules: TacRule[]): Record<string, unknown>[] {
  return rules.map((rule) => {
    const row: Record<string, unknown> = {
      id: rule.id,
      label: rule.label,
      severity: rule.severity,
      enabled: rule.enabled,
    };
    if (rule.code) {
      row.code = rule.code;
    }
    if (rule.pattern) {
      row.pattern = rule.pattern;
    }
    if (rule.sample) {
      row.sample = rule.sample;
    }
    if (rule.checkOp) {
      const check: Record<string, unknown> = { op: rule.checkOp };
      if (rule.checkOp === 'in') {
        check.values = rule.checkValues
          .split(',')
          .map((v) => v.trim())
          .filter(Boolean)
          .map((v) => Number(v));
      } else if (rule.checkValue.trim()) {
        check.value = Number(rule.checkValue.trim());
      }
      if (rule.checkField.trim()) {
        check.field = rule.checkField.trim();
      }
      if (rule.checkUnit.trim()) {
        check.unit = rule.checkUnit.trim();
      }
      row.check = check;
    }
    return row;
  });
}

/**
 * Author TAC validation rules with identity, levels, regex, and numeric bounds.
 *
 * @param props.accessToken - Bearer JWT
 */
export function TacValidationRulesPanel({ accessToken }: TacValidationRulesPanelProps) {
  const [assets, setAssets] = useState<LibraryAssetOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState('');
  const [rules, setRules] = useState<TacRule[]>([]);
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
      const res = await listLibraryAssets(accessToken, 'tac_validation');
      setAssets(res.items);
      if (res.items[0]) {
        applyAsset(res.items[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load rules');
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
      (r) =>
        r.id.toLowerCase().includes(q) ||
        r.label.toLowerCase().includes(q) ||
        (r.code ?? '').toLowerCase().includes(q),
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

  const updateRule = (ruleId: string, patch: Partial<TacRule>) => {
    if (!editable) {
      return;
    }
    setRules((prev) => prev.map((r) => (r.id === ruleId ? { ...r, ...patch } : r)));
    setSaveNote(null);
  };

  const addRule = () => {
    if (!editable) {
      return;
    }
    const id = `CUSTOM.RULE_${Date.now().toString(36).toUpperCase()}`;
    const next: TacRule = {
      id,
      label: 'Custom rule',
      severity: 'warning',
      pattern: '(?P<value>\\d+)',
      sample: '12',
      enabled: true,
      checkOp: '',
      checkValue: '',
      checkValues: '',
      checkUnit: '',
      checkField: 'value',
    };
    setRules((prev) => [next, ...prev]);
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
      const slug = `fork-tac-${Date.now().toString(36)}`.slice(0, 120);
      const created = await createLibraryAsset(accessToken, {
        slug,
        name: `${selected.name} (custom)`,
        kind: 'tac_validation',
        engineProfileId: selected.engineProfileId,
        attachedNationalLine: selected.attachedNationalLine,
        body: {
          ...(selected.body ?? {}),
          rules: rulesToBody(rules),
        },
        forkOf: selected.id,
        yamlBody: rulesToYaml(`${selected.name} (custom)`, rules),
        status: 'draft',
      });
      const res = await listLibraryAssets(accessToken, 'tac_validation');
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
      setError(PROFILES_TAC_RULES_READONLY);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const bodyRules = rulesToBody(rules);
      const updated = await updateLibraryAsset(accessToken, selected.id, {
        body: { ...(selected.body ?? {}), rules: bodyRules },
        yamlBody: rulesToYaml(selected.name, rules),
      });
      setAssets((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
      applyAsset(updated);
      setSaveNote(PROFILES_TAC_RULES_SAVED);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card className="space-y-3 p-4" data-testid="tac-validation-rules-panel">
      <div>
        <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">
          {PROFILES_TAC_RULES_HEADING}
        </h2>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          {PROFILES_TAC_RULES_HELP}
        </p>
      </div>

      {error ? (
        <p className="text-sm text-red-600" data-testid="tac-validation-rules-error">
          {error}
        </p>
      ) : null}
      {saveNote ? (
        <p className="text-sm text-green-700" data-testid="tac-validation-rules-saved">
          {saveNote}
        </p>
      ) : null}

      {loading ? (
        <p className="flex items-center gap-2 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          {PROFILES_TAC_RULES_LOADING}
        </p>
      ) : !selected ? (
        <p className="text-sm text-gray-500">{PROFILES_TAC_RULES_EMPTY}</p>
      ) : (
        <>
          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_TAC_RULES_SELECT}
            </span>
            <select
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="tac-validation-asset-select"
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
              data-testid="tac-validation-rules-readonly"
            >
              {PROFILES_TAC_RULES_READONLY}
            </p>
          ) : null}

          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {PROFILES_TAC_RULES_SEARCH}
            </span>
            <input
              type="search"
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="tac-validation-rules-search"
              placeholder={PROFILES_TAC_RULES_SEARCH_PLACEHOLDER}
              value={ruleQuery}
              onChange={(e) => setRuleQuery(e.target.value)}
            />
          </label>

          <label className="block text-sm">
            <span className="text-gray-700 dark:text-gray-300">Rule</span>
            <select
              className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="tac-validation-rule-select"
              value={selectedRule?.id ?? ''}
              onChange={(e) => setSelectedRuleId(e.target.value)}
            >
              {filteredRules.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.label} ({r.id})
                </option>
              ))}
            </select>
          </label>

          {filteredRules.length === 0 ? (
            <p className="text-sm text-gray-500">{PROFILES_TAC_RULES_EMPTY}</p>
          ) : null}

          {selectedRule ? (
            <div
              className="space-y-2 rounded border border-gray-200 p-3 dark:border-gray-700"
              data-testid={`tac-validation-rule-editor-${selectedRule.id}`}
            >
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">
                  {PROFILES_TAC_RULES_IDENTITY}
                </span>
                <input
                  className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="tac-validation-rule-id"
                  value={selectedRule.id}
                  disabled={!editable || !selectedRule.id.startsWith('CUSTOM.')}
                  onChange={(e) => {
                    const nextId = e.target.value;
                    updateRule(selectedRule.id, { id: nextId });
                    setSelectedRuleId(nextId);
                  }}
                />
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">
                  {PROFILES_TAC_RULES_LABEL}
                </span>
                <input
                  className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="tac-validation-rule-label"
                  value={selectedRule.label}
                  disabled={!editable}
                  onChange={(e) =>
                    updateRule(selectedRule.id, { label: e.target.value })
                  }
                />
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">
                  {PROFILES_TAC_RULES_SEVERITY}
                </span>
                <select
                  className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="tac-validation-rule-severity"
                  value={selectedRule.severity}
                  disabled={!editable}
                  onChange={(e) =>
                    updateRule(selectedRule.id, { severity: e.target.value })
                  }
                >
                  {SEVERITIES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </label>
              <label className="flex items-center gap-2 text-xs">
                <input
                  type="checkbox"
                  data-testid="tac-validation-rule-enabled"
                  checked={selectedRule.enabled}
                  disabled={!editable}
                  onChange={(e) =>
                    updateRule(selectedRule.id, { enabled: e.target.checked })
                  }
                />
                <span>{PROFILES_TAC_RULES_ENABLED}</span>
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">
                  {PROFILES_TAC_RULES_PATTERN}
                </span>
                <input
                  className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 font-mono dark:border-gray-600 dark:bg-gray-900"
                  data-testid="tac-validation-rule-pattern"
                  value={selectedRule.pattern ?? ''}
                  disabled={!editable}
                  onChange={(e) =>
                    updateRule(selectedRule.id, { pattern: e.target.value })
                  }
                />
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">
                  {PROFILES_TAC_RULES_SAMPLE}
                </span>
                <input
                  className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="tac-validation-rule-sample"
                  value={selectedRule.sample ?? ''}
                  disabled={!editable}
                  onChange={(e) =>
                    updateRule(selectedRule.id, { sample: e.target.value })
                  }
                />
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">
                  {PROFILES_TAC_RULES_CHECK_OP}
                </span>
                <select
                  className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="tac-validation-rule-check-op"
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
              {selectedRule.checkOp === 'in' ? (
                <label className="block text-xs">
                  <span className="text-gray-600 dark:text-gray-400">
                    {PROFILES_TAC_RULES_CHECK_VALUES}
                  </span>
                  <input
                    className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                    data-testid="tac-validation-rule-check-values"
                    value={selectedRule.checkValues}
                    disabled={!editable}
                    onChange={(e) =>
                      updateRule(selectedRule.id, {
                        checkValues: e.target.value,
                      })
                    }
                  />
                </label>
              ) : selectedRule.checkOp ? (
                <label className="block text-xs">
                  <span className="text-gray-600 dark:text-gray-400">
                    {PROFILES_TAC_RULES_CHECK_VALUE}
                  </span>
                  <input
                    className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                    data-testid="tac-validation-rule-check-value"
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
              {selectedRule.checkOp ? (
                <label className="block text-xs">
                  <span className="text-gray-600 dark:text-gray-400">
                    {PROFILES_TAC_RULES_CHECK_UNIT}
                  </span>
                  <input
                    className="mt-1 w-full rounded border border-gray-300 bg-white p-1.5 dark:border-gray-600 dark:bg-gray-900"
                    data-testid="tac-validation-rule-check-unit"
                    value={selectedRule.checkUnit}
                    disabled={!editable}
                    onChange={(e) =>
                      updateRule(selectedRule.id, {
                        checkUnit: e.target.value,
                      })
                    }
                  />
                </label>
              ) : null}
            </div>
          ) : null}

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
              data-testid="tac-validation-rules-fork"
              disabled={busy}
              onClick={() => void forkSelected()}
            >
              {PROFILES_TAC_RULES_FORK}
            </button>
            {editable ? (
              <>
                <button
                  type="button"
                  className="rounded border px-3 py-1.5 text-sm disabled:opacity-50"
                  data-testid="tac-validation-rules-add"
                  disabled={busy}
                  onClick={addRule}
                >
                  {PROFILES_TAC_RULES_ADD}
                </button>
                <button
                  type="button"
                  className="rounded border border-sky-700 px-3 py-1.5 text-sm text-sky-800 disabled:opacity-50 dark:text-sky-200"
                  data-testid="tac-validation-rules-save"
                  disabled={busy}
                  onClick={() => void saveSelected()}
                >
                  {PROFILES_TAC_RULES_SAVE}
                </button>
              </>
            ) : null}
          </div>
        </>
      )}
    </Card>
  );
}
