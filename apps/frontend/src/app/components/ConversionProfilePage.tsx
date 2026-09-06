/**
 * ConversionProfile editor — catalog inspector, rule packs, signed overlays (UJ-072 / F7.w).
 * Requires sign-in.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Loader2 } from 'lucide-react';
import {
  createOverlay,
  createRulePack,
  fetchProfileCatalog,
  listOverlays,
  listRulePacks,
  type OverlayOut,
  type ProfileCatalogEntry,
  type RulePackOut,
} from '@/utils/conversionProfilesApi';
import { SEMANTIC_PROFILE_OPTIONS } from '@/utils/semanticProfile';
import {
  PROFILES_EDITOR_LOGIN_REQUIRED,
  PROFILES_EDITOR_SIGN_IN,
  PROFILES_EDITOR_SUBTITLE,
  PROFILES_EDITOR_TITLE,
  PROFILES_COUNT_UNAVAILABLE,
  PROFILES_ERROR_PREFIX,
  PROFILES_INSPECTOR_EMPTY,
  PROFILES_INSPECTOR_HEADING,
  PROFILES_INSPECTOR_LOADING,
  PROFILES_INSPECTOR_SELECT,
  PROFILES_INSPECTOR_UNAVAILABLE,
  PROFILES_OVERLAY_BASE,
  PROFILES_OVERLAY_BODY,
  PROFILES_OVERLAY_HINT,
  PROFILES_OVERLAY_SAVE,
  PROFILES_OVERLAY_SLUG,
  PROFILES_OVERLAYS_EMPTY,
  PROFILES_OVERLAYS_HEADING,
  PROFILES_OVERLAYS_LOADING,
  PROFILES_OVERLAYS_UNAVAILABLE,
  PROFILES_PACK_EXPORT,
  PROFILES_PACK_MESSAGE,
  PROFILES_PACK_PRODUCT,
  PROFILES_PACK_PROFILE,
  PROFILES_PACK_REF,
  PROFILES_PACK_SAVE,
  PROFILES_PACK_SEVERITY,
  PROFILES_PACK_SLUG,
  PROFILES_PACK_STAGE,
  PROFILES_PACK_WHEN,
  PROFILES_PACKS_EMPTY,
  PROFILES_PACKS_HEADING,
  PROFILES_PACKS_LOADING,
  PROFILES_PACKS_UNAVAILABLE,
} from '@/utils/conversionProfilesCopy';
import { Button } from './ui/button';
import { Card } from './ui/card';

export interface ConversionProfilePageProps {
  /** Bearer JWT — when absent, show sign-in prompt. */
  accessToken?: string;
  /** Navigate to login. */
  onRequestLogin?: () => void;
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : 'Unknown error';
}

interface AuthedProps {
  accessToken: string;
}

interface LoadErrorState {
  catalog: string | null;
  packs: string | null;
  overlays: string | null;
}

const PROFILE_LABELS = new Map<string, string>(
  SEMANTIC_PROFILE_OPTIONS.map((option) => [option.value, option.label]),
);

function profileLabel(profileId: string): string {
  return PROFILE_LABELS.get(profileId) ?? profileId;
}

function compareValue(value: string): string {
  return value.trim() || '—';
}

function sameValue(left: string, right: string): boolean {
  return compareValue(left) === compareValue(right);
}

function countDisplay(value: number | null | undefined): string {
  return typeof value === 'number' ? String(value) : PROFILES_COUNT_UNAVAILABLE;
}

function unavailableMessage(detail: string | null): string {
  return [PROFILES_INSPECTOR_UNAVAILABLE, detail].filter(Boolean).join(' ');
}

function starterSlug(profileId: string, kind: 'pack' | 'overlay'): string {
  return `starter-${profileId.toLowerCase().replaceAll('_', '-')}-${kind}`;
}

function starterProduct(profile: ProfileCatalogEntry | null): string {
  return profile?.products[0] ?? 'METAR';
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
  const productLine = profile.products.join(', ');
  const compareProductLine = compareAgainst?.products.join(', ') ?? '';
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

      <div className="space-y-2 rounded-md border border-gray-200 p-3 dark:border-gray-700">
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
  const [packs, setPacks] = useState<RulePackOut[] | null>(null);
  const [overlays, setOverlays] = useState<OverlayOut[] | null>(null);
  const [loadErrors, setLoadErrors] = useState<LoadErrorState>({
    catalog: null,
    packs: null,
    overlays: null,
  });
  const [selectedId, setSelectedId] = useState<string>('');
  const [compareId, setCompareId] = useState<string>('');
  const [activeBlockId, setActiveBlockId] = useState<ProfileBlockId>('input');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savingOverlay, setSavingOverlay] = useState(false);
  const [packSeedDirty, setPackSeedDirty] = useState(false);
  const [overlaySeedDirty, setOverlaySeedDirty] = useState(false);

  const [slug, setSlug] = useState('my-pack');
  const [profile, setProfile] = useState('ICAO_2025');
  const [product, setProduct] = useState('METAR');
  const [stage, setStage] = useState('lint');
  const [severity, setSeverity] = useState('warning');
  const [whenExpr, setWhenExpr] = useState('');
  const [message, setMessage] = useState('');
  const [standardRef, setStandardRef] = useState('');

  const [overlaySlug, setOverlaySlug] = useState('my-overlay');
  const [overlayBase, setOverlayBase] = useState('ICAO_2025');
  const [overlayBodyText, setOverlayBodyText] = useState('{}');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const [catResult, packResult, overlayResult] = await Promise.allSettled([
      fetchProfileCatalog(accessToken),
      listRulePacks(accessToken),
      listOverlays(accessToken),
    ]);

    const nextLoadErrors: LoadErrorState = {
      catalog: catResult.status === 'rejected' ? errorMessage(catResult.reason) : null,
      packs: packResult.status === 'rejected' ? errorMessage(packResult.reason) : null,
      overlays:
        overlayResult.status === 'rejected' ? errorMessage(overlayResult.reason) : null,
    };
    setLoadErrors(nextLoadErrors);

    const nextCatalog =
      catResult.status === 'fulfilled' ? catResult.value.profiles : null;
    const nextPacks = packResult.status === 'fulfilled' ? packResult.value.items : null;
    const nextOverlays =
      overlayResult.status === 'fulfilled' ? overlayResult.value.items : null;
    setCatalog((current) => nextCatalog ?? current);
    setPacks((current) => nextPacks ?? current);
    setOverlays((current) => nextOverlays ?? current);

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

  /* eslint-disable react-hooks/set-state-in-effect -- keep starter forms aligned only while untouched */
  useEffect(() => {
    if (!selected || packs === null || packs.length > 0 || packSeedDirty) {
      return;
    }
    setSlug(starterSlug(selected.id, 'pack'));
    setProfile(selected.id);
    setProduct(starterProduct(selected));
    setStage('lint');
    setSeverity('warning');
    setWhenExpr('');
    setMessage(`Starter guidance for ${profileLabel(selected.id)}`);
    setStandardRef(selected.iwxxm_line ?? '');
  }, [packSeedDirty, packs, selected]);

  useEffect(() => {
    if (!selected || overlays === null || overlays.length > 0 || overlaySeedDirty) {
      return;
    }
    setOverlaySlug(starterSlug(selected.id, 'overlay'));
    setOverlayBase(selected.id);
    setOverlayBodyText('{}');
  }, [overlaySeedDirty, overlays, selected]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const onSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await createRulePack(accessToken, {
        slug,
        profile,
        product,
        stage,
        severity,
        when: whenExpr,
        message,
        standardReference: standardRef,
      });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const onSaveOverlay = async () => {
    setSavingOverlay(true);
    setError(null);
    try {
      let parsed: unknown;
      try {
        parsed = JSON.parse(overlayBodyText.trim() || '{}');
      } catch {
        throw new Error('Overlay JSON must be valid');
      }
      if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('Overlay JSON must be an object');
      }
      await createOverlay(accessToken, {
        slug: overlaySlug,
        baseProfileId: overlayBase,
        body: parsed as Record<string, unknown>,
      });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSavingOverlay(false);
    }
  };

  const onExport = () => {
    // Invoked only when the export control is enabled (packs loaded and non-empty).
    const blob = new Blob([JSON.stringify(packs, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rule-packs.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className="mx-auto max-w-6xl space-y-4 p-4"
      data-testid="conversion-profiles-page"
    >
      <header>
        <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          {PROFILES_EDITOR_TITLE}
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {PROFILES_EDITOR_SUBTITLE}
        </p>
      </header>

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
                <span className="text-gray-700 dark:text-gray-300">
                  {PROFILES_INSPECTOR_SELECT}
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
                      {p.id} ({p.kind})
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm">
                <span className="text-gray-700 dark:text-gray-300">Compare with</span>
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
                        {p.id}
                      </option>
                    ))}
                </select>
              </label>
            </div>
            {summaryCards}
          </>
        )}
      </Card>

      <Card className="space-y-3 p-4" data-testid="conversion-profiles-inspector">
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
          </dl>
        ) : loadErrors.catalog ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {unavailableMessage(loadErrors.catalog)}
          </p>
        ) : (
          <p className="text-sm text-gray-500">{PROFILES_INSPECTOR_EMPTY}</p>
        )}
      </Card>

      <Card className="space-y-4 p-4" data-testid="conversion-profiles-blocks">
        <h2 className="text-sm font-medium">Profile blocks</h2>
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
                  data-testid="conversion-profiles-block-jump-packs"
                  href="#conversion-profiles-packs"
                >
                  Open rule packs
                </a>
                <a
                  className="rounded border border-gray-300 px-3 py-1.5 text-gray-700 dark:border-gray-600 dark:text-gray-200"
                  data-testid="conversion-profiles-block-jump-overlays"
                  href="#conversion-profiles-overlays"
                >
                  Open signed overlays
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

      <Card
        className="space-y-3 p-4"
        data-testid="conversion-profiles-packs"
        id="conversion-profiles-packs"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-sm font-medium">{PROFILES_PACKS_HEADING}</h2>
          <Button
            type="button"
            variant="outline"
            size="sm"
            data-testid="conversion-profiles-export"
            onClick={onExport}
            disabled={!packs || packs.length === 0}
          >
            {PROFILES_PACK_EXPORT}
          </Button>
        </div>

        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <label className="text-sm">
            {PROFILES_PACK_SLUG}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-slug"
              value={slug}
              onChange={(e) => {
                setPackSeedDirty(true);
                setSlug(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PACK_PROFILE}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-profile"
              value={profile}
              onChange={(e) => {
                setPackSeedDirty(true);
                setProfile(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PACK_PRODUCT}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-product"
              value={product}
              onChange={(e) => {
                setPackSeedDirty(true);
                setProduct(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PACK_STAGE}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-stage"
              value={stage}
              onChange={(e) => {
                setPackSeedDirty(true);
                setStage(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PACK_SEVERITY}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-severity"
              value={severity}
              onChange={(e) => {
                setPackSeedDirty(true);
                setSeverity(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PACK_WHEN}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-when"
              value={whenExpr}
              onChange={(e) => {
                setPackSeedDirty(true);
                setWhenExpr(e.target.value);
              }}
            />
          </label>
          <label className="text-sm sm:col-span-2">
            {PROFILES_PACK_MESSAGE}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-message"
              value={message}
              onChange={(e) => {
                setPackSeedDirty(true);
                setMessage(e.target.value);
              }}
            />
          </label>
          <label className="text-sm sm:col-span-2">
            {PROFILES_PACK_REF}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-ref"
              value={standardRef}
              onChange={(e) => {
                setPackSeedDirty(true);
                setStandardRef(e.target.value);
              }}
            />
          </label>
        </div>
        {packs !== null && packs.length === 0 && !packSeedDirty ? (
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Starter pack fields stay in sync with the selected profile until you edit
            them.
          </p>
        ) : null}

        <Button
          type="button"
          data-testid="conversion-profiles-pack-save"
          onClick={() => void onSave()}
          disabled={saving}
        >
          {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : null}
          {PROFILES_PACK_SAVE}
        </Button>

        {loadErrors.packs && packs !== null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {PROFILES_PACKS_UNAVAILABLE} {loadErrors.packs}
          </p>
        ) : null}
        {loading && packs === null ? (
          <p className="text-sm text-gray-500">{PROFILES_PACKS_LOADING}</p>
        ) : loadErrors.packs && packs === null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {PROFILES_PACKS_UNAVAILABLE} {loadErrors.packs}
          </p>
        ) : !packs || packs.length === 0 ? (
          <p className="text-sm text-gray-500">{PROFILES_PACKS_EMPTY}</p>
        ) : (
          <ul className="space-y-1 text-sm" data-testid="conversion-profiles-pack-list">
            {packs.map((p) => (
              <li key={p.id}>
                <code>{p.slug}</code> — {p.profile} / {p.product} ({p.severity})
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card
        className="space-y-3 p-4"
        data-testid="conversion-profiles-overlays"
        id="conversion-profiles-overlays"
      >
        <h2 className="text-sm font-medium">{PROFILES_OVERLAYS_HEADING}</h2>
        <p className="text-xs text-gray-600 dark:text-gray-400">
          {PROFILES_OVERLAY_HINT}
        </p>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <label className="text-sm">
            {PROFILES_OVERLAY_SLUG}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-overlay-slug"
              value={overlaySlug}
              onChange={(e) => {
                setOverlaySeedDirty(true);
                setOverlaySlug(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_OVERLAY_BASE}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-overlay-base"
              value={overlayBase}
              onChange={(e) => {
                setOverlaySeedDirty(true);
                setOverlayBase(e.target.value);
              }}
            />
          </label>
          <label className="text-sm sm:col-span-2">
            {PROFILES_OVERLAY_BODY}
            <textarea
              className="mt-1 w-full rounded border p-2 font-mono text-xs dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-overlay-body"
              rows={4}
              value={overlayBodyText}
              onChange={(e) => {
                setOverlaySeedDirty(true);
                setOverlayBodyText(e.target.value);
              }}
            />
          </label>
        </div>
        {overlays !== null && overlays.length === 0 && !overlaySeedDirty ? (
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Starter overlay fields stay in sync with the selected profile until you edit
            them.
          </p>
        ) : null}
        <Button
          type="button"
          data-testid="conversion-profiles-overlay-save"
          onClick={() => void onSaveOverlay()}
          disabled={savingOverlay}
        >
          {savingOverlay ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          ) : null}
          {PROFILES_OVERLAY_SAVE}
        </Button>
        {loadErrors.overlays && overlays !== null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {PROFILES_OVERLAYS_UNAVAILABLE} {loadErrors.overlays}
          </p>
        ) : null}
        {loading && overlays === null ? (
          <p className="text-sm text-gray-500">{PROFILES_OVERLAYS_LOADING}</p>
        ) : loadErrors.overlays && overlays === null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {PROFILES_OVERLAYS_UNAVAILABLE} {loadErrors.overlays}
          </p>
        ) : !overlays || overlays.length === 0 ? (
          <p className="text-sm text-gray-500">{PROFILES_OVERLAYS_EMPTY}</p>
        ) : (
          <ul
            className="space-y-1 text-sm"
            data-testid="conversion-profiles-overlay-list"
          >
            {overlays.map((o) => (
              <li key={o.id}>
                <code>{o.slug}</code> — {o.baseProfileId}{' '}
                <span className="text-gray-500">({o.id})</span>
              </li>
            ))}
          </ul>
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
}: ConversionProfilePageProps) {
  if (!accessToken) {
    return (
      <div
        className="mx-auto max-w-lg space-y-4 p-8 text-center"
        data-testid="conversion-profiles-page"
      >
        <h1 className="text-xl font-semibold">{PROFILES_EDITOR_TITLE}</h1>
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
  return <ConversionProfileAuthed accessToken={accessToken} />;
}
