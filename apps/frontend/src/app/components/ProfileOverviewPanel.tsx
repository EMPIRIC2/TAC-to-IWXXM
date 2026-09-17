/**
 * Overview tab — profile compare + product/file-type/IWXXM enablement (EVWB P4).
 */

import { Loader2 } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import {
  fetchProfileCatalog,
  type ProfileCatalogEntry,
} from '../../utils/conversionProfilesApi';
import {
  PROFILES_OVERVIEW_COMPARE_HEADING,
  PROFILES_OVERVIEW_ENABLEMENT_HEADING,
  PROFILES_OVERVIEW_HEADING,
  PROFILES_OVERVIEW_HELP,
  PROFILES_OVERVIEW_YAML_HEADING,
} from '../../utils/conversionProfilesCopy';
import { Card } from './ui/card';

export type ProfileOverviewPanelProps = {
  accessToken: string;
  /** Preferred primary profile id from the Profiles catalog picker. */
  preferredProfileId?: string | null;
};

const PRODUCT_OPTIONS = [
  'METAR',
  'SPECI',
  'TAF',
  'SIGMET',
  'AIRMET',
  'TCA',
  'VAA',
] as const;
const FILE_TYPE_OPTIONS = ['tac', 'xml', 'bulletin'] as const;
const IWXXM_VERSION_OPTIONS = ['2025-2', '2023-1', '3.0'] as const;

type EnablementState = {
  products: Record<string, boolean>;
  fileTypes: Record<string, boolean>;
  iwxxmVersions: Record<string, boolean>;
};

function defaultEnablement(profile: ProfileCatalogEntry | null): EnablementState {
  const products: Record<string, boolean> = {};
  for (const p of PRODUCT_OPTIONS) {
    products[p] = profile?.products.includes(p) ?? p === 'METAR';
  }
  const fileTypes: Record<string, boolean> = {
    tac: true,
    xml: true,
    bulletin: false,
  };
  const iwxxmVersions: Record<string, boolean> = {};
  for (const v of IWXXM_VERSION_OPTIONS) {
    const line = profile?.iwxxm_line ?? '2025-2';
    iwxxmVersions[v] = line.includes(v) || (v === '2025-2' && !line);
  }
  return { products, fileTypes, iwxxmVersions };
}

function enablementToYaml(profileId: string, state: EnablementState): string {
  const products = PRODUCT_OPTIONS.filter((p) => state.products[p]);
  const fileTypes = FILE_TYPE_OPTIONS.filter((f) => state.fileTypes[f]);
  const versions = IWXXM_VERSION_OPTIONS.filter((v) => state.iwxxmVersions[v]);
  return [
    'kind: overview_enablement',
    `profile_id: ${JSON.stringify(profileId)}`,
    'products:',
    ...products.map((p) => `  - ${p}`),
    'file_types:',
    ...fileTypes.map((f) => `  - ${f}`),
    'iwxxm_versions:',
    ...versions.map((v) => `  - ${JSON.stringify(v)}`),
    '',
  ].join('\n');
}

function sameList(a: string[], b: string[]): boolean {
  if (a.length !== b.length) {
    return false;
  }
  const sa = [...a].sort().join('\0');
  const sb = [...b].sort().join('\0');
  return sa === sb;
}

/**
 * Compare two catalog profiles and edit embedded enablement YAML.
 *
 * @param props.accessToken - Bearer JWT
 * @param props.preferredProfileId - Optional primary profile from parent picker
 */
export function ProfileOverviewPanel({
  accessToken,
  preferredProfileId = null,
}: ProfileOverviewPanelProps) {
  const [profiles, setProfiles] = useState<ProfileCatalogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [leftId, setLeftId] = useState('');
  const [rightId, setRightId] = useState('');
  const [enablement, setEnablement] = useState<EnablementState>(() =>
    defaultEnablement(null),
  );

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const catalog = await fetchProfileCatalog(accessToken);
      setProfiles(catalog.profiles);
      const preferred =
        catalog.profiles.find((p) => p.id === preferredProfileId) ??
        catalog.profiles[0];
      const compare =
        catalog.profiles.find((p) => p.id !== preferred?.id) ??
        catalog.profiles[1] ??
        preferred;
      if (preferred) {
        setLeftId(preferred.id);
        setEnablement(defaultEnablement(preferred));
      }
      if (compare) {
        setRightId(compare.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load catalog');
      setProfiles([]);
    } finally {
      setLoading(false);
    }
  }, [accessToken, preferredProfileId]);

  /* eslint-disable react-hooks/set-state-in-effect -- initial catalog load */
  useEffect(() => {
    void load();
    // preferredProfileId is applied on load only; later parent picks update leftId below
    // eslint-disable-next-line react-hooks/exhaustive-deps -- avoid re-fetch on picker change
  }, [accessToken]);
  /* eslint-enable react-hooks/set-state-in-effect */

  /* eslint-disable react-hooks/set-state-in-effect -- sync primary from parent picker */
  useEffect(() => {
    if (!preferredProfileId || profiles.length === 0) {
      return;
    }
    if (profiles.some((p) => p.id === preferredProfileId)) {
      setLeftId(preferredProfileId);
    }
  }, [preferredProfileId, profiles]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const left = profiles.find((p) => p.id === leftId) ?? profiles[0] ?? null;
  const right = profiles.find((p) => p.id === rightId) ?? null;

  /* eslint-disable react-hooks/set-state-in-effect -- reset enablement when left profile changes */
  useEffect(() => {
    if (left) {
      setEnablement(defaultEnablement(left));
    }
  }, [left]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const diffs = useMemo(() => {
    if (!left || !right || left.id === right.id) {
      return [] as string[];
    }
    const out: string[] = [];
    if (!sameList(left.products, right.products)) {
      const leftProducts = left.products.length ? left.products.join(', ') : '—';
      const rightProducts = right.products.length ? right.products.join(', ') : '—';
      out.push(`Products: ${leftProducts} vs ${rightProducts}`);
    }
    if ((left.iwxxm_line ?? '') !== (right.iwxxm_line ?? '')) {
      const leftLine = left.iwxxm_line ? left.iwxxm_line : '—';
      const rightLine = right.iwxxm_line ? right.iwxxm_line : '—';
      out.push(`IWXXM line: ${leftLine} vs ${rightLine}`);
    }
    if ((left.rule_pack_count ?? null) !== (right.rule_pack_count ?? null)) {
      out.push(
        `Rule packs: ${left.rule_pack_count ?? '—'} vs ${right.rule_pack_count ?? '—'}`,
      );
    }
    if ((left.overlay_count ?? null) !== (right.overlay_count ?? null)) {
      out.push(
        `Overlays: ${left.overlay_count ?? '—'} vs ${right.overlay_count ?? '—'}`,
      );
    }
    const leftDeltas = left.deltas_vs_icao ?? [];
    const rightDeltas = right.deltas_vs_icao ?? [];
    if (!sameList(leftDeltas, rightDeltas)) {
      out.push('Difference notes vs ICAO differ between profiles.');
    }
    if (out.length === 0) {
      out.push('No catalog differences between the selected profiles.');
    }
    return out;
  }, [left, right]);

  const yamlBody = enablementToYaml(left?.id ?? 'unknown', enablement);

  return (
    <Card className="space-y-3 p-4" data-testid="profile-overview-panel">
      <div data-testid="profile-overview-stub">
        <h3 className="text-sm font-medium">{PROFILES_OVERVIEW_HEADING}</h3>
        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
          {PROFILES_OVERVIEW_HELP}
        </p>
      </div>

      {loading ? (
        <p className="flex items-center gap-2 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          Loading profiles…
        </p>
      ) : error ? (
        <p className="text-sm text-amber-700" data-testid="profile-overview-error">
          {error}
        </p>
      ) : (
        <>
          <div
            className="space-y-2 rounded border border-gray-200 p-3 dark:border-gray-700"
            data-testid="profile-overview-compare"
          >
            <h4 className="text-sm font-medium">{PROFILES_OVERVIEW_COMPARE_HEADING}</h4>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">Primary</span>
                <select
                  className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="profile-overview-left-select"
                  value={left?.id ?? ''}
                  onChange={(e) => setLeftId(e.target.value)}
                >
                  {profiles.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.id}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-xs">
                <span className="text-gray-600 dark:text-gray-400">Compare</span>
                <select
                  className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="profile-overview-right-select"
                  value={right?.id ?? ''}
                  onChange={(e) => setRightId(e.target.value)}
                >
                  {profiles.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.id}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <ul
              className="list-disc space-y-1 pl-5 text-sm text-gray-700 dark:text-gray-300"
              data-testid="profile-overview-compare-diffs"
            >
              {diffs.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
            {/* Compat with P0 stub test id */}
            <span className="sr-only" data-testid="profile-overview-compare-stub">
              {PROFILES_OVERVIEW_COMPARE_HEADING}
            </span>
          </div>

          <div
            className="space-y-2 rounded border border-gray-200 p-3 dark:border-gray-700"
            data-testid="profile-overview-enablement"
          >
            <h4 className="text-sm font-medium">
              {PROFILES_OVERVIEW_ENABLEMENT_HEADING}
            </h4>
            <p className="text-xs text-gray-500">
              Enablement applies to the primary profile. Activate stays fail-closed on
              library Fail diagnostics; this YAML is the portable enablement source of
              truth for the profile.
            </p>
            <fieldset className="space-y-1">
              <legend className="text-xs font-medium text-gray-600 dark:text-gray-400">
                Products
              </legend>
              <div className="flex flex-wrap gap-3">
                {PRODUCT_OPTIONS.map((p) => (
                  <label key={p} className="flex items-center gap-1 text-xs">
                    <input
                      type="checkbox"
                      data-testid={`profile-overview-product-${p}`}
                      checked={Boolean(enablement.products[p])}
                      onChange={(e) =>
                        setEnablement((prev) => ({
                          ...prev,
                          products: { ...prev.products, [p]: e.target.checked },
                        }))
                      }
                    />
                    {p}
                  </label>
                ))}
              </div>
            </fieldset>
            <fieldset className="space-y-1">
              <legend className="text-xs font-medium text-gray-600 dark:text-gray-400">
                File types
              </legend>
              <div className="flex flex-wrap gap-3">
                {FILE_TYPE_OPTIONS.map((f) => (
                  <label key={f} className="flex items-center gap-1 text-xs">
                    <input
                      type="checkbox"
                      data-testid={`profile-overview-filetype-${f}`}
                      checked={Boolean(enablement.fileTypes[f])}
                      onChange={(e) =>
                        setEnablement((prev) => ({
                          ...prev,
                          fileTypes: {
                            ...prev.fileTypes,
                            [f]: e.target.checked,
                          },
                        }))
                      }
                    />
                    {f}
                  </label>
                ))}
              </div>
            </fieldset>
            <fieldset className="space-y-1">
              <legend className="text-xs font-medium text-gray-600 dark:text-gray-400">
                IWXXM versions
              </legend>
              <div className="flex flex-wrap gap-3">
                {IWXXM_VERSION_OPTIONS.map((v) => (
                  <label key={v} className="flex items-center gap-1 text-xs">
                    <input
                      type="checkbox"
                      data-testid={`profile-overview-iwxxm-${v}`}
                      checked={Boolean(enablement.iwxxmVersions[v])}
                      onChange={(e) =>
                        setEnablement((prev) => ({
                          ...prev,
                          iwxxmVersions: {
                            ...prev.iwxxmVersions,
                            [v]: e.target.checked,
                          },
                        }))
                      }
                    />
                    {v}
                  </label>
                ))}
              </div>
            </fieldset>
            <span className="sr-only" data-testid="profile-overview-enablement-stub">
              {PROFILES_OVERVIEW_ENABLEMENT_HEADING}
            </span>
          </div>

          <div className="space-y-1">
            <h4 className="text-sm font-medium">{PROFILES_OVERVIEW_YAML_HEADING}</h4>
            <pre
              className="max-h-48 overflow-auto rounded border border-gray-200 bg-gray-50 p-2 text-xs dark:border-gray-700 dark:bg-gray-900"
              data-testid="profile-overview-enablement-yaml"
            >
              {yamlBody}
            </pre>
          </div>
        </>
      )}
    </Card>
  );
}
