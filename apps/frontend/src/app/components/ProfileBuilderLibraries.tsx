/**
 * Profile builder Libraries shell — five sub-tabs (Conversion + four stubs).
 */

import { CircleHelp } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import type {
  LibraryAssetKind,
  ProfileCatalogEntry,
} from '@/utils/conversionProfilesApi';
import { listLibraryAssets } from '@/utils/conversionProfilesApi';
import {
  CONVERT_RESET_WMO_LIBRARY_DEFAULTS,
  CONVERT_RESET_WMO_LIBRARY_DEFAULTS_HELP,
  PROFILES_INSPECTOR_ACCESS_BUILTIN,
  PROFILES_INSPECTOR_AUTHORITY_ICAO,
  PROFILES_INSPECTOR_COVERAGE_UNAVAILABLE,
  PROFILES_INSPECTOR_FAMILY_ICAO,
  PROFILES_INSPECTOR_FAMILY_NATIONAL,
  PROFILES_INSPECTOR_HEADING,
  PROFILES_INSPECTOR_STATUS_DRAFT,
  PROFILES_INSPECTOR_STATUS_READY,
  PROFILES_LIBRARIES_HEADING,
  PROFILES_LIBRARIES_HELP,
  PROFILES_LIBRARY_TAB_CONVERSION,
  PROFILES_LIBRARY_TAB_DECODING,
  PROFILES_LIBRARY_TAB_DISSEMINATION,
  PROFILES_LIBRARY_TAB_IWXXM_VALIDATION,
  PROFILES_LIBRARY_TAB_OVERVIEW,
  PROFILES_LIBRARY_TAB_TAC_VALIDATION,
  PROFILES_OVERVIEW_COMPARE_STUB,
  PROFILES_OVERVIEW_ENABLEMENT_STUB,
  PROFILES_OVERVIEW_HEADING,
  PROFILES_OVERVIEW_HELP,
  PROFILES_PROFILE_AUTHORITY,
  PROFILES_PROFILE_COVERAGE,
  PROFILES_PROFILE_FAMILY,
  PROFILES_TOOLTIP_LIBRARIES,
  PROFILES_TOOLTIP_LIBRARY_TAB_CONVERSION,
  PROFILES_TOOLTIP_LIBRARY_TAB_DECODING,
  PROFILES_TOOLTIP_LIBRARY_TAB_DISSEMINATION,
  PROFILES_TOOLTIP_LIBRARY_TAB_IWXXM_VALIDATION,
  PROFILES_TOOLTIP_LIBRARY_TAB_OVERVIEW,
  PROFILES_TOOLTIP_LIBRARY_TAB_TAC_VALIDATION,
} from '../../utils/conversionProfilesCopy';
import { resetWmoLibraryDefaultsSync } from '@/utils/wmoLibraryDefaultsSync';
import { BetaBadge } from './BetaBadge';
import { ConversionTemplatesPanel } from './ConversionTemplatesPanel';
import { DecodingLibraryPanel } from './DecodingLibraryPanel';
import { DisseminationLibraryPanel } from './DisseminationLibraryPanel';
import { LibraryAssetsListPanel } from './LibraryAssetsListPanel';
import { LibraryDraftShell, type LibraryDraftSchemaBlock } from './LibraryDraftShell';
import { LibraryWorkbenchShell } from './LibraryWorkbenchShell';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

export type ProfileBuilderLibrariesProps = {
  accessToken: string;
  /** Selected semantic profile from the catalog picker (conversion tab fields). */
  catalogProfile?: ProfileCatalogEntry | null;
};

type BuilderTabValue = LibraryAssetKind | 'overview';

const LIBRARY_TAB_LABELS: Record<LibraryAssetKind, string> = {
  conversion: PROFILES_LIBRARY_TAB_CONVERSION,
  tac_validation: PROFILES_LIBRARY_TAB_TAC_VALIDATION,
  iwxxm_validation: PROFILES_LIBRARY_TAB_IWXXM_VALIDATION,
  dissemination: PROFILES_LIBRARY_TAB_DISSEMINATION,
  decoding: PROFILES_LIBRARY_TAB_DECODING,
};

function profileFamily(profileId: string): string {
  if (profileId.startsWith('ICAO_')) {
    return PROFILES_INSPECTOR_FAMILY_ICAO;
  }
  return PROFILES_INSPECTOR_FAMILY_NATIONAL;
}

function profileAuthority(profileId: string): string {
  if (profileId.startsWith('ICAO_')) {
    return PROFILES_INSPECTOR_AUTHORITY_ICAO;
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
  return kinds.join(' | ') || PROFILES_INSPECTOR_COVERAGE_UNAVAILABLE;
}

function LibraryTab({
  value,
  testId,
  label,
  tooltip,
}: {
  value: string;
  testId: string;
  label: string;
  tooltip: string;
}) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <TabsTrigger value={value} data-testid={testId}>
          {label}
        </TabsTrigger>
      </TooltipTrigger>
      <TooltipContent side="bottom" className="max-w-xs text-balance">
        {tooltip}
      </TooltipContent>
    </Tooltip>
  );
}

/**
 * Five-library Profile builder sub-tabs.
 *
 * @param props.accessToken - Bearer JWT
 * @param props.catalogProfile - Selected catalog profile for conversion inspector fields
 */
export function ProfileBuilderLibraries({
  accessToken,
  catalogProfile = null,
}: ProfileBuilderLibrariesProps) {
  const [activeTab, setActiveTab] = useState<BuilderTabValue>('conversion');
  const [draftSavedByKind, setDraftSavedByKind] = useState<
    Partial<Record<LibraryAssetKind, boolean>>
  >({});
  const [conversionSchemaBlocks, setConversionSchemaBlocks] = useState<
    LibraryDraftSchemaBlock[] | undefined
  >(undefined);

  useEffect(() => {
    let cancelled = false;
    const nationalLine = catalogProfile?.id ?? 'ICAO_2025';
    void listLibraryAssets(accessToken, 'conversion')
      .then((response) => {
        if (cancelled) {
          return;
        }
        const asset =
          response.items.find((item) => item.attachedNationalLine === nationalLine) ??
          response.items.find((item) => item.id === `LIB.CONVERSION.${nationalLine}`);
        const raw = asset?.body?.schema_blocks;
        if (!Array.isArray(raw)) {
          setConversionSchemaBlocks(undefined);
          return;
        }
        const blocks: LibraryDraftSchemaBlock[] = raw
          .map((entry) => {
            if (!entry || typeof entry !== 'object') {
              return null;
            }
            const record = entry as Record<string, unknown>;
            const id = typeof record.id === 'string' ? record.id : '';
            const label = typeof record.label === 'string' ? record.label : id;
            const cardsRaw = Array.isArray(record.cards) ? record.cards : [];
            const cards = cardsRaw
              .map((card) => {
                if (!card || typeof card !== 'object') {
                  return null;
                }
                const cardRec = card as Record<string, unknown>;
                const cardId = typeof cardRec.id === 'string' ? cardRec.id : '';
                const cardLabel =
                  typeof cardRec.label === 'string' ? cardRec.label : cardId;
                if (!cardId) {
                  return null;
                }
                return { id: cardId, label: cardLabel };
              })
              .filter((card): card is { id: string; label: string } => card != null);
            if (!id) {
              return null;
            }
            return { id, label, cards };
          })
          .filter((block): block is LibraryDraftSchemaBlock => block != null);
        setConversionSchemaBlocks(blocks.length > 0 ? blocks : undefined);
      })
      .catch(() => {
        if (!cancelled) {
          setConversionSchemaBlocks(undefined);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [accessToken, catalogProfile?.id]);

  const handleDraftStatusChange = useCallback(
    (kind: LibraryAssetKind, status: 'idle' | 'draft' | 'saved' | 'activated') => {
      setDraftSavedByKind((prev) => ({
        ...prev,
        [kind]: status === 'saved' || status === 'activated',
      }));
    },
    [],
  );

  const onConversionDraftStatusChange = useCallback(
    (status: 'idle' | 'draft' | 'saved' | 'activated') =>
      handleDraftStatusChange('conversion', status),
    [handleDraftStatusChange],
  );
  const onTacValidationDraftStatusChange = useCallback(
    (status: 'idle' | 'draft' | 'saved' | 'activated') =>
      handleDraftStatusChange('tac_validation', status),
    [handleDraftStatusChange],
  );
  const onIwxxmValidationDraftStatusChange = useCallback(
    (status: 'idle' | 'draft' | 'saved' | 'activated') =>
      handleDraftStatusChange('iwxxm_validation', status),
    [handleDraftStatusChange],
  );
  const onDisseminationDraftStatusChange = useCallback(
    (status: 'idle' | 'draft' | 'saved' | 'activated') =>
      handleDraftStatusChange('dissemination', status),
    [handleDraftStatusChange],
  );
  const onDecodingDraftStatusChange = useCallback(
    (status: 'idle' | 'draft' | 'saved' | 'activated') =>
      handleDraftStatusChange('decoding', status),
    [handleDraftStatusChange],
  );

  const inspectorStatus =
    activeTab === 'overview'
      ? PROFILES_INSPECTOR_STATUS_READY
      : activeTab === 'conversion'
        ? (catalogProfile?.status ?? 'implemented')
        : draftSavedByKind[activeTab]
          ? PROFILES_INSPECTOR_STATUS_DRAFT
          : PROFILES_INSPECTOR_STATUS_READY;

  const inspectorKindLabel =
    activeTab === 'overview'
      ? PROFILES_LIBRARY_TAB_OVERVIEW
      : LIBRARY_TAB_LABELS[activeTab];

  return (
    <Card
      className="space-y-3 p-4"
      data-testid="profile-builder-libraries"
      id="profile-builder-libraries"
    >
      <div className="flex flex-wrap items-center gap-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <h2 className="cursor-default text-sm font-medium">
              {PROFILES_LIBRARIES_HEADING}
            </h2>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs text-balance">
            {PROFILES_TOOLTIP_LIBRARIES}
          </TooltipContent>
        </Tooltip>
        <BetaBadge showHelp />
        <div className="ml-auto flex shrink-0 items-center gap-1">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            data-testid="profile-builder-reset-wmo-defaults"
            className="text-xs text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
            onClick={() => {
              resetWmoLibraryDefaultsSync();
            }}
          >
            {CONVERT_RESET_WMO_LIBRARY_DEFAULTS}
          </Button>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                type="button"
                className="inline-flex h-6 w-6 items-center justify-center rounded text-gray-500 hover:text-gray-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:text-gray-400 dark:hover:text-gray-100"
                aria-label="About reset to WMO defaults"
                data-testid="profile-builder-reset-wmo-defaults-help"
              >
                <CircleHelp className="h-3.5 w-3.5" aria-hidden />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="max-w-xs text-balance">
              {CONVERT_RESET_WMO_LIBRARY_DEFAULTS_HELP}
            </TooltipContent>
          </Tooltip>
        </div>
      </div>
      <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
        {PROFILES_LIBRARIES_HELP}
      </p>
      <Tabs
        value={activeTab}
        onValueChange={(value) => setActiveTab(value as BuilderTabValue)}
        data-testid="profile-builder-library-tabs"
      >
        <TabsList className="flex h-auto w-full flex-wrap justify-start gap-1">
          <LibraryTab
            value="conversion"
            testId="profile-library-tab-conversion"
            label={PROFILES_LIBRARY_TAB_CONVERSION}
            tooltip={PROFILES_TOOLTIP_LIBRARY_TAB_CONVERSION}
          />
          <LibraryTab
            value="tac_validation"
            testId="profile-library-tab-tac-validation"
            label={PROFILES_LIBRARY_TAB_TAC_VALIDATION}
            tooltip={PROFILES_TOOLTIP_LIBRARY_TAB_TAC_VALIDATION}
          />
          <LibraryTab
            value="iwxxm_validation"
            testId="profile-library-tab-iwxxm-validation"
            label={PROFILES_LIBRARY_TAB_IWXXM_VALIDATION}
            tooltip={PROFILES_TOOLTIP_LIBRARY_TAB_IWXXM_VALIDATION}
          />
          <LibraryTab
            value="dissemination"
            testId="profile-library-tab-dissemination"
            label={PROFILES_LIBRARY_TAB_DISSEMINATION}
            tooltip={PROFILES_TOOLTIP_LIBRARY_TAB_DISSEMINATION}
          />
          <LibraryTab
            value="decoding"
            testId="profile-library-tab-decoding"
            label={PROFILES_LIBRARY_TAB_DECODING}
            tooltip={PROFILES_TOOLTIP_LIBRARY_TAB_DECODING}
          />
          <LibraryTab
            value="overview"
            testId="profile-library-tab-overview"
            label={PROFILES_LIBRARY_TAB_OVERVIEW}
            tooltip={PROFILES_TOOLTIP_LIBRARY_TAB_OVERVIEW}
          />
        </TabsList>
        <TabsContent
          value="conversion"
          forceMount
          className="data-[state=inactive]:hidden"
          data-testid="profile-library-panel-conversion"
        >
          <LibraryWorkbenchShell
            kind="conversion"
            catalog={
              <LibraryAssetsListPanel
                accessToken={accessToken}
                kind="conversion"
                heading={PROFILES_LIBRARY_TAB_CONVERSION}
              />
            }
            editor={
              <>
                <ConversionTemplatesPanel accessToken={accessToken} />
                <LibraryDraftShell
                  kind="conversion"
                  accessToken={accessToken}
                  schemaBlocks={conversionSchemaBlocks}
                  onDraftStatusChange={onConversionDraftStatusChange}
                />
              </>
            }
          />
        </TabsContent>
        <TabsContent
          value="tac_validation"
          forceMount
          className="data-[state=inactive]:hidden"
          data-testid="profile-library-panel-tac-validation"
        >
          <LibraryWorkbenchShell
            kind="tac_validation"
            catalog={
              <LibraryAssetsListPanel
                accessToken={accessToken}
                kind="tac_validation"
                heading={PROFILES_LIBRARY_TAB_TAC_VALIDATION}
              />
            }
            editor={
              <LibraryDraftShell
                kind="tac_validation"
                accessToken={accessToken}
                onDraftStatusChange={onTacValidationDraftStatusChange}
              />
            }
          />
        </TabsContent>
        <TabsContent
          value="iwxxm_validation"
          forceMount
          className="data-[state=inactive]:hidden"
          data-testid="profile-library-panel-iwxxm-validation"
        >
          <LibraryWorkbenchShell
            kind="iwxxm_validation"
            catalog={
              <LibraryAssetsListPanel
                accessToken={accessToken}
                kind="iwxxm_validation"
                heading={PROFILES_LIBRARY_TAB_IWXXM_VALIDATION}
              />
            }
            editor={
              <LibraryDraftShell
                kind="iwxxm_validation"
                accessToken={accessToken}
                onDraftStatusChange={onIwxxmValidationDraftStatusChange}
              />
            }
          />
        </TabsContent>
        <TabsContent
          value="dissemination"
          forceMount
          className="data-[state=inactive]:hidden"
          data-testid="profile-library-panel-dissemination"
        >
          <LibraryWorkbenchShell
            kind="dissemination"
            catalog={<DisseminationLibraryPanel accessToken={accessToken} />}
            editor={
              <LibraryDraftShell
                kind="dissemination"
                accessToken={accessToken}
                onDraftStatusChange={onDisseminationDraftStatusChange}
              />
            }
          />
        </TabsContent>
        <TabsContent
          value="decoding"
          forceMount
          className="data-[state=inactive]:hidden"
          data-testid="profile-library-panel-decoding"
        >
          <LibraryWorkbenchShell
            kind="decoding"
            catalog={<DecodingLibraryPanel accessToken={accessToken} />}
            editor={
              <LibraryDraftShell
                kind="decoding"
                accessToken={accessToken}
                onDraftStatusChange={onDecodingDraftStatusChange}
              />
            }
          />
        </TabsContent>
        <TabsContent
          value="overview"
          forceMount
          className="data-[state=inactive]:hidden"
          data-testid="profile-library-panel-overview"
        >
          <div className="space-y-3" data-testid="profile-overview-stub">
            <h3 className="text-sm font-medium">{PROFILES_OVERVIEW_HEADING}</h3>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {PROFILES_OVERVIEW_HELP}
            </p>
            <div
              className="rounded border border-dashed border-gray-300 p-3 text-sm dark:border-gray-600"
              data-testid="profile-overview-compare-stub"
            >
              {PROFILES_OVERVIEW_COMPARE_STUB}
            </div>
            <div
              className="rounded border border-dashed border-gray-300 p-3 text-sm dark:border-gray-600"
              data-testid="profile-overview-enablement-stub"
            >
              {PROFILES_OVERVIEW_ENABLEMENT_STUB}
            </div>
          </div>
        </TabsContent>
      </Tabs>

      <Card
        className="space-y-3 border-dashed p-4"
        data-testid="conversion-profiles-inspector"
        data-library-kind={activeTab}
      >
        <h3 className="text-sm font-medium">{PROFILES_INSPECTOR_HEADING}</h3>
        <dl
          className="grid grid-cols-1 gap-2 text-sm sm:grid-cols-2"
          data-testid="conversion-profiles-inspector-detail"
        >
          <div>
            <dt className="text-gray-500">Kind</dt>
            <dd>{inspectorKindLabel}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Status</dt>
            <dd>{inspectorStatus}</dd>
          </div>
          {activeTab === 'conversion' && catalogProfile ? (
            <>
              <div>
                <dt className="text-gray-500">Emit key</dt>
                <dd>{catalogProfile.emit_key ?? '—'}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Legacy alias</dt>
                <dd>{catalogProfile.legacy_alias ?? '—'}</dd>
              </div>
              <div>
                <dt className="text-gray-500">{PROFILES_PROFILE_FAMILY}</dt>
                <dd>{profileFamily(catalogProfile.id)}</dd>
              </div>
              <div>
                <dt className="text-gray-500">{PROFILES_PROFILE_AUTHORITY}</dt>
                <dd>{profileAuthority(catalogProfile.id)}</dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-gray-500">{PROFILES_PROFILE_COVERAGE}</dt>
                <dd>{profileCoverage(catalogProfile)}</dd>
              </div>
            </>
          ) : activeTab !== 'conversion' && activeTab !== 'overview' ? (
            <div className="sm:col-span-2">
              <dt className="text-gray-500">Access</dt>
              <dd>{PROFILES_INSPECTOR_ACCESS_BUILTIN}</dd>
            </div>
          ) : null}
        </dl>
      </Card>
    </Card>
  );
}
