/**
 * ConversionProfile editor — catalog inspector, rule packs, signed overlays (UJ-072 / F7.w).
 * Requires sign-in.
 */

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
} from 'react';
import { Loader2 } from 'lucide-react';
import {
  createOverlay,
  createPreset,
  createRulePack,
  createTemplate,
  deleteOverlay,
  deletePreset,
  deleteRulePack,
  deleteTemplate,
  fetchProfileCatalog,
  listPresets,
  listTemplates,
  listOverlays,
  listRulePacks,
  type DisseminationTemplateOut,
  type OverlayOut,
  type PresetOut,
  type ProfileCatalogEntry,
  type RulePackOut,
  updateTemplate,
  updateOverlay,
  updatePreset,
  updateRulePack,
} from '@/utils/conversionProfilesApi';
import {
  DEFAULT_SEMANTIC_PROFILE,
  SEMANTIC_PROFILE_OPTIONS,
  hydrateSemanticProfile,
} from '@/utils/semanticProfile';
import {
  PROFILES_EXAMPLES_EMPTY,
  PROFILES_EXAMPLES_HEADING,
  PROFILES_EXAMPLES_PREFIX,
  PROFILES_EXAMPLES_REUSE_NOTE,
  PROFILES_EDITOR_LOGIN_REQUIRED,
  PROFILES_EDITOR_SIGN_IN,
  PROFILES_EDITOR_SUBTITLE,
  PROFILES_EDITOR_TITLE,
  PROFILES_GLOSSARY_EXCHANGE,
  PROFILES_GLOSSARY_HEADING,
  PROFILES_GLOSSARY_OVERLAY,
  PROFILES_GLOSSARY_PROFILE,
  PROFILES_COUNT_UNAVAILABLE,
  PROFILES_ERROR_PREFIX,
  PROFILES_INSPECTOR_EMPTY,
  PROFILES_INSPECTOR_HEADING,
  PROFILES_INSPECTOR_LOADING,
  PROFILES_INSPECTOR_SELECT,
  PROFILES_INSPECTOR_UNAVAILABLE,
  PROFILES_OVERLAY_BASE,
  PROFILES_OVERLAY_BODY,
  PROFILES_OVERLAY_DELETE,
  PROFILES_OVERLAY_HINT,
  PROFILES_OVERLAY_NEW,
  PROFILES_OVERLAY_SAVE,
  PROFILES_OVERLAY_SLUG,
  PROFILES_OVERLAY_UPDATE,
  PROFILES_OVERLAYS_EMPTY,
  PROFILES_OVERLAYS_HEADING,
  PROFILES_OVERLAYS_LOADING,
  PROFILES_OVERLAYS_UNAVAILABLE,
  PROFILES_PRESET_DELETE,
  PROFILES_PRESET_IWXXM_VERSION,
  PROFILES_PRESET_NAME,
  PROFILES_PRESET_NEW,
  PROFILES_PRESET_OVERLAY,
  PROFILES_PRESET_PROFILE,
  PROFILES_PRESET_REPORT_VARIANT,
  PROFILES_PRESET_SAVE,
  PROFILES_PRESET_SHARED,
  PROFILES_PRESET_SLUG,
  PROFILES_PRESET_UPDATE,
  PROFILES_PRESETS_EMPTY,
  PROFILES_PRESETS_HEADING,
  PROFILES_PRESETS_LOADING,
  PROFILES_PRESETS_UNAVAILABLE,
  PROFILES_PROFILE_AUTHORITY,
  PROFILES_PROFILE_COVERAGE,
  PROFILES_PROFILE_FAMILY,
  PROFILES_PACK_EXPORT,
  PROFILES_PACK_IMPORT,
  PROFILES_PACK_DELETE,
  PROFILES_PACK_MESSAGE,
  PROFILES_PACK_NEW,
  PROFILES_PACK_PRODUCT,
  PROFILES_PACK_PROFILE,
  PROFILES_PACK_REF,
  PROFILES_PACK_SAVE,
  PROFILES_PACK_SEVERITY,
  PROFILES_PACK_SLUG,
  PROFILES_PACK_STAGE,
  PROFILES_PACK_UPDATE,
  PROFILES_PACK_WHEN,
  PROFILES_PACKS_EMPTY,
  PROFILES_PACKS_HEADING,
  PROFILES_PACKS_LOADING,
  PROFILES_PACKS_UNAVAILABLE,
  PROFILES_TEMPLATE_DDL,
  PROFILES_TEMPLATE_DELETE,
  PROFILES_TEMPLATE_HINT,
  PROFILES_TEMPLATE_NAME,
  PROFILES_TEMPLATE_NEW,
  PROFILES_TEMPLATE_PARAMS,
  PROFILES_TEMPLATE_PRODUCT,
  PROFILES_TEMPLATE_SAVE,
  PROFILES_TEMPLATE_SHARED,
  PROFILES_TEMPLATE_SINK,
  PROFILES_TEMPLATE_SLUG,
  PROFILES_TEMPLATE_UPDATE,
  PROFILES_TEMPLATES_EMPTY,
  PROFILES_TEMPLATES_HEADING,
  PROFILES_TEMPLATES_LOADING,
  PROFILES_TEMPLATES_UNAVAILABLE,
  PROFILES_WORKFLOWS_BODY,
  PROFILES_WORKFLOWS_DEFINITIONS_LINK,
  PROFILES_WORKFLOWS_DEFINITIONS_URL,
  PROFILES_WORKFLOWS_EXAMPLES_LINK,
  PROFILES_WORKFLOWS_HEADING,
  PROFILES_WORKFLOWS_RUNTIME_LINK,
  PROFILES_WORKFLOWS_RUNTIME_URL,
} from '@/utils/conversionProfilesCopy';
import {
  createConversionProfileShareBundle,
  parseConversionProfileShareBundle,
} from '@/utils/conversionProfileShare';
import { Button } from './ui/button';
import { Card } from './ui/card';

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
  onOpenConverterExamples?: () => void;
}

interface LoadErrorState {
  catalog: string | null;
  presets: string | null;
  packs: string | null;
  overlays: string | null;
  templates: string | null;
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

function usesReusedExamples(profileId: string): boolean {
  return hydrateSemanticProfile(profileId) !== DEFAULT_SEMANTIC_PROFILE;
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

function starterSlug(
  profileId: string,
  kind: 'pack' | 'overlay' | 'preset' | 'template',
): string {
  return `starter-${profileId.toLowerCase().replaceAll('_', '-')}-${kind}`;
}

function starterProduct(profile: ProfileCatalogEntry | null): string {
  return profile?.products[0] ?? 'METAR';
}

function starterPresetIwxxmVersion(profile: ProfileCatalogEntry | null): string {
  const match = profile?.iwxxm_line?.match(/\b(?:\d{4}-\d|\d+\.\d+\.\d+)\b/);
  return match?.[0] ?? '2025-2';
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

function ConversionProfileAuthed({
  accessToken,
  onOpenConverterExamples,
}: AuthedProps) {
  const [catalog, setCatalog] = useState<ProfileCatalogEntry[] | null>(null);
  const [presets, setPresets] = useState<PresetOut[] | null>(null);
  const [packs, setPacks] = useState<RulePackOut[] | null>(null);
  const [overlays, setOverlays] = useState<OverlayOut[] | null>(null);
  const [templates, setTemplates] = useState<DisseminationTemplateOut[] | null>(null);
  const [loadErrors, setLoadErrors] = useState<LoadErrorState>({
    catalog: null,
    presets: null,
    packs: null,
    overlays: null,
    templates: null,
  });
  const [selectedId, setSelectedId] = useState<string>('');
  const [compareId, setCompareId] = useState<string>('');
  const [activeBlockId, setActiveBlockId] = useState<ProfileBlockId>('input');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [savingPreset, setSavingPreset] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savingOverlay, setSavingOverlay] = useState(false);
  const [savingTemplate, setSavingTemplate] = useState(false);
  const [presetSeedDirty, setPresetSeedDirty] = useState(false);
  const [packSeedDirty, setPackSeedDirty] = useState(false);
  const [overlaySeedDirty, setOverlaySeedDirty] = useState(false);
  const [templateSeedDirty, setTemplateSeedDirty] = useState(false);
  const [editingPresetId, setEditingPresetId] = useState<string | null>(null);
  const [editingPackId, setEditingPackId] = useState<string | null>(null);
  const [editingOverlayId, setEditingOverlayId] = useState<string | null>(null);
  const [editingTemplateId, setEditingTemplateId] = useState<string | null>(null);
  const importInputRef = useRef<HTMLInputElement | null>(null);

  const [presetSlug, setPresetSlug] = useState('my-preset');
  const [presetName, setPresetName] = useState('My preset');
  const [presetProfile, setPresetProfile] = useState('ICAO_2025');
  const [presetIwxxmVersion, setPresetIwxxmVersion] = useState('2025-2');
  const [presetReportVariant, setPresetReportVariant] = useState('');
  const [presetOverlayId, setPresetOverlayId] = useState('');
  const [presetShared, setPresetShared] = useState(false);
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
  const [templateSlug, setTemplateSlug] = useState('my-template');
  const [templateName, setTemplateName] = useState('My template');
  const [templateSinkType, setTemplateSinkType] = useState('postgres');
  const [templateProduct, setTemplateProduct] = useState('metar');
  const [templateDdl, setTemplateDdl] = useState(false);
  const [templateShared, setTemplateShared] = useState(false);
  const [templateParamsText, setTemplateParamsText] = useState('{}');

  const resetPresetForm = useCallback((nextSelected: ProfileCatalogEntry | null) => {
    setEditingPresetId(null);
    setPresetSeedDirty(false);
    const nextProfile = nextSelected?.id ?? 'ICAO_2025';
    setPresetSlug(nextSelected ? starterSlug(nextSelected.id, 'preset') : 'my-preset');
    setPresetName(nextSelected ? `${profileLabel(nextProfile)} preset` : 'My preset');
    setPresetProfile(nextProfile);
    setPresetIwxxmVersion(starterPresetIwxxmVersion(nextSelected));
    setPresetReportVariant('');
    setPresetOverlayId('');
    setPresetShared(false);
  }, []);

  const resetPackForm = useCallback((nextSelected: ProfileCatalogEntry | null) => {
    setEditingPackId(null);
    setPackSeedDirty(false);
    setSlug(nextSelected ? starterSlug(nextSelected.id, 'pack') : 'my-pack');
    setProfile(nextSelected?.id ?? 'ICAO_2025');
    setProduct(nextSelected ? starterProduct(nextSelected) : 'METAR');
    setStage('lint');
    setSeverity('warning');
    setWhenExpr('');
    setMessage(
      nextSelected ? `Starter guidance for ${profileLabel(nextSelected.id)}` : '',
    );
    setStandardRef(nextSelected?.iwxxm_line ?? '');
  }, []);

  const resetOverlayForm = useCallback((nextSelected: ProfileCatalogEntry | null) => {
    setEditingOverlayId(null);
    setOverlaySeedDirty(false);
    setOverlaySlug(
      nextSelected ? starterSlug(nextSelected.id, 'overlay') : 'my-overlay',
    );
    setOverlayBase(nextSelected?.id ?? 'ICAO_2025');
    setOverlayBodyText('{}');
  }, []);

  const resetTemplateForm = useCallback((nextSelected: ProfileCatalogEntry | null) => {
    setEditingTemplateId(null);
    setTemplateSeedDirty(false);
    setTemplateSlug(
      nextSelected ? starterSlug(nextSelected.id, 'template') : 'my-template',
    );
    setTemplateName(
      nextSelected ? `${profileLabel(nextSelected.id)} destination` : 'My template',
    );
    setTemplateSinkType('postgres');
    setTemplateProduct(starterProduct(nextSelected).toLowerCase());
    setTemplateDdl(false);
    setTemplateShared(false);
    setTemplateParamsText('{}');
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const [catResult, presetResult, packResult, overlayResult, templateResult] =
      await Promise.allSettled([
        fetchProfileCatalog(accessToken),
        listPresets(accessToken),
        listRulePacks(accessToken),
        listOverlays(accessToken),
        listTemplates(accessToken),
      ]);

    const nextLoadErrors: LoadErrorState = {
      catalog: catResult.status === 'rejected' ? errorMessage(catResult.reason) : null,
      presets:
        presetResult.status === 'rejected' ? errorMessage(presetResult.reason) : null,
      packs: packResult.status === 'rejected' ? errorMessage(packResult.reason) : null,
      overlays:
        overlayResult.status === 'rejected' ? errorMessage(overlayResult.reason) : null,
      templates:
        templateResult.status === 'rejected'
          ? errorMessage(templateResult.reason)
          : null,
    };
    setLoadErrors(nextLoadErrors);

    const nextCatalog =
      catResult.status === 'fulfilled' ? catResult.value.profiles : null;
    const nextPresets =
      presetResult.status === 'fulfilled' ? presetResult.value.items : null;
    const nextPacks = packResult.status === 'fulfilled' ? packResult.value.items : null;
    const nextOverlays =
      overlayResult.status === 'fulfilled' ? overlayResult.value.items : null;
    const nextTemplates =
      templateResult.status === 'fulfilled' ? templateResult.value.items : null;
    setCatalog((current) => nextCatalog ?? current);
    setPresets((current) => nextPresets ?? current);
    setPacks((current) => nextPacks ?? current);
    setOverlays((current) => nextOverlays ?? current);
    setTemplates((current) => nextTemplates ?? current);

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
    if (!selected || presets === null || presets.length > 0 || presetSeedDirty) {
      return;
    }
    setPresetSlug(starterSlug(selected.id, 'preset'));
    setPresetName(`${profileLabel(selected.id)} preset`);
    setPresetProfile(selected.id);
    setPresetIwxxmVersion(starterPresetIwxxmVersion(selected));
    setPresetReportVariant('');
    setPresetOverlayId('');
    setPresetShared(false);
  }, [presetSeedDirty, presets, selected]);

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

  useEffect(() => {
    if (!selected || templates === null || templates.length > 0 || templateSeedDirty) {
      return;
    }
    setTemplateSlug(starterSlug(selected.id, 'template'));
    setTemplateName(`${profileLabel(selected.id)} destination`);
    setTemplateProduct(starterProduct(selected).toLowerCase());
    setTemplateSinkType('postgres');
    setTemplateDdl(false);
    setTemplateShared(false);
    setTemplateParamsText('{}');
  }, [selected, templateSeedDirty, templates]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const onSavePreset = async () => {
    setSavingPreset(true);
    setError(null);
    try {
      const payload = {
        slug: presetSlug,
        name: presetName,
        semanticProfile: presetProfile,
        iwxxmVersion: presetIwxxmVersion,
        extensions: [],
        reportVariant: presetReportVariant || null,
        overlayId: presetOverlayId || null,
        shared: presetShared,
      };
      if (editingPresetId) {
        await updatePreset(accessToken, editingPresetId, payload);
      } else {
        await createPreset(accessToken, payload);
      }
      await load();
      resetPresetForm(selected);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSavingPreset(false);
    }
  };

  const onSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const payload = {
        slug,
        profile,
        product,
        stage,
        severity,
        when: whenExpr,
        message,
        standardReference: standardRef,
      };
      if (editingPackId) {
        await updateRulePack(accessToken, editingPackId, payload);
      } else {
        await createRulePack(accessToken, payload);
      }
      await load();
      resetPackForm(selected);
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
      const payload = {
        slug: overlaySlug,
        baseProfileId: overlayBase,
        body: parsed as Record<string, unknown>,
      };
      if (editingOverlayId) {
        await updateOverlay(accessToken, editingOverlayId, payload);
      } else {
        await createOverlay(accessToken, payload);
      }
      await load();
      resetOverlayForm(selected);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSavingOverlay(false);
    }
  };

  const onSaveTemplate = async () => {
    setSavingTemplate(true);
    setError(null);
    try {
      let parsed: unknown;
      try {
        parsed = JSON.parse(templateParamsText.trim() || '{}');
      } catch {
        throw new Error('Template JSON must be valid');
      }
      if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('Template JSON must be an object');
      }
      const payload = {
        slug: templateSlug,
        name: templateName,
        sinkType: templateSinkType,
        product: templateProduct || null,
        ddl: templateDdl,
        params: parsed as Record<string, unknown>,
        shared: templateShared,
      };
      if (editingTemplateId) {
        await updateTemplate(accessToken, editingTemplateId, payload);
      } else {
        await createTemplate(accessToken, payload);
      }
      await load();
      resetTemplateForm(selected);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSavingTemplate(false);
    }
  };

  const onEditPack = (pack: RulePackOut) => {
    setEditingPackId(pack.id);
    setPackSeedDirty(true);
    setSlug(pack.slug);
    setProfile(pack.profile);
    setProduct(pack.product);
    setStage(pack.stage);
    setSeverity(pack.severity);
    setWhenExpr(pack.when);
    setMessage(pack.message);
    setStandardRef(pack.standardReference);
  };

  const onDeletePack = async (packId: string) => {
    setSaving(true);
    setError(null);
    try {
      await deleteRulePack(accessToken, packId);
      await load();
      resetPackForm(selected);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const onEditPreset = (preset: PresetOut) => {
    setEditingPresetId(preset.id);
    setPresetSeedDirty(true);
    setPresetSlug(preset.slug);
    setPresetName(preset.name);
    setPresetProfile(preset.semanticProfile);
    setPresetIwxxmVersion(preset.iwxxmVersion);
    setPresetReportVariant(preset.reportVariant ?? '');
    setPresetOverlayId(preset.overlayId ?? '');
    setPresetShared(preset.shared);
  };

  const onDeletePreset = async (presetId: string) => {
    setSavingPreset(true);
    setError(null);
    try {
      await deletePreset(accessToken, presetId);
      await load();
      resetPresetForm(selected);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSavingPreset(false);
    }
  };

  const onEditOverlay = (overlay: OverlayOut) => {
    setEditingOverlayId(overlay.id);
    setOverlaySeedDirty(true);
    setOverlaySlug(overlay.slug);
    setOverlayBase(overlay.baseProfileId);
    setOverlayBodyText(JSON.stringify(overlay.body, null, 2));
  };

  const onDeleteOverlay = async (overlayId: string) => {
    setSavingOverlay(true);
    setError(null);
    try {
      await deleteOverlay(accessToken, overlayId);
      await load();
      resetOverlayForm(selected);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSavingOverlay(false);
    }
  };

  const onEditTemplate = (template: DisseminationTemplateOut) => {
    setEditingTemplateId(template.id);
    setTemplateSeedDirty(true);
    setTemplateSlug(template.slug);
    setTemplateName(template.name);
    setTemplateSinkType(template.sinkType);
    setTemplateProduct(template.product ?? '');
    setTemplateDdl(template.ddl);
    setTemplateShared(template.shared);
    setTemplateParamsText(JSON.stringify(template.params, null, 2));
  };

  const onDeleteTemplate = async (templateId: string) => {
    setSavingTemplate(true);
    setError(null);
    try {
      await deleteTemplate(accessToken, templateId);
      await load();
      resetTemplateForm(selected);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSavingTemplate(false);
    }
  };

  const onExport = () => {
    const bundle = createConversionProfileShareBundle({
      rulePacks: packs ?? [],
      overlays: overlays ?? [],
    });
    const blob = new Blob([JSON.stringify(bundle, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'conversion-profile-share.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const onImportClick = () => {
    importInputRef.current?.click();
  };

  const onImport = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) {
      return;
    }

    setSaving(true);
    setSavingOverlay(true);
    setError(null);
    try {
      const bundle = parseConversionProfileShareBundle(await file.text());
      for (const pack of bundle.rulePacks) {
        await createRulePack(accessToken, pack);
      }
      for (const overlay of bundle.overlays) {
        await createOverlay(accessToken, overlay);
      }
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
      setSavingOverlay(false);
    }
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

      <Card className="space-y-3 p-4" data-testid="conversion-profiles-glossary">
        <h2 className="text-sm font-medium">{PROFILES_GLOSSARY_HEADING}</h2>
        <dl className="grid grid-cols-1 gap-3 text-sm md:grid-cols-3">
          <div className="rounded-md border border-gray-200 p-3 dark:border-gray-700">
            <dt className="font-medium text-gray-900 dark:text-gray-100">
              Semantic profile
            </dt>
            <dd className="mt-1 text-gray-700 dark:text-gray-300">
              {PROFILES_GLOSSARY_PROFILE}
            </dd>
          </div>
          <div className="rounded-md border border-gray-200 p-3 dark:border-gray-700">
            <dt className="font-medium text-gray-900 dark:text-gray-100">
              Exchange profile
            </dt>
            <dd className="mt-1 text-gray-700 dark:text-gray-300">
              {PROFILES_GLOSSARY_EXCHANGE}
            </dd>
          </div>
          <div className="rounded-md border border-gray-200 p-3 dark:border-gray-700">
            <dt className="font-medium text-gray-900 dark:text-gray-100">
              Signed overlay
            </dt>
            <dd className="mt-1 text-gray-700 dark:text-gray-300">
              {PROFILES_GLOSSARY_OVERLAY}
            </dd>
          </div>
        </dl>
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

      <Card className="space-y-3 p-4" data-testid="conversion-profiles-workflows">
        <h2 className="text-sm font-medium">{PROFILES_WORKFLOWS_HEADING}</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {PROFILES_WORKFLOWS_BODY}
        </p>
        <div className="flex flex-wrap gap-2">
          <a
            className="rounded border border-gray-300 px-3 py-1.5 text-sm text-gray-700 dark:border-gray-600 dark:text-gray-200"
            data-testid="conversion-profiles-workflow-definitions"
            href={PROFILES_WORKFLOWS_DEFINITIONS_URL}
            rel="noreferrer"
            target="_blank"
          >
            {PROFILES_WORKFLOWS_DEFINITIONS_LINK}
          </a>
          <a
            className="rounded border border-gray-300 px-3 py-1.5 text-sm text-gray-700 dark:border-gray-600 dark:text-gray-200"
            data-testid="conversion-profiles-workflow-runtime"
            href={PROFILES_WORKFLOWS_RUNTIME_URL}
            rel="noreferrer"
            target="_blank"
          >
            {PROFILES_WORKFLOWS_RUNTIME_LINK}
          </a>
          {onOpenConverterExamples ? (
            <Button
              type="button"
              variant="outline"
              size="sm"
              data-testid="conversion-profiles-open-examples"
              onClick={onOpenConverterExamples}
            >
              {PROFILES_WORKFLOWS_EXAMPLES_LINK}
            </Button>
          ) : null}
        </div>
      </Card>

      <Card className="space-y-3 p-4" data-testid="conversion-profiles-examples">
        <h2 className="text-sm font-medium">{PROFILES_EXAMPLES_HEADING}</h2>
        {selected && selected.products.length > 0 ? (
          <>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {PROFILES_EXAMPLES_PREFIX} {selected.products.join(', ')}
            </p>
            {usesReusedExamples(selected.id) ? (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {PROFILES_EXAMPLES_REUSE_NOTE}
              </p>
            ) : null}
          </>
        ) : (
          <p className="text-sm text-gray-500">{PROFILES_EXAMPLES_EMPTY}</p>
        )}
      </Card>

      <Card className="space-y-3 p-4" data-testid="conversion-profiles-presets">
        <h2 className="text-sm font-medium">{PROFILES_PRESETS_HEADING}</h2>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <label className="text-sm">
            {PROFILES_PRESET_SLUG}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-preset-slug"
              value={presetSlug}
              onChange={(e) => {
                setPresetSeedDirty(true);
                setPresetSlug(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PRESET_NAME}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-preset-name"
              value={presetName}
              onChange={(e) => {
                setPresetSeedDirty(true);
                setPresetName(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PRESET_PROFILE}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-preset-profile"
              value={presetProfile}
              onChange={(e) => {
                setPresetSeedDirty(true);
                setPresetProfile(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PRESET_IWXXM_VERSION}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-preset-iwxxm-version"
              value={presetIwxxmVersion}
              onChange={(e) => {
                setPresetSeedDirty(true);
                setPresetIwxxmVersion(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PRESET_REPORT_VARIANT}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-preset-report-variant"
              value={presetReportVariant}
              onChange={(e) => {
                setPresetSeedDirty(true);
                setPresetReportVariant(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PRESET_OVERLAY}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-preset-overlay-id"
              value={presetOverlayId}
              onChange={(e) => {
                setPresetSeedDirty(true);
                setPresetOverlayId(e.target.value);
              }}
            />
          </label>
          <label className="flex items-center gap-2 text-sm sm:col-span-2">
            <input
              data-testid="conversion-profiles-preset-shared"
              type="checkbox"
              checked={presetShared}
              onChange={(e) => {
                setPresetSeedDirty(true);
                setPresetShared(e.target.checked);
              }}
            />
            <span>{PROFILES_PRESET_SHARED}</span>
          </label>
        </div>
        {presets !== null && presets.length === 0 && !presetSeedDirty ? (
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Starter preset fields stay in sync with the selected profile until you edit
            them.
          </p>
        ) : null}
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            data-testid="conversion-profiles-preset-save"
            onClick={() => void onSavePreset()}
            disabled={savingPreset}
          >
            {savingPreset ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            ) : null}
            {editingPresetId ? PROFILES_PRESET_UPDATE : PROFILES_PRESET_SAVE}
          </Button>
          <Button
            type="button"
            variant="outline"
            data-testid="conversion-profiles-preset-reset"
            onClick={() => resetPresetForm(selected)}
            disabled={savingPreset}
          >
            {PROFILES_PRESET_NEW}
          </Button>
          {editingPresetId ? (
            <Button
              type="button"
              variant="destructive"
              data-testid="conversion-profiles-preset-delete"
              onClick={() => void onDeletePreset(editingPresetId)}
              disabled={savingPreset}
            >
              {PROFILES_PRESET_DELETE}
            </Button>
          ) : null}
        </div>
        {loadErrors.presets && presets !== null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {PROFILES_PRESETS_UNAVAILABLE} {loadErrors.presets}
          </p>
        ) : null}
        {loading && presets === null ? (
          <p className="text-sm text-gray-500">{PROFILES_PRESETS_LOADING}</p>
        ) : loadErrors.presets && presets === null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {PROFILES_PRESETS_UNAVAILABLE} {loadErrors.presets}
          </p>
        ) : !presets || presets.length === 0 ? (
          <p className="text-sm text-gray-500">{PROFILES_PRESETS_EMPTY}</p>
        ) : (
          <ul
            className="space-y-1 text-sm"
            data-testid="conversion-profiles-preset-list"
          >
            {presets.map((preset) => (
              <li key={preset.id} className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  className="rounded border border-gray-300 px-2 py-1 text-left text-xs dark:border-gray-600"
                  data-testid={`conversion-profiles-preset-edit-${preset.id}`}
                  onClick={() => onEditPreset(preset)}
                >
                  Edit
                </button>
                <code>{preset.slug}</code> - {preset.name} ({preset.semanticProfile})
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card
        className="space-y-3 p-4"
        data-testid="conversion-profiles-packs"
        id="conversion-profiles-packs"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-sm font-medium">{PROFILES_PACKS_HEADING}</h2>
          <div className="flex flex-wrap gap-2">
            <input
              ref={importInputRef}
              className="hidden"
              data-testid="conversion-profiles-import-input"
              type="file"
              accept="application/json,.json"
              onChange={(event) => void onImport(event)}
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              data-testid="conversion-profiles-import"
              onClick={onImportClick}
              disabled={saving || savingOverlay}
            >
              {PROFILES_PACK_IMPORT}
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              data-testid="conversion-profiles-export"
              onClick={onExport}
              disabled={
                (!packs || packs.length === 0) && (!overlays || overlays.length === 0)
              }
            >
              {PROFILES_PACK_EXPORT}
            </Button>
          </div>
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

        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            data-testid="conversion-profiles-pack-save"
            onClick={() => void onSave()}
            disabled={saving}
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : null}
            {editingPackId ? PROFILES_PACK_UPDATE : PROFILES_PACK_SAVE}
          </Button>
          <Button
            type="button"
            variant="outline"
            data-testid="conversion-profiles-pack-reset"
            onClick={() => resetPackForm(selected)}
            disabled={saving}
          >
            {PROFILES_PACK_NEW}
          </Button>
          {editingPackId ? (
            <Button
              type="button"
              variant="destructive"
              data-testid="conversion-profiles-pack-delete"
              onClick={() => void onDeletePack(editingPackId)}
              disabled={saving}
            >
              {PROFILES_PACK_DELETE}
            </Button>
          ) : null}
        </div>

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
              <li key={p.id} className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  className="rounded border border-gray-300 px-2 py-1 text-left text-xs dark:border-gray-600"
                  data-testid={`conversion-profiles-pack-edit-${p.id}`}
                  onClick={() => onEditPack(p)}
                >
                  Edit
                </button>
                <code>{p.slug}</code> — {p.profile} / {p.product} ({p.severity})
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card className="space-y-3 p-4" data-testid="conversion-profiles-templates">
        <h2 className="text-sm font-medium">{PROFILES_TEMPLATES_HEADING}</h2>
        <p className="text-xs text-gray-600 dark:text-gray-400">
          {PROFILES_TEMPLATE_HINT}
        </p>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <label className="text-sm">
            {PROFILES_TEMPLATE_SLUG}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-template-slug"
              value={templateSlug}
              onChange={(e) => {
                setTemplateSeedDirty(true);
                setTemplateSlug(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_TEMPLATE_NAME}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-template-name"
              value={templateName}
              onChange={(e) => {
                setTemplateSeedDirty(true);
                setTemplateName(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_TEMPLATE_SINK}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-template-sink"
              value={templateSinkType}
              onChange={(e) => {
                setTemplateSeedDirty(true);
                setTemplateSinkType(e.target.value);
              }}
            />
          </label>
          <label className="text-sm">
            {PROFILES_TEMPLATE_PRODUCT}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-template-product"
              value={templateProduct}
              onChange={(e) => {
                setTemplateSeedDirty(true);
                setTemplateProduct(e.target.value);
              }}
            />
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              data-testid="conversion-profiles-template-ddl"
              type="checkbox"
              checked={templateDdl}
              onChange={(e) => {
                setTemplateSeedDirty(true);
                setTemplateDdl(e.target.checked);
              }}
            />
            <span>{PROFILES_TEMPLATE_DDL}</span>
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              data-testid="conversion-profiles-template-shared"
              type="checkbox"
              checked={templateShared}
              onChange={(e) => {
                setTemplateSeedDirty(true);
                setTemplateShared(e.target.checked);
              }}
            />
            <span>{PROFILES_TEMPLATE_SHARED}</span>
          </label>
          <label className="text-sm sm:col-span-2">
            {PROFILES_TEMPLATE_PARAMS}
            <textarea
              className="mt-1 w-full rounded border p-2 font-mono text-xs dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-template-params"
              rows={4}
              value={templateParamsText}
              onChange={(e) => {
                setTemplateSeedDirty(true);
                setTemplateParamsText(e.target.value);
              }}
            />
          </label>
        </div>
        {templates !== null && templates.length === 0 && !templateSeedDirty ? (
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Starter template fields stay in sync with the selected profile until you
            edit them.
          </p>
        ) : null}
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            data-testid="conversion-profiles-template-save"
            onClick={() => void onSaveTemplate()}
            disabled={savingTemplate}
          >
            {savingTemplate ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            ) : null}
            {editingTemplateId ? PROFILES_TEMPLATE_UPDATE : PROFILES_TEMPLATE_SAVE}
          </Button>
          <Button
            type="button"
            variant="outline"
            data-testid="conversion-profiles-template-reset"
            onClick={() => resetTemplateForm(selected)}
            disabled={savingTemplate}
          >
            {PROFILES_TEMPLATE_NEW}
          </Button>
          {editingTemplateId ? (
            <Button
              type="button"
              variant="destructive"
              data-testid="conversion-profiles-template-delete"
              onClick={() => void onDeleteTemplate(editingTemplateId)}
              disabled={savingTemplate}
            >
              {PROFILES_TEMPLATE_DELETE}
            </Button>
          ) : null}
        </div>
        {loadErrors.templates && templates !== null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {PROFILES_TEMPLATES_UNAVAILABLE} {loadErrors.templates}
          </p>
        ) : null}
        {loading && templates === null ? (
          <p className="text-sm text-gray-500">{PROFILES_TEMPLATES_LOADING}</p>
        ) : loadErrors.templates && templates === null ? (
          <p className="text-sm text-amber-700 dark:text-amber-300">
            {PROFILES_TEMPLATES_UNAVAILABLE} {loadErrors.templates}
          </p>
        ) : !templates || templates.length === 0 ? (
          <p className="text-sm text-gray-500">{PROFILES_TEMPLATES_EMPTY}</p>
        ) : (
          <ul
            className="space-y-1 text-sm"
            data-testid="conversion-profiles-template-list"
          >
            {templates.map((template) => (
              <li key={template.id} className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  className="rounded border border-gray-300 px-2 py-1 text-left text-xs dark:border-gray-600"
                  data-testid={`conversion-profiles-template-edit-${template.id}`}
                  onClick={() => onEditTemplate(template)}
                >
                  Edit
                </button>
                <code>{template.slug}</code> - {template.name} ({template.sinkType})
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
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            data-testid="conversion-profiles-overlay-save"
            onClick={() => void onSaveOverlay()}
            disabled={savingOverlay}
          >
            {savingOverlay ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            ) : null}
            {editingOverlayId ? PROFILES_OVERLAY_UPDATE : PROFILES_OVERLAY_SAVE}
          </Button>
          <Button
            type="button"
            variant="outline"
            data-testid="conversion-profiles-overlay-reset"
            onClick={() => resetOverlayForm(selected)}
            disabled={savingOverlay}
          >
            {PROFILES_OVERLAY_NEW}
          </Button>
          {editingOverlayId ? (
            <Button
              type="button"
              variant="destructive"
              data-testid="conversion-profiles-overlay-delete"
              onClick={() => void onDeleteOverlay(editingOverlayId)}
              disabled={savingOverlay}
            >
              {PROFILES_OVERLAY_DELETE}
            </Button>
          ) : null}
        </div>
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
              <li key={o.id} className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  className="rounded border border-gray-300 px-2 py-1 text-left text-xs dark:border-gray-600"
                  data-testid={`conversion-profiles-overlay-edit-${o.id}`}
                  onClick={() => onEditOverlay(o)}
                >
                  Edit
                </button>
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
  onOpenConverterExamples,
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
  return (
    <ConversionProfileAuthed
      accessToken={accessToken}
      onOpenConverterExamples={onOpenConverterExamples}
    />
  );
}
