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
} from '../../utils/conversionProfilesCopy';
import { ConversionTemplatesPanel } from './ConversionTemplatesPanel';
import { DecodingLibraryPanel } from './DecodingLibraryPanel';
import { DisseminationLibraryPanel } from './DisseminationLibraryPanel';
import { LibraryAssetsListPanel } from './LibraryAssetsListPanel';
import { Card } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

export type ProfileBuilderLibrariesProps = {
  accessToken: string;
};

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
      {' '}
      <div>
        <h2 className="text-sm font-medium">{PROFILES_LIBRARIES_HEADING}</h2>
        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
          {PROFILES_LIBRARIES_HELP}
        </p>
      </div>
      <Tabs defaultValue="conversion" data-testid="profile-builder-library-tabs">
        <TabsList className="flex h-auto w-full flex-wrap justify-start gap-1">
          <TabsTrigger value="conversion" data-testid="profile-library-tab-conversion">
            {PROFILES_LIBRARY_TAB_CONVERSION}
          </TabsTrigger>
          <TabsTrigger
            value="tac_validation"
            data-testid="profile-library-tab-tac-validation"
          >
            {PROFILES_LIBRARY_TAB_TAC_VALIDATION}
          </TabsTrigger>
          <TabsTrigger
            value="iwxxm_validation"
            data-testid="profile-library-tab-iwxxm-validation"
          >
            {PROFILES_LIBRARY_TAB_IWXXM_VALIDATION}
          </TabsTrigger>
          <TabsTrigger
            value="dissemination"
            data-testid="profile-library-tab-dissemination"
          >
            {PROFILES_LIBRARY_TAB_DISSEMINATION}
          </TabsTrigger>
          <TabsTrigger value="decoding" data-testid="profile-library-tab-decoding">
            {PROFILES_LIBRARY_TAB_DECODING}
          </TabsTrigger>
        </TabsList>
        <TabsContent value="conversion" data-testid="profile-library-panel-conversion">
          <ConversionTemplatesPanel accessToken={accessToken} />
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
        </TabsContent>
        <TabsContent
          value="dissemination"
          data-testid="profile-library-panel-dissemination"
        >
          <DisseminationLibraryPanel accessToken={accessToken} />
        </TabsContent>
        <TabsContent value="decoding" data-testid="profile-library-panel-decoding">
          <DecodingLibraryPanel accessToken={accessToken} />
        </TabsContent>
      </Tabs>
    </Card>
  );
}
