/**
 * Profile builder Libraries shell — five sub-tabs (Conversion + four stubs).
 */

import {
  PROFILES_LIBRARIES_HEADING,
  PROFILES_LIBRARIES_HELP,
  PROFILES_LIBRARY_TAB_CONVERSION,
  PROFILES_LIBRARY_TAB_DECODING,
  PROFILES_LIBRARY_TAB_DISSEMINATION,
  PROFILES_LIBRARY_TAB_IWXXM_VALIDATION,
  PROFILES_LIBRARY_TAB_TAC_VALIDATION,
  PROFILES_TOOLTIP_LIBRARIES,
  PROFILES_TOOLTIP_LIBRARY_TAB_CONVERSION,
  PROFILES_TOOLTIP_LIBRARY_TAB_DECODING,
  PROFILES_TOOLTIP_LIBRARY_TAB_DISSEMINATION,
  PROFILES_TOOLTIP_LIBRARY_TAB_IWXXM_VALIDATION,
  PROFILES_TOOLTIP_LIBRARY_TAB_TAC_VALIDATION,
} from '../../utils/conversionProfilesCopy';
import { BetaBadge } from './BetaBadge';
import { ConversionTemplatesPanel } from './ConversionTemplatesPanel';
import { DecodingLibraryPanel } from './DecodingLibraryPanel';
import { DisseminationLibraryPanel } from './DisseminationLibraryPanel';
import { LibraryAssetsListPanel } from './LibraryAssetsListPanel';
import { LibraryDraftShell } from './LibraryDraftShell';
import { Card } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

export type ProfileBuilderLibrariesProps = {
  accessToken: string;
};

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
 */
export function ProfileBuilderLibraries({ accessToken }: ProfileBuilderLibrariesProps) {
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
      </div>
      <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
        {PROFILES_LIBRARIES_HELP}
      </p>
      <Tabs defaultValue="conversion" data-testid="profile-builder-library-tabs">
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
          <LibraryDraftShell kind="conversion" />
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
          <LibraryDraftShell kind="tac_validation" />
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
          <LibraryDraftShell kind="iwxxm_validation" />
        </TabsContent>
        <TabsContent
          value="dissemination"
          data-testid="profile-library-panel-dissemination"
        >
          <DisseminationLibraryPanel accessToken={accessToken} />
          <LibraryDraftShell kind="dissemination" />
        </TabsContent>
        <TabsContent value="decoding" data-testid="profile-library-panel-decoding">
          <DecodingLibraryPanel accessToken={accessToken} />
          <LibraryDraftShell kind="decoding" />
        </TabsContent>
      </Tabs>
    </Card>
  );
}
