/**
 * Profile builder Libraries shell — five sub-tabs (Conversion + four stubs).
 */

import { useCallback, useState } from 'react';
import type {
  LibraryAssetKind,
  ProfileCatalogEntry,
} from '@/utils/conversionProfilesApi';
import {
  CONVERT_RESET_WMO_LIBRARY_DEFAULTS,
  PROFILES_INSPECTOR_ACCESS_BUILTIN,
  PROFILES_INSPECTOR_HEADING,
  PROFILES_INSPECTOR_STATUS_DRAFT,
  PROFILES_INSPECTOR_STATUS_READY,
  PROFILES_LIBRARIES_HEADING,
  PROFILES_LIBRARIES_HELP,
  PROFILES_LIBRARY_TAB_CONVERSION,
  PROFILES_LIBRARY_TAB_DECODING,
  PROFILES_LIBRARY_TAB_DISSEMINATION,
  PROFILES_LIBRARY_TAB_IWXXM_VALIDATION,
  PROFILES_LIBRARY_TAB_TAC_VALIDATION,
  PROFILES_PROFILE_AUTHORITY,
  PROFILES_PROFILE_COVERAGE,
  PROFILES_PROFILE_FAMILY,
  PROFILES_TOOLTIP_LIBRARIES,
  PROFILES_TOOLTIP_LIBRARY_TAB_CONVERSION,
  PROFILES_TOOLTIP_LIBRARY_TAB_DECODING,
  PROFILES_TOOLTIP_LIBRARY_TAB_DISSEMINATION,
  PROFILES_TOOLTIP_LIBRARY_TAB_IWXXM_VALIDATION,
  PROFILES_TOOLTIP_LIBRARY_TAB_TAC_VALIDATION,
} from '../../utils/conversionProfilesCopy';
import { resetWmoLibraryDefaultsSync } from '@/utils/wmoLibraryDefaultsSync';
import { BetaBadge } from './BetaBadge';
import { ConversionTemplatesPanel } from './ConversionTemplatesPanel';
import { DecodingLibraryPanel } from './DecodingLibraryPanel';
import { DisseminationLibraryPanel } from './DisseminationLibraryPanel';
import { LibraryAssetsListPanel } from './LibraryAssetsListPanel';
import { LibraryDraftShell } from './LibraryDraftShell';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

export type ProfileBuilderLibrariesProps = {
  accessToken: string;
  /** Selected semantic profile from the catalog picker (conversion tab fields). */
  catalogProfile?: ProfileCatalogEntry | null;
};

type LibraryTabValue = LibraryAssetKind;

const LIBRARY_TAB_LABELS: Record<LibraryTabValue, string> = {
  conversion: PROFILES_LIBRARY_TAB_CONVERSION,
  tac_validation: PROFILES_LIBRARY_TAB_TAC_VALIDATION,
  iwxxm_validation: PROFILES_LIBRARY_TAB_IWXXM_VALIDATION,
  dissemination: PROFILES_LIBRARY_TAB_DISSEMINATION,
  decoding: PROFILES_LIBRARY_TAB_DECODING,
};

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
  const [activeTab, setActiveTab] = useState<LibraryTabValue>('conversion');
  const [draftSavedByKind, setDraftSavedByKind] = useState<
    Partial<Record<LibraryAssetKind, boolean>>
  >({});

  const handleDraftStatusChange = useCallback(
    (kind: LibraryAssetKind, status: 'idle' | 'draft' | 'saved') => {
      setDraftSavedByKind((prev) => ({
        ...prev,
        [kind]: status === 'saved',
      }));
    },
    [],
  );

  const onConversionDraftStatusChange = useCallback(
    (status: 'idle' | 'draft' | 'saved') =>
      handleDraftStatusChange('conversion', status),
    [handleDraftStatusChange],
  );
  const onTacValidationDraftStatusChange = useCallback(
    (status: 'idle' | 'draft' | 'saved') =>
      handleDraftStatusChange('tac_validation', status),
    [handleDraftStatusChange],
  );
  const onIwxxmValidationDraftStatusChange = useCallback(
    (status: 'idle' | 'draft' | 'saved') =>
      handleDraftStatusChange('iwxxm_validation', status),
    [handleDraftStatusChange],
  );
  const onDisseminationDraftStatusChange = useCallback(
    (status: 'idle' | 'draft' | 'saved') =>
      handleDraftStatusChange('dissemination', status),
    [handleDraftStatusChange],
  );
  const onDecodingDraftStatusChange = useCallback(
    (status: 'idle' | 'draft' | 'saved') => handleDraftStatusChange('decoding', status),
    [handleDraftStatusChange],
  );

  const inspectorStatus =
    activeTab === 'conversion'
      ? (catalogProfile?.status ?? 'implemented')
      : draftSavedByKind[activeTab]
        ? PROFILES_INSPECTOR_STATUS_DRAFT
        : PROFILES_INSPECTOR_STATUS_READY;

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
        <Button
          type="button"
          variant="ghost"
          size="sm"
          data-testid="profile-builder-reset-wmo-defaults"
          className="ml-auto text-xs text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
          onClick={() => {
            resetWmoLibraryDefaultsSync();
          }}
        >
          {CONVERT_RESET_WMO_LIBRARY_DEFAULTS}
        </Button>
      </div>
      <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
        {PROFILES_LIBRARIES_HELP}
      </p>
      <Tabs
        value={activeTab}
        onValueChange={(value) => setActiveTab(value as LibraryTabValue)}
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
        </TabsList>
        <TabsContent value="conversion" data-testid="profile-library-panel-conversion">
          <ConversionTemplatesPanel accessToken={accessToken} />
          <LibraryDraftShell
            kind="conversion"
            onDraftStatusChange={onConversionDraftStatusChange}
          />
        </TabsContent>
        <TabsContent
          value="tac_validation"
          data-testid="profile-library-panel-tac-validation"
        >
          <LibraryAssetsListPanel
            accessToken={accessToken}
            kind="tac_validation"
            heading={PROFILES_LIBRARY_TAB_TAC_VALIDATION}
          />
          <LibraryDraftShell
            kind="tac_validation"
            onDraftStatusChange={onTacValidationDraftStatusChange}
          />
        </TabsContent>
        <TabsContent
          value="iwxxm_validation"
          data-testid="profile-library-panel-iwxxm-validation"
        >
          <LibraryAssetsListPanel
            accessToken={accessToken}
            kind="iwxxm_validation"
            heading={PROFILES_LIBRARY_TAB_IWXXM_VALIDATION}
          />
          <LibraryDraftShell
            kind="iwxxm_validation"
            onDraftStatusChange={onIwxxmValidationDraftStatusChange}
          />
        </TabsContent>
        <TabsContent
          value="dissemination"
          data-testid="profile-library-panel-dissemination"
        >
          <DisseminationLibraryPanel accessToken={accessToken} />
          <LibraryDraftShell
            kind="dissemination"
            onDraftStatusChange={onDisseminationDraftStatusChange}
          />
        </TabsContent>
        <TabsContent value="decoding" data-testid="profile-library-panel-decoding">
          <DecodingLibraryPanel accessToken={accessToken} />
          <LibraryDraftShell
            kind="decoding"
            onDraftStatusChange={onDecodingDraftStatusChange}
          />
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
            <dd>{LIBRARY_TAB_LABELS[activeTab]}</dd>
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
          ) : activeTab !== 'conversion' ? (
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
