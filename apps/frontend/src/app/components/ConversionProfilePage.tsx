/**
 * ConversionProfile editor — catalog inspector and Libraries shell.
 * Requires sign-in.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { CircleHelp, Loader2 } from 'lucide-react';
import {
  fetchProfileCatalog,
  type ProfileCatalogEntry,
} from '@/utils/conversionProfilesApi';
import { SEMANTIC_PROFILE_OPTIONS } from '@/utils/semanticProfile';
import {
  PROFILES_COUNT_UNAVAILABLE,
  PROFILES_EDITOR_LOGIN_REQUIRED,
  PROFILES_EDITOR_SIGN_IN,
  PROFILES_EDITOR_SUBTITLE,
  PROFILES_EDITOR_TITLE,
  PROFILES_ERROR_PREFIX,
  PROFILES_INSPECTOR_EMPTY,
  PROFILES_INSPECTOR_HEADING,
  PROFILES_INSPECTOR_LOADING,
  PROFILES_INSPECTOR_SELECT,
  PROFILES_INSPECTOR_UNAVAILABLE,
  PROFILES_PROFILE_AUTHORITY,
  PROFILES_PROFILE_COVERAGE,
  PROFILES_PROFILE_FAMILY,
  PROFILES_TOOLTIP_INSPECTOR_COMPARE,
  PROFILES_TOOLTIP_INSPECTOR_PROFILE,
  PROFILES_TOOLTIP_PROFILE_BLOCKS,
} from '@/utils/conversionProfilesCopy';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { BetaBadge } from './BetaBadge';
import { ProfileBuilderLibraries } from './ProfileBuilderLibraries';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

export interface ConversionProfilePageProps {
  /** Bearer JWT — when absent, show sign-in prompt. */
  accessToken?: string;
  /** Navigate to login. */
  onRequestLogin?: () => void;
  /** Return to the convert workbench to open profile-aware examples. */
  onOpenConverterExamples?: () => void;
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : 'Unknown error';
}

interface AuthedProps {
  accessToken: string;
}

function FieldHelpTooltip({ label, tooltip }: { label: string; tooltip: string }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          type="button"
          className="inline-flex h-5 w-5 items-center justify-center rounded text-gray-500 hover:text-gray-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:text-gray-400 dark:hover:text-gray-100"
          aria-label={label}
        >
          <CircleHelp className="h-3.5 w-3.5" aria-hidden />
        </button>
      </TooltipTrigger>
      <TooltipContent side="bottom" className="max-w-xs text-balance">
        {tooltip}
      </TooltipContent>
    </Tooltip>
  );
}

const PROFILE_LABELS = new Map<string, string>(
  SEMANTIC_PROFILE_OPTIONS.map((option) => [option.value, option.label]),
);

function profileLabel(profileId: string): string {
  return PROFILE_LABELS.get(profileId) ?? profileId;
}

function profileFamily(profileId: string): string {
  if (profileId.startsWith('ICAO_')) {
    return 'ICAO / WMO baseline';
  }
  return 'National or regional extension';
}

function profileAuthority(profileId: string): string {
  if (profileId.startsWith('ICAO_')) {
    return 'ICAO / WMO';
  }
  const [country, ...rest] = profileId.split('_');
  const suffix = rest.join(' ');
  return suffix ? `${country} - ${suffix}` : profileId;
}

function profileCoverage(profile: ProfileCatalogEntry): string {
  const kinds: string[] = [];
  if (profile.products.length > 0) {
    kinds.push(profile.products.join(', '));
  }
  if (profile.iwxxm_line) {
    kinds.push(profile.iwxxm_line);
  }
  return kinds.join(' | ') || 'Coverage details unavailable';
}

function compareValue(value: string): string {
  return value.trim() || '—';
}

function sameValue(left: string, right: string): boolean {
  return compareValue(left) === compareValue(right);
}

function matchingDeltaLines(
  deltas: readonly string[],
  compareDeltas: readonly string[],
): boolean {
  if (deltas.length !== compareDeltas.length) {
    return false;
  }
  for (let index = 0; index < deltas.length; index += 1) {
    if (!sameValue(deltas[index]!, compareDeltas[index]!)) {
      return false;
    }
  }
  return true;
}

function countDisplay(value: number | null | undefined): string {
  return typeof value === 'number' ? String(value) : PROFILES_COUNT_UNAVAILABLE;
}

function unavailableMessage(detail: string | null): string {
  return [PROFILES_INSPECTOR_UNAVAILABLE, detail].filter(Boolean).join(' ');
}

interface ProfileSummaryCardProps {
  profile: ProfileCatalogEntry;
  heading: string;
  testId: string;
  compareAgainst?: ProfileCatalogEntry | null;
}

type ProfileBlockId =
  | 'input'
  | 'validation-tac'
  | 'conversion'
  | 'output-validation'
  | 'exchange';

interface ProfileBlockDefinition {
  id: ProfileBlockId;
  label: string;
  summary: (profile: ProfileCatalogEntry) => string;
}

function detailString(value: unknown, fallback: string): string {
  if (typeof value === 'string' && value.trim()) {
    return value;
  }
  return fallback;
}

const PROFILE_BLOCKS: readonly ProfileBlockDefinition[] = [
  {
    id: 'input',
    label: 'Input',
    summary: (profile) =>
      detailString(
        profile.implementation?.input,
        `Uses the ${profile.id} input path for supported TAC products.`,
      ),
  },
  {
    id: 'validation-tac',
    label: 'TAC lint',
    summary: (profile) =>
      detailString(
        profile.implementation?.validation_tac,
        profile.emit_key
          ? `TAC lint applies the ${profile.emit_key} registry path.`
          : 'TAC lint registry details are not listed for this profile.',
      ),
  },
  {
    id: 'conversion',
    label: 'Convert',
    summary: (profile) =>
      detailString(
        profile.implementation?.conversion,
        profile.emit_key
          ? `Convert emits with the ${profile.emit_key} profile mapper.`
          : 'Convert mapping details are not listed for this profile.',
      ),
  },
  {
    id: 'output-validation',
    label: 'IWXXM validate',
    summary: (profile) => {
      const iwxxmLine = detailString(profile.iwxxm_line, '');
      const vendorPin = detailString(profile.vendor_pins?.iwxxm, '');
      if (iwxxmLine && vendorPin && iwxxmLine !== vendorPin) {
        return `${iwxxmLine} (${vendorPin})`;
      }
      return detailString(
        iwxxmLine || vendorPin,
        'IWXXM validation line is not listed for this profile.',
      );
    },
  },
  {
    id: 'exchange',
    label: 'Exchange',
    summary: (profile) =>
      detailString(
        profile.implementation?.exchange,
        'No exchange default is listed for this profile.',
      ),
  },
] as const;

function ProfileSummaryCard({
  profile,
  heading,
  testId,
  compareAgainst = null,
}: ProfileSummaryCardProps) {
  const deltas = profile.deltas_vs_icao?.slice(0, 3) ?? [];
  const compareDeltas = compareAgainst?.deltas_vs_icao?.slice(0, 3) ?? [];
  const productLine = profile.products.join(', ');
  const compareProductLine = compareAgainst?.products.join(', ') ?? '';
  const deltaLinesMatch = matchingDeltaLines(deltas, compareDeltas);
  const counts = [
    { label: 'Rule packs', value: profile.rule_pack_count },
    { label: 'Overlays', value: profile.overlay_count },
  ];

  const fieldClass = (different: boolean) =>
    different
      ? 'rounded-md border border-amber-200 bg-amber-50 p-3 dark:border-amber-800 dark:bg-amber-950/30'
      : 'rounded-md border border-gray-200 p-3 dark:border-gray-700';

  return (
    <article
      className="space-y-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700"
      data-testid={testId}
    >
      <div className="space-y-1">
        <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
          {heading}
        </p>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {profileLabel(profile.id)}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">{profile.id}</p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div
          className={fieldClass(
            Boolean(compareAgainst) && !sameValue(productLine, compareProductLine),
          )}
        >
          <dt className="text-xs font-medium uppercase tracking-wide text-gray-500">
            Products
          </dt>
          <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">
            {productLine || '—'}
          </dd>
          {compareAgainst && !sameValue(productLine, compareProductLine) ? (
            <p className="mt-1 text-xs text-amber-900 dark:text-amber-200">
              Different from {compareAgainst.id}
            </p>
          ) : null}
        </div>
        <div
          className={fieldClass(
            Boolean(compareAgainst) &&
              !sameValue(profile.iwxxm_line ?? '', compareAgainst?.iwxxm_line ?? ''),
          )}
        >
          <dt className="text-xs font-medium uppercase tracking-wide text-gray-500">
            IWXXM line
          </dt>
          <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">
            {profile.iwxxm_line ?? '—'}
          </dd>
          {compareAgainst &&
          !sameValue(profile.iwxxm_line ?? '', compareAgainst?.iwxxm_line ?? '') ? (
            <p className="mt-1 text-xs text-amber-900 dark:text-amber-200">
              Different from {compareAgainst.id}
            </p>
          ) : null}
        </div>
      </div>

      <div className={fieldClass(Boolean(compareAgainst) && !deltaLinesMatch)}>
        <dt className="text-xs font-medium uppercase tracking-wide text-gray-500">
          Top differences vs ICAO
        </dt>
        {deltas.length > 0 ? (
          <ul className="space-y-1 text-sm text-gray-900 dark:text-gray-100">
            {deltas.map((delta) => (
              <li key={delta}>{delta}</li>
            ))}
          </ul>
        ) : (
          <dd className="text-sm text-gray-500">
            No profile-specific differences listed.
          </dd>
        )}
        {compareAgainst && !deltaLinesMatch ? (
          <p className="mt-1 text-xs text-amber-900 dark:text-amber-200">
            Difference notes compared with {compareAgainst.id}
          </p>
        ) : null}
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {counts.map((count) => {
          const otherValue =
            count.label === 'Rule packs'
              ? compareAgainst?.rule_pack_count
              : compareAgainst?.overlay_count;
          const different =
            compareAgainst !== null && (count.value ?? null) !== (otherValue ?? null);
          return (
            <div key={count.label} className={fieldClass(different)}>
              <dt className="text-xs font-medium uppercase tracking-wide text-gray-500">
                {count.label}
              </dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">
                {countDisplay(count.value)}
              </dd>
              {different ? (
                <p className="mt-1 text-xs text-amber-900 dark:text-amber-200">
                  Different from {compareAgainst?.id}
                </p>
              ) : null}
            </div>
          );
        })}
      </div>
    </article>
  );
}

function ConversionProfileAuthed({ accessToken }: AuthedProps) {
  const [catalog, setCatalog] = useState<ProfileCatalogEntry[] | null>(null);
  const [loadErrors, setLoadErrors] = useState<{ catalog: string | null }>({
    catalog: null,
  });
  const [selectedId, setSelectedId] = useState<string>('');
  const [compareId, setCompareId] = useState<string>('');
  const [activeBlockId, setActiveBlockId] = useState<ProfileBlockId>('input');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const settled = await Promise.allSettled([fetchProfileCatalog(accessToken)]);
    const [catResult] = settled;

    const nextLoadErrors = {
      catalog: catResult.status === 'rejected' ? errorMessage(catResult.reason) : null,
    };
    setLoadErrors(nextLoadErrors);

    const nextCatalog =
      catResult.status === 'fulfilled' ? catResult.value.profiles : null;
    setCatalog((current) => nextCatalog ?? current);

    const first = nextCatalog?.[0];
    if (!selectedId && first) {
      setSelectedId(first.id);
    }

    const failureMessages = Object.values(nextLoadErrors).filter(
      (value): value is string => value !== null,
    );
    setError(failureMessages.length > 0 ? failureMessages.join(' | ') : null);
    setLoading(false);
  }, [accessToken, selectedId]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when token changes */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const selected = useMemo(
    () => catalog?.find((p) => p.id === selectedId) ?? null,
    [catalog, selectedId],
  );
  const compareProfile = useMemo(
    () => catalog?.find((p) => p.id === compareId) ?? null,
    [catalog, compareId],
  );
  const activeBlock = useMemo(
    () =>
      /* v8 ignore next -- activeBlockId is always selected from PROFILE_BLOCKS ids */
      PROFILE_BLOCKS.find((block) => block.id === activeBlockId) ?? PROFILE_BLOCKS[0]!,
    [activeBlockId],
  );
  /* v8 ignore next 24 -- both selected and empty states are tested; v8 pins branch accounting to this JSX guard */
  const summaryCards = selected ? (
    <div
      className={
        compareProfile
          ? 'grid grid-cols-1 gap-4 xl:grid-cols-2'
          : 'grid grid-cols-1 gap-4'
      }
    >
      <ProfileSummaryCard
        profile={selected}
        heading="Selected profile"
        testId="conversion-profiles-summary-primary"
        compareAgainst={compareProfile}
      />
      {compareProfile ? (
        <ProfileSummaryCard
          profile={compareProfile}
          heading="Compare profile"
          testId="conversion-profiles-summary-compare"
          compareAgainst={selected}
        />
      ) : null}
    </div>
  ) : null;

  return (
    <div
      className="mx-auto max-w-6xl space-y-4 p-4"
      data-testid="conversion-profiles-page"
    >
      <header>
        <h1 className="flex flex-wrap items-center gap-2 text-xl font-semibold text-gray-900 dark:text-gray-100">
          {PROFILES_EDITOR_TITLE}
          <BetaBadge showHelp />
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {PROFILES_EDITOR_SUBTITLE}
        </p>
      </header>

      <ProfileBuilderLibraries accessToken={accessToken} />

      <Card className="space-y-4 p-4" data-testid="conversion-profiles-inspector">
        <h2 className="text-sm font-medium">{PROFILES_INSPECTOR_HEADING}</h2>
        {loadErrors.catalog && catalog !== null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {unavailableMessage(loadErrors.catalog)}
          </p>
        ) : null}
        {selected ? (
          <dl
            className="grid grid-cols-1 gap-2 text-sm sm:grid-cols-2"
            data-testid="conversion-profiles-inspector-detail"
          >
            <div>
              <dt className="text-gray-500">Kind</dt>
              <dd>{selected.kind}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Status</dt>
              <dd>{selected.status ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Emit key</dt>
              <dd>{selected.emit_key ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Legacy alias</dt>
              <dd>{selected.legacy_alias ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-gray-500">{PROFILES_PROFILE_FAMILY}</dt>
              <dd>{profileFamily(selected.id)}</dd>
            </div>
            <div>
              <dt className="text-gray-500">{PROFILES_PROFILE_AUTHORITY}</dt>
              <dd>{profileAuthority(selected.id)}</dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-gray-500">{PROFILES_PROFILE_COVERAGE}</dt>
              <dd>{profileCoverage(selected)}</dd>
            </div>
          </dl>
        ) : loadErrors.catalog ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {unavailableMessage(loadErrors.catalog)}
          </p>
        ) : (
          <p className="text-sm text-gray-500">{PROFILES_INSPECTOR_EMPTY}</p>
        )}
      </Card>

      {error && (
        <p className="text-sm text-red-600" data-testid="conversion-profiles-error">
          {PROFILES_ERROR_PREFIX} {error}
        </p>
      )}

      <Card className="space-y-4 p-4" data-testid="conversion-profiles-summary">
        {loadErrors.catalog && catalog !== null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {unavailableMessage(loadErrors.catalog)}
          </p>
        ) : null}
        {loading && catalog === null ? (
          <p className="flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            {PROFILES_INSPECTOR_LOADING}
          </p>
        ) : loadErrors.catalog && catalog === null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {unavailableMessage(loadErrors.catalog)}
          </p>
        ) : !catalog || catalog.length === 0 ? (
          <p className="text-sm text-gray-500">{PROFILES_INSPECTOR_EMPTY}</p>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
              <label className="block text-sm">
                <span className="inline-flex items-center gap-1 text-gray-700 dark:text-gray-300">
                  {PROFILES_INSPECTOR_SELECT}
                  <FieldHelpTooltip
                    label={`About ${PROFILES_INSPECTOR_SELECT}`}
                    tooltip={PROFILES_TOOLTIP_INSPECTOR_PROFILE}
                  />
                </span>
                <select
                  className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="conversion-profiles-select"
                  value={selectedId}
                  onChange={(e) => {
                    const nextId = e.target.value;
                    setSelectedId(nextId);
                    if (compareId === nextId) {
                      setCompareId('');
                    }
                  }}
                >
                  {catalog.map((p) => (
                    <option key={p.id} value={p.id}>
                      {profileLabel(p.id)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm">
                <span className="inline-flex items-center gap-1 text-gray-700 dark:text-gray-300">
                  Compare with
                  <FieldHelpTooltip
                    label="About compare profile"
                    tooltip={PROFILES_TOOLTIP_INSPECTOR_COMPARE}
                  />
                </span>
                <select
                  className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
                  data-testid="conversion-profiles-compare-select"
                  value={compareId}
                  onChange={(e) => setCompareId(e.target.value)}
                >
                  <option value="">None</option>
                  {catalog
                    .filter((p) => p.id !== selectedId)
                    .map((p) => (
                      <option key={p.id} value={p.id}>
                        {profileLabel(p.id)}
                      </option>
                    ))}
                </select>
              </label>
            </div>
            {summaryCards}
          </>
        )}
      </Card>

      <Card className="space-y-4 p-4" data-testid="conversion-profiles-blocks">
        <div className="flex items-center gap-1">
          <h2 className="text-sm font-medium">Profile blocks</h2>
          <FieldHelpTooltip
            label="About profile blocks"
            tooltip={PROFILES_TOOLTIP_PROFILE_BLOCKS}
          />
        </div>
        {loadErrors.catalog && catalog !== null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {unavailableMessage(loadErrors.catalog)}
          </p>
        ) : null}
        {selected ? (
          <>
            <div className="grid grid-cols-1 gap-2 md:grid-cols-5">
              {PROFILE_BLOCKS.map((block) => (
                <button
                  key={block.id}
                  type="button"
                  data-testid={`conversion-profiles-block-${block.id}`}
                  onClick={() => setActiveBlockId(block.id)}
                  className={`rounded-md border px-3 py-2 text-left text-sm ${
                    activeBlockId === block.id
                      ? 'border-blue-500 bg-blue-50 text-blue-950 dark:bg-blue-950/40 dark:text-blue-100'
                      : 'border-gray-200 bg-white text-gray-700 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300'
                  }`}
                >
                  <span className="font-medium">{block.label}</span>
                </button>
              ))}
            </div>

            <div
              className="rounded-md border border-gray-200 p-4 dark:border-gray-700"
              data-testid="conversion-profiles-block-detail"
            >
              <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {activeBlock.label}
              </h3>
              <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
                {activeBlock.summary(selected)}
              </p>
              <div className="mt-3 flex flex-wrap gap-2 text-sm">
                <a
                  className="rounded border border-gray-300 px-3 py-1.5 text-gray-700 dark:border-gray-600 dark:text-gray-200"
                  data-testid="conversion-profiles-block-jump-libraries"
                  href="#profile-builder-libraries"
                >
                  Open libraries
                </a>
              </div>
            </div>
          </>
        ) : loadErrors.catalog ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {unavailableMessage(loadErrors.catalog)}
          </p>
        ) : (
          <p className="text-sm text-gray-500">{PROFILES_INSPECTOR_EMPTY}</p>
        )}
      </Card>
    </div>
  );
}

/**
 * Conversion profiles shell page.
 *
 * @param props.accessToken - Optional JWT
 * @param props.onRequestLogin - Sign-in handler
 */
export function ConversionProfilePage({
  accessToken,
  onRequestLogin,
  onOpenConverterExamples,
}: ConversionProfilePageProps) {
  if (!accessToken) {
    return (
      <div
        className="mx-auto max-w-lg space-y-4 p-8 text-center"
        data-testid="conversion-profiles-page"
      >
        <h1 className="flex flex-wrap items-center justify-center gap-2 text-xl font-semibold">
          {PROFILES_EDITOR_TITLE}
          <BetaBadge showHelp />
        </h1>
        <p className="text-sm text-gray-600">{PROFILES_EDITOR_LOGIN_REQUIRED}</p>
        <Button
          type="button"
          data-testid="conversion-profiles-sign-in"
          onClick={() => onRequestLogin?.()}
        >
          {PROFILES_EDITOR_SIGN_IN}
        </Button>
      </div>
    );
  }
  void onOpenConverterExamples;
  return <ConversionProfileAuthed accessToken={accessToken} />;
}
